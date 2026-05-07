from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import SessionLocal



def get_db():
    with SessionLocal() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]