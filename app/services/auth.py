from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.crud.user import get_user_by_email, create_user
from app.core.security import verify_password, DUMMY_HASH



def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def register_user(db: Session, user_create: UserCreate) -> User | None:
    user = get_user_by_email(db, user_create.email)
    if user:
        return None
    user_db = create_user(db, user_create)
    return user_db