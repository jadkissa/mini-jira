from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_JWT_SECRET = "dev-secret-change-me-use-at-least-32-bytes"


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
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    @model_validator(mode="after")
    def require_real_secret_outside_development(self) -> "Settings":
        """Refuse to start with the public default secret anywhere but development."""
        if self.environment != "development" and self.jwt_secret == DEFAULT_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set when ENVIRONMENT is not development")
        return self


@lru_cache
def get_settings() -> Settings:
    """Load settings from the environment once and reuse them."""
    return Settings()
