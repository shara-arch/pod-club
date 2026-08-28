"""Channel invitations.

The frontend builds links of the form ``/channels?invite=<channelId>``, which
is not safe on its own — anyone who guesses a channel slug is in. So an invite
carries an unguessable token, and the API will accept the token rather than the
raw channel id.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.channel import Channel
    from app.models.user import User


def new_id() -> str:
    return str(uuid.uuid4())


def new_token() -> str:
    return secrets.token_urlsafe(24)


class Invite(Base, TimestampMixin):
    __tablename__ = "invites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    channel_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, default=new_token, nullable=False)

    created_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    # Optional: an invite may be addressed to someone specific, or be a plain
    # shareable link with no named recipient.
    invited_username: Mapped[str | None] = mapped_column(String(50))
    invited_email: Mapped[str | None] = mapped_column(String(255))

    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # A link can be reused up to max_uses times; NULL means unlimited.
    max_uses: Mapped[int | None] = mapped_column(Integer)
    use_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    channel: Mapped[Channel] = relationship(back_populates="invites")
    created_by: Mapped[User | None] = relationship()

    def __repr__(self) -> str:
        return f"<Invite {self.id} for {self.channel_id}>"
