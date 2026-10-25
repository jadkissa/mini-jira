from fastapi import HTTPException

from app.models.team import TeamMember
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
    """Return the membership, or 404 when the user is outside the team."""
    if team_id is None:
        raise HTTPException(status_code=404, detail=detail)
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
