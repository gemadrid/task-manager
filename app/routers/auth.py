from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token_for_user
from app.services.auth import authenticate_user, register_user
from app.dependencies.database import SessionDep
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserPublic



router = APIRouter(
    tags = ["auth"],
)


# POST /register
@router.post("/register", response_model=UserPublic)
def register_new_user(new_user: UserCreate, db: SessionDep):
    user = register_user(db, new_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    return user


# POST /login
@router.post("/token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep) -> Token:
    email = form_data.username
    user = authenticate_user(db, email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # return create_access_token_for_user(user.email)
    access_token = create_access_token_for_user(user.id)
    return Token(access_token=access_token, token_type="bearer")