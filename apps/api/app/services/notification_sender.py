from __future__ import annotations

from html import escape

import httpx

from app.core.config import settings


def build_approved_text(submission_id: int, comment: str | None = None) -> str:
    comment = (comment or "").strip()
    comment_block = f"\n\nКомментарий модератора: <i>{escape(comment)}</i>" if comment else ""
    return (
        "<b>Твой материал одобрен</b>\n\n"
        f"Материал <b>#{submission_id}</b> прошёл модерацию и теперь может быть показан в ленте."
        f"{comment_block}"
    )


def build_rejected_text(submission_id: int, comment: str | None = None) -> str:
    comment = (comment or "").strip()
    comment_block = f"\n\nКомментарий модератора: <i>{escape(comment)}</i>" if comment else ""
    return (
        "<b>Твой материал отклонён</b>\n\n"
        f"Материал <b>#{submission_id}</b> не прошёл модерацию."
        f"{comment_block}"
    )


def send_telegram_text(chat_id: int, text: str) -> tuple[bool, str | None]:
    token = (settings.telegram_bot_token or "").strip()
    if not token:
        return False, "TELEGRAM_BOT_TOKEN is empty in apps/api/.env"

    proxy_url = (settings.telegram_proxy_url or "").strip() or None

    request_data = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": settings.telegram_parse_mode,
        "disable_web_page_preview": True,
    }

    client_kwargs: dict = {
        "timeout": settings.telegram_request_timeout_seconds,
    }
    if proxy_url:
        client_kwargs["proxy"] = proxy_url

    try:
        with httpx.Client(**client_kwargs) as client:
            response = client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=request_data,
            )

        if response.is_success:
            return True, response.text

        return False, f"HTTP {response.status_code}: {response.text}"

    except httpx.HTTPError as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
    except Exception as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
