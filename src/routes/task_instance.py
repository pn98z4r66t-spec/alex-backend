"""
Enhanced Task Instance Routes with Native AI Integration
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import os
import requests
import json
from datetime import datetime

from ..models.models import db, User, File
from ..models.task_instance import TaskInstance, SubTask, TaskFile, TaskAILog, TaskCollaborator
from ..middleware.auth import token_required
from ..utils.errors import APIError, ValidationError
from ..utils.validation import validate_request, TaskInstanceSchema, SubTaskSchema

task_instance_bp = Blueprint('task_instance', __name__)


@task_instance_bp.route('/task-instances', methods=['POST'])
@token_required
@validate_request(TaskInstanceSchema())
def create_task_instance(current_user_id=None):
    """Create a new task instance with AI integration"""
    user_id = get_jwt_identity()
    data = request.validated_data
    
    task = TaskInstance(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        owner_id=user_id,
        supervisor_id=data.get('supervisor_id'),
        assignee_id=data.get('assignee_id'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        ai_enabled=data.get('ai_enabled', True),
    )
    
    db.session.add(task)
    db.session.commit()
    
    # Initialize AI context
    if task.ai_enabled:
        _initialize_ai_context(task)
    
    return jsonify({
        'message': 'Task instance created successfully',
        'task': task.to_dict(include_details=True)
    }), 201


@task_instance_bp.route('/task-instances/<int:task_id>', methods=['GET'])
@token_required
def get_task_instance(task_id, current_user_id=None):
    """Get full task instance with AI logs and subtasks"""
    user_id = get_jwt_identity()
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check access
    if not _check_task_access(task, user_id):
        raise APIError('Access denied', 403)
    
    # Get AI logs
    ai_logs = [log.to_dict() for log in task.ai_logs.order_by(TaskAILog.created_at.desc()).limit(50).all()]
    
    task_data = task.to_dict(include_details=True)
    task_data['ai_logs'] = ai_logs
    
    return jsonify(task_data), 200


@task_instance_bp.route('/task-instances/<int:task_id>/ai/chat', methods=['POST'])
@token_required
def task_ai_chat(task_id, current_user_id=None):
    """Chat with task-specific AI that has access to task files"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'message' not in data:
        raise ValidationError('Message is required')
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check access and AI permission
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_use_ai:
        raise APIError('AI access denied', 403)
    
    if not task.ai_enabled:
        raise APIError('AI is not enabled for this task', 400)
    
    # Build context from task files
    file_context = _build_file_context(task)
    
    # Build full prompt with task context
    full_prompt = f"""You are an AI assistant helping with a specific task.

Task Title: {task.title}
Task Description: {task.description}
Task Status: {task.status}
Task Priority: {task.priority}

"""
    
    if file_context:
        full_prompt += f"Reference Files:\n{file_context}\n\n"
    
    # Add subtasks context
    subtasks = task.subtasks.all()
    if subtasks:
        full_prompt += "Subtasks:\n"
        for st in subtasks:
            assignee_name = st.assignee.name if st.assignee else "Unassigned"
            full_prompt += f"- [{st.status}] {st.title} (Assigned to: {assignee_name})\n"
        full_prompt += "\n"
    
    full_prompt += f"User Question: {data['message']}\n\nProvide a helpful response based on the task context and files."
    
    # Call AI
    ai_response = _call_ai(full_prompt)
    
    # Log the interaction
    ai_log = TaskAILog(
        task_id=task.id,
        user_id=user_id,
        user_message=data['message'],
        ai_response=ai_response,
        files_referenced=json.dumps([f.file_id for f in task.task_files.all()]),
        action_taken='chat'
    )
    db.session.add(ai_log)
    
    # Update task AI context
    task.ai_context = ai_response[:500]  # Store summary
    task.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': data['message'],
        'response': ai_response,
        'log_id': ai_log.id
    }), 200


@task_instance_bp.route('/task-instances/<int:task_id>/ai/analyze', methods=['POST'])
@token_required
def task_ai_analyze(task_id, current_user_id=None):
    """AI analyzes all task files and provides insights"""
    user_id = get_jwt_identity()
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check access
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_use_ai:
        raise APIError('AI access denied', 403)
    
    # Build comprehensive context
    file_context = _build_file_context(task, detailed=True)
    
    if not file_context:
        raise APIError('No files to analyze', 400)
    
    prompt = f"""Analyze the following task and its files:

Task: {task.title}
Description: {task.description}
Status: {task.status}
Priority: {task.priority}

Files:
{file_context}

Provide:
1. Summary of the task based on files
2. Key insights and findings
3. Potential issues or concerns
4. Recommendations for next steps
5. Suggested subtasks to complete this task
"""
    
    ai_response = _call_ai(prompt)
    
    # Log the analysis
    ai_log = TaskAILog(
        task_id=task.id,
        user_id=user_id,
        user_message="Analyze task and files",
        ai_response=ai_response,
        files_referenced=json.dumps([f.file_id for f in task.task_files.all()]),
        action_taken='analyze'
    )
    db.session.add(ai_log)
    
    # Update AI suggestions
    task.ai_suggestions = ai_response
    task.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'analysis': ai_response,
        'log_id': ai_log.id
    }), 200


@task_instance_bp.route('/task-instances/<int:task_id>/subtasks', methods=['POST'])
@token_required
@validate_request(SubTaskSchema())
def create_subtask(task_id, current_user_id=None):
    """Create a subtask"""
    user_id = get_jwt_identity()
    data = request.validated_data
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check permission
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_add_subtasks:
        raise APIError('Permission denied to add subtasks', 403)
    
    subtask = SubTask(
        parent_task_id=task.id,
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'todo'),
        assignee_id=data.get('assignee_id'),
        created_by=user_id,
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
    )
    
    db.session.add(subtask)
    db.session.commit()
    
    return jsonify({
        'message': 'Subtask created successfully',
        'subtask': subtask.to_dict()
    }), 201


@task_instance_bp.route('/task-instances/<int:task_id>/subtasks', methods=['GET'])
@token_required
def get_subtasks(task_id):
    """Get all subtasks for a task"""
    user_id = get_jwt_identity()
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check access
    if not _check_task_access(task, user_id):
        raise APIError('Access denied', 403)
    
    subtasks = task.subtasks.all()
    
    return jsonify({
        'subtasks': [st.to_dict() for st in subtasks],
        'total': len(subtasks)
    }), 200


@task_instance_bp.route('/task-instances/<int:task_id>/subtasks/<int:subtask_id>', methods=['PUT'])
@token_required
def update_subtask(task_id, subtask_id):
    """Update a subtask"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task = TaskInstance.query.get_or_404(task_id)
    subtask = SubTask.query.get_or_404(subtask_id)
    
    if subtask.parent_task_id != task.id:
        raise APIError('Subtask does not belong to this task', 400)
    
    # Check permission
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_add_subtasks:
        raise APIError('Permission denied to update subtasks', 403)
    
    # Update fields
    if 'title' in data:
        subtask.title = data['title']
    if 'description' in data:
        subtask.description = data['description']
    if 'status' in data:
        subtask.status = data['status']
        if data['status'] == 'done':
            subtask.completed_at = datetime.utcnow()
    if 'assignee_id' in data:
        subtask.assignee_id = data['assignee_id']
    
    subtask.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Subtask updated successfully',
        'subtask': subtask.to_dict()
    }), 200


@task_instance_bp.route('/task-instances/<int:task_id>/files', methods=['POST'])
@token_required
def attach_file_to_task(task_id):
    """Attach an existing file to a task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'file_id' not in data:
        raise ValidationError('file_id is required')
    
    task = TaskInstance.query.get_or_404(task_id)
    file = File.query.get_or_404(data['file_id'])
    
    # Check permission
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_add_files:
        raise APIError('Permission denied to add files', 403)
    
    # Check if already attached
    existing = TaskFile.query.filter_by(task_id=task.id, file_id=file.id).first()
    if existing:
        raise APIError('File already attached to this task', 400)
    
    task_file = TaskFile(
        task_id=task.id,
        file_id=file.id,
        uploaded_by=user_id,
        is_reference=data.get('is_reference', False),
        notes=data.get('notes')
    )
    
    db.session.add(task_file)
    db.session.commit()
    
    return jsonify({
        'message': 'File attached to task successfully',
        'task_file': task_file.to_dict()
    }), 201


@task_instance_bp.route('/task-instances/<int:task_id>/files/<int:task_file_id>', methods=['DELETE'])
@token_required
def remove_file_from_task(task_id, task_file_id):
    """Remove a file from a task"""
    user_id = get_jwt_identity()
    
    task = TaskInstance.query.get_or_404(task_id)
    task_file = TaskFile.query.get_or_404(task_file_id)
    
    if task_file.task_id != task.id:
        raise APIError('File does not belong to this task', 400)
    
    # Check permission
    collaborator = _get_collaborator(task, user_id)
    if collaborator and not collaborator.can_delete_files:
        raise APIError('Permission denied to delete files', 403)
    
    db.session.delete(task_file)
    db.session.commit()
    
    return jsonify({'message': 'File removed from task successfully'}), 200


@task_instance_bp.route('/task-instances/<int:task_id>/collaborators', methods=['POST'])
@token_required
def add_collaborator(task_id):
    """Add a collaborator to a task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        raise ValidationError('user_id is required')
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Only owner or admin can add collaborators
    if task.owner_id != user_id:
        collaborator = _get_collaborator(task, user_id)
        if not collaborator or collaborator.role != 'admin':
            raise APIError('Permission denied', 403)
    
    # Check if already a collaborator
    existing = TaskCollaborator.query.filter_by(task_id=task.id, user_id=data['user_id']).first()
    if existing:
        raise APIError('User is already a collaborator', 400)
    
    role = data.get('role', 'viewer')
    permissions = TaskCollaborator.set_role_permissions(role)
    
    collab = TaskCollaborator(
        task_id=task.id,
        user_id=data['user_id'],
        role=role,
        added_by=user_id,
        **permissions
    )
    
    db.session.add(collab)
    db.session.commit()
    
    return jsonify({
        'message': 'Collaborator added successfully',
        'collaborator': collab.to_dict()
    }), 201


@task_instance_bp.route('/task-instances/<int:task_id>/export', methods=['GET'])
@token_required
def export_task_with_logs(task_id):
    """Export task instance with all AI logs and files"""
    user_id = get_jwt_identity()
    
    task = TaskInstance.query.get_or_404(task_id)
    
    # Check access
    if not _check_task_access(task, user_id):
        raise APIError('Access denied', 403)
    
    # Build complete export
    export_data = {
        'task': task.to_dict(include_details=True),
        'ai_logs': [log.to_dict() for log in task.ai_logs.order_by(TaskAILog.created_at).all()],
        'subtasks': [st.to_dict() for st in task.subtasks.all()],
        'files': [tf.to_dict() for tf in task.task_files.all()],
        'collaborators': [c.to_dict() for c in task.collaborators.all()],
        'exported_at': datetime.utcnow().isoformat(),
        'exported_by': user_id
    }
    
    return jsonify(export_data), 200


# Helper functions

def _check_task_access(task, user_id):
    """Check if user has access to task"""
    if task.owner_id == user_id or task.supervisor_id == user_id or task.assignee_id == user_id:
        return True
    
    collaborator = TaskCollaborator.query.filter_by(task_id=task.id, user_id=user_id).first()
    return collaborator is not None


def _get_collaborator(task, user_id):
    """Get collaborator record if exists"""
    # Owner has all permissions
    if task.owner_id == user_id:
        return None  # None means full access
    
    return TaskCollaborator.query.filter_by(task_id=task.id, user_id=user_id).first()


def _build_file_context(task, detailed=False):
    """Build context from task files"""
    task_files = task.task_files.all()
    
    if not task_files:
        return ""
    
    context = ""
    for tf in task_files:
        file = tf.file
        context += f"\n--- File: {file.filename} ---\n"
        
        if detailed and tf.notes:
            context += f"Notes: {tf.notes}\n"
        
        if file.extracted_text:
            # Limit text length
            text = file.extracted_text[:2000] if not detailed else file.extracted_text[:5000]
            context += f"{text}\n"
        else:
            context += f"[File type: {file.mime_type}, Size: {file.file_size_formatted}]\n"
    
    return context


def _initialize_ai_context(task):
    """Initialize AI context for a new task"""
    prompt = f"""Analyze this new task and provide initial guidance:

Title: {task.title}
Description: {task.description}
Priority: {task.priority}

Provide:
1. Understanding of the task objective
2. Suggested approach
3. Potential challenges
4. Recommended subtasks
"""
    
    try:
        ai_response = _call_ai(prompt)
        task.ai_context = ai_response[:500]
        task.ai_suggestions = ai_response
        db.session.commit()
    except Exception as e:
        print(f"Error initializing AI context: {e}")


def _call_ai(prompt):
    """Call AI API"""
    ai_api_url = os.getenv('AI_API_URL', 'http://localhost:11434/api/generate')
    ai_model = os.getenv('AI_MODEL', 'phi3')
    
    try:
        response = requests.post(
            ai_api_url,
            json={
                'model': ai_model,
                'prompt': prompt,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response from AI')
        else:
            raise APIError(f'AI API error: {response.status_code}', 500)
    
    except requests.exceptions.RequestException as e:
        raise APIError(f'AI service unavailable: {str(e)}', 503)

