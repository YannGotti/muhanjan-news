from pydantic import BaseModel


class BotUserUpsert(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class TwitchNicknameUpdate(BaseModel):
    telegram_id: int
    twitch_nickname: str


class AttachmentIn(BaseModel):
    telegram_file_id: str | None = None
    telegram_unique_file_id: str | None = None
    file_type: str
    original_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    storage_path: str
    public_url: str | None = None


class SubmissionCreate(BaseModel):
    telegram_id: int
    message_text: str | None = None
    links: list[str] = []
    source_message_id: int | None = None
    attachments: list[AttachmentIn] = []
