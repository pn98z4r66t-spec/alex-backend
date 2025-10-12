"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime
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
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


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
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user
    ---
    POST /api/auth/logout
    Headers: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user:
        user.online = False
        db.session.commit()
    
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    POST /api/auth/refresh
    Headers: Authorization: Bearer <refresh_token>
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user info
    ---
    GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """
    Update current user info
    ---
    PUT /api/auth/me
    Headers: Authorization: Bearer <token>
    {
        "name": "New Name",
        "role": "Manager"
    }
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    data = request.json
    
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

