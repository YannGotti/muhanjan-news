from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.schemas.admin import ModerationToggleRequest
from app.schemas.common import ModerationModeResponse
from app.services.settings import is_moderation_enabled, set_moderation_enabled

router = APIRouter(tags=["settings"])


@router.get('/settings/public', response_model=ModerationModeResponse)
def public_settings(db: Session = Depends(get_db)) -> ModerationModeResponse:
    return ModerationModeResponse(moderation_enabled=is_moderation_enabled(db))


@router.get('/admin/settings/moderation', response_model=ModerationModeResponse)
def get_moderation_setting(
    _: str = Depends(get_current_admin), db: Session = Depends(get_db)
) -> ModerationModeResponse:
    return ModerationModeResponse(moderation_enabled=is_moderation_enabled(db))


@router.post('/admin/settings/moderation', response_model=ModerationModeResponse)
def set_moderation_setting(
    payload: ModerationToggleRequest,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ModerationModeResponse:
    value = set_moderation_enabled(db, payload.moderation_enabled)
    return ModerationModeResponse(moderation_enabled=value)
