from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    created_at: datetime 

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None

