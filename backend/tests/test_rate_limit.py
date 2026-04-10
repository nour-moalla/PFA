"""Tests for rate limiting configuration"""
from app.core.rate_limit import limiter


def test_limiter_exists():
    """Test that rate limiter is properly initialized"""
    assert limiter is not None


def test_limiter_is_limiter_instance():
    """Test that limiter is an instance of slowapi Limiter"""
    from slowapi import Limiter
    assert isinstance(limiter, Limiter)


def test_limiter_has_key_function():
    """Test that limiter has a key function configured"""
    assert limiter.key_func is not None
    assert callable(limiter.key_func)


def test_limiter_key_function_is_remote_address():
    """Test that limiter uses remote address as key function"""
    from slowapi.util import get_remote_address
    # The key function should be get_remote_address
    assert limiter.key_func == get_remote_address
