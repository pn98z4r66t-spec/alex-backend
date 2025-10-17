"""
User management routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User
from src.utils.errors import AuthenticationError, ValidationError
from src.middleware.auth import token_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information
    ---
    GET /api/users/me
    Headers: Authorization: Bearer <token>
    
    Returns:
        User object with profile information
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """
    Update current user profile
    ---
    PUT /api/users/me
    Headers: Authorization: Bearer <token>
    {
        "name": "New Name",
        "role": "New Role"
    }
    
    Returns:
        Updated user object
    """
    user_id = get_jwt_identity()
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    data = request.get_json()
    
    # Update allowed fields
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    """
    List all users (admin only in future)
    ---
    GET /api/users
    Headers: Authorization: Bearer <token>
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        search: Search by name or email
    
    Returns:
        Paginated list of users
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    # Search filter
    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    # Paginate
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get user by ID
    ---
    GET /api/users/{user_id}
    Headers: Authorization: Bearer <token>
    
    Returns:
        User object
    """
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError('User not found')
    
    return jsonify(user.to_dict()), 200

