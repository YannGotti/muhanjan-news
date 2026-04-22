from __future__ import annotations

import json

from muhanjan_bot.config import settings
from muhanjan_bot.services.redis_runtime import redis_runtime


def _draft_key(user_id: int) -> str:
    return f"mn:draft:{user_id}"


def _album_notice_key(user_id: int, media_group_id: str) -> str:
    return f"mn:draft:notice:{user_id}:{media_group_id}"


def _default_payload(telegram_id: int) -> dict:
    return {
        "telegram_id": telegram_id,
        "message_text": "",
        "source_message_id": None,
        "attachments": [],
        "links": [],
    }


def _merge_payloads(base: dict, part: dict) -> dict:
    result = dict(base)

    incoming_text = (part.get("message_text") or "").strip()
    current_text = (result.get("message_text") or "").strip()
    if incoming_text and not current_text:
        result["message_text"] = incoming_text

    current_links = list(result.get("links") or [])
    for link in list(part.get("links") or []):
        if link not in current_links:
            current_links.append(link)
    result["links"] = current_links

    attachments = list(result.get("attachments") or [])
    attachments.extend(list(part.get("attachments") or []))
    result["attachments"] = attachments

    if result.get("source_message_id") is None and part.get("source_message_id") is not None:
        result["source_message_id"] = part.get("source_message_id")

    return result


async def get_draft_payload(user_id: int) -> dict | None:
    redis = redis_runtime.get_client()
    raw = await redis.get(_draft_key(user_id))
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        return None


async def save_draft_payload(user_id: int, payload: dict) -> None:
    redis = redis_runtime.get_client()
    await redis.set(
        _draft_key(user_id),
        json.dumps(payload, ensure_ascii=False),
        ex=settings.draft_ttl_seconds,
    )


async def clear_draft_payload(user_id: int) -> None:
    redis = redis_runtime.get_client()
    await redis.delete(_draft_key(user_id))


async def append_album_part(user_id: int, media_group_id: str, part: dict) -> dict:
    current = await get_draft_payload(user_id)
    if not current:
        current = _default_payload(user_id)

    merged = _merge_payloads(current, part)
    merged["draft_type"] = "album"
    merged["media_group_id"] = media_group_id

    await save_draft_payload(user_id, merged)
    return merged


async def acquire_album_notice(user_id: int, media_group_id: str) -> bool:
    redis = redis_runtime.get_client()
    created = await redis.set(
        _album_notice_key(user_id, media_group_id),
        "1",
        ex=60,
        nx=True,
    )
    return bool(created)


def draft_has_content(payload: dict | None) -> bool:
    if not payload:
        return False

    return bool(
        (payload.get("message_text") or "").strip()
        or payload.get("attachments")
        or payload.get("links")
    )
