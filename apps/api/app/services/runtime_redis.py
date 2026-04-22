from __future__ import annotations

from redis import Redis

from app.core.config import settings


_redis_client: Redis | None = None
_blocking_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=settings.redis_socket_timeout_seconds,
            health_check_interval=30,
        )
    return _redis_client


def get_blocking_redis() -> Redis:
    global _blocking_redis_client
    if _blocking_redis_client is None:
        _blocking_redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=settings.redis_blocking_socket_timeout_seconds,
            health_check_interval=30,
        )
    return _blocking_redis_client


def reset_blocking_redis() -> Redis:
    global _blocking_redis_client
    try:
        if _blocking_redis_client is not None:
            _blocking_redis_client.close()
    except Exception:
        pass

    _blocking_redis_client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=settings.redis_blocking_socket_timeout_seconds,
        health_check_interval=30,
    )
    return _blocking_redis_client
