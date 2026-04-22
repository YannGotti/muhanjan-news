from __future__ import annotations

from html import escape
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import settings


def _send_telegram_message(chat_id: int, text: str) -> bool:
    token = (settings.telegram_bot_token or "").strip()
    if not token:
        return False

    payload = urlencode(
        {
            "chat_id": str(chat_id),
            "text": text,
            "parse_mode": settings.telegram_parse_mode,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = Request(
        url=f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urlopen(request, timeout=settings.telegram_request_timeout_seconds) as response:
            return 200 <= getattr(response, "status", 200) < 300
    except Exception:
        return False


def notify_submission_approved(chat_id: int, submission_id: int, comment: str | None = None) -> bool:
    comment = (comment or "").strip()
    comment_block = f"\n\nКомментарий модератора: <i>{escape(comment)}</i>" if comment else ""
    text = (
        "<b>Твой материал одобрен</b>\n\n"
        f"Материал <b>#{submission_id}</b> прошёл модерацию и теперь может быть показан в ленте."
        f"{comment_block}"
    )
    return _send_telegram_message(chat_id, text)


def notify_submission_rejected(chat_id: int, submission_id: int, comment: str | None = None) -> bool:
    comment = (comment or "").strip()
    comment_block = f"\n\nКомментарий модератора: <i>{escape(comment)}</i>" if comment else ""
    text = (
        "<b>Твой материал отклонён</b>\n\n"
        f"Материал <b>#{submission_id}</b> не прошёл модерацию."
        f"{comment_block}"
    )
    return _send_telegram_message(chat_id, text)
