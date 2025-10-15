"""
Error handling utilities
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert error to dictionary for JSON response"""
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """Validation error"""
    status_code = 400


class AuthenticationError(APIError):
    """Authentication error"""
    status_code = 401


class AuthorizationError(APIError):
    """Authorization error"""
    status_code = 403


class NotFoundError(APIError):
    """Resource not found error"""
    status_code = 404


class ConflictError(APIError):
    """Resource conflict error"""
    status_code = 409


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    status_code = 429


def register_error_handlers(app):
    """
    Register error handlers with Flask app
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        logger.error(f'API Error: {error.message}')
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions"""
        logger.error(f'HTTP Exception: {error.description}')
        return jsonify({
            'error': error.description,
            'status_code': error.code
        }), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        logger.exception(f'Unexpected error: {str(error)}')
        return jsonify({
            'error': 'An unexpected error occurred',
            'status_code': 500
        }), 500

