from app.models.task import Task
from sqlalchemy.orm import Session

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list_by_project(self, project_id: int) -> list[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    