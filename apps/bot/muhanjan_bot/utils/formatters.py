from __future__ import annotations

from html import escape


def html_safe(value: str | None) -> str:
    return escape((value or "").strip())


def format_ban_reason(reason: str | None) -> str:
    reason = (reason or "").strip()
    return reason if reason else "не указана"


def format_seconds(seconds: int | None) -> int:
    if not seconds or seconds < 1:
        return 1
    return int(seconds)
