from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import user as model
from app.schemas import user as schema
from app.core.security import get_password_hash



def get_user_by_id(db: Session, user_id: int) -> model.User | None:
    stmt = select(model.User).where(model.User.id == user_id)
    result = db.execute(stmt)
    return result.scalars().first()

def get_user_by_email(db: Session, email: str) -> model.User | None:
    stmt = select(model.User).where(model.User.email == email)
    result = db.execute(stmt)
    return result.scalars().first()


def create_user(db: Session, user_create: schema.UserCreate) -> model.User:
    hashed_password = get_password_hash(user_create.password)
    user = model.User(email=user_create.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_update: schema.UserUpdate) -> model.User | None:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user_data = user_update.model_dump(exclude_unset=True)

    if "password" in user_data:
        user.hashed_password = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True