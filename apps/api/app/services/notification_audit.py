from __future__ import annotations

import json
import time
from typing import Any

from app.core.config import settings
from app.services.runtime_redis import get_redis


def record_notification_event(
    *,
    status: str,
    kind: str,
    chat_id: int,
    submission_id: int | None,
    retries: int = 0,
    detail: str | None = None,
) -> None:
    payload = {
        "timestamp": int(time.time()),
        "status": status,
        "kind": kind,
        "chat_id": int(chat_id),
        "submission_id": submission_id,
        "retries": int(retries),
        "detail": (detail or "").strip() or None,
    }

    redis = get_redis()
    redis.lpush(settings.notification_audit_list_key, json.dumps(payload, ensure_ascii=False))
    redis.ltrim(settings.notification_audit_list_key, 0, max(settings.notification_audit_max_items - 1, 0))


def move_to_dead_letter(job: dict, detail: str | None = None) -> None:
    payload: dict[str, Any] = dict(job)
    payload["dead_lettered_at"] = int(time.time())
    payload["detail"] = (detail or "").strip() or None

    redis = get_redis()
    redis.lpush(settings.notification_dead_letter_queue_key, json.dumps(payload, ensure_ascii=False))


def read_notification_audit(limit: int = 20) -> list[dict[str, Any]]:
    redis = get_redis()
    rows = redis.lrange(settings.notification_audit_list_key, 0, max(limit - 1, 0))
    items: list[dict[str, Any]] = []
    for raw in rows:
        try:
            items.append(json.loads(raw))
        except Exception:
            continue
    return items


def read_dead_letter_items(limit: int = 20) -> list[dict[str, Any]]:
    redis = get_redis()
    rows = redis.lrange(settings.notification_dead_letter_queue_key, 0, max(limit - 1, 0))
    items: list[dict[str, Any]] = []
    for raw in rows:
        try:
            items.append(json.loads(raw))
        except Exception:
            continue
    return items
