from pydantic import BaseModel


class ReviewRequest(BaseModel):
    comment: str | None = None


class BanRequest(BaseModel):
    reason: str | None = None


class ModerationToggleRequest(BaseModel):
    moderation_enabled: bool
