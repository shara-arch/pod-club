# migrations/versions/20260828_initial_relational_schema.py
"""Initial relational schema for PodClub

Revision ID: initial_relational_schema
Revises: 
Create Date: 2026-08-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = 'initial_relational_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ============================================
    # CREATE TABLES
    # ============================================
    
    # 1. Users table
    op.create_table('users',
        sa.Column('id', sa.String(80), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('role', sa.String(20), server_default='user', nullable=False),
        sa.Column('is_banned', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('banned_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('settings', JSONB, nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_display_name', 'users', ['display_name'])
    
    # 2. Channels table
    op.create_table('channels',
        sa.Column('id', sa.String(80), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('is_private', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('channel_type', sa.String(20), server_default='group', nullable=False),
        sa.Column('owner_id', sa.String(80), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('settings', JSONB, nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_channels_name', 'channels', ['name'])
    op.create_index('ix_channels_category', 'channels', ['category'])
    
    # 3. Channel Memberships
    op.create_table('channel_memberships',
        sa.Column('channel_id', sa.String(80), nullable=False),
        sa.Column('user_id', sa.String(80), nullable=False),
        sa.Column('role', sa.String(20), server_default='member', nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('channel_id', 'user_id')
    )
    op.create_index('ix_channel_memberships_user_id', 'channel_memberships', ['user_id'])
    op.create_index('ix_channel_memberships_channel_id', 'channel_memberships', ['channel_id'])
    
    # 4. Messages table
    op.create_table('messages',
        sa.Column('id', sa.String(80), nullable=False),
        sa.Column('channel_id', sa.String(80), nullable=False),
        sa.Column('author_id', sa.String(80), nullable=False),
        sa.Column('parent_id', sa.String(80), nullable=True),
        sa.Column('message_type', sa.String(20), server_default='text', nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('subtitle', sa.String(255), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('image_caption', sa.String(255), nullable=True),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['parent_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_channel_created', 'messages', ['channel_id', 'created_at'])
    op.create_index('ix_messages_author_id', 'messages', ['author_id'])
    op.create_index('ix_messages_parent_id', 'messages', ['parent_id'])
    
    # 5. Invitations table
    op.create_table('invitations',
        sa.Column('id', UUID, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('channel_id', sa.String(80), nullable=False),
        sa.Column('created_by_id', sa.String(80), nullable=False),
        sa.Column('token', sa.String(128), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('uses', sa.Integer(), server_default='0', nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invitations_token', 'invitations', ['token'], unique=True)
    op.create_index('ix_invitations_channel_id', 'invitations', ['channel_id'])
    
    # 6. Reports table
    op.create_table('reports',
        sa.Column('id', UUID, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('reporter_id', sa.String(80), nullable=False),
        sa.Column('reported_user_id', sa.String(80), nullable=False),
        sa.Column('message_id', sa.String(80), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), server_default='open', nullable=False),
        sa.Column('resolved_by_id', sa.String(80), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['reported_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_check_constraint('ck_reporter_not_reported', 'reports', 'reporter_id != reported_user_id')
    op.create_index('ix_reports_status', 'reports', ['status'])
    op.create_index('ix_reports_reported_user', 'reports', ['reported_user_id'])
    op.create_index('ix_reports_reporter', 'reports', ['reporter_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('ix_reports_reporter', table_name='reports')
    op.drop_index('ix_reports_reported_user', table_name='reports')
    op.drop_index('ix_reports_status', table_name='reports')
    op.drop_table('reports')
    
    op.drop_index('ix_invitations_channel_id', table_name='invitations')
    op.drop_index('ix_invitations_token', table_name='invitations')
    op.drop_table('invitations')
    
    op.drop_index('ix_messages_parent_id', table_name='messages')
    op.drop_index('ix_messages_author_id', table_name='messages')
    op.drop_index('ix_messages_channel_created', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('ix_channel_memberships_channel_id', table_name='channel_memberships')
    op.drop_index('ix_channel_memberships_user_id', table_name='channel_memberships')
    op.drop_table('channel_memberships')
    
    op.drop_index('ix_channels_category', table_name='channels')
    op.drop_index('ix_channels_name', table_name='channels')
    op.drop_table('channels')
    
    op.drop_index('ix_users_display_name', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')