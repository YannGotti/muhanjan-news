from __future__ import annotations

import mimetypes
from pathlib import Path

from aiogram import Bot

from muhanjan_bot.config import settings


async def save_telegram_file(bot: Bot, file_id: str, original_name: str | None) -> tuple[str, str | None, int | None]:
    tg_file = await bot.get_file(file_id)

    ext = Path(tg_file.file_path).suffix or (Path(original_name).suffix if original_name else "")
    target_name = f"{file_id}{ext}"
    target_path = settings.local_upload_dir / target_name

    await bot.download_file(tg_file.file_path, destination=target_path)

    mime_type, _ = mimetypes.guess_type(str(target_path))
    size = target_path.stat().st_size if target_path.exists() else None
    return str(target_path), mime_type, size
