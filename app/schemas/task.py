from pydantic import BaseModel



class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    completed: bool
    user_id: int

    class Config:
        from_attributes = True


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskResponse(TaskBase):
    id: int
    completed: bool

    class Config:
        from_attributes = True