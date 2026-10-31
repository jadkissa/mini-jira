from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _reject_null(value):
    """Reject an explicit null. Omitted fields never reach this validator."""
    if value is None:
        raise ValueError("cannot be null")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    is_superuser: bool | None = None

    @field_validator("email", "password", "is_active", "is_superuser")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        return _reject_null(value)
