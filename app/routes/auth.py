from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flasgger import swag_from
from datetime import datetime
from ..extensions import db, limiter
from ..models import User, now_utc
from ..schemas import UserRegisterSchema, UserLoginSchema
from ..exceptions import ValidationError, AuthenticationError, ConflictError, ForbiddenError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Auth"],
    "summary": "Register a new user",
    "description": "Create a new user account with email and password",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["email", "password", "display_name"],
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "user@example.com"},
                    "password": {"type": "string", "minLength": 6, "example": "SecurePass123"},
                    "display_name": {"type": "string", "example": "John Doe"},
                    "avatar_url": {"type": "string", "format": "url", "example": "https://example.com/avatar.jpg"}
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "User registered successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user": {"$ref": "#/definitions/User"}
                }
            }
        },
        "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
        "409": {"description": "Email already registered", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")
    
    schema = UserRegisterSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", errors)
    
    if User.query.filter_by(email=data['email']).first():
        raise ConflictError("Email already registered")
    
    user = User(
        id=data['email'].split('@')[0] + '-' + str(int(datetime.now().timestamp())),
        email=data['email'],
        display_name=data['display_name'],
        avatar_url=data.get('avatar_url')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Auth"],
    "summary": "Login user",
    "description": "Authenticate user and get JWT tokens",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "user@example.com"},
                    "password": {"type": "string", "example": "SecurePass123"}
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Login successful",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "user": {"$ref": "#/definitions/User"}
                }
            }
        },
        "401": {"description": "Invalid credentials", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def login():
    """Login and get access token."""
    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")
    
    schema = UserLoginSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", errors)
    
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        raise AuthenticationError("Invalid email or password")
    
    if user.is_banned:
        raise ForbiddenError("Account is banned")
    
    user.last_login_at = now_utc()
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@swag_from({
    "tags": ["Auth"],
    "summary": "Refresh access token",
    "description": "Get a new access token using refresh token",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Token refreshed",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"}
                }
            }
        },
        "401": {"description": "Invalid or expired refresh token", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        raise AuthenticationError("User not found")
    
    if user.is_banned:
        raise ForbiddenError("Account is banned")
    
    new_access_token = create_access_token(identity=user_id)
    
    return jsonify({
        "access_token": new_access_token
    }), 200


@auth_bp.post("/logout")
@jwt_required()
@swag_from({
    "tags": ["Auth"],
    "summary": "Logout user",
    "description": "Invalidate current session (client-side token removal)",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Logout successful",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        }
    }
})
def logout():
    """Logout (client-side - remove tokens)."""
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.get("/me")
@jwt_required()
@swag_from({
    "tags": ["Auth"],
    "summary": "Get current user info",
    "description": "Get details of the authenticated user",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "User details",
            "schema": {"$ref": "#/definitions/User"}
        },
        "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}}
    }
})
def get_current_user():
    """Get current user info."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        raise AuthenticationError("User not found")
    
    return jsonify(user.to_dict()), 200