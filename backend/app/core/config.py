"""
Configuration settings for the application
"""

import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "UtopiaHire Career Services API"
    API_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ]
    
    # AI Service Configuration
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "meta/llama-3.1-405b-instruct")
    
    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "docx"]
    
    # Career Insights Configuration
    DEMANDED_SKILLS_CSV_PATH: str = "data/skill_summary_ranked.csv"
    TOP_N_DEMANDED_SKILLS: int = 10
    
    # Job Matching Configuration
    JOBS_DATABASE_PATH: str = "data/jobs_database.csv"
    TOP_K_MATCHES: int = 6
    
    # Interview Configuration
    MAX_QUESTIONS: int = 10
    MIN_QUESTIONS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

