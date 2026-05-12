from pydantic import BaseModel, Field, ConfigDict, EmailStr



class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserPublic(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)