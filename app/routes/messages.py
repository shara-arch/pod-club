from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func
from flasgger import swag_from
from ..extensions import db, limiter
from ..models import Message, Channel, now_utc
from ..schemas import MessageCreateSchema, MessageUpdateSchema, PaginationSchema
from ..serializers import message_dict
from ..decorators import get_current_user
from ..exceptions import ValidationError, NotFoundError, ForbiddenError, APIError

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")


def ensure_membership(channel, user):
    """Auto-join the user to a public channel so they can read/send messages."""
    if channel.is_member(user.id):
        return
    if channel.is_private:
        raise ForbiddenError("You must be a channel member")
    from ..models import ChannelMembership, MembershipRole
    db.session.add(ChannelMembership(
        channel_id=channel.id,
        user_id=user.id,
        role=MembershipRole.MEMBER,
    ))
    db.session.commit()


@messages_bp.get("")
@jwt_required()
@swag_from({
    "tags": ["Messages"],
    "summary": "List messages in a channel",
    "description": "Get paginated messages for a channel",
    "parameters": [
        {"name": "channelId", "in": "query", "type": "string", "required": True},
        {"name": "page", "in": "query", "type": "integer", "default": 1},
        {"name": "per_page", "in": "query", "type": "integer", "default": 50}
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "List of messages",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"$ref": "#/definitions/Message"}},
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "per_page": {"type": "integer"},
                            "total": {"type": "integer"},
                            "pages": {"type": "integer"}
                        }
                    }
                }
            }
        },
        "403": {"description": "Not a member", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def list_messages():
    """List messages in a channel."""
    user = get_current_user()
    channel_id = request.args.get('channelId')

    if not channel_id:
        raise ValidationError("channelId is required")

    # Check access (public channels auto-join)
    channel = db.session.get(Channel, channel_id)
    if not channel:
        raise NotFoundError("Channel not found")

    ensure_membership(channel, user)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Get messages
    query = select(Message).where(
        Message.channel_id == channel_id,
        Message.parent_id.is_(None),
        Message.deleted_at.is_(None)
    )

    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    query = query.order_by(Message.created_at.desc()).offset((page - 1) * per_page).limit(per_page)

    messages = db.session.scalars(query).all()

    return jsonify({
        "data": [message_dict(m) for m in messages],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }), 200


@messages_bp.post("")
@jwt_required()
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Messages"],
    "summary": "Send a message",
    "description": "Send a new message to a channel",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["channelId", "content"],
                "properties": {
                    "channelId": {"type": "string"},
                    "content": {"type": "string", "maxLength": 2000},
                    "type": {"type": "string", "enum": ["text", "image", "episode-share"]},
                    "subtitle": {"type": "string"},
                    "image_url": {"type": "string", "format": "url"},
                    "image_caption": {"type": "string"}
                }
            }
        }
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "201": {"description": "Message sent", "schema": {"$ref": "#/definitions/Message"}},
        "403": {"description": "Not a member", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def create_message():
    """Send a new message."""
    user = get_current_user()
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    schema = MessageCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", errors)

    channel = db.session.get(Channel, data['channel_id'])
    if not channel:
        raise NotFoundError("Channel not found")

    ensure_membership(channel, user)

    parent_id = data.get('parent_id')
    if data.get('type', 'text') == 'text' and not (data.get('content') or '').strip():
        raise ValidationError("Message content is required")
    if parent_id:
        parent = db.session.get(Message, parent_id)
        if not parent or parent.channel_id != data['channel_id']:
            raise ValidationError("Invalid parent message")

    message = Message(
        id=f"m-{now_utc().timestamp()}-{user.id[:8]}",
        channel_id=data['channel_id'],
        author_id=user.id,
        parent_id=parent_id,
        message_type=data.get('type', 'text'),
        content=(data.get('content') or '').strip() or ('🖼 ' + data['image_caption'] if data.get('type') == 'image' and data.get('image_caption') else ''),
        subtitle=data.get('subtitle'),
        image_url=data.get('image_url'),
        image_caption=data.get('image_caption')
    )

    db.session.add(message)
    db.session.commit()

    return jsonify(message_dict(message, reply_count=0)), 201


@messages_bp.patch("/<message_id>")
@jwt_required()
@swag_from({
    "tags": ["Messages"],
    "summary": "Update a message",
    "description": "Edit an existing message",
    "parameters": [
        {"name": "message_id", "in": "path", "type": "string", "required": True},
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["content"],
                "properties": {
                    "content": {"type": "string", "maxLength": 2000}
                }
            }
        }
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {"description": "Message updated", "schema": {"$ref": "#/definitions/Message"}},
        "403": {"description": "Not the author", "schema": {"$ref": "#/definitions/Error"}},
        "404": {"description": "Message not found", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def update_message(message_id):
    """Update a message."""
    user = get_current_user()
    message = db.session.get(Message, message_id)

    if not message:
        raise NotFoundError("Message not found")

    if message.author_id != user.id:
        raise ForbiddenError("Only the author can edit this message")

    if message.is_deleted():
        raise ForbiddenError("Cannot edit a deleted message")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    schema = MessageUpdateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", errors)

    message.content = data['content'].strip()
    message.edited_at = now_utc()
    db.session.commit()

    return jsonify(message_dict(message)), 200


@messages_bp.delete("/<message_id>")
@jwt_required()
@swag_from({
    "tags": ["Messages"],
    "summary": "Delete a message",
    "description": "Soft delete a message",
    "parameters": [
        {"name": "message_id", "in": "path", "type": "string", "required": True}
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "204": {"description": "Message deleted"},
        "403": {"description": "Not the author", "schema": {"$ref": "#/definitions/Error"}},
        "404": {"description": "Message not found", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def delete_message(message_id):
    """Delete a message."""
    user = get_current_user()
    message = db.session.get(Message, message_id)

    if not message:
        raise NotFoundError("Message not found")

    if message.author_id != user.id:
        raise ForbiddenError("Only the author can delete this message")

    message.deleted_at = now_utc()
    db.session.commit()

    return "", 204


@messages_bp.get("/<message_id>/thread")
@jwt_required()
def get_thread(message_id):
    """Get a thread: root message + replies."""
    user = get_current_user()
    root = db.session.get(Message, message_id)
    if not root:
        raise NotFoundError("Message not found")

    channel = db.session.get(Channel, root.channel_id)
    if not channel:
        raise NotFoundError("Channel not found")
    ensure_membership(channel, user)
    if channel.is_private and not channel.is_member(user.id) and not user.is_admin():
        raise ForbiddenError("Access denied")

    replies_q = select(Message).where(
        Message.parent_id == message_id,
        Message.deleted_at.is_(None),
    ).order_by(Message.created_at.asc())
    replies = db.session.scalars(replies_q).all()

    return jsonify({
        "id": root.id,
        "channelId": root.channel_id,
        "rootMessage": message_dict(root),
        "replies": [message_dict(r) for r in replies],
    }), 200