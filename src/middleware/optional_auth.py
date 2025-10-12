"""
Optional authentication middleware
Allows endpoints to work with or without authentication
"""
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.models import User


def optional_token(f):
    """
    Decorator that makes authentication optional
    If token is provided and valid, current_user is set
    If no token or invalid token, current_user is None
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        
        try:
            # Try to verify JWT
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            if user_id:
                current_user = User.query.get(user_id)
        except Exception:
            # No token or invalid token - that's okay
            pass
        
        return f(*args, current_user=current_user, **kwargs)
    
    return decorated

