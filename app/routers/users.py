from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserPublic, UserUpdate
from app.dependencies.auth import CurrentActiveUserDep
from app.dependencies.database import SessionDep
from app.crud import user as crud



router = APIRouter(
    prefix = "/users",
    tags = ["users"],
)


@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: CurrentActiveUserDep):
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_users_me(user_update: UserUpdate, db: SessionDep, current_user: CurrentActiveUserDep):
    result = crud.update_user(db, current_user.id, user_update)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return result


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me(db: SessionDep, current_user: CurrentActiveUserDep):
    success = crud.delete_user(db, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")