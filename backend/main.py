"""
Unified Backend API for UtopiaHire Career Services
Combines features from:
- AI Interviewer
- Career Insight Report
- CV Reviewer
- Job Matcher
"""

import logging
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.routers import (
    resume,
    interview,
    career_insights,
    job_matching
)
from app.core.config import settings
from app.core.auth import get_current_user

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="UtopiaHire Career Services API",
    description=" Unified backend API providing comprehensive career services: ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    resume.router,
    prefix="/api/resume",
    tags=["Resume Analysis"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    interview.router,
    prefix="/api/interview",
    tags=["AI Interview"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    career_insights.router,
    prefix="/api/career",
    tags=["Career Insights"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    job_matching.router,
    prefix="/api/jobs",
    tags=["Job Matching"],
    dependencies=[Depends(get_current_user)],
)

logger.info("UtopiaHire Career Services API started successfully")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "UtopiaHire Career Services API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "UtopiaHire Career Services API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/api/resume/analyze")
