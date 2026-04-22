from __future__ import annotations

from app.core.config import settings
from app.services.runtime_redis import get_redis


def _key(login_identity: str) -> str:
    return f"mn:auth:login:{login_identity}"


def is_login_allowed(login_identity: str) -> bool:
    redis = get_redis()
    value = redis.get(_key(login_identity))
    if value is None:
        return True
    try:
        attempts = int(value)
    except Exception:
        attempts = settings.auth_login_rate_limit_attempts
    return attempts < settings.auth_login_rate_limit_attempts


def register_login_failure(login_identity: str) -> int:
    redis = get_redis()
    key = _key(login_identity)
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, settings.auth_login_rate_limit_window_seconds)
    result = pipe.execute()
    return int(result[0])


def clear_login_failures(login_identity: str) -> None:
    redis = get_redis()
    redis.delete(_key(login_identity))
