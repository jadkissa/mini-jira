from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Turn a plain password into an argon2 hash."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when the plain password matches the stored hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Return a short-lived JWT that identifies this user."""
    settings = get_settings()
    return _create_token(
        user_id,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    """Return a long-lived JWT that can be exchanged for a new access token."""
    settings = get_settings()
    return _create_token(
        user_id,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict:
    """Return the token payload, or raise if the signature or expiry is invalid."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def _create_token(user_id: int, token_type: str, expires_in: timedelta) -> str:
    settings = get_settings()
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": datetime.now(UTC) + expires_in,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
