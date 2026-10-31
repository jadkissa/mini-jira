from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    duration_days: int | None = None
    created_at: datetime 
    updated_at: datetime
    delivery_date: date | None = None
    project_id: int
    reporter_id: int | None = None
    assignee_id: int | None = None
    
class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.todo) 
    priority: TaskPriority = Field(default=TaskPriority.medium)
    duration_days: int | None = Field(default=None, ge=0)
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    duration_days: int | None = Field(default=None, ge=0)
    assignee_id: int | None = None

    @field_validator("title", "status", "priority")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value
