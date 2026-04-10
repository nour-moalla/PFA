"""Pytest configuration and shared fixtures"""
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_auth_user():
    """Fixture for a mock authenticated user"""
    from app.core.auth import AuthUser
    return AuthUser(uid="test-user-123", email="test@example.com")


@pytest.fixture
def mock_pdf_file():
    """Fixture for a mock PDF UploadFile"""
    from fastapi.uploadfile import UploadFile
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest content")
    return mock_file


@pytest.fixture
def mock_invalid_file():
    """Fixture for a mock invalid/non-PDF file"""
    from fastapi.uploadfile import UploadFile
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "malware.exe"
    mock_file.content_type = "application/x-msdownload"
    mock_file.read = AsyncMock(return_value=b"MZ\x90\x00\x03")  # PE header
    return mock_file


@pytest.fixture
def settings_override():
    """Fixture to allow overriding settings in tests"""
    from app.core.config import settings
    original_values = {}
    
    def set_setting(key, value):
        original_values[key] = getattr(settings, key)
        setattr(settings, key, value)
    
    yield set_setting
    
    # Restore original values after test
    for key, value in original_values.items():
        setattr(settings, key, value)


# Configure pytest markers
def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (deselect with '-m \"not asyncio\"')"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
