"""Channel messages and threaded replies.

Threads are modelled as their own table rather than a self-join on ``messages``
because the frontend already treats a thread as a distinct object with a root
message and a reply list (``mockThreads``), and the channel view only needs a
``reply_count`` plus a thread id to render.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.channel import Channel
    from app.models.user import User


def new_id() -> str:
    return str(uuid.uuid4())


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    EPISODE_SHARE = "episode-share"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    __table_args__ = (
        # The polling endpoint reads "messages in this channel newer than X",
        # which is exactly this composite index.
        Index("ix_messages_channel_id_created_at", "channel_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    channel_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    kind: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type", values_callable=lambda e: [m.value for m in e]),
        default=MessageType.TEXT,
        nullable=False,
    )

    # Nullable because an image-only message carries no body text.
    content: Mapped[str | None] = mapped_column(Text)
    # Secondary line on an episode-share card (the show name).
    subtitle: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(String(500))
    image_caption: Mapped[str | None] = mapped_column(String(255))

    # Direct reply within the channel, as opposed to a full thread.
    reply_to_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("messages.id", ondelete="SET NULL")
    )

    # Edits and deletes are soft, so the client can show "edited" and so a
    # deleted message doesn't orphan its replies.
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    channel: Mapped[Channel] = relationship(back_populates="messages")
    author: Mapped[User | None] = relationship(back_populates="messages")
    reply_to: Mapped[Message | None] = relationship(remote_side=[id])
    thread: Mapped[Thread | None] = relationship(
        back_populates="root_message", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Message {self.id} in {self.channel_id}>"


class Thread(Base, TimestampMixin):
    __tablename__ = "threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    channel_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    root_message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Denormalised so the channel list can show "3 replies" without counting.
    reply_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    channel: Mapped[Channel] = relationship(back_populates="threads")
    root_message: Mapped[Message] = relationship(back_populates="thread")
    replies: Mapped[list[ThreadMessage]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="ThreadMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<Thread {self.id}>"


class ThreadMessage(Base, TimestampMixin):
    __tablename__ = "thread_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    thread_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    thread: Mapped[Thread] = relationship(back_populates="replies")
    author: Mapped[User | None] = relationship(back_populates="thread_messages")

    def __repr__(self) -> str:
        return f"<ThreadMessage {self.id}>"
