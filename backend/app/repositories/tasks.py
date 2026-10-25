from app.models.task import Task
from sqlalchemy.orm import Session

class TaskRepository:
    """Database access for tasks."""

    def __init__(self, db: Session):
        """Store the database session used by every method."""
        self.db = db
    
    def get_by_id(self, task_id: int) -> Task | None:
        """Return the task with this id, or None."""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list_by_project(
        self,
        project_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
        sort_field: str = "id",
        descending: bool = False,
    ) -> list[Task]:
        """Return one page of a project's tasks, optionally filtered and sorted."""
        offset = (page - 1) * page_size
        query = self.db.query(Task).filter(Task.project_id == project_id)
        if status is not None:
            query = query.filter(Task.status == status)
        column = getattr(Task, sort_field)
        order = column.desc() if descending else column.asc()
        return query.order_by(order).offset(offset).limit(page_size).all()

    def create(self, task: Task) -> Task:
        """Insert a task and return it with its database id."""
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update(self, task: Task) -> Task:
        """Save changes already made on the task and return it."""
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        """Delete the task."""
        self.db.delete(task)
        self.db.commit()
