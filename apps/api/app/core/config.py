from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "MuhanjanNews API"
    app_env: str = "production"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    admin_username: str = "admin"
    admin_password: str = "admin"
    admin_password_hash: str | None = None

    upload_dir: str = "../../storage/uploads"
    base_public_api_url: str = "http://127.0.0.1:8002"
    base_public_web_url: str = "http://127.0.0.1:5174"
    cors_allow_origins: str = "http://localhost:5174"

    telegram_bot_token: str | None = None
    telegram_parse_mode: str = "HTML"
    telegram_request_timeout_seconds: int = 10
    telegram_proxy_url: str | None = None

    redis_url: str = "redis://localhost:6379/0"
    notification_queue_key: str = "mn:queue:notifications"
    notification_retry_queue_key: str = "mn:queue:notifications:retry"

    redis_socket_timeout_seconds: int = 2
    redis_blocking_socket_timeout_seconds: int = 15
    notification_worker_block_timeout_seconds: int = 5

    notification_worker_heartbeat_key: str = "mn:worker:notifications:heartbeat"
    notification_worker_heartbeat_interval_seconds: int = 10
    notification_worker_stale_after_seconds: int = 35

    max_attachment_file_size_bytes: int = 20 * 1024 * 1024

    auth_login_rate_limit_attempts: int = 5
    auth_login_rate_limit_window_seconds: int = 900

    admin_auto_refresh_default_seconds: int = 15

    db_pool_size: int = 20
    db_max_overflow: int = 20
    db_pool_timeout_seconds: int = 10
    db_pool_recycle_seconds: int = 1800

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore",
    )

    @property
    def upload_dir_path(self) -> Path:
        return Path(self.upload_dir).resolve()


settings = Settings()
settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
