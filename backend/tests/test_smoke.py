def test_app_imports():
    from app.core.config import settings
    assert settings is not None