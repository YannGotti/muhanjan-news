from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import SubmissionOut, UserOut


class ReviewRequest(BaseModel):
    comment: str | None = None


class BanRequest(BaseModel):
    reason: str | None = None


class ModerationToggleRequest(BaseModel):
    moderation_enabled: bool


class ModerationActionOut(BaseModel):
    id: int
    submission_id: int | None
    action_type: str
    actor_username: str
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserDetailStats(BaseModel):
    total_submissions: int
    pending: int
    approved: int
    rejected: int


class UserDetailsResponse(BaseModel):
    user: UserOut
    stats: UserDetailStats
    recent_submissions: list[SubmissionOut]
    actions: list[ModerationActionOut]
