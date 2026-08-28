"""Users, plus the moderation flags the admin panel acts on."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.channel import ChannelMember
    from app.models.message import Message, ThreadMessage
    from app.models.report import Report


def new_id() -> str:
    return str(uuid.uuid4())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    # The frontend addresses people by handle (@name) and displays `name`
    # separately, so both exist and only the handle is unique.
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    # Password hashing is deliberately absent here. It belongs to the Auth area
    # (Section 5.3), which adds password_hash in its own migration. Nothing in
    # this branch authenticates anyone.

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Ban state lives on the user, not on the report, because AdminDashboard
    # bans a member globally and then filters their content everywhere.
    is_banned: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    banned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    banned_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    memberships: Mapped[list[ChannelMember]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    messages: Mapped[list[Message]] = relationship(back_populates="author")
    thread_messages: Mapped[list[ThreadMessage]] = relationship(back_populates="author")

    reports_filed: Mapped[list[Report]] = relationship(
        back_populates="reporter", foreign_keys="Report.reporter_id"
    )
    reports_against: Mapped[list[Report]] = relationship(
        back_populates="reported_user", foreign_keys="Report.reported_user_id"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
