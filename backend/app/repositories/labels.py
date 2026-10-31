from sqlalchemy.orm import Session

from app.models.label import Label, TaskLabel


class LabelRepository:
    """Database access for labels and the task-label join."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, label_id: int) -> Label | None:
        """Return the label with this id, or None."""
        return self.db.query(Label).filter(Label.id == label_id).first()

    def get_by_name(self, project_id: int, name: str) -> Label | None:
        """Return the label with this name on the project, or None."""
        return (
            self.db.query(Label)
            .filter(Label.project_id == project_id, Label.name == name)
            .first()
        )

    def list_by_project(self, project_id: int, page: int, page_size: int) -> list[Label]:
        """Return one page of labels on a project."""
        offset = (page - 1) * page_size
        return (
            self.db.query(Label)
            .filter(Label.project_id == project_id)
            .order_by(Label.id)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def create(self, label: Label) -> Label:
        """Insert a label and return it."""
        self.db.add(label)
        self.db.flush()
        self.db.refresh(label)
        return label

    def delete(self, label: Label) -> None:
        """Delete a label. Task links are removed by the database cascade."""
        self.db.delete(label)
        self.db.flush()

    def get_task_label(self, task_id: int, label_id: int) -> TaskLabel | None:
        """Return the link between this task and label, or None."""
        return (
            self.db.query(TaskLabel)
            .filter(TaskLabel.task_id == task_id, TaskLabel.label_id == label_id)
            .first()
        )

    def list_for_task(self, task_id: int) -> list[Label]:
        """Return every label attached to this task."""
        return (
            self.db.query(Label)
            .join(TaskLabel, TaskLabel.label_id == Label.id)
            .filter(TaskLabel.task_id == task_id)
            .order_by(Label.id)
            .all()
        )

    def add_task_label(self, link: TaskLabel) -> TaskLabel:
        """Attach a label to a task."""
        self.db.add(link)
        self.db.flush()
        self.db.refresh(link)
        return link

    def remove_task_label(self, link: TaskLabel) -> None:
        """Remove a label from a task."""
        self.db.delete(link)
        self.db.flush()
