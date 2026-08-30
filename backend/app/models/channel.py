"""Channels and channel membership."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.community import Community
    from app.models.invite import Invite
    from app.models.message import Message, Thread
    from app.models.user import User


class ChannelRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"
    __table_args__ = (
        # Channel names are referenced as "#general" within a community, so they
        # have to be unique there — but "general" may exist in many communities.
        UniqueConstraint("community_id", "name", name="community_id_name"),
    )

    # Slug primary key, matching the frontend's ids ("case-file-theories") and
    # the ?invite=<channelId> links it generates.
    id: Mapped[str] = mapped_column(String(80), primary_key=True)

    community_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80))
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    community: Mapped[Community] = relationship(back_populates="channels")
    members: Mapped[list[ChannelMember]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    messages: Mapped[list[Message]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    threads: Mapped[list[Thread]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    invites: Mapped[list[Invite]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Channel {self.id}>"


class ChannelMember(Base):
    """Who may read a private channel, and who owns it.

    Rooms are invite-only in the product, so membership is the access-control
    table the API will check once auth exists.
    """

    __tablename__ = "channel_members"
    __table_args__ = (UniqueConstraint("channel_id", "user_id", name="channel_id_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ChannelRole] = mapped_column(
        Enum(ChannelRole, name="channel_role", values_callable=lambda e: [m.value for m in e]),
        default=ChannelRole.MEMBER,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    channel: Mapped[Channel] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")

    def __repr__(self) -> str:
        return f"<ChannelMember {self.user_id}@{self.channel_id}>"
