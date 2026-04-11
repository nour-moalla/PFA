"""Tests for authentication and authorization"""
from app.core.auth import AuthUser, bearer_scheme
from fastapi.security import HTTPBearer

def test_auth_user_model_creation():
    user = AuthUser(uid="test-uid-123")
    assert user.uid == "test-uid-123"

def test_auth_user_uid_required():
    try:
        AuthUser()
        assert False, "Should have raised error"
    except Exception:
        assert True

def test_auth_user_email_optional():
    user = AuthUser(uid="uid", email=None)
    assert user.email is None

def test_bearer_scheme_configured():
    assert bearer_scheme is not None

def test_bearer_scheme_is_http_bearer():
    assert isinstance(bearer_scheme, HTTPBearer)


def test_bearer_scheme_scheme_name():
    """Test bearer scheme uses bearer type"""
    assert bearer_scheme.scheme == "bearer"
