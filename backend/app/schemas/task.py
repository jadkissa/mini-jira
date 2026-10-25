from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date

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
    title: str
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.todo) 
    priority: TaskPriority = Field(default=TaskPriority.medium)
    duration_days: int | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    duration_days: int | None = None
    assignee_id: int | None = None
