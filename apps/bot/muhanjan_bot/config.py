from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    bot_token: str
    api_base_url: str
    local_upload_dir: Path
    proxy_url: str | None
    parse_mode: str
    http_timeout: float
    http_connect_timeout: float
    redis_url: str
    redis_fsm_ttl_seconds: int
    submission_cooldown_seconds: int
    submission_deduplicate_ttl_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        upload_dir = Path(os.getenv("LOCAL_UPLOAD_DIR", "../../storage/uploads")).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)

        proxy_url = (os.getenv("BOT_PROXY_URL") or "").strip() or None

        return cls(
            bot_token=(os.getenv("BOT_TOKEN") or "").strip(),
            api_base_url=(os.getenv("API_BASE_URL") or "http://127.0.0.1:8002/api/v1").rstrip("/"),
            local_upload_dir=upload_dir,
            proxy_url=proxy_url,
            parse_mode=(os.getenv("BOT_PARSE_MODE") or "HTML").strip(),
            http_timeout=float(os.getenv("HTTP_TIMEOUT") or 25),
            http_connect_timeout=float(os.getenv("HTTP_CONNECT_TIMEOUT") or 5),
            redis_url=(os.getenv("BOT_REDIS_URL") or "redis://localhost:6379/0").strip(),
            redis_fsm_ttl_seconds=int(os.getenv("REDIS_FSM_TTL_SECONDS") or 86400),
            submission_cooldown_seconds=int(os.getenv("SUBMISSION_COOLDOWN_SECONDS") or 8),
            submission_deduplicate_ttl_seconds=int(os.getenv("SUBMISSION_DEDUPLICATE_TTL_SECONDS") or 3600),
        )


settings = Settings.from_env()
