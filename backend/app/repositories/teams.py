from sqlalchemy.orm import Session

from app.models.team import Team, TeamMember
from app.models.user import User


class TeamRepository:
    """Database access for teams and memberships."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, team_id: int) -> Team | None:
        """Return the team with this id, or None."""
        return self.db.query(Team).filter(Team.id == team_id).first()

    def list_for_user(self, user_id: int, page: int, page_size: int) -> list[Team]:
        """Return one page of teams this user belongs to."""
        offset = (page - 1) * page_size
        return (
            self.db.query(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .filter(TeamMember.user_id == user_id)
            .order_by(Team.id)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def list_all(self, page: int, page_size: int) -> list[Team]:
        """Return one page of every team."""
        offset = (page - 1) * page_size
        return self.db.query(Team).order_by(Team.id).offset(offset).limit(page_size).all()

    def is_superuser(self, user_id: int) -> bool:
        """Return True when this user has full permissions on every team."""
        user = self.db.get(User, user_id)
        return bool(user and user.is_superuser)

    def create(self, team: Team) -> Team:
        """Insert a team and return it."""
        self.db.add(team)
        self.db.flush()
        self.db.refresh(team)
        return team

    def delete(self, team: Team) -> None:
        """Delete a team. Projects are removed by the database cascade."""
        self.db.delete(team)
        self.db.flush()

    def owns_team(self, user_id: int) -> bool:
        """Return True when this user is the owner_id of any team."""
        return self.db.query(Team.id).filter(Team.owner_id == user_id).first() is not None

    def get_membership(self, team_id: int, user_id: int) -> TeamMember | None:
        """Return this user's membership on the team, or None."""
        return (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            .first()
        )

    def team_ids_for_user(self, user_id: int) -> list[int]:
        """Return the ids of every team this user belongs to."""
        rows = (
            self.db.query(TeamMember.team_id)
            .filter(TeamMember.user_id == user_id)
            .all()
        )
        return [row[0] for row in rows]

    def add_member(self, member: TeamMember) -> TeamMember:
        """Insert a membership and return it."""
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member

    def remove_member(self, member: TeamMember) -> None:
        """Remove a user from a team."""
        self.db.delete(member)
        self.db.flush()
