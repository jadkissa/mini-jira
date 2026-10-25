from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: int
    actor_id: int | None = None
    action: str
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime
