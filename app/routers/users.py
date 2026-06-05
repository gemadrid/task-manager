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
    if user_update.email and user_update.email != current_user.email:
        existing = crud.get_user_by_email(db, user_update.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    result = crud.update_user(db, current_user.id, user_update)
    return result


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me(db: SessionDep, current_user: CurrentActiveUserDep):
    crud.delete_user(db, current_user.id)