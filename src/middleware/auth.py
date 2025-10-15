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
        """Wrapper function that verifies JWT and injects user_id"""
        try:
            verify_jwt_in_request()
            # Get user ID and convert to int if it's a string
            user_id = get_jwt_identity()
            if isinstance(user_id, str):
                user_id = int(user_id)
            # Pass user_id to the function via kwargs
            kwargs['current_user_id'] = user_id
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
        """Wrapper function that optionally verifies JWT"""
        from ..models.models import User
        current_user = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                # Convert to int if string
                if isinstance(user_id, str):
                    user_id = int(user_id)
                current_user = User.query.get(user_id)
        except Exception:
            pass
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """
    Get the current authenticated user identity
    """
    try:
        user_id = get_jwt_identity()
        if isinstance(user_id, str):
            user_id = int(user_id)
        return user_id
    except Exception:
        return None

