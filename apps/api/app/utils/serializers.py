import json
from pathlib import Path

from app.core.config import settings
from app.models.submission import Submission
from app.schemas.common import AttachmentOut, SubmissionOut


def _resolve_attachment_public_url(attachment) -> str | None:
    if attachment.public_url:
        return attachment.public_url

    storage_path = getattr(attachment, "storage_path", None)
    if not storage_path:
        return None

    filename = Path(storage_path).name
    if not filename:
        return None

    return f"{settings.base_public_api_url.rstrip('/')}/uploads/{filename}"


def _resolve_attachment_download_url(attachment) -> str:
    return f"{settings.base_public_api_url.rstrip('/')}{settings.api_v1_prefix}/attachments/{attachment.id}/download"


def submission_to_schema(item: Submission) -> SubmissionOut:
    attachments = [
        AttachmentOut(
            id=att.id,
            file_type=att.file_type,
            original_name=att.original_name,
            mime_type=att.mime_type,
            file_size=att.file_size,
            public_url=_resolve_attachment_public_url(att),
            download_url=_resolve_attachment_download_url(att),
        )
        for att in item.attachments
    ]

    return SubmissionOut(
        id=item.id,
        user=item.user,
        message_text=item.message_text,
        links=json.loads(item.links_json or "[]"),
        status=item.status,
        approved_at=item.approved_at,
        rejected_at=item.rejected_at,
        review_comment=item.review_comment,
        created_at=item.created_at,
        attachments=attachments,
    )
