"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-08-28 07:03:05.386899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('communities',
    sa.Column('id', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('artwork_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_communities'))
    )
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_banned', sa.Boolean(), nullable=False),
    sa.Column('banned_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('banned_by_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['banned_by_id'], ['users.id'], name=op.f('fk_users_banned_by_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_is_banned'), 'users', ['is_banned'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('channels',
    sa.Column('id', sa.String(length=80), nullable=False),
    sa.Column('community_id', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('is_private', sa.Boolean(), nullable=False),
    sa.Column('created_by_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name=op.f('fk_channels_community_id_communities'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name=op.f('fk_channels_created_by_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_channels')),
    sa.UniqueConstraint('community_id', 'name', name='community_id_name')
    )
    op.create_index(op.f('ix_channels_community_id'), 'channels', ['community_id'], unique=False)
    op.create_table('channel_members',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('channel_id', sa.String(length=80), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.Enum('owner', 'member', name='channel_role'), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], name=op.f('fk_channel_members_channel_id_channels'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_channel_members_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_channel_members')),
    sa.UniqueConstraint('channel_id', 'user_id', name='channel_id_user_id')
    )
    op.create_index(op.f('ix_channel_members_channel_id'), 'channel_members', ['channel_id'], unique=False)
    op.create_index(op.f('ix_channel_members_user_id'), 'channel_members', ['user_id'], unique=False)
    op.create_table('invites',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('channel_id', sa.String(length=80), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('created_by_id', sa.String(length=36), nullable=True),
    sa.Column('invited_username', sa.String(length=50), nullable=True),
    sa.Column('invited_email', sa.String(length=255), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('use_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], name=op.f('fk_invites_channel_id_channels'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name=op.f('fk_invites_created_by_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_invites')),
    sa.UniqueConstraint('token', name=op.f('uq_invites_token'))
    )
    op.create_index(op.f('ix_invites_channel_id'), 'invites', ['channel_id'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('channel_id', sa.String(length=80), nullable=False),
    sa.Column('author_id', sa.String(length=36), nullable=True),
    sa.Column('kind', sa.Enum('text', 'image', 'episode-share', name='message_type'), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('subtitle', sa.String(length=255), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('image_caption', sa.String(length=255), nullable=True),
    sa.Column('reply_to_id', sa.String(length=36), nullable=True),
    sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_messages_author_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], name=op.f('fk_messages_channel_id_channels'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reply_to_id'], ['messages.id'], name=op.f('fk_messages_reply_to_id_messages'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_index('ix_messages_channel_id_created_at', 'messages', ['channel_id', 'created_at'], unique=False)
    op.create_table('reports',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('reporter_id', sa.String(length=36), nullable=True),
    sa.Column('reported_user_id', sa.String(length=36), nullable=False),
    sa.Column('channel_id', sa.String(length=80), nullable=True),
    sa.Column('message_id', sa.String(length=36), nullable=True),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('open', 'reviewed', 'dismissed', name='report_status'), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reviewed_by_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], name=op.f('fk_reports_channel_id_channels'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], name=op.f('fk_reports_message_id_messages'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reported_user_id'], ['users.id'], name=op.f('fk_reports_reported_user_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], name=op.f('fk_reports_reporter_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], name=op.f('fk_reports_reviewed_by_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_reports'))
    )
    op.create_index(op.f('ix_reports_reported_user_id'), 'reports', ['reported_user_id'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)
    op.create_table('threads',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('channel_id', sa.String(length=80), nullable=False),
    sa.Column('root_message_id', sa.String(length=36), nullable=False),
    sa.Column('reply_count', sa.Integer(), nullable=False),
    sa.Column('last_reply_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], name=op.f('fk_threads_channel_id_channels'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['root_message_id'], ['messages.id'], name=op.f('fk_threads_root_message_id_messages'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_threads')),
    sa.UniqueConstraint('root_message_id', name=op.f('uq_threads_root_message_id'))
    )
    op.create_index(op.f('ix_threads_channel_id'), 'threads', ['channel_id'], unique=False)
    op.create_table('thread_messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('thread_id', sa.String(length=36), nullable=False),
    sa.Column('author_id', sa.String(length=36), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_thread_messages_author_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['thread_id'], ['threads.id'], name=op.f('fk_thread_messages_thread_id_threads'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_thread_messages'))
    )
    op.create_index(op.f('ix_thread_messages_thread_id'), 'thread_messages', ['thread_id'], unique=False)



def downgrade() -> None:
    op.drop_index(op.f('ix_thread_messages_thread_id'), table_name='thread_messages')
    op.drop_table('thread_messages')
    op.drop_index(op.f('ix_threads_channel_id'), table_name='threads')
    op.drop_table('threads')
    op.drop_index(op.f('ix_reports_status'), table_name='reports')
    op.drop_index(op.f('ix_reports_reported_user_id'), table_name='reports')
    op.drop_table('reports')
    op.drop_index('ix_messages_channel_id_created_at', table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_invites_channel_id'), table_name='invites')
    op.drop_table('invites')
    op.drop_index(op.f('ix_channel_members_user_id'), table_name='channel_members')
    op.drop_index(op.f('ix_channel_members_channel_id'), table_name='channel_members')
    op.drop_table('channel_members')
    op.drop_index(op.f('ix_channels_community_id'), table_name='channels')
    op.drop_table('channels')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_is_banned'), table_name='users')
    op.drop_table('users')
    op.drop_table('communities')

    # Postgres keeps ENUM types after their tables are dropped, and Alembic
    # does not generate these. Without them a downgrade followed by an upgrade
    # fails with "type already exists".
    sa.Enum(name='report_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='message_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='channel_role').drop(op.get_bind(), checkfirst=True)
