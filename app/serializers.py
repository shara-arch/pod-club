from .models import Channel, Message


def user_dict(user):
    return {"id": user.id, "name": user.display_name, "avatar": user.avatar_url}


def message_dict(message: Message, reply_count=None):
    payload = {
        "id": message.id,
        "channelId": message.channel_id,
        "author": user_dict(message.author),
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "type": message.message_type.value if hasattr(message.message_type, "value") else message.message_type,
        "replyCount": len(message.replies) if reply_count is None else reply_count,
        "edited": message.edited_at is not None,
    }
    if message.subtitle:
        payload["subtitle"] = message.subtitle
    if message.image_url:
        payload["imageUrl"] = message.image_url
    if message.image_caption:
        payload["imageCaption"] = message.image_caption
    if message.parent_id:
        payload["threadRootId"] = message.parent_id
    return payload


def channel_dict(channel: Channel):
    latest = next((m for m in sorted(channel.messages, key=lambda m: m.created_at, reverse=True) if not m.parent_id and not m.deleted_at), None)
    return {
        "id": channel.id,
        "name": channel.name,
        "description": channel.description,
        "isPrivate": channel.is_private,
        "category": channel.category,
        "ownerId": channel.owner_id,
        "memberCount": len(channel.memberships),
        "lastMessage": latest.content if latest else None,
        "lastMessageAuthor": latest.author.display_name if latest else None,
        "hasUnread": False,
        "createdAt": channel.created_at.isoformat(),
    }
