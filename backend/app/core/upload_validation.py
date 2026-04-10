"""
Secure upload validation helpers.
"""

from typing import Tuple  # pragma: no cover
from uuid import uuid4  # pragma: no cover

import magic  # pragma: no cover
from fastapi import HTTPException, UploadFile  # pragma: no cover


MAX_SIZE = 5 * 1024 * 1024  # 5MB


async def validate_pdf_upload(file: UploadFile) -> Tuple[bytes, str]:
    """Validate uploaded file content and return bytes with a safe storage name."""
    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")

    mime = magic.from_buffer(content, mime=True)
    if mime != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")

    safe_name = f"{uuid4()}.pdf"
    return content, safe_name
