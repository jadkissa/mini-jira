"""Promote an existing user to superuser.

Usage: python -m app.scripts.make_superuser someone@example.com
"""
import sys

from app.db.session import SessionLocal
from app.models.activity import ActivityLog  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.label import Label, TaskLabel  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.team import Team, TeamMember  # noqa: F401
from app.repositories.users import UserRepository


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m app.scripts.make_superuser <email>")
    email = sys.argv[1]
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user:
            sys.exit(f"No user with email {email}")
        user.is_superuser = True
        repo.update(user)
        print(f"{email} is now a superuser")
    finally:
        db.close()


if __name__ == "__main__":
    main()
