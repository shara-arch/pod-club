"""User reports feeding the admin moderation queue.

Mirrors what AdminDashboard.jsx renders today: who was reported, in which
channel, why, and whether the report has been reviewed.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.channel import Channel
    from app.models.user import User


def new_id() -> str:
    return str(uuid.uuid4())


class ReportStatus(str, enum.Enum):
    OPEN = "open"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    reporter_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    reported_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Where it happened. Nullable so a report can be about a person generally.
    channel_id: Mapped[str | None] = mapped_column(
        String(80), ForeignKey("channels.id", ondelete="SET NULL")
    )
    # Optional pointer to the specific message being reported.
    message_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("messages.id", ondelete="SET NULL")
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status", values_callable=lambda e: [m.value for m in e]),
        default=ReportStatus.OPEN,
        nullable=False,
        index=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    reporter: Mapped[User | None] = relationship(
        back_populates="reports_filed", foreign_keys=[reporter_id]
    )
    reported_user: Mapped[User] = relationship(
        back_populates="reports_against", foreign_keys=[reported_user_id]
    )
    channel: Mapped[Channel | None] = relationship()

    def __repr__(self) -> str:
        return f"<Report {self.id} status={self.status.value}>"
