"""Report and ban-list business rules."""

from storage import get_next_id, iso_timestamp


def create_report(data, payload):
    user = payload.get('user') or payload.get('username')
    if not user:
        return None, 'user is required'
    report = {
        'id': payload.get('id') or get_next_id('report'), 'user': user,
        'channel': payload.get('channel'), 'channelId': payload.get('channelId'),
        'reason': payload.get('reason', 'Abusive or offensive content'),
        'reporter': payload.get('reporter', 'Anonymous'), 'status': payload.get('status', 'Open'),
        'banned': bool(payload.get('banned', False)), 'createdAt': payload.get('createdAt') or iso_timestamp(),
    }
    data['reports'].append(report)
    return report, None


def set_banned(data, username, banned=True):
    users = data['bannedUsers']
    if banned and username not in users:
        users.append(username)
    if not banned:
        data['bannedUsers'] = [user for user in users if user != username]
