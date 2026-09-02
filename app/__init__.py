# app/__init__.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger

load_dotenv()

from .config import config  # This should work
from .extensions import db, migrate, jwt, cache, limiter, swagger, setup_logging
from .exceptions import APIError, ValidationError, AuthenticationError, ForbiddenError, NotFoundError, ConflictError


def create_app(config_name=None):
    """Application factory."""

    # Determine config
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    if isinstance(config_name, dict):
        # Allow passing a config dict directly (used in tests)
        app.config.from_object(config['testing'])
        app.config.update(config_name)
    else:
        app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # CORS
    CORS(app, resources={
        r"/api/*": {"origins": app.config['CORS_ORIGINS']},
        r"/apidocs/*": {"origins": "*"}
    })

    # Setup logging
    setup_logging(app)

    # Initialize Swagger
    swagger.template = {
        "swagger": "2.0",
        "info": {
            "title": "PodClub API",
            "description": "API for PodClub - A music and podcast social platform",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@podclub.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [{"BearerAuth": []}],
        "tags": [
            {"name": "Auth", "description": "Authentication endpoints"},
            {"name": "Channels", "description": "Channel management"},
            {"name": "Messages", "description": "Message operations"},
            {"name": "Moderation", "description": "Moderation and reporting"},
            {"name": "Admin", "description": "Administrative endpoints"},
            {"name": "Health", "description": "Health checks"}
        ],
        "definitions": {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "status": {"type": "integer"},
                    "errors": {"type": "array", "items": {"type": "string"}}
                }
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "email": {"type": "string"},
                    "display_name": {"type": "string"},
                    "avatar_url": {"type": "string"},
                    "role": {"type": "string"},
                    "is_banned": {"type": "boolean"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "Channel": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                    "isPrivate": {"type": "boolean"},
                    "ownerId": {"type": "string"},
                    "memberCount": {"type": "integer"},
                    "createdAt": {"type": "string", "format": "date-time"},
                    "updatedAt": {"type": "string", "format": "date-time"}
                }
            },
            "Message": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "channelId": {"type": "string"},
                    "author": {"$ref": "#/definitions/User"},
                    "content": {"type": "string"},
                    "type": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "replyCount": {"type": "integer"},
                    "imageUrl": {"type": "string"},
                    "imageCaption": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "edited": {"type": "boolean"},
                    "parentId": {"type": "string"}
                }
            }
        }
    }
    swagger.init_app(app)

    # Register blueprints
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    from .routes.channels import channels_bp
    from .routes.messages import messages_bp
    from .routes.moderation import moderation_bp
    from .routes.admin import admin_bp
    from .routes.itunes import itunes_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(channels_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(moderation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(itunes_bp)

    # Error handlers
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return error.to_response()

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed", "status": 405}), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Unhandled error: {error}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "status": 500}), 500

    return app