from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.projects import ProjectRepository
from app.repositories.teams import TeamRepository
from app.schemas.project import ProjectRead, ProjectUpdate
from app.services.projects import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)


def _service(db: Session) -> ProjectService:
    """Build a project service bound to this request's database session."""
    return ProjectService(ProjectRepository(db), TeamRepository(db))


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Return one page of projects from the user's teams."""
    return _service(db).list(current_user.id, page, page_size)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return one project the user can see, or 404."""
    return _service(db).get(project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project. Only an owner or admin may do this."""
    return _service(db).update(project_id, payload, current_user.id)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a project. Only an owner or admin may do this."""
    _service(db).delete(project_id, current_user.id)
