"""
Task Group Chat Routes
Handles group chat functionality for task boards
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_

from ..models.models import db, User, Task
from ..models.chat_models import TaskChat, ChatMessage, ChatParticipant
from ..middleware.auth import token_required
from ..utils.errors import APIError, NotFoundError, AuthorizationError
from ..utils.validation import sanitize_string

task_chat_bp = Blueprint('task_chat', __name__)


@task_chat_bp.route('/tasks/<int:task_id>/chat', methods=['POST', 'GET'])
@token_required
def get_or_create_chat(task_id, current_user_id=None):
    """
    Get or create chat for a task
    ---
    POST/GET /api/tasks/1/chat
    Headers: Authorization: Bearer <token>
    """
    # Verify task exists
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task not found')
    
    # Verify user has access to task
    if not _user_has_task_access(current_user_id, task):
        raise AuthorizationError('You do not have access to this task')
    
    # Get or create chat
    chat = TaskChat.query.filter_by(task_id=task_id).first()
    
    if not chat:
        # Create new chat
        chat = TaskChat(task_id=task_id)
        db.session.add(chat)
        db.session.commit()
        
        # Add task participants to chat
        _add_task_participants_to_chat(chat, task)
    
    # Ensure current user is a participant
    participant = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=current_user_id
    ).first()
    
    if not participant:
        participant = ChatParticipant(
            chat_id=chat.id,
            user_id=current_user_id,
            role='member'
        )
        db.session.add(participant)
        db.session.commit()
    
    return jsonify(chat.to_dict()), 200


@task_chat_bp.route('/tasks/<int:task_id>/chat/messages', methods=['GET'])
@token_required
def get_messages(task_id, current_user_id=None):
    """
    Get chat messages with pagination
    ---
    GET /api/tasks/1/chat/messages?page=1&per_page=50&before=<message_id>
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    chat = _get_chat_with_access(task_id, current_user_id)
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    before_id = request.args.get('before', type=int)
    
    # Build query
    query = ChatMessage.query.filter_by(chat_id=chat.id, is_deleted=False)
    
    if before_id:
        query = query.filter(ChatMessage.id < before_id)
    
    # Order by newest first
    query = query.order_by(ChatMessage.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    messages = [msg.to_dict() for msg in pagination.items]
    
    # Update last_read_at for current user
    participant = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=current_user_id
    ).first()
    
    if participant:
        participant.last_read_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        'messages': messages,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@task_chat_bp.route('/tasks/<int:task_id>/chat/messages', methods=['POST'])
@token_required
def send_message(task_id, current_user_id=None):
    """
    Send a message to the chat
    ---
    POST /api/tasks/1/chat/messages
    Headers: Authorization: Bearer <token>
    Body: {
        "message": "Hello team!",
        "message_type": "text",
        "metadata": {}
    }
    """
    # Verify access
    chat = _get_chat_with_access(task_id, current_user_id)
    
    data = request.get_json()
    if not data or 'message' not in data:
        raise APIError('Message is required', 400)
    
    message_text = sanitize_string(data['message'])
    if not message_text or len(message_text.strip()) == 0:
        raise APIError('Message cannot be empty', 400)
    
    if len(message_text) > 5000:
        raise APIError('Message too long (max 5000 characters)', 400)
    
    message_type = data.get('message_type', 'text')
    if message_type not in ['text', 'file', 'system']:
        raise APIError('Invalid message type', 400)
    
    # Create message
    message = ChatMessage(
        chat_id=chat.id,
        user_id=current_user_id,
        message=message_text,
        message_type=message_type,
        message_metadata=data.get('metadata')
    )
    
    db.session.add(message)
    
    # Update chat updated_at
    chat.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(message.to_dict()), 201


@task_chat_bp.route('/tasks/<int:task_id>/chat/messages/<int:message_id>', methods=['PUT'])
@token_required
def edit_message(task_id, message_id, current_user_id=None):
    """
    Edit a message (only by the author)
    ---
    PUT /api/tasks/1/chat/messages/123
    Headers: Authorization: Bearer <token>
    Body: {"message": "Updated message"}
    """
    # Verify access
    chat = _get_chat_with_access(task_id, current_user_id)
    
    message = ChatMessage.query.filter_by(id=message_id, chat_id=chat.id).first()
    if not message:
        raise NotFoundError('Message not found')
    
    # Only author can edit
    if message.user_id != current_user_id:
        raise AuthorizationError('You can only edit your own messages')
    
    if message.is_deleted:
        raise APIError('Cannot edit deleted message', 400)
    
    data = request.get_json()
    if not data or 'message' not in data:
        raise APIError('Message is required', 400)
    
    new_message = sanitize_string(data['message'])
    if not new_message or len(new_message.strip()) == 0:
        raise APIError('Message cannot be empty', 400)
    
    message.message = new_message
    message.edited_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(message.to_dict()), 200


@task_chat_bp.route('/tasks/<int:task_id>/chat/messages/<int:message_id>', methods=['DELETE'])
@token_required
def delete_message(task_id, message_id, current_user_id=None):
    """
    Delete a message (soft delete)
    ---
    DELETE /api/tasks/1/chat/messages/123
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    chat = _get_chat_with_access(task_id, current_user_id)
    
    message = ChatMessage.query.filter_by(id=message_id, chat_id=chat.id).first()
    if not message:
        raise NotFoundError('Message not found')
    
    # Only author can delete (or chat admin)
    participant = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=current_user_id
    ).first()
    
    if message.user_id != current_user_id and participant.role != 'admin':
        raise AuthorizationError('You can only delete your own messages')
    
    message.is_deleted = True
    message.message = '[Message deleted]'
    
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'}), 200


@task_chat_bp.route('/tasks/<int:task_id>/chat/participants', methods=['GET'])
@token_required
def get_participants(task_id, current_user_id=None):
    """
    Get chat participants
    ---
    GET /api/tasks/1/chat/participants
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    chat = _get_chat_with_access(task_id, current_user_id)
    
    participants = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        is_active=True
    ).all()
    
    return jsonify({
        'participants': [p.to_dict() for p in participants],
        'total': len(participants)
    }), 200


@task_chat_bp.route('/tasks/<int:task_id>/chat/participants', methods=['POST'])
@token_required
def add_participant(task_id, current_user_id=None):
    """
    Add a participant to the chat
    ---
    POST /api/tasks/1/chat/participants
    Headers: Authorization: Bearer <token>
    Body: {"user_id": 2, "role": "member"}
    """
    # Verify access and admin role
    chat = _get_chat_with_access(task_id, current_user_id, require_admin=True)
    
    data = request.get_json()
    if not data or 'user_id' not in data:
        raise APIError('user_id is required', 400)
    
    user_id = data['user_id']
    role = data.get('role', 'member')
    
    if role not in ['admin', 'member', 'viewer']:
        raise APIError('Invalid role', 400)
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    
    # Check if already a participant
    existing = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=user_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise APIError('User is already a participant', 400)
        else:
            # Reactivate
            existing.is_active = True
            existing.role = role
            db.session.commit()
            return jsonify(existing.to_dict()), 200
    
    # Add new participant
    participant = ChatParticipant(
        chat_id=chat.id,
        user_id=user_id,
        role=role
    )
    
    db.session.add(participant)
    db.session.commit()
    
    return jsonify(participant.to_dict()), 201


@task_chat_bp.route('/tasks/<int:task_id>/chat/participants/<int:user_id>', methods=['DELETE'])
@token_required
def remove_participant(task_id, user_id, current_user_id=None):
    """
    Remove a participant from the chat
    ---
    DELETE /api/tasks/1/chat/participants/2
    Headers: Authorization: Bearer <token>
    """
    # Verify access and admin role
    chat = _get_chat_with_access(task_id, current_user_id, require_admin=True)
    
    participant = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=user_id
    ).first()
    
    if not participant:
        raise NotFoundError('Participant not found')
    
    participant.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Participant removed successfully'}), 200


# Helper functions

def _user_has_task_access(user_id, task):
    """Check if user has access to the task"""
    # Check if user has access to task
    if task.assignee_id == user_id or task.supervisor_id == user_id:
        return True
    
    # Check collaborators (may be stored as strings or objects)
    if hasattr(task, 'collaborators') and task.collaborators:
        for c in task.collaborators:
            if isinstance(c, str):
                try:
                    if int(c) == user_id:
                        return True
                except (ValueError, TypeError):
                    logger.debug(f"Exception handled: {str(e)}")
                    pass
            elif hasattr(c, 'id') and c.id == user_id:
                return True
    
    return False


def _get_chat_with_access(task_id, user_id, require_admin=False):
    """Get chat and verify user has access"""
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task not found')
    
    if not _user_has_task_access(user_id, task):
        raise AuthorizationError('You do not have access to this task')
    
    chat = TaskChat.query.filter_by(task_id=task_id).first()
    if not chat:
        raise NotFoundError('Chat not found')
    
    participant = ChatParticipant.query.filter_by(
        chat_id=chat.id,
        user_id=user_id,
        is_active=True
    ).first()
    
    if not participant:
        raise AuthorizationError('You are not a participant in this chat')
    
    if require_admin and participant.role != 'admin':
        raise AuthorizationError('Admin access required')
    
    return chat


def _add_task_participants_to_chat(chat, task):
    """Add all task participants to the chat"""
    participants_to_add = set()
    
    if task.assignee_id:
        participants_to_add.add(task.assignee_id)
    
    if task.supervisor_id:
        participants_to_add.add(task.supervisor_id)
    
    # Handle collaborators (may be stored as strings or objects)
    if hasattr(task, 'collaborators') and task.collaborators:
        for collaborator in task.collaborators:
            if isinstance(collaborator, str):
                try:
                    participants_to_add.add(int(collaborator))
                except (ValueError, TypeError):
                    logger.debug(f"Exception handled: {str(e)}")
                    pass
            elif hasattr(collaborator, 'id'):
                participants_to_add.add(collaborator.id)
    
    for user_id in participants_to_add:
        # Determine role
        role = 'admin' if user_id == task.supervisor_id else 'member'
        
        participant = ChatParticipant(
            chat_id=chat.id,
            user_id=user_id,
            role=role
        )
        db.session.add(participant)
    
    db.session.commit()

