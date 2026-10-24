from datetime import datetime, UTC
from fastapi import HTTPException
from app.repositories.projects import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.project import Project


class ProjectService:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo
    
    def create(self, payload: ProjectCreate) -> Project: 
        project = Project(**payload.model_dump())
        return self.repo.create(project)
         
    def list(self) -> list[Project]:
        return self.repo.list_all()
    
    def get(self, project_id: int) -> Project:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def update(self, project_id: int, payload: ProjectUpdate) -> Project:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        project.updated_at = datetime.now(UTC)
        return self.repo.update(project)
    
    def delete(self, project_id: int) -> None:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        self.repo.delete(project)