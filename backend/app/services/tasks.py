from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException

from app.models.task import Task
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


_SORT_FIELDS = {"id", "delivery_date", "priority", "status", "created_at"}


def _parse_sort(sort: str | None) -> tuple[str, bool]:
    """Return the column name and whether the order is descending."""
    if sort is None:
        return "id", False
    descending = sort.startswith("-")
    field = sort[1:] if descending else sort
    if field not in _SORT_FIELDS:
        raise HTTPException(status_code=422, detail="Invalid sort field")
    return field, descending


def _delivery_date_for(duration_days: int | None, created_at: datetime) -> date | None:
    """Return created_at plus duration_days, or None when duration is missing."""
    if duration_days is None:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return created_at.astimezone(UTC).date() + timedelta(days=duration_days)


class TaskService:
    """Task rules: project must exist, and delivery_date follows duration_days."""

    def __init__(self, repo: TaskRepository, project_repo: ProjectRepository):
        """Store the task and project repositories for this request."""
        self.repo = repo
        self.project_repo = project_repo

    def _get_project_or_404(self, project_id: int):
        """Return the project, or 404 if it does not exist."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create(self, payload: TaskCreate, project_id: int) -> Task:
        """Create a task on an existing project and set its delivery date."""
        self._get_project_or_404(project_id)
        now = datetime.now(UTC)
        task = Task(
            **payload.model_dump(),
            project_id=project_id,
            delivery_date=_delivery_date_for(payload.duration_days, now),
        )
        return self.repo.create(task)

    def list(
        self,
        project_id: int,
        page: int,
        page_size: int,
        status: TaskStatus | None = None,
        sort: str | None = None,
    ) -> list[Task]:
        """Return one page of a project's tasks, optionally filtered and sorted."""
        self._get_project_or_404(project_id)
        sort_field, descending = _parse_sort(sort)
        return self.repo.list_by_project(
            project_id, page, page_size, status, sort_field, descending
        )

    def get(self, task_id: int) -> Task:
        """Return a task, or 404 if it does not exist."""
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def update(self, task_id: int, payload: TaskUpdate) -> Task:
        """Apply the sent fields and recompute delivery_date when duration changes."""
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
        """Delete a task, or 404 if it does not exist."""
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        self.repo.delete(task)
