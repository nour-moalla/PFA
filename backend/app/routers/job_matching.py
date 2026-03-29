"""
Job Matching Router
Handles CV-to-job matching using semantic search
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
import pandas as pd
import numpy as np
# Temporarily commented due to Python 3.13 compatibility issues
# import torch
import ast

from app.core.ai_service import ai_service
from app.core.resume_parser import ResumeParser
from app.core.config import settings
from app.core.upload_validation import validate_pdf_upload
# from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize resume parser
resume_parser = ResumeParser()

# Initialize embedding model (lazy loading)
embedding_model = None
jobs_df = None
job_embeddings = None


def get_embedding_model():
    """Lazy load embedding model"""
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return embedding_model


def load_jobs_database():
    """Load jobs database and embeddings"""
    global jobs_df, job_embeddings
    
    if jobs_df is not None:
        return jobs_df, job_embeddings
    
    try:
        csv_path = Path(settings.JOBS_DATABASE_PATH)
        if not csv_path.exists():
            return None, None
        
        jobs_df = pd.read_csv(csv_path)
        
        # Parse embeddings if they exist
        if 'embedding' in jobs_df.columns:
            jobs_df['embedding'] = jobs_df['embedding'].apply(ast.literal_eval)
            job_embeddings = np.array(jobs_df['embedding'].tolist(), dtype=np.float32)
        else:
            # Generate embeddings if not present
            model = get_embedding_model()
            job_embeddings = np.array([
                model.encode(str(row.get('description', '')), normalize_embeddings=True)
                for _, row in jobs_df.iterrows()
            ], dtype=np.float32)
        
        return jobs_df, job_embeddings
    except Exception as e:
        logger.error("Error loading jobs database: %s", str(e))
        return None, None


@router.post("/match-cv")
async def match_cv(file: UploadFile = File(...)):
    """
    Match a CV against the job database
    
    Returns top matching jobs based on semantic similarity
    """
    # Load jobs database
    jobs_df, job_embeddings = load_jobs_database()
    
    if jobs_df is None or job_embeddings is None:
        raise HTTPException(
            status_code=503,
            detail="Jobs database not available. Please ensure data/jobs_database.csv exists."
        )
    
    # Save uploaded file
    save_folder = Path(settings.UPLOAD_FOLDER)
    save_folder.mkdir(parents=True, exist_ok=True)

    content, safe_name = await validate_pdf_upload(file)
    save_path = save_folder / safe_name
    
    try:
        with open(save_path, "wb") as f:
            f.write(content)
        
        # Extract text from CV
        cv_text = resume_parser.extract_text_from_pdf(save_path)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Get structured CV data using AI
        current_date = datetime.now().strftime("%B %d, %Y")
        structured_cv_data = ai_service.extract_cv_data(cv_text, current_date)
        
        # Extract match_context for embedding
        cv_match_context = structured_cv_data.get('match_context', cv_text[:1000])
        
        if not cv_match_context:
            raise HTTPException(status_code=500, detail="Failed to generate match context from CV")
        
        # Embed the CV's match_context
        model = get_embedding_model()
        cv_embedding = model.encode(cv_match_context, normalize_embeddings=True)
        
        # Perform semantic search
        top_k = settings.TOP_K_MATCHES
        try:
            search_results = util.semantic_search(
                torch.tensor(cv_embedding),
                torch.tensor(job_embeddings),
                top_k=top_k
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")
        
        # Format the output
        top_matches = []
        if not search_results or len(search_results) == 0:
            raise HTTPException(status_code=500, detail="No search results returned")
        
        for result in search_results[0]:
            try:
                job_index = result.get('corpus_id', -1)
                if job_index < 0 or job_index >= len(jobs_df):
                    continue
                
                job_data = jobs_df.iloc[job_index]
                
                # Safely convert score to float, handling NaN and infinity
                score = result.get('score', 0.0)
                try:
                    if isinstance(score, torch.Tensor):
                        score = score.item()
                    
                    score = float(score)
                    
                    # Check for NaN or infinity
                    if np.isnan(score) or np.isinf(score):
                        score = 0.0
                    else:
                        # Ensure score is within valid JSON float range and clamp to [0, 1] for similarity
                        score = max(0.0, min(1.0, score))
                except (ValueError, TypeError, OverflowError):
                    score = 0.0
                
                top_matches.append({
                    "title": str(job_data.get("title", "N/A")),
                    "description": str(job_data.get("description", "N/A")),
                    "company": str(job_data.get("company", "N/A")),
                    "location": str(job_data.get("location", "N/A")),
                    "job_url": str(job_data.get("job_url", "N/A")),
                    "similarity_score": round(score, 4)  # Round to 4 decimal places for JSON compliance
                })
            except Exception as e:
                # Skip invalid results but continue processing
                logger.warning("Skipping invalid search result: %s", str(e))
                continue
        
        return {
            "matches": top_matches,
            "cv_data": structured_cv_data,
            "total_jobs_searched": len(jobs_df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching CV: {str(e)}")
    finally:
        if save_path.exists():
            save_path.unlink()


@router.get("/database-info")
async def get_database_info():
    """Get information about the jobs database"""
    jobs_df, job_embeddings = load_jobs_database()
    
    if jobs_df is None:
        return {
            "available": False,
            "message": "Jobs database not loaded"
        }
    
    return {
        "available": True,
        "total_jobs": len(jobs_df),
        "columns": list(jobs_df.columns),
        "has_embeddings": job_embeddings is not None,
        "embedding_dimension": job_embeddings.shape[1] if job_embeddings is not None else None
    }

