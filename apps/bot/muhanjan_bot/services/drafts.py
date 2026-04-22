from __future__ import annotations

import json
from datetime import datetime, timezone

from muhanjan_bot.config import settings
from muhanjan_bot.services.redis_runtime import redis_runtime


def _draft_key(user_id: int) -> str:
    return f"mn:draft:{user_id}"


def _album_notice_key(user_id: int, media_group_id: str) -> str:
    return f"mn:draft:notice:{user_id}:{media_group_id}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_payload(telegram_id: int) -> dict:
    return {
        "telegram_id": telegram_id,
        "message_text": "",
        "source_message_id": None,
        "attachments": [],
        "links": [],
        "draft_type": "manual",
        "media_group_id": None,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
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

    result["updated_at"] = _now_iso()
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


async def get_draft_ttl(user_id: int) -> int:
    redis = redis_runtime.get_client()
    ttl = await redis.ttl(_draft_key(user_id))
    return max(int(ttl or 0), 0)


async def save_draft_payload(user_id: int, payload: dict) -> None:
    redis = redis_runtime.get_client()
    payload["updated_at"] = _now_iso()
    await redis.set(
        _draft_key(user_id),
        json.dumps(payload, ensure_ascii=False),
        ex=settings.draft_ttl_seconds,
    )


async def clear_draft_payload(user_id: int) -> None:
    redis = redis_runtime.get_client()
    await redis.delete(_draft_key(user_id))


async def append_album_part(user_id: int, media_group_id: str, part: dict) -> tuple[dict, bool]:
    current = await get_draft_payload(user_id)
    replaced = False

    if not current:
        current = _default_payload(user_id)
    elif current.get("draft_type") == "album" and current.get("media_group_id") not in (None, media_group_id):
        current = _default_payload(user_id)
        replaced = True

    merged = _merge_payloads(current, part)
    merged["draft_type"] = "album"
    merged["media_group_id"] = media_group_id

    await save_draft_payload(user_id, merged)
    return merged, replaced


async def acquire_album_notice(user_id: int, media_group_id: str) -> bool:
    redis = redis_runtime.get_client()
    created = await redis.set(
        _album_notice_key(user_id, media_group_id),
        "1",
        ex=60,
        nx=True,
    )
    return bool(created)


async def append_text_to_draft(user_id: int, text: str) -> dict | None:
    current = await get_draft_payload(user_id)
    if not current:
        return None

    existing = (current.get("message_text") or "").strip()
    addition = text.strip()
    if not addition:
        return current

    if existing:
        current["message_text"] = f"{existing}\n\n{addition}"
    else:
        current["message_text"] = addition

    await save_draft_payload(user_id, current)
    return current


def draft_has_content(payload: dict | None) -> bool:
    if not payload:
        return False

    return bool(
        (payload.get("message_text") or "").strip()
        or payload.get("attachments")
        or payload.get("links")
    )


def format_ttl_text(ttl_seconds: int) -> str:
    if ttl_seconds <= 0:
        return "меньше минуты"

    minutes, seconds = divmod(ttl_seconds, 60)
    if minutes <= 0:
        return f"{seconds} сек."

    if seconds == 0:
        return f"{minutes} мин."
    return f"{minutes} мин. {seconds} сек."
