from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    upload_dir: str = "../../storage/uploads"
    base_public_api_url: str = "http://127.0.0.1:8002"
    base_public_web_url: str = "http://127.0.0.1:5174"
    cors_allow_origins: str = "http://localhost:5174"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def upload_dir_path(self) -> Path:
        return Path(self.upload_dir).resolve()


settings = Settings()
settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
