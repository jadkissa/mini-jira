from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth import AuthService

router = APIRouter(tags=["users"])

def _service(db: Session) -> AuthService:
    return AuthService(UserRepository(db))

@router.post("/users", response_model=UserRead, status_code=201)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a user. This route stays public."""
    return _service(db).register(payload)


@router.get("/users/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the user identified by the access token."""
    return current_user


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return one user, or 404 if they do not exist."""
    return _service(db).get(user_id)


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update the fields sent in the body and return the user."""
    return _service(db).update(user_id, payload)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Delete a user, or 404 if they do not exist."""
    _service(db).delete(user_id)
