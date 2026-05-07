from fastapi import APIRouter

from app.schemas.user import UserPublic
from app.dependencies.auth import CurrentActiveUserDep



router = APIRouter(
    prefix = "/users",
    tags = ["users"],
)


@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: CurrentActiveUserDep):
    return current_user