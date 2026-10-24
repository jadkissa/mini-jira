from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException

from app.models.task import Task
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


def _delivery_date_for(duration_days: int | None, created_at: datetime) -> date | None:
    if duration_days is None:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return created_at.astimezone(UTC).date() + timedelta(days=duration_days)


class TaskService:
    def __init__(self, repo: TaskRepository, project_repo: ProjectRepository):
        self.repo = repo
        self.project_repo = project_repo

    def _get_project_or_404(self, project_id: int):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create(self, payload: TaskCreate, project_id: int) -> Task:
        self._get_project_or_404(project_id)
        now = datetime.now(UTC)
        task = Task(
            **payload.model_dump(),
            project_id=project_id,
            delivery_date=_delivery_date_for(payload.duration_days, now),
        )
        return self.repo.create(task)

    def list(self, project_id: int) -> list[Task]:
        self._get_project_or_404(project_id)
        return self.repo.list_by_project(project_id)

    def get(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def update(self, task_id: int, payload: TaskUpdate) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(task, key, value)
        if "duration_days" in data:
            task.delivery_date = _delivery_date_for(task.duration_days, task.created_at)
        task.updated_at = datetime.now(UTC)
        return self.repo.update(task)

    def delete(self, task_id: int) -> None:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        self.repo.delete(task)
