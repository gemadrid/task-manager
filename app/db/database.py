from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings



# Engine
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

# Session
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)

# Base (for models)
class Base(DeclarativeBase):
    pass