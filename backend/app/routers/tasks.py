from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter(tags=["tasks"])


def _service(db: Session) -> TaskService:
    """Build a task service bound to this request's database session."""
    return TaskService(TaskRepository(db), ProjectRepository(db))


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
    """Create a task under a project and return it."""
    return _service(db).create(payload, project_id)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(project_id: int, db: Session = Depends(get_db),
                page: int = Query(1, ge=1),
                page_size: int = Query(20, ge=1, le=100),
                status: TaskStatus | None = None,
                sort: str | None = None):
    """Return one page of tasks for a project, optionally filtered and sorted."""
    return _service(db).list(project_id, page, page_size, status, sort)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Return one task, or 404 if it does not exist."""
    return _service(db).get(task_id)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
):
    """Update the fields sent in the body and return the task."""
    return _service(db).update(task_id, payload)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task, or 404 if it does not exist."""
    _service(db).delete(task_id)
