"""Tests for rate limiting configuration"""
from app.core.rate_limit import limiter
from slowapi import Limiter

def test_limiter_exists():
    assert limiter is not None

def test_limiter_is_limiter_instance():
    assert isinstance(limiter, Limiter)

def test_limiter_can_be_imported():
    from app.core.rate_limit import limiter as l
    assert l is not None


def test_limiter_key_function_is_remote_address():
    """Test that limiter uses remote address as key function"""
    from slowapi.util import get_remote_address
    # The key function should be get_remote_address
    assert limiter.key_func == get_remote_address
