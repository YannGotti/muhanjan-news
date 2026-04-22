from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.services.monitoring import get_health_snapshot

router = APIRouter(tags=["monitoring"])


@router.get("/admin/monitoring/summary")
def monitoring_summary(_: str = Depends(get_current_admin)):
    return get_health_snapshot()
