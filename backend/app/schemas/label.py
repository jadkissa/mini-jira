from pydantic import BaseModel, ConfigDict, Field


class LabelCreate(BaseModel):
    name: str = Field(min_length=1)
    color: str | None = None


class LabelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    name: str
    color: str | None = None


class TaskLabelCreate(BaseModel):
    label_id: int
