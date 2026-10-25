from fastapi import HTTPException

from app.models.team import Team, TeamMember
from app.models.user import User
from app.repositories.teams import TeamRepository
from app.repositories.users import UserRepository
from app.schemas.team import TeamCreate, TeamMemberCreate
from app.services.access import (
    ADMIN,
    OWNER,
    require_manager,
    require_membership,
    require_owner,
)


class TeamService:
    """Team rules: membership, invites, and who may delete the team."""

    def __init__(self, repo: TeamRepository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo

    def create(self, payload: TeamCreate, owner: User) -> Team:
        """Create a team and make the current user its owner."""
        team = self.repo.create(Team(name=payload.name, owner_id=owner.id))
        self.repo.add_member(
            TeamMember(team_id=team.id, user_id=owner.id, role=OWNER)
        )
        return team

    def list(self, user_id: int, page: int, page_size: int) -> list[Team]:
        """Return teams the user belongs to."""
        return self.repo.list_for_user(user_id, page, page_size)

    def get(self, team_id: int, user_id: int) -> Team:
        """Return a team the user belongs to, or 404."""
        require_membership(self.repo, team_id, user_id)
        team = self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team

    def delete(self, team_id: int, user_id: int) -> None:
        """Delete a team. Only the owner may do this."""
        membership = require_membership(self.repo, team_id, user_id)
        require_owner(membership)
        team = self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        self.repo.delete(team)

    def add_member(self, team_id: int, actor_id: int, payload: TeamMemberCreate) -> TeamMember:
        """Invite a user. Owners may add admins. Admins may add members."""
        membership = require_membership(self.repo, team_id, actor_id)
        require_manager(membership)
        if payload.role == ADMIN and membership.role != OWNER:
            raise HTTPException(status_code=403, detail="Not allowed")
        if not self.user_repo.get_by_id(payload.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        if self.repo.get_membership(team_id, payload.user_id):
            raise HTTPException(status_code=409, detail="User is already a member")
        return self.repo.add_member(
            TeamMember(team_id=team_id, user_id=payload.user_id, role=payload.role.value)
        )

    def remove_member(self, team_id: int, actor_id: int, user_id: int) -> None:
        """Remove a member. An admin cannot remove the owner or another admin."""
        membership = require_membership(self.repo, team_id, actor_id)
        require_manager(membership)
        target = self.repo.get_membership(team_id, user_id)
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target.role == OWNER:
            raise HTTPException(status_code=403, detail="Not allowed")
        if target.role == ADMIN and membership.role != OWNER:
            raise HTTPException(status_code=403, detail="Not allowed")
        self.repo.remove_member(target)
