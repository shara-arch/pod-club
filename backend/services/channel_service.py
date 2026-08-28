"""Channel and invitation business rules."""

from config import FRONTEND_URL
from storage import get_next_id, iso_timestamp, slugify


def create_channel(data, payload):
    name = payload.get('name')
    if not name or not str(name).strip():
        return None, 'Channel name is required'
    owner_id = payload.get('ownerId') or payload.get('owner') or 'anonymous'
    if sum(channel.get('ownerId', 'anonymous') == owner_id for channel in data['channels']) >= 5:
        return None, 'A user can create a maximum of 5 channels'
    base_id = payload.get('id') or slugify(name)
    channel_id = base_id
    suffix = 1
    while any(channel.get('id') == channel_id for channel in data['channels']):
        channel_id = f'{base_id}-{suffix}'
        suffix += 1
    channel = {
        'id': channel_id, 'communityId': payload.get('communityId'), 'name': str(name).strip(),
        'description': payload.get('description', ''), 'isPrivate': bool(payload.get('isPrivate', False)),
        'category': payload.get('category', 'True Crime'), 'lastMessage': payload.get('lastMessage'),
        'lastMessageAuthor': payload.get('lastMessageAuthor'), 'hasUnread': bool(payload.get('hasUnread', False)),
        'ownerId': owner_id, 'members': list(dict.fromkeys([owner_id, *payload.get('members', [])])),
    }
    data['channels'].append(channel)
    return channel, None


def create_invite(data, payload):
    channel_id = payload.get('channelId') or payload.get('channel')
    if not channel_id:
        return None, 'channelId is required'
    if not any(channel.get('id') == channel_id for channel in data['channels']):
        return None, 'Channel not found'
    invite = {
        'id': payload.get('id') or get_next_id('invite'), 'channelId': channel_id,
        'code': payload.get('code') or get_next_id('join'), 'createdAt': payload.get('createdAt') or iso_timestamp(),
        'expiresAt': payload.get('expiresAt'),
    }
    invite['joinUrl'] = f'{FRONTEND_URL}/channels?invite={channel_id}&inviteCode={invite["code"]}'
    data['invites'].append(invite)
    return invite, None
