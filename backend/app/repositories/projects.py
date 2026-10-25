from app.models.project import Project
from sqlalchemy.orm import Session

class ProjectRepository:
    """Database access for projects."""

    def __init__(self, db: Session):
        """Store the database session used by every method."""
        self.db = db

    def get_by_id(self, project_id: int) -> Project | None:
        """Return the project with this id, or None."""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def list_all(self, page: int, page_size: int) -> list[Project]:
        """Return one page of projects ordered by id."""
        offset = (page - 1) * page_size
        return (self.db.query(Project)
        .order_by(Project.id)
        .offset(offset)
        .limit(page_size)
        .all())

    def create(self, project: Project) -> Project:
        """Insert a project and return it with its database id."""
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        """Save changes already made on the project and return it."""
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        """Delete the project. Its tasks are removed by the database cascade."""
        self.db.delete(project)
        self.db.commit()
