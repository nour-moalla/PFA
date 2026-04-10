"""Tests for application configuration settings"""
from app.core.config import settings


def test_settings_loads():
    """Test that settings loads successfully"""
    assert settings is not None


def test_settings_has_required_fields():
    """Test that all required configuration fields exist"""
    assert hasattr(settings, 'AI_API_KEY')
    assert hasattr(settings, 'AI_BASE_URL')
    assert hasattr(settings, 'AI_MODEL')
    assert hasattr(settings, 'UPLOAD_FOLDER')
    assert hasattr(settings, 'CORS_ORIGINS')


def test_api_configuration():
    """Test API configuration is set correctly"""
    assert settings.API_TITLE == "UtopiaHire Career Services API"
    assert settings.API_VERSION == "1.0.0"


def test_cors_origins_configured():
    """Test CORS origins are properly configured"""
    assert len(settings.CORS_ORIGINS) > 0
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_file_upload_configuration():
    """Test file upload settings are valid"""
    assert settings.UPLOAD_FOLDER == "uploads"
    assert settings.MAX_FILE_SIZE == 16 * 1024 * 1024
    assert "pdf" in settings.ALLOWED_EXTENSIONS


def test_ai_model_configuration():
    """Test AI model settings"""
    assert settings.EMBEDDING_MODEL_NAME == "all-MiniLM-L6-v2"
    assert settings.AI_BASE_URL == "https://integrate.api.nvidia.com/v1"


def test_career_insights_configuration():
    """Test career insights settings"""
    assert settings.TOP_N_DEMANDED_SKILLS == 10
    assert settings.DEMANDED_SKILLS_CSV_PATH == "data/skill_summary_ranked.csv"


def test_job_matching_configuration():
    """Test job matching settings"""
    assert settings.TOP_K_MATCHES == 6
    assert settings.JOBS_DATABASE_PATH == "data/jobs_database.csv"