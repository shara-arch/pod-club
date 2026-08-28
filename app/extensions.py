from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
import logging

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'simple'})  # Fix: Configure cache type
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])  # Fix: Set default limits
swagger = Swagger()


def setup_logging(app):
    """Setup application logging."""
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


# JWT error handlers
@jwt.unauthorized_loader
def unauthorized_response(callback):
    """Handle missing or invalid JWT."""
    from flask import jsonify
    return jsonify({
        "error": "Missing or invalid authorization token",
        "status": 401
    }), 401


@jwt.invalid_token_loader
def invalid_token_response(callback):
    """Handle invalid JWT."""
    from flask import jsonify
    return jsonify({
        "error": "Invalid authorization token",
        "status": 401
    }), 401


@jwt.expired_token_loader
def expired_token_response(callback):
    """Handle expired JWT."""
    from flask import jsonify
    return jsonify({
        "error": "Authorization token has expired",
        "status": 401
    }), 401


@jwt.revoked_token_loader
def revoked_token_response(callback):
    """Handle revoked JWT."""
    from flask import jsonify
    return jsonify({
        "error": "Authorization token has been revoked",
        "status": 401
    }), 401