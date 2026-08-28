import re
import time
from datetime import datetime, timezone

from psycopg import connect
from psycopg.types.json import Jsonb

from config import DATABASE_URL


COLLECTIONS = {
    'users': 'users', 'channels': 'channels', 'messages': 'messages',
    'threads': 'threads', 'reports': 'reports', 'invites': 'invites',
    'podcasts': 'podcasts', 'music': 'music', 'playlists': 'playlists',
}


def ensure_db_shape(data):
    if not isinstance(data, dict):
        data = {}
    for key in (*COLLECTIONS, 'bannedUsers'):
        data.setdefault(key, [])
    return data


def seed_demo_admin(data):
    data = ensure_db_shape(data)
    if not any(user.get('username') == 'admin' for user in data['users']):
        data['users'].insert(0, {
            'id': 'admin-1', 'username': 'admin', 'email': 'admin@podclub.local',
            'role': 'admin', 'password': 'podclub', 'createdAt': iso_timestamp(),
        })
    return data


def seed_demo_media(data):
    data = ensure_db_shape(data)
    if not data['podcasts']:
        data['podcasts'].extend([
            {'id': 'pod-1', 'title': 'The Midnight Alibi', 'host': 'Lena Hart', 'description': 'A weekly investigation into cold cases, witness contradictions, and the stories behind the evidence.', 'genre': 'True Crime', 'coverImage': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=800&q=80', 'audioUrl': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'duration': '42:18', 'createdAt': iso_timestamp()},
            {'id': 'pod-2', 'title': 'After the Credits', 'host': 'Nora Bloom', 'description': 'Film and music analysis for listeners who want to hear the story behind the soundtrack.', 'genre': 'Culture', 'coverImage': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=800&q=80', 'audioUrl': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', 'duration': '36:44', 'createdAt': iso_timestamp()},
        ])
    if not data['music']:
        data['music'].extend([
            {'id': 'track-1', 'title': 'Night Signal', 'artist': 'Velvet Circuit', 'album': 'Static Bloom', 'genre': 'Electronic', 'coverImage': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=800&q=80', 'audioUrl': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', 'duration': '3:42', 'createdAt': iso_timestamp()},
            {'id': 'track-2', 'title': 'Slow Burn', 'artist': 'Coastal Echo', 'album': 'Afterglow', 'genre': 'Indie', 'coverImage': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&q=80', 'audioUrl': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', 'duration': '4:08', 'createdAt': iso_timestamp()},
        ])
    if not data['playlists']:
        data['playlists'].append({'id': 'playlist-1', 'name': 'Focus Session', 'description': 'A mellow mix for working, writing, and keeping the room calm.', 'tracks': ['track-1', 'track-2'], 'createdAt': iso_timestamp()})
    return data


def seed_demo_community(data):
    """Create the original True Crime Circle rooms for a new database."""
    data = ensure_db_shape(data)
    if not data['channels']:
        data['channels'].extend([
            {
                'id': 'general', 'communityId': 'true-crime-circle', 'name': 'general',
                'description': 'Main discussion for the community', 'isPrivate': False,
                'category': 'True Crime', 'lastMessage': 'Check the timeline of the murder weapon...',
                'lastMessageAuthor': 'Lexi', 'hasUnread': True, 'ownerId': 'admin-1',
                'members': ['admin-1', 'u1', 'u2', 'u3'],
            },
            {
                'id': 'weekly-recommendations', 'communityId': 'true-crime-circle',
                'name': 'weekly-recommendations', 'description': 'Share podcast episodes worth a listen',
                'isPrivate': False, 'category': 'True Crime',
                'lastMessage': 'Podcast Share: Dark Audio Archives Ep 42',
                'lastMessageAuthor': None, 'hasUnread': False, 'ownerId': 'admin-1',
                'members': ['admin-1', 'u1', 'u2'],
            },
            {
                'id': 'case-file-theories', 'communityId': 'true-crime-circle',
                'name': 'case-file-theories', 'description': 'Break down evidence and swap theories',
                'isPrivate': False, 'category': 'True Crime',
                'lastMessage': "He couldn't have been in Boston.", 'lastMessageAuthor': 'Liam',
                'hasUnread': True, 'ownerId': 'admin-1', 'members': ['admin-1', 'u1', 'u3'],
            },
        ])
    return data


def _prepared(data):
    return seed_demo_community(seed_demo_media(seed_demo_admin(ensure_db_shape(data))))


def _create_schema(cursor):
    # Each resource has its own PostgreSQL table, making data easy to inspect in VS Code.
    for table in COLLECTIONS.values():
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {table} (id TEXT PRIMARY KEY, data JSONB NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS banned_users (username TEXT PRIMARY KEY)')
    cursor.execute('CREATE TABLE IF NOT EXISTS artists (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            playlist_id TEXT NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
            track_id TEXT NOT NULL,
            PRIMARY KEY (playlist_id, track_id)
        )
    ''')


def _read_state(cursor):
    data = {key: [] for key in (*COLLECTIONS, 'bannedUsers')}
    for key, table in COLLECTIONS.items():
        cursor.execute(f'SELECT data FROM {table} ORDER BY id')
        data[key] = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT username FROM banned_users ORDER BY username')
    data['bannedUsers'] = [row[0] for row in cursor.fetchall()]
    return data


def _write_state(cursor, data):
    # Clear relationship rows before their referenced playlists.
    cursor.execute('DELETE FROM playlist_tracks')
    for key, table in COLLECTIONS.items():
        cursor.execute(f'DELETE FROM {table}')
        for item in data[key]:
            cursor.execute(f'INSERT INTO {table} (id, data) VALUES (%s, %s)', (str(item['id']), Jsonb(item)))

    cursor.execute('DELETE FROM banned_users')
    for username in data['bannedUsers']:
        cursor.execute('INSERT INTO banned_users (username) VALUES (%s)', (username,))

    cursor.execute('DELETE FROM artists')
    artist_names = {track.get('artist') for track in data['music'] if track.get('artist')}
    for name in artist_names:
        cursor.execute('INSERT INTO artists (id, name) VALUES (%s, %s)', (slugify(name), name))

    for playlist in data['playlists']:
        for track_id in playlist.get('tracks', []):
            cursor.execute('INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (%s, %s)', (str(playlist['id']), str(track_id)))


def load_db():
    """Load state from PostgreSQL and create tables/demo records on first run."""
    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            _create_schema(cursor)
            data = _read_state(cursor)
            prepared = _prepared(data)
            if prepared != data:
                _write_state(cursor, prepared)
            return prepared


def save_db(data):
    """Persist state to PostgreSQL; no local JSON file is read or written."""
    payload = _prepared(data)
    with connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            _create_schema(cursor)
            _write_state(cursor, payload)
    return payload


def iso_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def get_next_id(prefix):
    return f'{prefix}-{int(time.time() * 1000)}'


def slugify(value):
    slug = re.sub(r'[^a-z0-9]+', '-', str(value).strip().lower()).strip('-')
    return slug or f'item-{int(time.time() * 1000)}'
