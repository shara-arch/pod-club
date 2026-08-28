from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func, or_
from flasgger import swag_from
from ..extensions import db, limiter
from ..models import Channel, ChannelMembership, MembershipRole
from ..schemas import ChannelCreateSchema, ChannelUpdateSchema, PaginationSchema
from ..serializers import channel_dict
from ..decorators import get_current_user
from ..exceptions import ValidationError, NotFoundError, ForbiddenError, ConflictError

channels_bp = Blueprint("channels", __name__, url_prefix="/api/channels")


@channels_bp.get("")
@jwt_required()
@swag_from({
    "tags": ["Channels"],
    "summary": "List channels",
    "description": "Get paginated list of channels with optional filtering",
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "default": 1},
        {"name": "per_page", "in": "query", "type": "integer", "default": 50, "maximum": 100},
        {"name": "q", "in": "query", "type": "string", "description": "Search query"},
        {"name": "category", "in": "query", "type": "string"},
        {"name": "my", "in": "query", "type": "boolean", "description": "Only show channels I'm in"}
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "List of channels",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"$ref": "#/definitions/Channel"}},
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
        "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def list_channels():
    """List all channels with pagination and filtering."""
    user = get_current_user()
    
    schema = PaginationSchema()
    errors = schema.validate(request.args)
    if errors:
        raise ValidationError("Invalid pagination parameters", errors)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('q')
    category = request.args.get('category')
    only_my = request.args.get('my', 'false').lower() == 'true'
    
    query = select(Channel)
    
    if not user.is_admin():
        query = query.where(
            or_(
                Channel.is_private == False,
                Channel.id.in_(
                    select(ChannelMembership.channel_id).where(
                        ChannelMembership.user_id == user.id
                    )
                )
            )
        )
    
    if only_my:
        query = query.where(
            Channel.id.in_(
                select(ChannelMembership.channel_id).where(
                    ChannelMembership.user_id == user.id
                )
            )
        )
    
    if search:
        query = query.where(
            or_(
                Channel.name.ilike(f'%{search}%'),
                Channel.description.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.where(Channel.category == category)
    
    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    query = query.order_by(Channel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    
    channels = db.session.scalars(query).all()
    
    return jsonify({
        "data": [channel_dict(c) for c in channels],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }), 200


@channels_bp.post("")
@jwt_required()
@limiter.limit("5 per hour")
@swag_from({
    "tags": ["Channels"],
    "summary": "Create a channel",
    "description": "Create a new channel (max 5 per user)",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["id", "name", "category"],
                "properties": {
                    "id": {"type": "string", "pattern": "^[a-z0-9-]+$", "example": "my-channel"},
                    "name": {"type": "string", "example": "My Channel"},
                    "description": {"type": "string", "example": "Channel description"},
                    "category": {"type": "string", "enum": ["True Crime", "Comedy", "Music Lab", "Tech & Dev", "Culture", "Sports Room", "General"]},
                    "is_private": {"type": "boolean", "default": True}
                }
            }
        }
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "201": {
            "description": "Channel created",
            "schema": {"$ref": "#/definitions/Channel"}
        },
        "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
        "409": {"description": "Channel exists or limit reached", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def create_channel():
    """Create a new channel (max 5 per user)."""
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    schema = ChannelCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", errors)
    
    if Channel.query.get(data['id']):
        raise ConflictError(f"Channel '{data['id']}' already exists")
    
    owned_count = db.session.scalar(
        select(func.count(Channel.id)).where(Channel.owner_id == user.id)
    )
    if owned_count >= 5:
        raise ConflictError("Maximum 5 channels allowed per user")
    
    channel = Channel(
        id=data['id'],
        name=data['name'].strip(),
        description=data.get('description', '').strip(),
        category=data['category'],
        is_private=data.get('is_private', True),
        owner_id=user.id
    )
    
    membership = ChannelMembership(
        channel_id=channel.id,
        user_id=user.id,
        role=MembershipRole.OWNER
    )
    
    db.session.add(channel)
    db.session.add(membership)
    db.session.commit()
    
    return jsonify(channel_dict(channel)), 201


@channels_bp.get("/<channel_id>")
@jwt_required()
@swag_from({
    "tags": ["Channels"],
    "summary": "Get channel details",
    "parameters": [
        {"name": "channel_id", "in": "path", "type": "string", "required": True}
    ],
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {"description": "Channel details", "schema": {"$ref": "#/definitions/Channel"}},
        "404": {"description": "Channel not found", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def get_channel(channel_id):
    """Get channel details."""
    user = get_current_user()
    channel = db.session.get(Channel, channel_id)
    
    if not channel:
        raise NotFoundError("Channel not found")
    
    if channel.is_private and not channel.is_member(user.id) and not user.is_admin():
        raise ForbiddenError("You don't have access to this channel")
    
    return jsonify(channel_dict(channel)), 200