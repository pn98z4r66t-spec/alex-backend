"""
Email Routes - Email Management API
Handles email listing, reading, and basic operations
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime

from src.models.models import db, Email, User
from src.middleware.auth import token_required

email_bp = Blueprint('email', __name__)


@email_bp.route('/emails', methods=['GET'])
@jwt_required()
@token_required
def get_emails(current_user_id):
    """
    Get emails for current user with filtering and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - priority: Filter by priority (priority, normal, low)
    - read: Filter by read status (true/false)
    - search: Search in subject and body
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        priority = request.args.get('priority', type=str)
        read_status = request.args.get('read', type=str)
        search = request.args.get('search', type=str)
        
        # Build query
        query = Email.query.filter_by(user_id=current_user_id)
        
        # Apply filters
        if priority:
            query = query.filter_by(priority=priority)
        
        if read_status is not None:
            is_read = read_status.lower() == 'true'
            query = query.filter_by(read=is_read)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Email.subject.ilike(search_term),
                    Email.body.ilike(search_term),
                    Email.sender.ilike(search_term)
                )
            )
        
        # Order by timestamp (newest first)
        query = query.order_by(Email.received_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Format response
        emails = [{
            'id': email.id,
            'sender': email.sender,
            'subject': email.subject,
            'body': email.body,
            'priority': email.priority,
            'read': email.read,
            'timestamp': email.received_at.isoformat(),
        } for email in pagination.items]
        
        return jsonify({
            'emails': emails,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/<int:email_id>', methods=['GET'])
@jwt_required()
@token_required
def get_email(current_user_id, email_id):
    """Get a specific email by ID"""
    try:
        email = Email.query.filter_by(
            id=email_id,
            user_id=current_user_id
        ).first()
        
        if not email:
            return jsonify({'error': 'Email not found'}), 404
        
        # Mark as read when accessed
        if not email.read:
            email.read = True
            db.session.commit()
        
        return jsonify({
            'id': email.id,
            'sender': email.sender,
            'subject': email.subject,
            'body': email.body,
            'priority': email.priority,
            'read': email.read,
            'timestamp': email.received_at.isoformat(),
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/<int:email_id>/read', methods=['PATCH'])
@jwt_required()
@token_required
def mark_email_read(current_user_id, email_id):
    """Mark an email as read or unread"""
    try:
        email = Email.query.filter_by(
            id=email_id,
            user_id=current_user_id
        ).first()
        
        if not email:
            return jsonify({'error': 'Email not found'}), 404
        
        data = request.get_json()
        read_status = data.get('read', True)
        
        email.read = read_status
        db.session.commit()
        
        return jsonify({
            'message': 'Email status updated',
            'email_id': email_id,
            'read': email.read
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/<int:email_id>', methods=['DELETE'])
@jwt_required()
@token_required
def delete_email(current_user_id, email_id):
    """Delete an email"""
    try:
        email = Email.query.filter_by(
            id=email_id,
            user_id=current_user_id
        ).first()
        
        if not email:
            return jsonify({'error': 'Email not found'}), 404
        
        db.session.delete(email)
        db.session.commit()
        
        return jsonify({
            'message': 'Email deleted successfully',
            'email_id': email_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/stats', methods=['GET'])
@jwt_required()
@token_required
def get_email_stats(current_user_id):
    """Get email statistics for current user"""
    try:
        total = Email.query.filter_by(user_id=current_user_id).count()
        unread = Email.query.filter_by(user_id=current_user_id, read=False).count()
        priority = Email.query.filter_by(
            user_id=current_user_id,
            priority='priority'
        ).count()
        
        return jsonify({
            'total': total,
            'unread': unread,
            'priority': priority,
            'read': total - unread
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/bulk/read', methods=['PATCH'])
@jwt_required()
@token_required
def bulk_mark_read(current_user_id):
    """Mark multiple emails as read"""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        read_status = data.get('read', True)
        
        if not email_ids:
            return jsonify({'error': 'No email IDs provided'}), 400
        
        # Update emails
        Email.query.filter(
            and_(
                Email.id.in_(email_ids),
                Email.user_id == current_user_id
            )
        ).update({'read': read_status}, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated {len(email_ids)} emails',
            'count': len(email_ids)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_bp.route('/emails/bulk/delete', methods=['DELETE'])
@jwt_required()
@token_required
def bulk_delete_emails(current_user_id):
    """Delete multiple emails"""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return jsonify({'error': 'No email IDs provided'}), 400
        
        # Delete emails
        deleted = Email.query.filter(
            and_(
                Email.id.in_(email_ids),
                Email.user_id == current_user_id
            )
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Deleted {deleted} emails',
            'count': deleted
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

