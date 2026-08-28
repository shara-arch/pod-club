from flask import Flask, jsonify, request
from flask_cors import CORS

from config import DATABASE_URL, FRONTEND_URL, HOST, PORT
from extensions import db, migrate
import models  # Registers tables with SQLAlchemy metadata for Flask-Migrate.
from services.channel_service import create_channel as build_channel, create_invite as build_invite
from services.itunes import fetch_itunes, normalize_itunes_podcast, normalize_itunes_track
from services.moderation_service import create_report as build_report, set_banned
from storage import get_next_id, iso_timestamp, load_db, save_db, slugify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate.init_app(app, db)
CORS(app, resources={r'/api/*': {'origins': '*'}})


@app.after_request
def log_request(response):
    print(f'{request.method} {request.path} {response.status_code}')
    return response


@app.get('/health')
@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.get('/api/users')
def list_users():
    data = load_db()
    users = data.get('users', [])
    public_users = []
    for user in users:
        safe_user = dict(user)
        safe_user.pop('password', None)
        public_users.append(safe_user)
    return jsonify(public_users)


@app.get('/api/admin')
def get_admin():
    data = load_db()
    admin = next((user for user in data.get('users', []) if user.get('username') == 'admin' or user.get('role') == 'admin'), None)
    if admin is None:
        return jsonify({'error': 'Admin not found'}), 404
    safe_admin = dict(admin)
    safe_admin.pop('password', None)
    return jsonify(safe_admin)


@app.get('/api/channels')
def list_channels():
    data = load_db()
    channels = data.get('channels', [])
    community_id = request.args.get('communityId')
    owner_id = request.args.get('ownerId')
    if community_id:
        channels = [channel for channel in channels if channel.get('communityId') == community_id]
    if owner_id:
        channels = [channel for channel in channels if channel.get('ownerId') == owner_id]
    return jsonify(channels)


@app.get('/api/admin/channels')
def admin_list_channels():
    """Administrative view of every channel, including its owner and members."""
    return list_channels()


@app.get('/api/channels/<channel_id>')
def get_channel(channel_id):
    data = load_db()
    channel = next((item for item in data.get('channels', []) if item.get('id') == channel_id), None)
    if channel is None:
        return jsonify({'error': 'Channel not found'}), 404
    return jsonify(channel)


@app.post('/api/channels')
def create_channel():
    payload = request.get_json(silent=True) or {}
    data = load_db()
    channel, error = build_channel(data, payload)
    if error:
        return jsonify({'error': error}), 400
    save_db(data)
    return jsonify(channel), 201


@app.post('/api/channels/<channel_id>/join')
def join_channel(channel_id):
    """Add a user to a public channel or to a private channel with a valid invite."""
    payload = request.get_json(silent=True) or {}
    user_id = payload.get('userId') or payload.get('username') or payload.get('user')
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400

    data = load_db()
    channel = next((item for item in data.get('channels', []) if item.get('id') == channel_id), None)
    if channel is None:
        return jsonify({'error': 'Channel not found'}), 404

    invite_id = payload.get('inviteId') or payload.get('inviteCode')
    invite = next((
        item for item in data.get('invites', [])
        if item.get('channelId') == channel_id
        and (item.get('id') == invite_id or item.get('code') == invite_id)
    ), None)
    if channel.get('isPrivate') and not invite:
        return jsonify({'error': 'A valid invite is required to join this private channel'}), 403

    members = channel.setdefault('members', [])
    if user_id not in members:
        members.append(user_id)
        save_db(data)
    return jsonify(channel)


@app.patch('/api/channels/<channel_id>')
def update_channel(channel_id):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON body must be an object'}), 400

    data = load_db()
    channel = next((item for item in data.get('channels', []) if item.get('id') == channel_id), None)
    if channel is None:
        return jsonify({'error': 'Channel not found'}), 404

    for key, value in payload.items():
        if key == 'id':
            continue
        channel[key] = value

    save_db(data)
    return jsonify(channel)


@app.delete('/api/channels/<channel_id>')
def delete_channel(channel_id):
    data = load_db()
    before = len(data.get('channels', []))
    data['channels'] = [item for item in data.get('channels', []) if item.get('id') != channel_id]
    data['messages'] = [item for item in data.get('messages', []) if item.get('channelId') != channel_id]
    data['threads'] = [item for item in data.get('threads', []) if item.get('channelId') != channel_id]
    data['reports'] = [item for item in data.get('reports', []) if item.get('channelId') != channel_id]

    if len(data['channels']) == before:
        return jsonify({'error': 'Channel not found'}), 404

    save_db(data)
    return '', 204


@app.get('/api/messages')
def list_messages():
    data = load_db()
    channel_id = request.args.get('channelId')
    if not channel_id:
        return jsonify([])

    messages = [item for item in data.get('messages', []) if item.get('channelId') == channel_id]
    sort_field = request.args.get('_sort') or 'timestamp'
    order = (request.args.get('_order') or 'asc').lower()
    messages.sort(key=lambda item: str(item.get(sort_field) or ''), reverse=(order == 'desc'))
    return jsonify(messages)


@app.post('/api/messages')
def create_message():
    payload = request.get_json(silent=True) or {}
    if not payload.get('channelId'):
        return jsonify({'error': 'channelId is required'}), 400

    data = load_db()
    message_id = payload.get('id') or get_next_id('m')
    message = {
        'id': message_id,
        'channelId': payload['channelId'],
        'author': payload.get('author') or {'id': 'me', 'name': 'You', 'avatar': None},
        'content': payload.get('content'),
        'timestamp': payload.get('timestamp') or iso_timestamp(),
        'type': payload.get('type', 'text'),
        'replyCount': payload.get('replyCount', 0),
    }
    for optional_field in ('subtitle', 'imageUrl', 'imageCaption', 'threadRootId', 'edited'):
        if optional_field in payload:
            message[optional_field] = payload[optional_field]
    data['messages'].append(message)
    save_db(data)
    return jsonify(message), 201


@app.patch('/api/messages/<message_id>')
def update_message(message_id):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON body must be an object'}), 400

    data = load_db()
    message = next((item for item in data.get('messages', []) if item.get('id') == message_id), None)
    if message is None:
        return jsonify({'error': 'Message not found'}), 404

    for key, value in payload.items():
        if key == 'id':
            continue
        message[key] = value

    save_db(data)
    return jsonify(message)


@app.delete('/api/messages/<message_id>')
def delete_message(message_id):
    data = load_db()
    before = len(data.get('messages', []))
    data['messages'] = [item for item in data.get('messages', []) if item.get('id') != message_id]
    if len(data['messages']) == before:
        return jsonify({'error': 'Message not found'}), 404
    save_db(data)
    return '', 204


@app.get('/api/threads/<thread_id>')
def get_thread(thread_id):
    data = load_db()
    thread = next((item for item in data.get('threads', []) if item.get('id') == thread_id), None)
    if thread is None:
        # The first reply to a message creates its thread automatically.
        root_message = next((item for item in data.get('messages', []) if item.get('id') == thread_id), None)
        if root_message is None:
            return jsonify({'error': 'Thread not found'}), 404
        thread = {
            'id': thread_id,
            'channelId': root_message.get('channelId'),
            'rootMessage': root_message,
            'replies': [],
        }
        data['threads'].append(thread)
        save_db(data)
    return jsonify(thread)


@app.patch('/api/threads/<thread_id>')
def update_thread(thread_id):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON body must be an object'}), 400

    data = load_db()
    thread = next((item for item in data.get('threads', []) if item.get('id') == thread_id), None)
    if thread is None:
        return jsonify({'error': 'Thread not found'}), 404

    for key, value in payload.items():
        if key == 'id':
            continue
        thread[key] = value

    if 'replies' in payload:
        root_message = next((item for item in data.get('messages', []) if item.get('id') == thread_id), None)
        if root_message is not None:
            root_message['threadRootId'] = thread_id
            root_message['replyCount'] = len(thread.get('replies', []))

    save_db(data)
    return jsonify(thread)


@app.get('/api/podcasts')
def list_podcasts():
    term = request.args.get('query') or request.args.get('term') or 'culture'
    limit = int(request.args.get('limit', '10'))
    results = fetch_itunes(term, entity='podcast', media='podcast', limit=limit)
    if results:
        return jsonify([normalize_itunes_podcast(item) for item in results])
    data = load_db()
    return jsonify(data.get('podcasts', []))


@app.get('/api/podcasts/<podcast_id>')
def get_podcast(podcast_id):
    data = load_db()
    item = next((podcast for podcast in data.get('podcasts', []) if podcast.get('id') == podcast_id), None)
    if item is None:
        return jsonify({'error': 'Podcast not found'}), 404
    return jsonify(item)


@app.get('/api/music')
def list_music():
    term = request.args.get('query') or request.args.get('term') or 'music'
    limit = int(request.args.get('limit', '10'))
    results = fetch_itunes(term, entity='musicTrack', limit=limit)
    if results:
        return jsonify([normalize_itunes_track(item) for item in results])
    data = load_db()
    return jsonify(data.get('music', []))


@app.get('/api/music/<track_id>')
def get_music(track_id):
    data = load_db()
    item = next((track for track in data.get('music', []) if track.get('id') == track_id), None)
    if item is None:
        return jsonify({'error': 'Track not found'}), 404
    return jsonify(item)


@app.get('/api/playlists')
def list_playlists():
    data = load_db()
    return jsonify(data.get('playlists', []))


@app.get('/api/playlists/<playlist_id>')
def get_playlist(playlist_id):
    data = load_db()
    item = next((playlist for playlist in data.get('playlists', []) if playlist.get('id') == playlist_id), None)
    if item is None:
        return jsonify({'error': 'Playlist not found'}), 404
    return jsonify(item)


@app.post('/api/playlists')
def create_playlist():
    payload = request.get_json(silent=True) or {}
    name = payload.get('name') or payload.get('title')
    if not name:
        return jsonify({'error': 'Playlist name is required'}), 400

    data = load_db()
    playlist = {
        'id': payload.get('id') or get_next_id('playlist'),
        'name': str(name),
        'description': payload.get('description', ''),
        'tracks': payload.get('tracks', []),
        'createdAt': payload.get('createdAt') or iso_timestamp(),
    }
    data['playlists'].append(playlist)
    save_db(data)
    return jsonify(playlist), 201


@app.get('/api/reports')
def list_reports():
    data = load_db()
    return jsonify(data.get('reports', []))


@app.post('/api/reports')
def create_report():
    payload = request.get_json(silent=True) or {}
    data = load_db()
    report, error = build_report(data, payload)
    if error:
        return jsonify({'error': error}), 400
    save_db(data)
    return jsonify(report), 201


@app.patch('/api/reports/<report_id>')
def update_report(report_id):
    payload = request.get_json(silent=True) or {}
    data = load_db()
    report = next((item for item in data.get('reports', []) if item.get('id') == report_id), None)
    if report is None:
        return jsonify({'error': 'Report not found'}), 404

    for key, value in payload.items():
        if key == 'id':
            continue
        report[key] = value

    if payload.get('banned') is True:
        set_banned(data, report.get('user'))
    elif payload.get('banned') is False:
        set_banned(data, report.get('user'), banned=False)

    save_db(data)
    return jsonify(report)


@app.delete('/api/reports/<report_id>')
def delete_report(report_id):
    data = load_db()
    reports = data.get('reports', [])
    data['reports'] = [item for item in reports if item.get('id') != report_id]
    if len(data['reports']) == len(reports):
        return jsonify({'error': 'Report not found'}), 404
    save_db(data)
    return '', 204


@app.get('/api/banned-users')
def list_banned_users():
    data = load_db()
    return jsonify(data.get('bannedUsers', []))


@app.post('/api/banned-users')
def create_banned_user():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username') or payload.get('user')
    if not username:
        return jsonify({'error': 'username is required'}), 400

    data = load_db()
    set_banned(data, username)
    save_db(data)
    return jsonify({'username': username, 'banned': True})


@app.delete('/api/banned-users/<username>')
def delete_banned_user(username):
    data = load_db()
    before = data.get('bannedUsers', [])
    set_banned(data, username, banned=False)
    if len(data['bannedUsers']) == len(before):
        return jsonify({'error': 'User not found in banned list'}), 404
    save_db(data)
    return '', 204


@app.post('/api/invites')
def create_invite():
    payload = request.get_json(silent=True) or {}
    data = load_db()
    invite, error = build_invite(data, payload)
    if error:
        status = 404 if error == 'Channel not found' else 400
        return jsonify({'error': error}), status
    save_db(data)
    return jsonify(invite), 201


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
