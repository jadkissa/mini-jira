from app.models.activity import ActivityLog
from app.models.comment import Comment
from app.repositories.activity import ActivityRepository
from app.repositories.comments import CommentRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.schemas.comment import CommentCreate
from app.services.access import visible_task


class CommentService:
    """Comment rules: any member of the task's team may read and write."""

    def __init__(
        self,
        repo: CommentRepository,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
        activity_repo: ActivityRepository,
    ):
        self.repo = repo
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.team_repo = team_repo
        self.activity_repo = activity_repo

    def create(self, task_id: int, payload: CommentCreate, author_id: int) -> Comment:
        """Add a comment and record it on the task."""
        visible_task(self.task_repo, self.project_repo, self.team_repo, task_id, author_id)
        comment = self.repo.create(
            Comment(task_id=task_id, author_id=author_id, body=payload.body)
        )
        self.activity_repo.create(
            ActivityLog(
                task_id=task_id,
                actor_id=author_id,
                action="commented",
                new_value=payload.body,
            )
        )
        return comment

    def list(self, task_id: int, user_id: int, page: int, page_size: int) -> list[Comment]:
        """Return one page of comments on a visible task."""
        visible_task(self.task_repo, self.project_repo, self.team_repo, task_id, user_id)
        return self.repo.list_by_task(task_id, page, page_size)
