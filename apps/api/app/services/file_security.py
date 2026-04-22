from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings


ALLOWED_FILE_TYPES = {"photo", "document", "video", "audio", "voice", "animation"}
FORBIDDEN_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".scr",
    ".com",
    ".msi",
    ".ps1",
    ".jar",
    ".sh",
    ".apk",
}
ALLOWED_MIME_PREFIXES = {
    "photo": ("image/",),
    "video": ("video/",),
    "audio": ("audio/",),
    "voice": ("audio/", "application/ogg"),
    "animation": ("video/", "image/gif"),
}


def validate_attachment_path(storage_path: str) -> str:
    base_dir = settings.upload_dir_path.resolve()
    target_path = Path(storage_path).resolve()

    try:
        target_path.relative_to(base_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Некорректный путь вложения") from exc

    if not target_path.exists():
        raise HTTPException(status_code=400, detail="Файл вложения не найден")

    return str(target_path)


def validate_attachment_payload(
    *,
    file_type: str,
    original_name: str | None,
    mime_type: str | None,
    file_size: int | None,
    storage_path: str,
) -> str:
    normalized_type = (file_type or "").strip().lower()
    if normalized_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Недопустимый тип вложения")

    if file_size is not None and file_size > settings.max_attachment_file_size_bytes:
        raise HTTPException(status_code=400, detail="Файл превышает допустимый размер")

    ext = Path(original_name or storage_path).suffix.lower()
    if ext in FORBIDDEN_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Недопустимое расширение файла")

    prefixes = ALLOWED_MIME_PREFIXES.get(normalized_type)
    current_mime = (mime_type or "").strip().lower()
    if prefixes and current_mime and not any(current_mime.startswith(prefix) for prefix in prefixes):
        raise HTTPException(status_code=400, detail="Недопустимый MIME-тип файла")

    return validate_attachment_path(storage_path)
