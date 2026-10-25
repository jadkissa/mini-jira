from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "Project",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(String, nullable=False)

    team = relationship("Team", back_populates="members")
