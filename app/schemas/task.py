from pydantic import BaseModel, ConfigDict



class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    completed: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskResponse(TaskBase):
    id: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)