from __future__ import annotations

import json

from app.services.runtime_redis import get_redis
from app.core.config import settings


def _enqueue(payload: dict) -> bool:
    try:
        redis = get_redis()
        redis.lpush(settings.notification_queue_key, json.dumps(payload, ensure_ascii=False))
        return True
    except Exception:
        return False


def notify_submission_approved(chat_id: int, submission_id: int, comment: str | None = None) -> bool:
    return _enqueue(
        {
            "kind": "submission_approved",
            "chat_id": int(chat_id),
            "submission_id": int(submission_id),
            "comment": (comment or "").strip() or None,
        }
    )


def notify_submission_rejected(chat_id: int, submission_id: int, comment: str | None = None) -> bool:
    return _enqueue(
        {
            "kind": "submission_rejected",
            "chat_id": int(chat_id),
            "submission_id": int(submission_id),
            "comment": (comment or "").strip() or None,
        }
    )
