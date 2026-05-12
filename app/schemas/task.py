from datetime import datetime

from pydantic import BaseModel, ConfigDict



class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskPublic(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)