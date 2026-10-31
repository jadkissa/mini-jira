from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import AccessToken, LoginRequest, Token, UserCreate, UserUpdate

_SUPERUSER_ONLY_FIELDS = {"is_active", "is_superuser"}


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        return self.repo.create(user)

    def login(self, payload: LoginRequest) -> Token:
        """Return access and refresh tokens when the email and password match."""
        user = self.repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        return Token(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> AccessToken:
        """Return a new access token for a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
        user = self.repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid token")
        return AccessToken(access_token=create_access_token(user.id))

    def get(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update(self, user_id: int, payload: UserUpdate, actor: User) -> User:
        """Users may edit themselves. Only a superuser may edit others or change roles."""
        self._require_self_or_superuser(user_id, actor)
        data = payload.model_dump(exclude_unset=True)
        if not actor.is_superuser and _SUPERUSER_ONLY_FIELDS & data.keys():
            raise HTTPException(status_code=403, detail="Not allowed")
        user = self.get(user_id)
        if "email" in data and data["email"] != user.email and self.repo.get_by_email(data["email"]):
            raise HTTPException(status_code=409, detail="Email already registered")
        if "password" in data:
            user.hashed_password = hash_password(data.pop("password"))
        for key, value in data.items():
            setattr(user, key, value)
        return self.repo.update(user)

    def delete(self, user_id: int, actor: User) -> None:
        """Users may delete themselves. A superuser may delete anyone."""
        self._require_self_or_superuser(user_id, actor)
        self.repo.delete(self.get(user_id))

    def _require_self_or_superuser(self, user_id: int, actor: User) -> None:
        if actor.id != user_id and not actor.is_superuser:
            raise HTTPException(status_code=403, detail="Not allowed")
