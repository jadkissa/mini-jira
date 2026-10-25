from app.repositories.users import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password

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