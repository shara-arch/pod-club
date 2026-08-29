from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, select, func
from flasgger import swag_from
from ..extensions import db
from ..models import User, Channel, Message, UserReport, ReportStatus
from ..decorators import admin_required
from ..serializers import user_dict

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/stats")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Get admin dashboard stats",
    "description": "Get statistics for admin dashboard",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Dashboard statistics",
            "schema": {
                "type": "object",
                "properties": {
                    "total_users": {"type": "integer"},
                    "total_channels": {"type": "integer"},
                    "open_reports": {"type": "integer"},
                    "banned_users": {"type": "integer"},
                    "active_channels": {"type": "integer"},
                    "total_messages": {"type": "integer"}
                }
            }
        },
        "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def get_stats():
    """Get admin dashboard statistics."""
    total_users = db.session.scalar(select(func.count(User.id)))
    total_channels = db.session.scalar(select(func.count(Channel.id)))
    open_reports = db.session.scalar(
        select(func.count(UserReport.id)).where(UserReport.status == ReportStatus.OPEN)
    )
    banned_users = db.session.scalar(select(func.count(User.id)).where(User.is_banned == True))
    total_messages = db.session.scalar(select(func.count(Message.id)))
    
    return jsonify({
        "total_users": total_users or 0,
        "total_channels": total_channels or 0,
        "open_reports": open_reports or 0,
        "banned_users": banned_users or 0,
        "total_messages": total_messages or 0,
        "active_channels": total_channels or 0
    }), 200


@admin_bp.get("/users")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "List all users",
    "description": "Get all users with pagination",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "default": 1},
        {"name": "per_page", "in": "query", "type": "integer", "default": 50},
        {"name": "search", "in": "query", "type": "string"}
    ],
    "responses": {
        "200": {
            "description": "List of users",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"$ref": "#/definitions/User"}},
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
        }
    }
})
def list_users():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search')
    
    query = select(User)
    
    if search:
        query = query.where(
            or_(
                User.display_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    query = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    
    users = db.session.scalars(query).all()
    
    return jsonify({
        "data": [user_dict(u) for u in users],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }), 200