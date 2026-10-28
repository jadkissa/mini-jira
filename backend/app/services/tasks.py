from datetime import UTC, date, datetime, timedelta
from enum import Enum

from fastapi import HTTPException

from app.models.activity import ActivityLog
from app.models.task import Task
from app.repositories.activity import ActivityRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.repositories.users import UserRepository
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate
from app.services.access import MEMBER, require_membership

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


def _as_text(value) -> str | None:
    """Store enum and date values as plain text in the activity log."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    return str(value)


def _delivery_date_for(duration_days: int | None, created_at: datetime) -> date | None:
    """Return created_at plus duration_days, or None when duration is missing."""
    if duration_days is None:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return created_at.astimezone(UTC).date() + timedelta(days=duration_days)


class TaskService:
    """Task rules: project must exist, and delivery_date follows duration_days."""

    def __init__(
        self,
        repo: TaskRepository,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
        team_repo: TeamRepository,
        activity_repo: ActivityRepository,
    ):
        """Store the repositories for this request."""
        self.repo = repo
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.team_repo = team_repo
        self.activity_repo = activity_repo

    def _visible_project(self, project_id: int, user_id: int):
        """Return a project the user belongs to, or 404."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        membership = require_membership(
            self.team_repo,
            project.team_id,
            user_id,
            detail="Project not found",
        )
        return project, membership

    def _visible_task(self, task_id: int, user_id: int):
        """Return a task the user can see, or 404."""
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        try:
            _, membership = self._visible_project(task.project_id, user_id)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Task not found")
        return task, membership

    def _get_user_or_404(self, user_id: int):
        """Return the user, or 404 if they do not exist."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create(self, payload: TaskCreate, project_id: int, reporter_id: int) -> Task:
        """Create a task on a visible project, reported by the logged-in user."""
        self._visible_project(project_id, reporter_id)
        if payload.assignee_id is not None:
            self._get_user_or_404(payload.assignee_id)
        now = datetime.now(UTC)
        task = Task(
            **payload.model_dump(),
            project_id=project_id,
            reporter_id=reporter_id,
            delivery_date=_delivery_date_for(payload.duration_days, now),
        )
        task = self.repo.create(task)
        self._log(task.id, reporter_id, "created", None, task.title)
        return task

    def list(
        self,
        project_id: int,
        page: int,
        page_size: int,
        status: TaskStatus | None = None,
        sort: str | None = None,
        *,
        user_id: int,
    ) -> list[Task]:
        """Return one page of a visible project's tasks, optionally filtered and sorted."""
        self._visible_project(project_id, user_id)
        sort_field, descending = _parse_sort(sort)
        return self.repo.list_by_project(
            project_id, page, page_size, status, sort_field, descending
        )

    def get(self, task_id: int, user_id: int) -> Task:
        """Return a task the user can see, or 404."""
        task, _ = self._visible_task(task_id, user_id)
        return task

    def update(self, task_id: int, payload: TaskUpdate, user_id: int) -> Task:
        """Apply the sent fields. Any team member may edit a task."""
        task, _ = self._visible_task(task_id, user_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("assignee_id") is not None:
            self._get_user_or_404(data["assignee_id"])
        changes: list[tuple[str, str | None, str | None]] = []
        for key, value in data.items():
            old = _as_text(getattr(task, key))
            new = _as_text(value)
            if old != new:
                changes.append((key, old, new))
            setattr(task, key, value)
        if "duration_days" in data:
            task.delivery_date = _delivery_date_for(task.duration_days, task.created_at)
        task.updated_at = datetime.now(UTC)
        task = self.repo.update(task)
        for key, old, new in changes:
            self._log(task.id, user_id, key, old, new)
        return task

    def delete(self, task_id: int, user_id: int) -> None:
        """Delete a task. Only an owner or admin may do this."""
        task, membership = self._visible_task(task_id, user_id)
        if membership.role == MEMBER:
            raise HTTPException(status_code=403, detail="Not allowed")
        self.repo.delete(task)

    def _log(
        self,
        task_id: int,
        actor_id: int,
        action: str,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        """Append one activity row for this task."""
        self.activity_repo.create(
            ActivityLog(
                task_id=task_id,
                actor_id=actor_id,
                action=action,
                old_value=old_value,
                new_value=new_value,
            )
        )
