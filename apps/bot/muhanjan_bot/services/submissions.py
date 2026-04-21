from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message

from muhanjan_bot.services.api import BotApiError, api_client, extract_error_detail
from muhanjan_bot.services.files import save_telegram_file


STATUS_LABELS = {
    "pending": "ждёт проверки",
    "approved": "одобрен",
    "rejected": "отклонён",
}


def _base_payload(message: Message) -> dict:
    return {
        "telegram_id": message.from_user.id,
        "message_text": message.text or message.caption or "",
        "source_message_id": message.message_id,
        "attachments": [],
        "links": [],
    }


async def _append_attachment(attachments: list[dict], payload: dict) -> None:
    attachments.append(payload)


async def build_submission_payload(bot: Bot, message: Message) -> dict:
    payload = _base_payload(message)
    attachments = payload["attachments"]

    if message.photo:
        largest = message.photo[-1]
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            largest.file_id,
            f"{largest.file_unique_id}.jpg",
            largest.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": largest.file_id,
                "telegram_unique_file_id": largest.file_unique_id,
                "file_type": "photo",
                "original_name": f"{largest.file_unique_id}.jpg",
                "mime_type": mime_type or "image/jpeg",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    if message.document:
        doc = message.document
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            doc.file_id,
            doc.file_name,
            doc.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": doc.file_id,
                "telegram_unique_file_id": doc.file_unique_id,
                "file_type": "document",
                "original_name": doc.file_name,
                "mime_type": mime_type or doc.mime_type,
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    if message.video:
        video = message.video
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            video.file_id,
            getattr(video, "file_name", None) or f"{video.file_unique_id}.mp4",
            video.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": video.file_id,
                "telegram_unique_file_id": video.file_unique_id,
                "file_type": "video",
                "original_name": getattr(video, "file_name", None) or f"{video.file_unique_id}.mp4",
                "mime_type": mime_type or video.mime_type or "video/mp4",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    if message.audio:
        audio = message.audio
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            audio.file_id,
            getattr(audio, "file_name", None) or f"{audio.file_unique_id}.mp3",
            audio.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": audio.file_id,
                "telegram_unique_file_id": audio.file_unique_id,
                "file_type": "audio",
                "original_name": getattr(audio, "file_name", None) or f"{audio.file_unique_id}.mp3",
                "mime_type": mime_type or audio.mime_type or "audio/mpeg",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    if message.voice:
        voice = message.voice
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            voice.file_id,
            f"{voice.file_unique_id}.ogg",
            voice.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": voice.file_id,
                "telegram_unique_file_id": voice.file_unique_id,
                "file_type": "voice",
                "original_name": f"{voice.file_unique_id}.ogg",
                "mime_type": mime_type or voice.mime_type or "audio/ogg",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    if message.animation:
        animation = message.animation
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            animation.file_id,
            getattr(animation, "file_name", None) or f"{animation.file_unique_id}.mp4",
            animation.file_size,
        )
        await _append_attachment(
            attachments,
            {
                "telegram_file_id": animation.file_id,
                "telegram_unique_file_id": animation.file_unique_id,
                "file_type": "animation",
                "original_name": getattr(animation, "file_name", None) or f"{animation.file_unique_id}.mp4",
                "mime_type": mime_type or animation.mime_type or "video/mp4",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            },
        )

    return payload


def is_message_usable_for_submission(message: Message) -> bool:
    return bool(
        (message.text and message.text.strip())
        or message.caption
        or message.photo
        or message.document
        or message.video
        or message.audio
        or message.voice
        or message.animation
    )


async def send_submission(payload: dict) -> dict:
    try:
        response = await api_client.post("/bot/submissions", payload)
    except BotApiError:
        raise

    if response.status_code >= 400:
        return {
            "ok": False,
            "status_code": response.status_code,
            "detail": extract_error_detail(response),
        }

    return {
        "ok": True,
        **response.json(),
    }


async def fetch_recent_submissions(telegram_id: int, limit: int = 5) -> list[dict]:
    response = await api_client.get(f"/bot/users/{telegram_id}/recent-submissions?limit={limit}")
    if response.status_code >= 400:
        return []
    data = response.json()
    return data.get("items", [])


def human_status(status: str) -> str:
    return STATUS_LABELS.get(status, status)
