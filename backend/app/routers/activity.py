from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.schemas.activity import ActivityRead
from app.services.activity import ActivityService

router = APIRouter(tags=["activity"], dependencies=[Depends(get_current_user)])


def _service(db: Session) -> ActivityService:
    """Build an activity service bound to this request's database session."""
    return ActivityService(
        ActivityRepository(db),
        TaskRepository(db),
        ProjectRepository(db),
        TeamRepository(db),
    )


@router.get("/tasks/{task_id}/activity", response_model=list[ActivityRead])
def list_activity(
    task_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Return one page of activity for a task the user can see."""
    return _service(db).list(task_id, current_user.id, page, page_size)
