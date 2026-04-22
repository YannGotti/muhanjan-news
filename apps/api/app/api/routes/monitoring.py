from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.services.monitoring import get_health_snapshot, get_notification_audit_snapshot

router = APIRouter(tags=["monitoring"])


@router.get("/admin/monitoring/summary")
def monitoring_summary(_: str = Depends(get_current_admin)):
    return get_health_snapshot()


@router.get("/admin/monitoring/notifications")
def monitoring_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    _: str = Depends(get_current_admin),
):
    return get_notification_audit_snapshot(limit=limit)
