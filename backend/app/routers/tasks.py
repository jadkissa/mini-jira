from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.repositories.users import UserRepository
from app.schemas.task import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter(tags=["tasks"], dependencies=[Depends(get_current_user)])


def _service(db: Session) -> TaskService:
    """Build a task service bound to this request's database session."""
    return TaskService(
        TaskRepository(db),
        ProjectRepository(db),
        UserRepository(db),
        TeamRepository(db),
    )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=201,
)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a task under a project, reported by the logged-in user."""
    return _service(db).create(payload, project_id, current_user.id)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(project_id: int, db: Session = Depends(get_db),
                page: int = Query(1, ge=1),
                page_size: int = Query(20, ge=1, le=100),
                status: TaskStatus | None = None,
                sort: str | None = None,
                current_user: User = Depends(get_current_user)):
    """Return one page of tasks for a project the user belongs to."""
    return _service(db).list(
        project_id, page, page_size, status, sort, user_id=current_user.id
    )


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return one task the user can see, or 404."""
    return _service(db).get(task_id, current_user.id)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task. Any member of the project's team may do this."""
    return _service(db).update(task_id, payload, current_user.id)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task. Only an owner or admin may do this."""
    _service(db).delete(task_id, current_user.id)
