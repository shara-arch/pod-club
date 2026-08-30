"""Engine, session factory and declarative base.

Every model inherits from ``Base``; every request-scoped unit of work goes
through ``get_db``. Routers should depend on ``get_db`` rather than importing
``SessionLocal`` directly, so tests can override the dependency.
"""

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    # Recycle before Postgres' idle timeout and check liveness on checkout, so
    # a connection dropped by the host doesn't surface as a request error.
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Explicit constraint naming, so Alembic autogenerate produces stable,
# readable names instead of database-assigned ones that differ per environment.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """``created_at`` / ``updated_at`` in UTC, maintained by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def utcnow() -> datetime:
    """Timezone-aware UTC now, for values set in Python rather than by the DB."""
    return datetime.now(timezone.utc)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a session that always gets closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
