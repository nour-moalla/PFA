"""
Authentication and authorization helpers.
"""

from typing import Optional, Annotated
import json

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials as firebase_credentials
import firebase_admin

from app.core.config import settings


bearer_scheme = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    """Authenticated user details extracted from Firebase token."""

    uid: str
    email: Optional[str] = None


def _initialize_firebase() -> bool:
    """Initialize Firebase Admin app once. Returns True when available."""
    if firebase_admin._apps:
        return True

    try:
        if settings.FIREBASE_CREDENTIALS_JSON:
            cred = firebase_credentials.Certificate(json.loads(settings.FIREBASE_CREDENTIALS_JSON))
            firebase_admin.initialize_app(cred)
        elif settings.FIREBASE_CREDENTIALS_FILE:
            cred = firebase_credentials.Certificate(settings.FIREBASE_CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to ADC for container/cloud environments.
            firebase_admin.initialize_app()
        return True
    except Exception:
        return False


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)] = None,
) -> AuthUser:
    """Validate Firebase ID token and return authenticated user."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    if not _initialize_firebase():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured",
        )

    token = credentials.credentials
    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from exc

    return AuthUser(uid=decoded_token.get("uid", ""), email=decoded_token.get("email"))
