from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.database import Base
from app.main import app
from app.dependencies.database import get_db
from app.core.security import get_password_hash, create_access_token_for_user
from app.models.user import User
from app.models.task import Task
from app.schemas.user import UserCreate
from app.schemas.task import TaskCreate, TaskUpdate
from app.crud.user import create_user
from app.crud.task import create_user_task



# Create database in memory before all tests, and delete it after they finish
TEST_DATABASE_URL: str = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Yield a sesion with the test database, and rollback transactions so that each test is isolated
@pytest.fixture(scope="function")
def db() -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# Override original get_db dependency and create a TestClient for each test user
@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def second_client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Test user (and second test user)
@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    test_user = create_user(db, UserCreate(
        email="test@example.com",
        password="password123"
    ))
    return test_user

@pytest.fixture(scope="function")
def second_test_user(db: Session) -> User:
    second_test_user = create_user(db, UserCreate(
        email="second@example.com",
        password="password123"
    ))
    return second_test_user

# Add token headers to test client
@pytest.fixture(scope="function")
def auth_client(client: TestClient, test_user: User) -> Generator[TestClient, None, None]:
    access_token = create_access_token_for_user(test_user.id)
    headers = {"Authorization": f"Bearer {access_token}"}
    client.headers.update(headers)
    yield client
    client.headers.clear()

@pytest.fixture(scope="function")
def second_auth_client(second_client: TestClient, second_test_user: User) -> Generator[TestClient, None, None]:
    access_token = create_access_token_for_user(second_test_user.id)
    headers = {"Authorization": f"Bearer {access_token}"}
    second_client.headers.update(headers)
    yield second_client
    second_client.headers.clear()

# Task fixtures for each user (for GET by id, UPDATE and DELETE tests)
@pytest.fixture(scope="function")
def user_task(db: Session, test_user: User) -> Task:
    task = create_user_task(db, test_user.id, TaskCreate(
        title="First user test task 1",
        description="Test task 1 for the first user"
        ))
    return task

@pytest.fixture(scope="function")
def second_user_task(db: Session, second_test_user: User) -> Task:
    second_task = create_user_task(db, second_test_user.id, TaskCreate(
        title="Second user test task 1",
        description="Test task 1 for the second user"
        ))
    return second_task