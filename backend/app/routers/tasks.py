from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(tags=["tasks"])


def _delivery_date_for(duration_days: int | None, created_at: datetime) -> date | None:
    if duration_days is None:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return created_at.astimezone(UTC).date() + timedelta(days=duration_days)


def _get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=201,
)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
):
    _get_project_or_404(project_id, db)

    now = datetime.now(UTC)
    task = Task(
        **payload.model_dump(),
        project_id=project_id,
        delivery_date=_delivery_date_for(payload.duration_days, now),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(project_id: int, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    return db.query(Task).filter(Task.project_id == project_id).all()


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_task_or_404(task_id, db)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = _get_task_or_404(task_id, db)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)

    if "duration_days" in data:
        task.delivery_date = _delivery_date_for(task.duration_days, task.created_at)

    task.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()
