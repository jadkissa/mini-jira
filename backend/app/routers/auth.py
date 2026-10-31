from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.teams import TeamRepository
from app.repositories.users import UserRepository
from app.schemas.user import AccessToken, LoginRequest, RefreshRequest, Token
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _service(db: Session) -> AuthService:
    """Build an auth service bound to this request's database session."""
    return AuthService(UserRepository(db), TeamRepository(db))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Return access and refresh tokens when the email and password match."""
    return _service(db).login(payload)


@router.post("/refresh", response_model=AccessToken)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Return a new access token for a valid refresh token."""
    return _service(db).refresh(payload.refresh_token)
