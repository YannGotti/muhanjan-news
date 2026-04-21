from datetime import datetime
from pydantic import BaseModel


class AttachmentOut(BaseModel):
    id: int
    file_type: str
    original_name: str | None
    mime_type: str | None
    file_size: int | None
    public_url: str | None = None
    download_url: str | None = None


class UserOut(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    twitch_nickname: str | None
    is_banned: bool
    ban_reason: str | None

    model_config = {"from_attributes": True}


class SubmissionOut(BaseModel):
    id: int
    user: UserOut
    message_text: str | None
    links: list[str]
    status: str
    approved_at: datetime | None
    rejected_at: datetime | None
    review_comment: str | None
    created_at: datetime
    attachments: list[AttachmentOut]


class ModerationModeResponse(BaseModel):
    moderation_enabled: bool
