"""
Team Routes - Team Collaboration API
Handles team member management and collaboration features
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime

from src.models.models import db, User, Task
from src.middleware.auth import token_required

team_bp = Blueprint('team', __name__)


@team_bp.route('/team/members', methods=['GET'])
@jwt_required()
@token_required
def get_team_members(current_user_id):
    """
    Get all team members with optional filtering
    
    Query Parameters:
    - role: Filter by role
    - online: Filter by online status (true/false)
    - search: Search by name or email
    """
    try:
        # Get query parameters
        role = request.args.get('role', type=str)
        online_status = request.args.get('online', type=str)
        search = request.args.get('search', type=str)
        
        # Build query
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter_by(role=role)
        
        if online_status is not None:
            is_online = online_status.lower() == 'true'
            query = query.filter_by(online=is_online)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        # Order by name
        query = query.order_by(User.name.asc())
        
        # Get all members
        members = query.all()
        
        # Format response
        members_data = [{
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'role': member.role,
            'online': member.online,
            'created_at': member.created_at.isoformat() if member.created_at else None
        } for member in members]
        
        return jsonify({
            'members': members_data,
            'total': len(members_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/members/<int:member_id>', methods=['GET'])
@jwt_required()
@token_required
def get_team_member(current_user_id, member_id):
    """Get detailed information about a specific team member"""
    try:
        member = User.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        # Get member's task statistics
        assigned_tasks = Task.query.filter_by(assignee_id=member_id).count()
        supervised_tasks = Task.query.filter_by(supervisor_id=member_id).count()
        completed_tasks = Task.query.filter_by(
            assignee_id=member_id,
            status='completed'
        ).count()
        
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'role': member.role,
            'online': member.online,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'statistics': {
                'assigned_tasks': assigned_tasks,
                'supervised_tasks': supervised_tasks,
                'completed_tasks': completed_tasks
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/members/<int:member_id>/tasks', methods=['GET'])
@jwt_required()
@token_required
def get_member_tasks(current_user_id, member_id):
    """Get tasks assigned to or supervised by a team member"""
    try:
        member = User.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        # Get query parameters
        task_type = request.args.get('type', 'assigned')  # assigned or supervised
        status = request.args.get('status', type=str)
        
        # Build query based on type
        if task_type == 'supervised':
            query = Task.query.filter_by(supervisor_id=member_id)
        else:
            query = Task.query.filter_by(assignee_id=member_id)
        
        # Apply status filter
        if status:
            query = query.filter_by(status=status)
        
        # Order by deadline
        query = query.order_by(Task.deadline.asc())
        
        tasks = query.all()
        
        # Format response
        tasks_data = [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'urgent': task.urgent,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'assignee_id': task.assignee_id,
            'supervisor_id': task.supervisor_id
        } for task in tasks]
        
        return jsonify({
            'member_id': member_id,
            'member_name': member.name,
            'task_type': task_type,
            'tasks': tasks_data,
            'total': len(tasks_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/stats', methods=['GET'])
@jwt_required()
@token_required
def get_team_stats(current_user_id):
    """Get overall team statistics"""
    try:
        total_members = User.query.count()
        online_members = User.query.filter_by(online=True).count()
        
        # Count by role
        roles = db.session.query(
            User.role,
            db.func.count(User.id)
        ).group_by(User.role).all()
        
        role_counts = {role: count for role, count in roles}
        
        # Task statistics
        total_tasks = Task.query.count()
        active_tasks = Task.query.filter(
            Task.status.in_(['todo', 'in-progress'])
        ).count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        
        return jsonify({
            'team': {
                'total_members': total_members,
                'online_members': online_members,
                'offline_members': total_members - online_members,
                'roles': role_counts
            },
            'tasks': {
                'total': total_tasks,
                'active': active_tasks,
                'completed': completed_tasks
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/online', methods=['GET'])
@jwt_required()
@token_required
def get_online_members(current_user_id):
    """Get list of currently online team members"""
    try:
        online_members = User.query.filter_by(online=True).order_by(User.name.asc()).all()
        
        members_data = [{
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'role': member.role,
        } for member in online_members]
        
        return jsonify({
            'online_members': members_data,
            'count': len(members_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/roles', methods=['GET'])
@jwt_required()
@token_required
def get_roles(current_user_id):
    """Get list of all roles in the team"""
    try:
        roles = db.session.query(User.role).distinct().all()
        role_list = [role[0] for role in roles if role[0]]
        
        return jsonify({
            'roles': role_list,
            'count': len(role_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/search', methods=['GET'])
@jwt_required()
@token_required
def search_team_members(current_user_id):
    """
    Search team members by name, email, or role
    
    Query Parameters:
    - q: Search query
    """
    try:
        search_query = request.args.get('q', '').strip()
        
        if not search_query:
            return jsonify({'error': 'Search query required'}), 400
        
        search_term = f"%{search_query}%"
        
        members = User.query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                User.role.ilike(search_term)
            )
        ).order_by(User.name.asc()).all()
        
        members_data = [{
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'role': member.role,
            'online': member.online,
        } for member in members]
        
        return jsonify({
            'query': search_query,
            'members': members_data,
            'count': len(members_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/collaborators', methods=['GET'])
@jwt_required()
@token_required
def get_potential_collaborators(current_user_id):
    """
    Get list of team members who can be added as collaborators
    Excludes the current user
    """
    try:
        members = User.query.filter(
            User.id != current_user_id
        ).order_by(User.name.asc()).all()
        
        members_data = [{
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'role': member.role,
            'online': member.online
        } for member in members]
        
        return jsonify({
            'collaborators': members_data,
            'count': len(members_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

