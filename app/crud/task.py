from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_

from app.models import task as model
from app.schemas import task as schema



def get_user_tasks(db: Session, user_id: int,
                   completed: bool | None = None, title: str | None = None, search: str | None = None,
                   skip: int = 0, limit: int = 100) -> list[model.Task]:
    # Basic query
    stmt = select(model.Task).where(model.Task.user_id == user_id)
    # Optional queries (filters)
    if completed is not None:
        stmt = stmt.where(model.Task.completed == completed)
    if title:
        # Delete whitespaces
        # title = title.strip()
        # if title:
        stmt = stmt.where(model.Task.title.icontains(title))
    if search:
        stmt = stmt.where(or_(model.Task.title.icontains(search), model.Task.description.icontains(search)))
    # Finally, offset and limit
    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()

def get_user_task_by_id(db: Session, user_id: int, task_id: int) -> model.Task | None:
    stmt = select(model.Task).where(model.Task.user_id == user_id).where(model.Task.id == task_id)
    result = db.execute(stmt)
    return result.scalars().first()


def create_user_task(db: Session, user_id: int, task_create: schema.TaskCreate) -> model.Task:
    # db_task = model.Task(title=task.title, description=task.description)
    task = model.Task(**task_create.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_user_task(db: Session, user_id: int, task_id: int, task_update: schema.TaskUpdate) -> model.Task | None:
    task = get_user_task_by_id(db, user_id, task_id)
    if not task:
        return None
    
    task_data = task_update.model_dump(exclude_unset=True)
    for field, value in task_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task


def delete_user_task(db: Session, user_id: int, task_id: int) -> bool:
    task = get_user_task_by_id(db, user_id, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True