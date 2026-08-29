from flask import jsonify


class APIError(Exception):
    """Base API exception."""
    
    def __init__(self, message: str, status_code: int = 400, errors: list = None):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)
    
    def to_response(self):
        response = {
            "error": self.message,
            "status": self.status_code
        }
        if self.errors:
            response["errors"] = self.errors
        return jsonify(response), self.status_code


class ValidationError(APIError):
    """Validation error."""
    def __init__(self, message: str = "Validation error", errors: list = None):
        super().__init__(message, 400, errors)


class AuthenticationError(APIError):
    """Authentication error."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class ForbiddenError(APIError):
    """Forbidden error."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, 403)


class NotFoundError(APIError):
    """Not found error."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ConflictError(APIError):
    """Conflict error."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409)


class RateLimitError(APIError):
    """Rate limit error."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)