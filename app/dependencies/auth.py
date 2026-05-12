from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from app.core.security import decode_token
from app.crud.user import get_user_by_id
from app.dependencies.database import SessionDep
from app.schemas.token import TokenData
from app.models.user import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Convert the int id back from str
        try:
            user_id = int(user_id)
        except ValueError:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_id(db, token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]