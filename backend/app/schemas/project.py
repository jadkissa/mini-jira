from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    team_id: int | None = None

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value
