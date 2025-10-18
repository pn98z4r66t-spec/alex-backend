"""
Authentication routes with httpOnly cookie support
"""
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, unset_jwt_cookies
)
from datetime import datetime, timedelta
from src.models.models import db, User
from src.utils.validation import validate_request, LoginSchema, RegisterSchema
from src.utils.errors import AuthenticationError, ValidationError, ConflictError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_request(RegisterSchema)
def register():
    """
    Register a new user
    ---
    POST /api/auth/register
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword",
        "role": "Developer"
    }
    
    Returns tokens in httpOnly cookies for security
    """
    data = request.validated_data
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        raise ConflictError('User with this email already exists')
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        role=data.get('role', 'Developer'),
        online=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create tokens with string identity
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Create response with httpOnly cookies
    response = make_response(jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201)
    
    # Set access token cookie (httpOnly, secure in production)
    response.set_cookie(
        'access_token',
        value=access_token,
        httponly=True,
        secure=request.is_secure,  # True in production with HTTPS
        samesite='Lax',
        max_age=timedelta(hours=1)
    )
    
    # Set refresh token cookie (httpOnly, secure in production)
    response.set_cookie(
        'refresh_token',
        value=refresh_token,
        httponly=True,
        secure=request.is_secure,
        samesite='Lax',
        max_age=timedelta(days=30)
    )
    
    return response


@auth_bp.route('/login', methods=['POST'])
@validate_request(LoginSchema)
def login():
    """
    Login user
    ---
    POST /api/auth/login
    {
        "email": "john@example.com",
        "password": "securepassword"
    }
    
    Returns tokens in httpOnly cookies for security
    """
    data = request.validated_data
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        raise AuthenticationError('Invalid email or password')
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.online = True
    db.session.commit()
    
    # Create tokens with string identity
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Create response with httpOnly cookies
    response = make_response(jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200)
    
    # Set access token cookie (httpOnly, secure in production)
    response.set_cookie(
        'access_token',
        value=access_token,
        httponly=True,
        secure=request.is_secure,
        samesite='Lax',
        max_age=timedelta(hours=1)
    )
    
    # Set refresh token cookie (httpOnly, secure in production)
    response.set_cookie(
        'refresh_token',
        value=refresh_token,
        httponly=True,
        secure=request.is_secure,
        samesite='Lax',
        max_age=timedelta(days=30)
    )
    
    return response


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user
    ---
    POST /api/auth/logout
    Cookies: access_token (httpOnly)
    
    Clears authentication cookies
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if user:
        user.online = False
        db.session.commit()
    
    # Create response and clear cookies
    response = make_response(jsonify({'message': 'Logout successful'}), 200)
    
    # Clear both tokens
    response.set_cookie('access_token', '', expires=0, httponly=True, secure=request.is_secure, samesite='Lax')
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=request.is_secure, samesite='Lax')
    
    return response


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    POST /api/auth/refresh
    Cookies: refresh_token (httpOnly)
    
    Returns new access token in httpOnly cookie
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    # Create new access token with string identity
    access_token = create_access_token(identity=str(user_id))
    
    # Create response with new access token cookie
    response = make_response(jsonify({
        'message': 'Token refreshed successfully'
    }), 200)
    
    response.set_cookie(
        'access_token',
        value=access_token,
        httponly=True,
        secure=request.is_secure,
        samesite='Lax',
        max_age=timedelta(hours=1)
    )
    
    return response


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information
    ---
    GET /api/auth/me
    Cookies: access_token (httpOnly)
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile
    ---
    PUT /api/auth/me
    Cookies: access_token (httpOnly)
    {
        "name": "New Name",
        "role": "New Role"
    }
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

