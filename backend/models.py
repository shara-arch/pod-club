"""SQLAlchemy table metadata used by Flask-Migrate/Alembic."""

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from extensions import db


def record_table(name):
    return Table(name, db.metadata, Column('id', String, primary_key=True), Column('data', JSONB, nullable=False))


users = record_table('users')
channels = record_table('channels')
messages = record_table('messages')
threads = record_table('threads')
reports = record_table('reports')
invites = record_table('invites')
podcasts = record_table('podcasts')
music = record_table('music')
playlists = record_table('playlists')

artists = Table('artists', db.metadata, Column('id', String, primary_key=True), Column('name', String, unique=True, nullable=False))
banned_users = Table('banned_users', db.metadata, Column('username', String, primary_key=True))
playlist_tracks = Table(
    'playlist_tracks', db.metadata,
    Column('playlist_id', String, ForeignKey('playlists.id', ondelete='CASCADE'), primary_key=True),
    Column('track_id', String, primary_key=True),
)
