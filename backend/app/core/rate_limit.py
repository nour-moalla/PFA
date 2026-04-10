"""
Rate limiting configuration shared across routers.
"""

from slowapi import Limiter  # pragma: no cover
from slowapi.util import get_remote_address  # pragma: no cover


limiter = Limiter(key_func=get_remote_address)
