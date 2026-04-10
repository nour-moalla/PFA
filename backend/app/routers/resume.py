"""
Resume Analysis Router
Handles resume/CV upload, parsing, and ATS analysis
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request  # pragma: no cover
from typing import Optional  # pragma: no cover
from pathlib import Path  # pragma: no cover
from datetime import datetime  # pragma: no cover
import os  # pragma: no cover
import anyio  # pragma: no cover
from app.core.resume_parser import ResumeParser  # pragma: no cover
from app.core.ai_service import ai_service  # pragma: no cover
from app.core.config import settings  # pragma: no cover
from app.core.rate_limit import limiter  # pragma: no cover
from app.core.upload_validation import validate_pdf_upload  # pragma: no cover

router = APIRouter()

# Initialize resume parser
resume_parser = ResumeParser()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    experience: Optional[int] = Form(None)
):
    """
    Upload and parse a resume/CV
    
    - **file**: PDF file containing the resume
    - **job_description**: Optional job description for targeted analysis
    - **job_title**: Optional job title
    - **company**: Optional company name
    - **experience**: Optional years of experience
    """
    # Save uploaded file
    save_folder = Path(settings.UPLOAD_FOLDER)
    save_folder.mkdir(parents=True, exist_ok=True)

    content, safe_name = await validate_pdf_upload(file)
    save_path = save_folder / safe_name
    file_id = Path(safe_name).stem
    
    try:
        async with await anyio.open_file(save_path, "wb") as f:
            await f.write(content)
        
        # Parse resume
        structured_data = resume_parser.parse(save_path)
        extracted_text = resume_parser.extract_text_from_pdf(save_path)
        resume_summary = resume_parser.get_summary_for_analysis(structured_data, max_chars=3000)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "structured_data": structured_data,
            "extracted_text": extracted_text,
            "summary": resume_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    finally:
        # Clean up uploaded file
        if save_path.exists():
            save_path.unlink()


@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    experience: Optional[int] = Form(None)
):
    """
    Analyze resume with ATS scoring and detailed feedback
    
    Returns comprehensive analysis including:
    - Overall ATS score (0-100)
    - Detailed feedback summary
    - Pros and cons
    - ATS criteria ratings
    - Improvement suggestions
    - Top matches and gaps
    """
    # Save uploaded file
    save_folder = Path(settings.UPLOAD_FOLDER)
    save_folder.mkdir(parents=True, exist_ok=True)

    content, safe_name = await validate_pdf_upload(file)
    save_path = save_folder / safe_name
    
    try:
        async with await anyio.open_file(save_path, "wb") as f:
            await f.write(content)
        
        # Parse resume
        structured_data = resume_parser.parse(save_path)
        extracted_text = resume_parser.extract_text_from_pdf(save_path)
        resume_summary = resume_parser.get_summary_for_analysis(structured_data, max_chars=3000)
        
        # Get detected skills and experience
        detected_skills = ', '.join(structured_data.get('skills', [])[:15]) if structured_data.get('skills') else 'Not detected'
        detected_experience = structured_data.get('estimated_experience_years', experience)
        
        # Analyze with AI
        current_date = datetime.now().strftime("%B %d, %Y")
        analysis = ai_service.analyze_resume_ats(
            resume_summary=resume_summary,
            job_description=job_description,
            job_title=job_title,
            company=company,
            experience=detected_experience,
            current_date=current_date
        )
        
        # Add additional metadata
        analysis['extracted_text'] = extracted_text
        analysis['filename'] = file.filename
        analysis['analyzed_at'] = current_date
        analysis['structured_data'] = structured_data
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")
    finally:
        # Clean up uploaded file
        if save_path.exists():
            save_path.unlink()


@router.post("/extract-skills")
async def extract_skills(file: UploadFile = File(...)):
    """
    Extract technical skills from a resume
    
    Returns a list of detected technical skills
    """
    # Save uploaded file
    save_folder = Path(settings.UPLOAD_FOLDER)
    save_folder.mkdir(parents=True, exist_ok=True)

    content, safe_name = await validate_pdf_upload(file)
    save_path = save_folder / safe_name
    
    try:
        async with await anyio.open_file(save_path, "wb") as f:
            await f.write(content)
        
        # Extract text
        extracted_text = resume_parser.extract_text_from_pdf(save_path)
        
        # Extract skills using AI
        skills = ai_service.extract_skills(extracted_text)
        
        # Also get skills from parser
        structured_data = resume_parser.parse(save_path)
        parser_skills = structured_data.get('skills', [])
        
        # Combine and deduplicate
        all_skills = list(set(skills + parser_skills))
        
        return {
            "skills": all_skills,
            "count": len(all_skills),
            "ai_extracted": skills,
            "parser_extracted": parser_skills
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting skills: {str(e)}")
    finally:
        # Clean up uploaded file
        if save_path.exists():
            save_path.unlink()

