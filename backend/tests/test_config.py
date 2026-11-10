import pytest
from pydantic import ValidationError

from app.core.config import DEFAULT_JWT_SECRET, Settings


def test_default_secret_is_allowed_in_development():
    settings = Settings(_env_file=None, environment="development", jwt_secret=DEFAULT_JWT_SECRET)
    assert settings.jwt_secret == DEFAULT_JWT_SECRET


def test_default_secret_is_rejected_outside_development():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production", jwt_secret=DEFAULT_JWT_SECRET)


def test_custom_secret_is_allowed_outside_development():
    secret = "a-real-secret-that-is-long-enough-123"
    settings = Settings(_env_file=None, environment="production", jwt_secret=secret)
    assert settings.jwt_secret == secret
