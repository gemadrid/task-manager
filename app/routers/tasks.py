from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies.database import SessionDep
from app.dependencies.auth import CurrentActiveUserDep
from app.schemas.task import TaskPublic, TaskCreate, TaskUpdate
from app.crud import task as crud



router = APIRouter(
    prefix = "/tasks",
    tags = ["tasks"],
)


### PATH OPERATIONS ###

@router.get("/", response_model=list[TaskPublic])
def read_tasks(db: SessionDep, current_user: CurrentActiveUserDep,
               completed: bool | None = None, title: str | None = None, search: str | None = None,
               order_by: str | None = None, order: str = "asc",
               skip: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=0, le=100)] = 100):
    return crud.get_user_tasks(db, current_user.id, completed, title, search, order_by, order, skip, limit)


@router.get("/{task_id}", response_model=TaskPublic)
def read_task(task_id: int, db: SessionDep, current_user: CurrentActiveUserDep):
    task = crud.get_user_task_by_id(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(new_task: TaskCreate, db: SessionDep, current_user: CurrentActiveUserDep):
    return crud.create_user_task(db, current_user.id, new_task)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, task_update: TaskUpdate, db: SessionDep, current_user: CurrentActiveUserDep):
    result = crud.update_user_task(db, current_user.id, task_id, task_update)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return result


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: SessionDep, current_user: CurrentActiveUserDep):
    success = crud.delete_user_task(db, current_user.id, task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")