from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies.database import SessionDep
from app.dependencies.auth import CurrentActiveUserDep
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.crud import task as crud



router = APIRouter(
    prefix = "/tasks",
    tags = ["tasks"],
)


### PATH OPERATIONS ###

@router.get("/", response_model=list[TaskResponse])
def read_tasks(db: SessionDep, current_user: CurrentActiveUserDep,
               completed: bool | None = None, title: str | None = None, search: str | None = None,
               skip: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=0, le=100)] = 100):
    return crud.get_user_tasks(db, current_user.id, completed, title, search, skip, limit)


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: SessionDep, current_user: CurrentActiveUserDep):
    task = crud.get_user_task_by_id(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskResponse)
def create_task(new_task: TaskCreate, db: SessionDep, current_user: CurrentActiveUserDep):
    return crud.create_user_task(db, current_user.id, new_task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: SessionDep, current_user: CurrentActiveUserDep):
    result = crud.update_user_task(db, current_user.id, task_id, task_update)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.delete("/{task_id}")
def delete_task(task_id: int, db: SessionDep, current_user: CurrentActiveUserDep) -> dict[str, str]:
    success = crud.delete_user_task(db, current_user.id, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}