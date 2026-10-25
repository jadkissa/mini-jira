from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.comments import CommentRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.teams import TeamRepository
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comments import CommentService

router = APIRouter(tags=["comments"], dependencies=[Depends(get_current_user)])


def _service(db: Session) -> CommentService:
    """Build a comment service bound to this request's database session."""
    return CommentService(
        CommentRepository(db),
        TaskRepository(db),
        ProjectRepository(db),
        TeamRepository(db),
        ActivityRepository(db),
    )


@router.post("/tasks/{task_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment. Any member of the task's team may do this."""
    return _service(db).create(task_id, payload, current_user.id)


@router.get("/tasks/{task_id}/comments", response_model=list[CommentRead])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Return one page of comments on a task the user can see."""
    return _service(db).list(task_id, current_user.id, page, page_size)
