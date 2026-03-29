"""
Career Insights Router
Handles career analysis, skill gap identification, and roadmap generation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json
from fpdf import FPDF
import os
import time
import uuid

from app.core.ai_service import ai_service
from app.core.resume_parser import ResumeParser
from app.core.config import settings
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.decomposition import PCA

router = APIRouter()

# Initialize resume parser
resume_parser = ResumeParser()

# Initialize sentence transformer model (lazy loading)
sentence_model = None


def get_sentence_model():
    """Lazy load sentence transformer model"""
    global sentence_model
    if sentence_model is None:
        sentence_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return sentence_model


@router.get("/market-insights")
async def get_market_insights():
    """
    Get top demanded skills from the market
    
    Returns the top N most demanded skills from the skills database
    """
    try:
        csv_path = Path(settings.DEMANDED_SKILLS_CSV_PATH)
        if not csv_path.exists():
            return {
                "top_10_skills": [],
                "message": "Skills database not found. Please ensure data/skill_summary_ranked.csv exists."
            }
        
        demanded_df = pd.read_csv(csv_path)
        top_10_skills = []
        
        for idx, row in demanded_df.head(settings.TOP_N_DEMANDED_SKILLS).iterrows():
            top_10_skills.append({
                'category': row.get('final_label', 'Unknown'),
                'count': int(row.get('count', 0)),
                'skills': row.get('original_skills', '')
            })
        
        return {
            'top_10_skills': top_10_skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading market insights: {str(e)}")


@router.post("/upload-cv")
async def upload_cv_for_insights(file: UploadFile = File(...)):
    """
    Upload CV for career insights analysis
    
    Returns extracted skills from the CV
    """
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    # Save uploaded file
    save_folder = Path(settings.UPLOAD_FOLDER)
    save_folder.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    save_path = save_folder / f"{file_id}_{file.filename}"
    
    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text from CV
        if file.filename.lower().endswith('.pdf'):
            cv_text = resume_parser.extract_text_from_pdf(save_path)
        else:
            with open(save_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
        
        # Extract skills using AI
        user_cv_skills = ai_service.extract_skills(cv_text)
        
        if not user_cv_skills:
            return {
                'success': False,
                'error': 'No technical skills found in CV',
                'skills': []
            }
        
        return {
            'success': True,
            'skills': user_cv_skills,
            'filename': file.filename,
            'file_id': file_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error processing CV: {str(e)}')
    finally:
        if save_path.exists():
            save_path.unlink()


@router.post("/analyze")
async def analyze_skills(data: Dict):
    """
    Analyze user skills against market demands
    
    Request body should contain:
    - **skills**: List of user's skills
    """
    user_skills = data.get('skills', [])
    
    if not user_skills:
        raise HTTPException(status_code=400, detail='No skills provided')
    
    try:
        # Load demanded skills
        csv_path = Path(settings.DEMANDED_SKILLS_CSV_PATH)
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="Skills database not found")
        
        demanded_df = pd.read_csv(csv_path)
        top_demanded_categories = set(demanded_df.head(settings.TOP_N_DEMANDED_SKILLS)['final_label'])
        demanded_skills_details = demanded_df.head(settings.TOP_N_DEMANDED_SKILLS).set_index('final_label')['original_skills'].to_dict()
        
        # Categorize user skills
        user_has_categories = set(ai_service.categorize_skills(user_skills, list(top_demanded_categories)))
        
        missing_categories = top_demanded_categories - user_has_categories
        
        # Get top 10 demanded skills with details
        top_10_skills = []
        for _, row in demanded_df.head(10).iterrows():
            top_10_skills.append({
                'category': row['final_label'],
                'count': int(row['count']),
                'skills': row['original_skills']
            })
        
        result = {
            'user_categories': list(user_has_categories),
            'missing_categories': list(missing_categories),
            'demanded_categories': list(top_demanded_categories),
            'top_10_skills': top_10_skills
        }
        
        # Generate roadmap if there are missing categories
        if missing_categories:
            missing_details = {cat: demanded_skills_details[cat] for cat in missing_categories}
            roadmap = ai_service.generate_roadmap(user_skills, missing_details)
            result['roadmap'] = roadmap
        else:
            roadmap = "Congratulations! Your skills are highly aligned with market demands!\n\nYour current skills cover all the top demanded categories in the market. Keep enhancing your expertise and stay updated with the latest trends in your field."
            result['roadmap'] = roadmap
        
        # Generate PDF
        timestamp = int(time.time())
        pdf_filename = f"roadmap_{timestamp}.pdf"
        pdf_path = create_pdf(roadmap, pdf_filename)
        
        if pdf_path and Path(pdf_path).exists():
            result['pdf_url'] = f'/api/career/download/{os.path.basename(pdf_path)}'
        else:
            result['pdf_url'] = None
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Analysis error: {str(e)}')


@router.post("/cluster-skills")
async def cluster_skills(data: Dict):
    """
    Cluster skills and create visualization data
    
    Request body should contain:
    - **skills**: List of skills to cluster
    """
    skills_list = data.get('skills', [])
    
    if not skills_list or len(skills_list) < 3:
        return {
            "error": "Need at least 3 skills to perform clustering",
            "clusters": None
        }
    
    try:
        model = get_sentence_model()
        unique_skills = list(set(skills_list))
        
        # Generate embeddings
        skill_embeddings = np.array([model.encode(skill) for skill in unique_skills])
        
        # Cluster with HDBSCAN
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=max(2, len(unique_skills) // 10),
            min_samples=1,
            metric='euclidean',
            cluster_selection_epsilon=0.05,
            cluster_selection_method='leaf'
        )
        clusterer.fit(skill_embeddings)
        
        # Create dataframe
        df = pd.DataFrame({
            'skill': unique_skills,
            'cluster': clusterer.labels_
        })
        
        # PCA for visualization
        pca = PCA(n_components=2, random_state=42)
        embedding_2d = pca.fit_transform(skill_embeddings)
        df['x'] = embedding_2d[:, 0]
        df['y'] = embedding_2d[:, 1]
        
        # Label clusters using LLM
        cluster_labels = {}
        for cluster_id in df[df['cluster'] != -1]['cluster'].unique():
            skills_in_cluster = df[df['cluster'] == cluster_id]['skill'].tolist()
            if len(skills_in_cluster) > 0:
                skills_str = ", ".join(skills_in_cluster[:10])
                category_name = ai_service.chat_completion(
                    system_prompt="You are an expert technical recruiter.",
                    user_prompt=f"Based on these skills, provide ONE concise category name (2-3 words max): {skills_str}",
                    temperature=0.1,
                    max_tokens=20
                )
                cluster_labels[cluster_id] = category_name.strip()
        
        df['category'] = df['cluster'].map(lambda x: cluster_labels.get(x, 'Uncategorized'))
        
        return {
            "clusters": df.to_dict('records'),
            "cluster_labels": cluster_labels
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clustering skills: {str(e)}")


def create_pdf(content: str, filename: str = "roadmap.pdf") -> Optional[str]:
    """Create a PDF from text content"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Your Personalized Career Roadmap", ln=True, align='C')
        pdf.ln(5)
        
        # Add content
        pdf.set_font("Arial", size=10)
        
        # Clean content - remove emojis and special characters
        clean_content = content.encode('latin-1', 'ignore').decode('latin-1')
        
        for line in clean_content.split("\n"):
            if line.strip():
                try:
                    pdf.multi_cell(0, 6, line.strip())
                except:
                    simple_line = ''.join(c for c in line if ord(c) < 128)
                    if simple_line.strip():
                        pdf.multi_cell(0, 6, simple_line.strip())
            else:
                pdf.ln(3)
        
        pdf_path = Path("static") / filename
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(pdf_path))
        return str(pdf_path)
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """Download generated roadmap PDF"""
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.startswith("roadmap_") or not safe_name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = Path("static") / safe_name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=safe_name
    )

