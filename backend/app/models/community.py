"""Communities — the "listening rooms" that own channels."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.channel import Channel


class Community(Base, TimestampMixin):
    __tablename__ = "communities"

    # Slug primary key, matching the frontend's ids ("true-crime-circle").
    id: Mapped[str] = mapped_column(String(80), primary_key=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    artwork_url: Mapped[str | None] = mapped_column(String(500))

    channels: Mapped[list[Channel]] = relationship(
        back_populates="community", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Community {self.id}>"
