from pydantic import BaseModel, Field, ConfigDict

from app.schemas.task import Task



class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class User(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    tasks: list[Task] = []

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    email: str | None = None
    is_active: bool | None = None


class UserPublic(UserBase):
    id: int
    is_active: bool