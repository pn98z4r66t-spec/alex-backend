"""
Authentication middleware using JWT
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError


def token_required(f):
    """
    Decorator to require valid JWT token for endpoint access
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except NoAuthorizationError:
            return jsonify({'error': 'Missing authorization token'}), 401
        except InvalidHeaderError:
            return jsonify({'error': 'Invalid authorization header'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    return decorated


def optional_token(f):
    """
    Decorator for endpoints that work with or without authentication
    Passes current_user to the function if authenticated, None otherwise
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from ..models.models import User
        current_user = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                current_user = User.query.get(user_id)
        except Exception:
            pass
        return f(*args, current_user=current_user, **kwargs)
    return decorated


def get_current_user():
    """
    Get the current authenticated user identity
    """
    try:
        return get_jwt_identity()
    except Exception:
        return None

