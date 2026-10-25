from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


class ActivityRepository:
    """Database access for the task activity log."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_task(self, task_id: int, page: int, page_size: int) -> list[ActivityLog]:
        """Return one page of activity for a task, oldest first."""
        offset = (page - 1) * page_size
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.task_id == task_id)
            .order_by(ActivityLog.id)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def create(self, entry: ActivityLog) -> ActivityLog:
        """Insert one activity row and return it."""
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
