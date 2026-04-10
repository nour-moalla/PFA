"""Tests for upload file validation"""
import pytest
from io import BytesIO
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.uploadfile import UploadFile
from fastapi import HTTPException

from app.core.upload_validation import validate_pdf_upload, MAX_SIZE


@pytest.mark.asyncio
async def test_validate_pdf_upload_rejects_oversized_files():
    """Test that files larger than MAX_SIZE are rejected"""
    # Create a mock file larger than MAX_SIZE
    oversized_content = b"x" * (MAX_SIZE + 1)
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=oversized_content)
    mock_file.filename = "large_file.pdf"
    
    with pytest.raises(HTTPException) as exc_info:
        await validate_pdf_upload(mock_file)
    
    assert exc_info.value.status_code == 400
    assert "too large" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_validate_pdf_upload_rejects_non_pdf():
    """Test that non-PDF files are rejected"""
    # Create mock file with incorrect MIME type
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"fake image data")
    mock_file.filename = "image.txt"
    
    with patch('app.core.upload_validation.magic.from_buffer') as mock_magic:
        mock_magic.return_value = "text/plain"  # Not PDF
        
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf_upload(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "pdf" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_validate_pdf_upload_accepts_valid_pdf():
    """Test that valid PDF files are accepted"""
    # Minimal valid PDF header
    valid_pdf_content = b"%PDF-1.4\n%fake pdf content"
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=valid_pdf_content)
    mock_file.filename = "valid.pdf"
    
    with patch('app.core.upload_validation.magic.from_buffer') as mock_magic:
        mock_magic.return_value = "application/pdf"
        
        content, safe_name = await validate_pdf_upload(mock_file)
        
        assert content == valid_pdf_content
        assert safe_name.endswith('.pdf')
        assert len(safe_name) > 5  # UUID + .pdf


@pytest.mark.asyncio
async def test_validate_pdf_upload_generates_safe_filename():
    """Test that filename is safely generated with UUID"""
    valid_pdf_content = b"%PDF-1.4\ntest"
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=valid_pdf_content)
    mock_file.filename = "../../malicious/path/file.pdf"
    
    with patch('app.core.upload_validation.magic.from_buffer') as mock_magic:
        mock_magic.return_value = "application/pdf"
        
        content, safe_name = await validate_pdf_upload(mock_file)
        
        # Safe name should not contain path separators
        assert ".." not in safe_name
        assert "/" not in safe_name
        assert "\\" not in safe_name
        assert safe_name.endswith('.pdf')


@pytest.mark.asyncio
async def test_validate_pdf_upload_exact_max_size():
    """Test that files exactly at MAX_SIZE are accepted"""
    exact_size_content = b"x" * MAX_SIZE
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=exact_size_content)
    mock_file.filename = "exact_size.pdf"
    
    with patch('app.core.upload_validation.magic.from_buffer') as mock_magic:
        mock_magic.return_value = "application/pdf"
        
        content, safe_name = await validate_pdf_upload(mock_file)
        
        assert content == exact_size_content
        assert safe_name.endswith('.pdf')


def test_max_size_constant_is_reasonable():
    """Test that MAX_SIZE constant is set to 5MB"""
    assert MAX_SIZE == 5 * 1024 * 1024
