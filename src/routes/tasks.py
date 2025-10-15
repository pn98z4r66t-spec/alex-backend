"""
Task management routes with validation and pagination
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.models import db, Task
from src.middleware.auth import token_required, get_current_user
from src.utils.validation import validate_request, TaskSchema
from src.utils.errors import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user_id=None):
    """
    Get all tasks with pagination and filtering
    ---
    GET /api/tasks?page=1&per_page=20&status=todo&urgent=true
    Headers: Authorization: Bearer <token>
    """
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
    
    # Filtering parameters
    status = request.args.get('status')
    urgent = request.args.get('urgent')
    assignee_id = request.args.get('assignee_id', type=int)
    
    # Build query
    query = Task.query
    
    if status:
        if status not in ['todo', 'in-progress', 'done']:
            raise ValidationError('Invalid status value')
        query = query.filter_by(status=status)
    
    if urgent is not None:
        urgent_bool = urgent.lower() in ['true', '1', 'yes']
        query = query.filter_by(urgent=urgent_bool)
    
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    # Order by urgent first, then by deadline
    query = query.order_by(Task.urgent.desc(), Task.deadline.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'tasks': [task.to_dict(include_relations=True) for task in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id, current_user_id=None):
    """
    Get specific task by ID
    ---
    GET /api/tasks/1
    Headers: Authorization: Bearer <token>
    """
    task = Task.query.get(task_id)
    
    if not task:
        raise NotFoundError(f'Task with ID {task_id} not found')
    
    return jsonify(task.to_dict(include_relations=True)), 200


@tasks_bp.route('/tasks', methods=['POST'])
@token_required
@validate_request(TaskSchema)
def create_task(current_user_id=None):
    """
    Create a new task
    ---
    POST /api/tasks
    Headers: Authorization: Bearer <token>
    {
        "title": "Complete Project Report",
        "description": "Finish Q4 report",
        "status": "todo",
        "urgent": true,
        "deadline": "2025-10-15T17:00:00",
        "assignee_id": 1,
        "supervisor_id": 2,
        "collaborators": [3, 4]
    }
    """
    data = request.validated_data
    
    try:
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'todo'),
            urgent=data.get('urgent', False),
            deadline=data.get('deadline'),
            assignee_id=data['assignee_id'],
            supervisor_id=data.get('supervisor_id'),
            collaborators=','.join(map(str, data.get('collaborators', [])))
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        logger.info(f'Task created: {new_task.id} - {new_task.title}')
        
        return jsonify({
            'message': 'Task created successfully',
            'task': new_task.to_dict(include_relations=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating task: {str(e)}')
        raise


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id, current_user_id=None):
    """
    Update an existing task
    ---
    PUT /api/tasks/1
    Headers: Authorization: Bearer <token>
    {
        "title": "Updated Title",
        "status": "in-progress",
        "urgent": false
    }
    """
    task = Task.query.get(task_id)
    
    if not task:
        raise NotFoundError(f'Task with ID {task_id} not found')
    
    data = request.json or {}
    
    try:
        # Update allowed fields
        if 'title' in data:
            if not data['title'] or len(data['title']) > 200:
                raise ValidationError('Title must be 1-200 characters')
            task.title = data['title']
        
        if 'description' in data:
            if len(data.get('description', '')) > 1000:
                raise ValidationError('Description must be max 1000 characters')
            task.description = data['description']
        
        if 'status' in data:
            if data['status'] not in ['todo', 'in-progress', 'done']:
                raise ValidationError('Invalid status value')
            task.status = data['status']
        
        if 'urgent' in data:
            task.urgent = bool(data['urgent'])
        
        if 'deadline' in data:
            if data['deadline']:
                task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            else:
                task.deadline = None
        
        if 'assignee_id' in data:
            task.assignee_id = data['assignee_id']
        
        if 'supervisor_id' in data:
            task.supervisor_id = data['supervisor_id']
        
        if 'collaborators' in data:
            task.collaborators = ','.join(map(str, data['collaborators']))
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'Task updated: {task.id} - {task.title}')
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating task: {str(e)}')
        raise


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id, current_user_id=None):
    """
    Delete a task
    ---
    DELETE /api/tasks/1
    Headers: Authorization: Bearer <token>
    """
    task = Task.query.get(task_id)
    
    if not task:
        raise NotFoundError(f'Task with ID {task_id} not found')
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f'Task deleted: {task_id}')
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting task: {str(e)}')
        raise


@tasks_bp.route('/tasks/<int:task_id>/status', methods=['PATCH'])
@token_required
def update_task_status(task_id):
    """
    Quick update task status
    ---
    PATCH /api/tasks/1/status
    Headers: Authorization: Bearer <token>
    {
        "status": "done"
    }
    """
    task = Task.query.get(task_id)
    
    if not task:
        raise NotFoundError(f'Task with ID {task_id} not found')
    
    data = request.json or {}
    new_status = data.get('status')
    
    if not new_status or new_status not in ['todo', 'in-progress', 'done']:
        raise ValidationError('Valid status is required (todo, in-progress, done)')
    
    try:
        task.status = new_status
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'Task status updated: {task_id} -> {new_status}')
        
        return jsonify({
            'message': 'Task status updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating task status: {str(e)}')
        raise

