from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Mini Jira"
    app_description: str = (
        "Task and project API. Send Authorization: Bearer <access_token> "
        "except on /health, POST /api/v1/users, POST /api/v1/auth/login, "
        "and POST /api/v1/auth/refresh."
    )
    environment: str = "development"
    debug: bool = True
    # Used in Phase 2+ (SQLAlchemy). Inside Compose, host is `db`.
    database_url: str = (
        "postgresql+psycopg://mini_jira:mini_jira@localhost:5432/mini_jira"
    )
    jwt_secret: str = "dev-secret-change-me-use-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7



@lru_cache
def get_settings() -> Settings:
    """Load settings from the environment once and reuse them."""
    return Settings()
