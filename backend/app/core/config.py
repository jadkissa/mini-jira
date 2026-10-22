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
    app_description: str = "A simple project management tool"
    environment: str = "development"
    debug: bool = True
    # Used in Phase 2+ (SQLAlchemy). Inside Compose, host is `db`.
    database_url: str = (
        "postgresql+psycopg://mini_jira:mini_jira@localhost:5432/mini_jira"
    )



@lru_cache
def get_settings() -> Settings:
    return Settings()
