from datetime import datetime, UTC
from fastapi import HTTPException
from app.repositories.projects import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.project import Project


class ProjectService:
    """Project rules: create, list, fetch, update, and delete."""

    def __init__(self, repo: ProjectRepository):
        """Store the repository that talks to the database."""
        self.repo = repo
    
    def create(self, payload: ProjectCreate) -> Project: 
        """Build a project from the request and save it."""
        project = Project(**payload.model_dump())
        return self.repo.create(project)
         
    def list(self, page: int, page_size: int) -> list[Project]:
        """Return one page of projects."""
        return self.repo.list_all(page, page_size)
    
    def get(self, project_id: int) -> Project:
        """Return a project, or 404 if it does not exist."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def update(self, project_id: int, payload: ProjectUpdate) -> Project:
        """Apply the sent fields, refresh updated_at, and save."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        project.updated_at = datetime.now(UTC)
        return self.repo.update(project)
    
    def delete(self, project_id: int) -> None:
        """Delete a project, or 404 if it does not exist."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        self.repo.delete(project)
