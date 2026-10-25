from app.repositories.users import UserRepository
from app.models.user import User
from jwt.exceptions import InvalidTokenError

from app.schemas.user import AccessToken, LoginRequest, Token, UserCreate, UserUpdate
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

from fastapi import HTTPException


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
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return AccessToken(access_token=create_access_token(user.id))

    def get(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update(self, user_id: int, payload: UserUpdate) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        data = payload.model_dump(exclude_unset=True)
        if "password" in data:
            user.hashed_password = hash_password(data.pop("password"))
        for key, value in data.items():
            setattr(user, key, value)
        return self.repo.update(user)
    

    def delete(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.repo.delete(user)