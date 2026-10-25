from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.projects import ProjectRepository
from app.repositories.teams import TeamRepository
from app.repositories.users import UserRepository
from app.schemas.project import ProjectCreate, ProjectRead
from app.schemas.team import (
    TeamCreate,
    TeamDetail,
    TeamMemberCreate,
    TeamMemberRead,
    TeamRead,
)
from app.services.projects import ProjectService
from app.services.teams import TeamService

router = APIRouter(prefix="/teams", tags=["teams"], dependencies=[Depends(get_current_user)])


def _teams(db: Session) -> TeamService:
    """Build a team service bound to this request's database session."""
    return TeamService(TeamRepository(db), UserRepository(db))


def _projects(db: Session) -> ProjectService:
    """Build a project service bound to this request's database session."""
    return ProjectService(ProjectRepository(db), TeamRepository(db))


@router.post("", response_model=TeamRead, status_code=201)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a team and make the current user its owner."""
    return _teams(db).create(payload, current_user)


@router.get("", response_model=list[TeamRead])
def list_teams(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Return one page of teams the current user belongs to."""
    return _teams(db).list(current_user.id, page, page_size)


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a team the current user belongs to, including its members."""
    return _teams(db).get(team_id, current_user.id)


@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a team. Only the owner may do this."""
    _teams(db).delete(team_id, current_user.id)


@router.post("/{team_id}/members", response_model=TeamMemberRead, status_code=201)
def add_member(
    team_id: int,
    payload: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a user to the team."""
    return _teams(db).add_member(team_id, current_user.id, payload)


@router.delete("/{team_id}/members/{user_id}", status_code=204)
def remove_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a user from the team."""
    _teams(db).remove_member(team_id, current_user.id, user_id)


@router.post("/{team_id}/projects", response_model=ProjectRead, status_code=201)
def create_project(
    team_id: int,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a project on this team. Only an owner or admin may do this."""
    return _projects(db).create(team_id, payload, current_user.id)
