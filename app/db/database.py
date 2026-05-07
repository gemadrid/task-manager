from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings



# Engine
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base (para modelos)
class Base(DeclarativeBase):
    pass