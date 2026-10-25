from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.labels import LabelRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.schemas.label import LabelCreate, LabelRead, TaskLabelCreate
from app.services.labels import LabelService

router = APIRouter(tags=["labels"], dependencies=[Depends(get_current_user)])


def _service(db: Session) -> LabelService:
    """Build a label service bound to this request's database session."""
    return LabelService(
        LabelRepository(db),
        ProjectRepository(db),
        TaskRepository(db),
        TeamRepository(db),
        ActivityRepository(db),
    )


@router.post("/projects/{project_id}/labels", response_model=LabelRead, status_code=201)
def create_label(
    project_id: int,
    payload: LabelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a label. Only an owner or admin may do this."""
    return _service(db).create(project_id, payload, current_user.id)


@router.get("/projects/{project_id}/labels", response_model=list[LabelRead])
def list_labels(
    project_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Return one page of labels on a project the user can see."""
    return _service(db).list(project_id, current_user.id, page, page_size)


@router.delete("/projects/{project_id}/labels/{label_id}", status_code=204)
def delete_label(
    project_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a label. Only an owner or admin may do this."""
    _service(db).delete(project_id, label_id, current_user.id)


@router.get("/tasks/{task_id}/labels", response_model=list[LabelRead])
def list_task_labels(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the labels attached to a task the user can see."""
    return _service(db).list_for_task(task_id, current_user.id)


@router.post("/tasks/{task_id}/labels", response_model=LabelRead, status_code=201)
def add_task_label(
    task_id: int,
    payload: TaskLabelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach a project label to a task. Any member may do this."""
    return _service(db).add_to_task(task_id, payload.label_id, current_user.id)


@router.delete("/tasks/{task_id}/labels/{label_id}", status_code=204)
def remove_task_label(
    task_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a label from a task. Any member may do this."""
    _service(db).remove_from_task(task_id, label_id, current_user.id)
