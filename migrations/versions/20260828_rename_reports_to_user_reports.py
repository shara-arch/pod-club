"""Rename reports table to user_reports to match the ORM model.

Revision ID: rename_reports_user_reports
Revises: add_user_password_fields
Create Date: 2026-08-28 16:26:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "rename_reports_user_reports"
down_revision = "add_user_password_fields"
branch_labels = None
depends_on = None

report_status = sa.Enum("OPEN", "RESOLVED", "DISMISSED", name="report_status")


def _table_names():
    inspector = sa.inspect(op.get_bind())
    return set(inspector.get_table_names())


def upgrade():
    tables = _table_names()

    if "user_reports" in tables:
        return

    if "reports" in tables:
        op.rename_table("reports", "user_reports")
        op.execute(
            sa.text(
                "UPDATE user_reports SET status = UPPER(status) "
                "WHERE status IN ('open', 'resolved', 'dismissed')"
            )
        )
        report_status.create(op.get_bind(), checkfirst=True)
        op.execute(sa.text("ALTER TABLE user_reports ALTER COLUMN status DROP DEFAULT"))
        op.execute(
            sa.text(
                "ALTER TABLE user_reports ALTER COLUMN status TYPE report_status "
                "USING status::report_status"
            )
        )
        op.execute(
            sa.text("ALTER TABLE user_reports ALTER COLUMN status SET DEFAULT 'OPEN'::report_status")
        )
        return

    report_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "user_reports",
        sa.Column("id", UUID, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("reporter_id", sa.String(80), nullable=False),
        sa.Column("reported_user_id", sa.String(80), nullable=False),
        sa.Column("message_id", sa.String(80), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", report_status, server_default="OPEN", nullable=False),
        sa.Column("resolved_by_id", sa.String(80), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reported_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("reporter_id <> reported_user_id", name="ck_reporter_not_reported"),
    )
    op.create_index("ix_reports_status", "user_reports", ["status"])
    op.create_index("ix_reports_reported_user", "user_reports", ["reported_user_id"])
    op.create_index("ix_reports_reporter", "user_reports", ["reporter_id"])


def downgrade():
    tables = _table_names()
    if "user_reports" not in tables:
        return

    op.rename_table("user_reports", "reports")
    op.execute(sa.text("ALTER TABLE reports ALTER COLUMN status DROP DEFAULT"))
    op.execute(
        sa.text("ALTER TABLE reports ALTER COLUMN status TYPE varchar(20) USING status::text")
    )
    op.execute(
        sa.text(
            "UPDATE reports SET status = LOWER(status) "
            "WHERE status IN ('OPEN', 'RESOLVED', 'DISMISSED')"
        )
    )
    op.execute(sa.text("ALTER TABLE reports ALTER COLUMN status SET DEFAULT 'open'"))
    report_status.drop(op.get_bind(), checkfirst=True)
