from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity
from .extensions import db
from .models import User
from .exceptions import AuthenticationError, ForbiddenError, ValidationError


def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    if not user_id:
        raise AuthenticationError("Invalid authentication token")
    
    user = db.session.get(User, user_id)
    if not user:
        raise AuthenticationError("User not found")
    
    if user.is_banned:
        raise ForbiddenError("User is banned")
    
    return user


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user.role.value != "admin":
            raise ForbiddenError("Admin access required")
        return f(*args, **kwargs)
    return decorated


def channel_member_required(channel_id_param='channel_id'):
    """Decorator to require channel membership."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            channel_id = kwargs.get(channel_id_param) or request.json.get(channel_id_param)
            
            if not channel_id:
                raise ValidationError(f"{channel_id_param} is required")
            
            from .models import Channel
            channel = db.session.get(Channel, channel_id)
            if not channel:
                raise NotFoundError("Channel not found")
            
            # Check if user is a member
            membership = None
            for m in channel.memberships:
                if m.user_id == user.id:
                    membership = m
                    break
            
            if not membership and not user.is_admin():
                raise ForbiddenError("You must be a channel member")
            
            return f(*args, **kwargs)
        return decorated
    return decorator