from __future__ import annotations

import json
import logging
import time

from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.core.config import settings
from app.services.notification_sender import (
    build_approved_text,
    build_rejected_text,
    send_telegram_text,
)
from app.services.runtime_redis import get_blocking_redis, reset_blocking_redis

logger = logging.getLogger(__name__)


def _build_text(job: dict) -> str | None:
    kind = str(job.get("kind") or "").strip()
    submission_id = int(job.get("submission_id") or 0)
    comment = job.get("comment")

    if kind == "submission_approved":
        return build_approved_text(submission_id=submission_id, comment=comment)
    if kind == "submission_rejected":
        return build_rejected_text(submission_id=submission_id, comment=comment)
    return None


def run_worker() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    redis = get_blocking_redis()
    queue_keys = [settings.notification_retry_queue_key, settings.notification_queue_key]

    logger.info("Notification worker started")

    while True:
        try:
            item = redis.brpop(
                queue_keys,
                timeout=settings.notification_worker_block_timeout_seconds,
            )
            if not item:
                continue

            _, raw_payload = item
            job = json.loads(raw_payload)
            chat_id = int(job["chat_id"])
            text = _build_text(job)

            if not text:
                logger.warning("Skipped unknown notification job: %s", job)
                continue

            ok, detail = send_telegram_text(chat_id=chat_id, text=text)
            if not ok:
                job["retries"] = int(job.get("retries") or 0) + 1
                logger.warning(
                    "Notification delivery failed (attempt %s) for chat_id=%s submission_id=%s: %s",
                    job["retries"],
                    chat_id,
                    job.get("submission_id"),
                    detail,
                )
                if job["retries"] <= 3:
                    redis.lpush(settings.notification_retry_queue_key, json.dumps(job, ensure_ascii=False))
                    time.sleep(1)
                else:
                    logger.error("Notification permanently failed: %s | detail=%s", job, detail)
                continue

            logger.info("Notification delivered: %s", job)

        except KeyboardInterrupt:
            logger.info("Notification worker stopped")
            break

        except RedisTimeoutError:
            continue

        except RedisConnectionError:
            logger.warning("Redis connection lost in notification worker, reconnecting...")
            time.sleep(2)
            redis = reset_blocking_redis()

        except Exception:
            logger.exception("Notification worker loop error")
            time.sleep(2)
            redis = reset_blocking_redis()
