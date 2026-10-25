from __future__ import annotations

from fastapi import HTTPException

from app.models.activity import ActivityLog
from app.models.label import Label, TaskLabel
from app.repositories.activity import ActivityRepository
from app.repositories.labels import LabelRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.schemas.label import LabelCreate
from app.services.access import require_manager, visible_project, visible_task


class LabelService:
    """Label rules: managers define labels, any member can put them on tasks."""

    def __init__(
        self,
        repo: LabelRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
        team_repo: TeamRepository,
        activity_repo: ActivityRepository,
    ):
        self.repo = repo
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.team_repo = team_repo
        self.activity_repo = activity_repo

    def create(self, project_id: int, payload: LabelCreate, user_id: int) -> Label:
        """Create a label. Only an owner or admin may do this."""
        _, membership = visible_project(
            self.project_repo, self.team_repo, project_id, user_id
        )
        require_manager(membership)
        if self.repo.get_by_name(project_id, payload.name):
            raise HTTPException(status_code=409, detail="Label already exists")
        return self.repo.create(
            Label(project_id=project_id, name=payload.name, color=payload.color)
        )

    def list(self, project_id: int, user_id: int, page: int, page_size: int) -> list[Label]:
        """Return one page of labels on a visible project."""
        visible_project(self.project_repo, self.team_repo, project_id, user_id)
        return self.repo.list_by_project(project_id, page, page_size)

    def delete(self, project_id: int, label_id: int, user_id: int) -> None:
        """Delete a label. Only an owner or admin may do this."""
        _, membership = visible_project(
            self.project_repo, self.team_repo, project_id, user_id
        )
        require_manager(membership)
        label = self._label_on_project(project_id, label_id)
        self.repo.delete(label)

    def list_for_task(self, task_id: int, user_id: int) -> list[Label]:
        """Return the labels attached to a visible task."""
        visible_task(self.task_repo, self.project_repo, self.team_repo, task_id, user_id)
        return self.repo.list_for_task(task_id)

    def add_to_task(self, task_id: int, label_id: int, user_id: int) -> Label:
        """Attach a label from the same project. Any member may do this."""
        task, _ = visible_task(
            self.task_repo, self.project_repo, self.team_repo, task_id, user_id
        )
        label = self._label_on_project(task.project_id, label_id)
        if self.repo.get_task_label(task_id, label_id):
            raise HTTPException(status_code=409, detail="Label already on task")
        self.repo.add_task_label(TaskLabel(task_id=task_id, label_id=label_id))
        self.activity_repo.create(
            ActivityLog(
                task_id=task_id,
                actor_id=user_id,
                action="label_added",
                new_value=label.name,
            )
        )
        return label

    def remove_from_task(self, task_id: int, label_id: int, user_id: int) -> None:
        """Remove a label from a task. Any member may do this."""
        task, _ = visible_task(
            self.task_repo, self.project_repo, self.team_repo, task_id, user_id
        )
        label = self._label_on_project(task.project_id, label_id)
        link = self.repo.get_task_label(task_id, label_id)
        if not link:
            raise HTTPException(status_code=404, detail="Label not found")
        self.repo.remove_task_label(link)
        self.activity_repo.create(
            ActivityLog(
                task_id=task_id,
                actor_id=user_id,
                action="label_removed",
                old_value=label.name,
            )
        )

    def _label_on_project(self, project_id: int, label_id: int) -> Label:
        label = self.repo.get_by_id(label_id)
        if not label or label.project_id != project_id:
            raise HTTPException(status_code=404, detail="Label not found")
        return label
