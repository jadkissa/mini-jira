from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.repositories.projects import ProjectRepository
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("",response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    service = ProjectService(ProjectRepository(db))
    return service.create(payload)

@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    service = ProjectService(ProjectRepository(db))
    return service.list()

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(ProjectRepository(db))
    return service.get(project_id)

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    service = ProjectService(ProjectRepository(db))
    return service.update(project_id, payload)

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(ProjectRepository(db))
    service.delete(project_id)