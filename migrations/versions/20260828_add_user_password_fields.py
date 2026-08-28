"""Add password_hash and last_login_at to users

Revision ID: add_user_password_fields
Revises: initial_relational_schema
Create Date: 2026-08-28 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "add_user_password_fields"
down_revision = "initial_relational_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "password_hash")
