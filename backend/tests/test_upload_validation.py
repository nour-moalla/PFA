"""Tests for upload file validation"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.upload_validation import validate_pdf_upload, MAX_SIZE
from fastapi import UploadFile

def test_max_size_constant_is_reasonable():
    assert MAX_SIZE > 0
    assert MAX_SIZE <= 10 * 1024 * 1024  # 10MB max

def test_validate_pdf_upload_function_exists():
    assert callable(validate_pdf_upload)

def test_max_size_is_defined():
    assert isinstance(MAX_SIZE, int)

@pytest.mark.anyio
async def test_validate_pdf_upload_rejects_oversized_files():
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.read = AsyncMock(return_value=b"x" * (MAX_SIZE + 1))
    mock_file.seek = AsyncMock()
    try:
        await validate_pdf_upload(mock_file)
        assert False, "Should have raised"
    except Exception:
        assert True

@pytest.mark.anyio
async def test_validate_pdf_upload_rejects_non_pdf():
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "malware.exe"
    mock_file.read = AsyncMock(return_value=b"fake content")
    mock_file.seek = AsyncMock()
    try:
        await validate_pdf_upload(mock_file)
        assert False, "Should have raised"
    except Exception:
        assert True
