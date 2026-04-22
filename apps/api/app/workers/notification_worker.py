from __future__ import annotations

import json
import logging
import time

from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.core.config import settings
from app.services.notification_audit import move_to_dead_letter, record_notification_event
from app.services.notification_sender import (
    build_approved_text,
    build_rejected_text,
    send_telegram_text,
)
from app.services.runtime_redis import get_blocking_redis, get_redis, reset_blocking_redis

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


def _write_heartbeat(now_ts: int) -> None:
    try:
        redis = get_redis()
        redis.set(
            settings.notification_worker_heartbeat_key,
            str(now_ts),
            ex=settings.notification_worker_stale_after_seconds * 3,
        )
    except Exception:
        logger.exception("Failed to write notification worker heartbeat")


def run_worker() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    redis = get_blocking_redis()
    queue_keys = [settings.notification_retry_queue_key, settings.notification_queue_key]
    last_heartbeat_ts = 0

    logger.info("Notification worker started")

    while True:
        try:
            now_ts = int(time.time())
            if now_ts - last_heartbeat_ts >= settings.notification_worker_heartbeat_interval_seconds:
                _write_heartbeat(now_ts)
                last_heartbeat_ts = now_ts

            item = redis.brpop(
                queue_keys,
                timeout=settings.notification_worker_block_timeout_seconds,
            )
            if not item:
                continue

            _, raw_payload = item
            job = json.loads(raw_payload)
            chat_id = int(job["chat_id"])
            kind = str(job.get("kind") or "")
            submission_id = int(job["submission_id"]) if job.get("submission_id") is not None else None
            text = _build_text(job)

            if not text:
                logger.warning("Skipped unknown notification job: %s", job)
                record_notification_event(
                    status="skipped_unknown_kind",
                    kind=kind or "unknown",
                    chat_id=chat_id,
                    submission_id=submission_id,
                    retries=int(job.get("retries") or 0),
                    detail="Unknown notification kind",
                )
                continue

            ok, detail = send_telegram_text(chat_id=chat_id, text=text)
            if not ok:
                job["retries"] = int(job.get("retries") or 0) + 1
                logger.warning(
                    "Notification delivery failed (attempt %s) for chat_id=%s submission_id=%s: %s",
                    job["retries"],
                    chat_id,
                    submission_id,
                    detail,
                )

                if job["retries"] <= 3:
                    record_notification_event(
                        status="retry_scheduled",
                        kind=kind,
                        chat_id=chat_id,
                        submission_id=submission_id,
                        retries=int(job["retries"]),
                        detail=detail,
                    )
                    redis.lpush(settings.notification_retry_queue_key, json.dumps(job, ensure_ascii=False))
                    time.sleep(1)
                else:
                    record_notification_event(
                        status="permanent_failed",
                        kind=kind,
                        chat_id=chat_id,
                        submission_id=submission_id,
                        retries=int(job["retries"]),
                        detail=detail,
                    )
                    move_to_dead_letter(job, detail=detail)
                    logger.error("Notification permanently failed: %s | detail=%s", job, detail)
                continue

            record_notification_event(
                status="delivered",
                kind=kind,
                chat_id=chat_id,
                submission_id=submission_id,
                retries=int(job.get("retries") or 0),
                detail=detail,
            )
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
