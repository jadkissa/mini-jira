from fastapi import HTTPException

from app.models.project import Project
from app.models.task import Task
from app.models.team import TeamMember
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository

OWNER = "owner"
ADMIN = "admin"
MEMBER = "member"
MANAGERS = {OWNER, ADMIN}


def require_membership(
    repo: TeamRepository,
    team_id: int | None,
    user_id: int,
    detail: str = "Team not found",
) -> TeamMember:
    """Return the membership, or 404 when the user is outside the team.

    A superuser gets an unsaved owner membership on every existing team.
    """
    if team_id is None:
        raise HTTPException(status_code=404, detail=detail)
    if repo.is_superuser(user_id):
        if not repo.get_by_id(team_id):
            raise HTTPException(status_code=404, detail=detail)
        return TeamMember(team_id=team_id, user_id=user_id, role=OWNER)
    membership = repo.get_membership(team_id, user_id)
    if not membership:
        raise HTTPException(status_code=404, detail=detail)
    return membership


def require_manager(membership: TeamMember) -> None:
    """Allow only an owner or an admin."""
    if membership.role not in MANAGERS:
        raise HTTPException(status_code=403, detail="Not allowed")


def require_owner(membership: TeamMember) -> None:
    """Allow only the team owner."""
    if membership.role != OWNER:
        raise HTTPException(status_code=403, detail="Not allowed")


def visible_project(
    project_repo: ProjectRepository,
    team_repo: TeamRepository,
    project_id: int,
    user_id: int,
    detail: str = "Project not found",
) -> tuple[Project, TeamMember]:
    """Return a project the user belongs to, or 404."""
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=detail)
    membership = require_membership(team_repo, project.team_id, user_id, detail=detail)
    return project, membership


def visible_task(
    task_repo: TaskRepository,
    project_repo: ProjectRepository,
    team_repo: TeamRepository,
    task_id: int,
    user_id: int,
) -> tuple[Task, TeamMember]:
    """Return a task the user can see, or 404."""
    task = task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        _, membership = visible_project(
            project_repo,
            team_repo,
            task.project_id,
            user_id,
            detail="Task not found",
        )
    except HTTPException:
        raise HTTPException(status_code=404, detail="Task not found") from None
    return task, membership
