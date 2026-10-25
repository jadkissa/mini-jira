from app.models.activity import ActivityLog
from app.repositories.activity import ActivityRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.services.access import visible_task


class ActivityService:
    """Read the activity recorded against a task."""

    def __init__(
        self,
        repo: ActivityRepository,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
    ):
        self.repo = repo
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.team_repo = team_repo

    def list(self, task_id: int, user_id: int, page: int, page_size: int) -> list[ActivityLog]:
        """Return one page of activity for a visible task."""
        visible_task(self.task_repo, self.project_repo, self.team_repo, task_id, user_id)
        return self.repo.list_by_task(task_id, page, page_size)
