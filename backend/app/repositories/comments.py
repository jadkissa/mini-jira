from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    """Database access for comments."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_task(self, task_id: int, page: int, page_size: int) -> list[Comment]:
        """Return one page of comments on a task, oldest first."""
        offset = (page - 1) * page_size
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.id)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def create(self, comment: Comment) -> Comment:
        """Insert a comment and return it."""
        self.db.add(comment)
        self.db.flush()
        self.db.refresh(comment)
        return comment
