from __future__ import annotations

from muhanjan_bot.config import settings
from muhanjan_bot.services.redis_runtime import redis_runtime


async def acquire_submission_cooldown(user_id: int) -> tuple[bool, int]:
    redis = redis_runtime.get_client()
    key = f"mn:submit:cooldown:{user_id}"

    allowed = await redis.set(
        key,
        "1",
        ex=settings.submission_cooldown_seconds,
        nx=True,
    )
    if allowed:
        return True, 0

    ttl = await redis.ttl(key)
    return False, max(int(ttl or 1), 1)


async def register_submission_message(user_id: int, message_id: int) -> bool:
    redis = redis_runtime.get_client()
    key = f"mn:submit:message:{user_id}:{message_id}"

    created = await redis.set(
        key,
        "1",
        ex=settings.submission_deduplicate_ttl_seconds,
        nx=True,
    )
    return bool(created)
