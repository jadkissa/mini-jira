from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.projects import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def _service(db: Session) -> ProjectService:
    """Build a project service bound to this request's database session."""
    return ProjectService(ProjectRepository(db))


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Create a project and return it."""
    return _service(db).create(payload)


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db),
                    page: int = Query(1, ge=1),
                    page_size: int = Query(20, ge=1, le=100)):
    """Return one page of projects."""
    return _service(db).list(page, page_size)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Return one project, or 404 if it does not exist."""
    return _service(db).get(project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    """Update the fields sent in the body and return the project."""
    return _service(db).update(project_id, payload)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and its tasks, or 404 if it does not exist."""
    _service(db).delete(project_id)
