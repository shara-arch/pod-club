from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

import bcrypt
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


def now_utc():
    return datetime.now(timezone.utc)


class StringEnum(str, enum.Enum):
    pass


class Role(StringEnum):
    USER = "user"
    ADMIN = "admin"


class MembershipRole(StringEnum):
    OWNER = "owner"
    MEMBER = "member"


class ChannelType(StringEnum):
    GROUP = "group"


class MessageType(StringEnum):
    TEXT = "text"
    IMAGE = "image"
    EPISODE_SHARE = "episode-share"


class ReportStatus(StringEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role"), default=Role.USER, nullable=False)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
    banned_at: Mapped[Optional[datetime]] = mapped_column()
    last_login_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "role": self.role.value if isinstance(self.role, Role) else self.role,
            "is_banned": self.is_banned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Channel(db.Model):
    __tablename__ = "channels"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    is_private: Mapped[bool] = mapped_column(default=True, nullable=False)
    channel_type: Mapped[ChannelType] = mapped_column(Enum(ChannelType, name="channel_type"), default=ChannelType.GROUP, nullable=False)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=now_utc, onupdate=now_utc, nullable=False)

    owner: Mapped[User] = relationship()
    memberships: Mapped[list["ChannelMembership"]] = relationship(back_populates="channel", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="channel", cascade="all, delete-orphan")

    def is_member(self, user_id: str) -> bool:
        return any(membership.user_id == user_id for membership in self.memberships)


class ChannelMembership(db.Model):
    __tablename__ = "channel_memberships"
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole, name="membership_role"), default=MembershipRole.MEMBER, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)

    channel: Mapped[Channel] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship()


class Invitation(db.Model):
    __tablename__ = "invitations"
    __table_args__ = (Index("ix_invitations_token", "token", unique=True),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(128), nullable=False, default=lambda: uuid.uuid4().hex)
    expires_at: Mapped[Optional[datetime]] = mapped_column()
    max_uses: Mapped[Optional[int]] = mapped_column()
    uses: Mapped[int] = mapped_column(default=0, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)


class Message(db.Model):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_channel_created", "channel_id", "created_at"),)
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType, name="message_type"), default=MessageType.TEXT, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    subtitle: Mapped[Optional[str]] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    image_caption: Mapped[Optional[str]] = mapped_column(String(255))
    edited_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=now_utc, onupdate=now_utc, nullable=False)

    channel: Mapped[Channel] = relationship(back_populates="messages")
    author: Mapped[User] = relationship()
    parent: Mapped[Optional["Message"]] = relationship(remote_side="Message.id", backref="replies")

    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class UserReport(db.Model):
    __tablename__ = "user_reports"
    __table_args__ = (CheckConstraint("reporter_id <> reported_user_id", name="ck_reporter_not_reported"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reported_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus, name="report_status"), default=ReportStatus.OPEN, nullable=False)
    resolved_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=now_utc, nullable=False)

    reporter: Mapped[User] = relationship(foreign_keys=[reporter_id])
    reported_user: Mapped[User] = relationship(foreign_keys=[reported_user_id])
    resolved_by: Mapped[Optional[User]] = relationship(foreign_keys=[resolved_by_id])
