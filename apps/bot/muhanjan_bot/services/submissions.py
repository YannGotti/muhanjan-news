from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message

from muhanjan_bot.services.api import api_client
from muhanjan_bot.services.files import save_telegram_file


def _base_payload(message: Message) -> dict:
    return {
        "telegram_id": message.from_user.id,
        "message_text": message.text or message.caption or "",
        "source_message_id": message.message_id,
        "attachments": [],
        "links": [],
    }


async def build_submission_payload(bot: Bot, message: Message) -> dict:
    payload = _base_payload(message)
    attachments = payload["attachments"]

    if message.photo:
        largest = message.photo[-1]
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            largest.file_id,
            f"{largest.file_unique_id}.jpg",
        )
        attachments.append(
            {
                "telegram_file_id": largest.file_id,
                "telegram_unique_file_id": largest.file_unique_id,
                "file_type": "photo",
                "original_name": f"{largest.file_unique_id}.jpg",
                "mime_type": mime_type or "image/jpeg",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            }
        )

    if message.document:
        doc = message.document
        storage_path, mime_type, size = await save_telegram_file(bot, doc.file_id, doc.file_name)
        attachments.append(
            {
                "telegram_file_id": doc.file_id,
                "telegram_unique_file_id": doc.file_unique_id,
                "file_type": "document",
                "original_name": doc.file_name,
                "mime_type": mime_type or doc.mime_type,
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            }
        )

    if message.video:
        video = message.video
        storage_path, mime_type, size = await save_telegram_file(
            bot,
            video.file_id,
            f"{video.file_unique_id}.mp4",
        )
        attachments.append(
            {
                "telegram_file_id": video.file_id,
                "telegram_unique_file_id": video.file_unique_id,
                "file_type": "video",
                "original_name": getattr(video, "file_name", None) or f"{video.file_unique_id}.mp4",
                "mime_type": mime_type or video.mime_type or "video/mp4",
                "file_size": size,
                "storage_path": storage_path,
                "public_url": None,
            }
        )

    return payload


def is_message_usable_for_submission(message: Message) -> bool:
    return bool(
        (message.text and message.text.strip())
        or message.caption
        or message.photo
        or message.document
        or message.video
    )


async def send_submission(payload: dict) -> dict:
    response = await api_client.post("/bot/submissions", payload)

    if response.status_code >= 400:
        detail = None
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None
        return {
            "ok": False,
            "status_code": response.status_code,
            "detail": detail,
        }

    return {
        "ok": True,
        **response.json(),
    }
