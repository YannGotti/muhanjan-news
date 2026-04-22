from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.notification_audit import read_dead_letter_items, read_notification_audit
from app.services.runtime_redis import get_redis


def check_database() -> dict[str, Any]:
    started = time.perf_counter()
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": True,
            "duration_ms": duration_ms,
        }
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "duration_ms": duration_ms,
            "error": f"{exc.__class__.__name__}: {exc}",
        }
    finally:
        db.close()


def check_redis() -> dict[str, Any]:
    started = time.perf_counter()
    try:
        redis = get_redis()
        pong = redis.ping()
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": bool(pong),
            "duration_ms": duration_ms,
        }
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "duration_ms": duration_ms,
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def get_notification_metrics() -> dict[str, Any]:
    try:
        redis = get_redis()
        main_queue = redis.llen(settings.notification_queue_key)
        retry_queue = redis.llen(settings.notification_retry_queue_key)
        dead_queue = redis.llen(settings.notification_dead_letter_queue_key)

        heartbeat_raw = redis.get(settings.notification_worker_heartbeat_key)
        now = int(time.time())
        heartbeat_ts = int(heartbeat_raw) if heartbeat_raw else None

        if heartbeat_ts is None:
            worker_alive = False
            worker_age_seconds = None
        else:
            worker_age_seconds = max(now - heartbeat_ts, 0)
            worker_alive = worker_age_seconds <= settings.notification_worker_stale_after_seconds

        return {
            "queue_main": int(main_queue),
            "queue_retry": int(retry_queue),
            "queue_dead": int(dead_queue),
            "worker_last_heartbeat_ts": heartbeat_ts,
            "worker_age_seconds": worker_age_seconds,
            "worker_alive": worker_alive,
        }
    except Exception as exc:
        return {
            "queue_main": None,
            "queue_retry": None,
            "queue_dead": None,
            "worker_last_heartbeat_ts": None,
            "worker_age_seconds": None,
            "worker_alive": False,
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def get_health_snapshot() -> dict[str, Any]:
    db = check_database()
    redis = check_redis()
    notifications = get_notification_metrics()

    ready = bool(db.get("ok")) and bool(redis.get("ok")) and bool(notifications.get("worker_alive"))

    return {
        "status": "ok" if ready else "degraded",
        "ready": ready,
        "database": db,
        "redis": redis,
        "notifications": notifications,
    }


def get_notification_audit_snapshot(limit: int = 20) -> dict[str, Any]:
    return {
        "notifications": get_notification_metrics(),
        "recent_events": read_notification_audit(limit=limit),
        "dead_letter_items": read_dead_letter_items(limit=limit),
    }
