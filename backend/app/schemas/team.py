from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class InviteRole(str, Enum):
    admin = "admin"
    member = "member"


class TeamCreate(BaseModel):
    name: str = Field(min_length=1)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    owner_id: int
    created_at: datetime


class TeamMemberCreate(BaseModel):
    user_id: int
    role: InviteRole = InviteRole.member


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: str


class TeamDetail(TeamRead):
    members: list[TeamMemberRead]
