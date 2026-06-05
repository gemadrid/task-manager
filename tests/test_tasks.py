import time
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.crud.task import create_user_task, update_user_task



# Helper function to create tasks (for GET tests)
def create_task(db: Session, user: User, title: str, description: str = None, completed=False) -> Task:
    new_task = create_user_task(db, user.id, TaskCreate(title=title, description=description))
    if completed:
        new_task = update_user_task(db, user.id, new_task.id, TaskUpdate(completed=True))
    return new_task

def create_n_tasks(db: Session, user: User, n: int) -> list[Task]:
    tasks = []
    for i in range(n):
        task = create_task(db, user, title=f"Task {i+1}")
        tasks.append(task)
    return sorted(tasks, key=lambda t: t.id)



### POST ###
def test_create_task_success(auth_client: TestClient):
    title = "Test task"
    description = "A simple test task"
    data = {
        "title": title,
        "description": description
    }
    response = auth_client.post("/tasks/", json=data)
    assert response.status_code == 201
    task_data = response.json()
    assert task_data["id"] > 0
    assert task_data["title"] == title
    assert task_data["description"] == description
    assert task_data["completed"] == False
    assert "created_at" in task_data
    created_at = datetime.fromisoformat(task_data["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    assert now - timedelta(seconds=5) < created_at <= now
    assert "updated_at" in task_data
    assert "user_id" not in task_data

def test_create_task_success_no_description(auth_client: TestClient):
    title = "Test task"
    data = {
        "title": title
    }
    response = auth_client.post("/tasks/", json=data)
    assert response.status_code == 201
    task_data = response.json()
    assert task_data["id"] > 0
    assert task_data["title"] == title
    assert task_data["description"] is None
    assert task_data["completed"] == False

def test_create_task_empty_body(auth_client: TestClient):
    data = {}
    response = auth_client.post("/tasks/", json=data)
    assert response.status_code == 422

def test_create_task_no_title(auth_client: TestClient):
    data = {
        "title": ""
    }
    response = auth_client.post("/tasks/", json=data)
    assert response.status_code == 422


### GET /tasks/ ###
def test_get_tasks_empty_list(auth_client: TestClient):
    response = auth_client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_success(db: Session, auth_client: TestClient, test_user: User):
    task1 = create_task(db, test_user, title="First test task", description="Description 1")
    task2 = create_task(db, test_user, title="Second test task")
    response = auth_client.get("/tasks/")
    assert response.status_code == 200
    task_list: list = response.json()
    assert len(task_list) == 2
    ids = [task["id"] for task in task_list]
    assert task1.id in ids
    assert task2.id in ids
    task1_data = next(task for task in task_list if task["id"] == task1.id)
    task2_data = next(task for task in task_list if task["id"] == task2.id)
    assert task1_data["id"] == task1.id
    assert task1_data["title"] == task1.title
    assert task1_data["description"] == task1.description
    assert task1_data["completed"] == task1.completed
    assert task2_data["id"] == task2.id
    assert task2_data["title"] == task2.title
    assert task2_data["description"] == task2.description
    assert task2_data["completed"] == task2.completed

def test_get_tasks_user_isolation(db: Session, auth_client: TestClient, second_auth_client: TestClient, test_user: User, second_test_user: User):
    user1_task1 = create_task(db, test_user, title="User 1 task 1")
    user1_task2 = create_task(db, test_user, title="User 1 task 2")
    user2_task = create_task(db, second_test_user, title="User 2 task")
    # First user
    response = auth_client.get("/tasks/")
    assert response.status_code == 200
    task_list: list = response.json()
    assert len(task_list) == 2
    ids = [task["id"] for task in task_list]
    assert user1_task1.id in ids
    assert user1_task2.id in ids
    assert user2_task.id not in ids
    # Second user
    response = second_auth_client.get("/tasks/")
    assert response.status_code == 200
    task_list: list = response.json()
    assert len(task_list) == 1
    ids = [task["id"] for task in task_list]
    assert user1_task1.id not in ids
    assert user1_task2.id not in ids
    assert user2_task.id in ids

# Filters
@pytest.mark.parametrize("completed, expected_count", [
    (True, 2),
    (False, 1),
])
def test_get_tasks_filter_completed(db: Session, auth_client: TestClient, test_user: User, completed, expected_count):
    create_task(db, test_user, title="Completed task 1", completed=True)
    create_task(db, test_user, title="Completed task 2", completed=True)
    create_task(db, test_user, title="Not completed task")
    response = auth_client.get("/tasks/", params={"completed": completed})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == expected_count
    assert all(task["completed"]==completed for task in task_list)

def test_get_tasks_filter_title_match(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Buy milk")
    create_task(db, test_user, title="Buy eggs")
    create_task(db, test_user, title="Read book")
    response = auth_client.get("/tasks/", params={"title": "buy"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 2
    assert all("buy" in task["title"].lower() for task in task_list)

def test_get_tasks_filter_title_match_case_insensitive(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Buy milk")
    response = auth_client.get("/tasks/", params={"title": "BUY"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 1

def test_get_tasks_filter_title_no_match(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Read book")
    response = auth_client.get("/tasks/", params={"title": "xyz_nonexistent"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 0

def test_get_tasks_filter_title_no_match_in_description(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Go to the grocery store", description="and buy vegetables")
    response = auth_client.get("/tasks/", params={"title": "buy"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 0

def test_get_tasks_filter_search_match_description(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Go to the grocery store", description="and buy vegetables")
    response = auth_client.get("/tasks/", params={"search": "buy"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 1

def test_get_tasks_filter_search_match_title(db: Session, auth_client: TestClient, test_user: User):
    create_task(db, test_user, title="Buy milk")
    response = auth_client.get("/tasks/", params={"search": "MILK"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 1

# Order by
@pytest.mark.parametrize("order, expected_titles", [
    ("asc", ["Apple", "Banana", "Cherry"]),
    ("desc", ["Cherry", "Banana", "Apple"]),
])
def test_get_tasks_order_by_title(db: Session, auth_client: TestClient, test_user: User, order, expected_titles):
    for title in ["Banana", "Apple", "Cherry"]:
        create_task(db, test_user, title=title)
    response = auth_client.get("/tasks", params={"order_by": "title", "order": order})
    assert response.status_code == 200
    task_list = response.json()
    titles = [task["title"] for task in task_list]
    assert titles == expected_titles

@pytest.mark.parametrize("order, expected_completed", [
    ("asc", [False, False, True]),
    ("desc", [True, False, False]),
])
def test_get_tasks_order_by_completed(db: Session, auth_client: TestClient, test_user: User, order, expected_completed):
    for completed in [False, True, False]:
        create_task(db, test_user, title="Nonimportant title", completed=completed)
    response = auth_client.get("/tasks", params={"order_by": "completed", "order": order})
    assert response.status_code == 200
    task_list = response.json()
    completed = [task["completed"] for task in task_list]
    assert completed == expected_completed

def test_get_tasks_order_by_id(db: Session, auth_client: TestClient, test_user: User):
    for i in range(3):
        create_task(db, test_user, title=f"Task {i+1}")
    # Asc
    response = auth_client.get("/tasks", params={"order_by": "id", "order": "asc"})
    assert response.status_code == 200
    task_list = response.json()
    ids = [task["id"] for task in task_list]
    assert ids == sorted(ids)
    # Desc
    response = auth_client.get("/tasks", params={"order_by": "id", "order": "desc"})
    assert response.status_code == 200
    task_list = response.json()
    ids = [task["id"] for task in task_list]
    assert ids == sorted(ids, reverse=True)

# Pagination
def test_get_tasks_pagination_limit_less_than_total(db: Session, auth_client: TestClient, test_user: User):
    n = 5
    task_ids = [task.id for task in create_n_tasks(db, test_user, n)]
    response = auth_client.get("/tasks", params={"order_by": "id", "limit": "2"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 2
    ids = [task["id"] for task in task_list]
    assert task_ids[:2] == ids

def test_get_tasks_pagination_limit_equals_total(db: Session, auth_client: TestClient, test_user: User):
    n = 5
    task_ids = [task.id for task in create_n_tasks(db, test_user, n)]
    response = auth_client.get("/tasks", params={"order_by": "id", "limit": str(n)})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == n
    ids = [task["id"] for task in task_list]
    assert task_ids == ids

def test_get_tasks_pagination_limit_exceeds_total(db: Session, auth_client: TestClient, test_user: User):
    n = 5
    task_ids = [task.id for task in create_n_tasks(db, test_user, n)]
    response = auth_client.get("/tasks", params={"order_by": "id", "limit": str(n+10)})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == n
    ids = [task["id"] for task in task_list]
    assert task_ids == ids

def test_get_tasks_pagination_skip_less_than_total(db: Session, auth_client: TestClient, test_user: User):
    n = 5
    task_ids = [task.id for task in create_n_tasks(db, test_user, n)]
    response = auth_client.get("/tasks", params={"order_by": "id", "skip": "2"})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == n-2
    ids = [task["id"] for task in task_list]
    assert task_ids[2:] == ids

def test_get_tasks_pagination_skip_equals_total(db: Session, auth_client: TestClient, test_user: User):
    n = 5
    create_n_tasks(db, test_user, n)
    response = auth_client.get("/tasks", params={"order_by": "id", "skip": str(n)})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 0

@pytest.mark.parametrize("parameter, parameter_value", [
    ("limit", "0"),
    ("skip", "100"),
])
def test_get_tasks_pagination_empty_results(db: Session, auth_client: TestClient, test_user: User, parameter, parameter_value):
    n = 5
    create_n_tasks(db, test_user, n)
    response = auth_client.get("/tasks", params={"order_by": "id", parameter: parameter_value})
    assert response.status_code == 200
    task_list = response.json()
    assert len(task_list) == 0

@pytest.mark.parametrize("parameter, parameter_value", [
    ("limit", "101"),
    ("skip", "-1"),
])
def test_get_tasks_pagination_invalid_values(db: Session, auth_client: TestClient, test_user: User, parameter, parameter_value):
    response = auth_client.get("/tasks", params={"order_by": "id", parameter: parameter_value})
    assert response.status_code == 422


### GET /tasks/{id} ###
def test_get_task_by_id(auth_client: TestClient, user_task: Task):
    response = auth_client.get(f"/tasks/{user_task.id}")
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["id"] == user_task.id
    assert task_data["title"] == user_task.title
    assert task_data["description"] == user_task.description
    assert task_data["completed"] == user_task.completed
    created_at = datetime.fromisoformat(task_data["created_at"])
    assert created_at == user_task.created_at
    updated_at = datetime.fromisoformat(task_data["updated_at"])
    assert updated_at == user_task.updated_at

def test_get_nonexistent_task(auth_client: TestClient):
    response = auth_client.get("/tasks/99999")
    assert response.status_code == 404

def test_get_task_unauthorized(auth_client: TestClient, second_user_task: Task):
    response = auth_client.get(f"/tasks/{second_user_task.id}")
    assert response.status_code == 404


### UPDATE ###
def test_update_task_complete(auth_client: TestClient, user_task: Task):
    title = "Modified task"
    description = "Modified description"
    completed = True
    data = {
        "title": title,
        "description": description,
        "completed": completed
    }
    response = auth_client.patch(f"/tasks/{user_task.id}", json=data)
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["title"] == title
    assert task_data["description"] == description
    assert task_data["completed"] == completed

def test_update_task_partial(auth_client: TestClient, user_task: Task):
    title = "Modified task"
    data = {
        "title": title
    }
    response = auth_client.patch(f"/tasks/{user_task.id}", json=data)
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["title"] == title
    assert task_data["description"] == user_task.description
    assert task_data["completed"] == user_task.completed

def test_update_nonexistent_task(auth_client: TestClient):
    response = auth_client.patch("/tasks/99999", json={})
    assert response.status_code == 404

def test_update_task_unauthorized(auth_client: TestClient, second_user_task: Task):
    response = auth_client.patch(f"/tasks/{second_user_task.id}", json={})
    assert response.status_code == 404

def test_update_date_change(auth_client: TestClient, user_task: Task):
    data = {
        "title": "check date change"
    }
    updated_at = user_task.updated_at
    time.sleep(0.01)
    response = auth_client.patch(f"/tasks/{user_task.id}", json=data)
    assert response.status_code == 200
    task_data = response.json()
    modified_updated_at = datetime.fromisoformat(task_data["updated_at"])
    assert modified_updated_at > updated_at


### DELETE ###
def test_delete_task_success(auth_client: TestClient, user_task: Task):
    response = auth_client.delete(f"/tasks/{user_task.id}")
    assert response.status_code == 204

def test_delete_nonexistent_task(auth_client: TestClient):
    response = auth_client.delete("/tasks/99999")
    assert response.status_code == 404

def test_delete_task_unauthorized(auth_client: TestClient, second_user_task: Task):
    response = auth_client.delete(f"/tasks/{second_user_task.id}")
    assert response.status_code == 404