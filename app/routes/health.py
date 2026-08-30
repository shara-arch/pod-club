from flask import Blueprint, jsonify
from flasgger import swag_from

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
@swag_from({
    "tags": ["Health"],
    "summary": "Health check endpoint",
    "description": "Check if the API is running and healthy",
    "responses": {
        "200": {
            "description": "API is healthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }
    }
})
def health():
    """Health check endpoint."""
    from datetime import datetime
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200