"""Tests for authentication and authorization"""
from unittest.mock import patch, MagicMock
import pytest
from fastapi import HTTPException
from app.core.auth import AuthUser, bearer_scheme


def test_auth_user_model_creation():
    """Test that AuthUser model can be created"""
    user = AuthUser(uid="test-uid", email="test@example.com")
    
    assert user.uid == "test-uid"
    assert user.email == "test@example.com"


def test_auth_user_uid_required():
    """Test that AuthUser requires uid"""
    with pytest.raises(Exception):  # Pydantic validation error
        AuthUser(email="test@example.com")


def test_auth_user_email_optional():
    """Test that AuthUser email is optional"""
    user = AuthUser(uid="test-uid")
    
    assert user.uid == "test-uid"
    assert user.email is None


def test_bearer_scheme_configured():
    """Test that bearer scheme is properly configured"""
    from fastapi.security import HTTPBearer
    assert isinstance(bearer_scheme, HTTPBearer)
    # auto_error=False allows the function to handle missing auth gracefully
    assert bearer_scheme.auto_error is False


def test_bearer_scheme_scheme_name():
    """Test bearer scheme uses bearer type"""
    assert bearer_scheme.scheme == "bearer"
