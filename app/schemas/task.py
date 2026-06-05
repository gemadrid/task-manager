from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict



class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    title: str = Field(min_length=1)


class TaskUpdate(TaskBase):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    completed: bool | None = None


class TaskPublic(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)