from app.models.project import Project
from app.repositories.projects import ProjectRepository
from app.repositories.teams import TeamRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.access import require_manager, require_membership, visible_project


class ProjectService:
    """Project rules, limited to teams the user belongs to."""

    def __init__(self, repo: ProjectRepository, team_repo: TeamRepository):
        self.repo = repo
        self.team_repo = team_repo

    def create(self, team_id: int, payload: ProjectCreate, user_id: int) -> Project:
        """Create a project on a team. Only an owner or admin may do this."""
        membership = require_membership(self.team_repo, team_id, user_id)
        require_manager(membership)
        project = Project(**payload.model_dump(), team_id=team_id)
        return self.repo.create(project)

    def list(self, user_id: int, page: int, page_size: int) -> list[Project]:
        """Return one page of projects from the user's teams, or every project for a superuser."""
        if self.team_repo.is_superuser(user_id):
            return self.repo.list_all(page, page_size)
        team_ids = self.team_repo.team_ids_for_user(user_id)
        return self.repo.list_for_teams(team_ids, page, page_size)

    def get(self, project_id: int, user_id: int) -> Project:
        """Return a project the user can see, or 404."""
        return self._visible(project_id, user_id)[0]

    def update(self, project_id: int, payload: ProjectUpdate, user_id: int) -> Project:
        """Update a project. Only an owner or admin may do this."""
        project, membership = self._visible(project_id, user_id)
        require_manager(membership)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        return self.repo.update(project)

    def delete(self, project_id: int, user_id: int) -> None:
        """Delete a project. Only an owner or admin may do this."""
        project, membership = self._visible(project_id, user_id)
        require_manager(membership)
        self.repo.delete(project)

    def _visible(self, project_id: int, user_id: int):
        return visible_project(self.repo, self.team_repo, project_id, user_id)
