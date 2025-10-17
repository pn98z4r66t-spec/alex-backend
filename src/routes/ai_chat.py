"""
AI Assistant Chat Routes
Handles private 1-to-1 chat with AI assistant that can read group chat history
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
import os
import requests
import time

from ..models.models import db, User, Task
from ..models.chat_models import AIChat, AIChatMessage, TaskChat, ChatMessage
from ..middleware.auth import token_required
from ..utils.errors import APIError, NotFoundError, AuthorizationError
from ..utils.validation import sanitize_string

ai_chat_bp = Blueprint('ai_chat', __name__)


@ai_chat_bp.route('/tasks/<int:task_id>/ai-chat', methods=['POST', 'GET'])
@token_required
def get_or_create_ai_chat(task_id, current_user_id=None):
    """
    Get or create AI chat for a task
    ---
    POST/GET /api/tasks/1/ai-chat
    Headers: Authorization: Bearer <token>
    """
    # Verify task exists and user has access
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task not found')
    
    if not _user_has_task_access(current_user_id, task):
        raise AuthorizationError('You do not have access to this task')
    
    # Get or create AI chat
    ai_chat = AIChat.query.filter_by(
        user_id=current_user_id,
        task_id=task_id
    ).first()
    
    if not ai_chat:
        # Create new AI chat
        ai_chat = AIChat(
            user_id=current_user_id,
            task_id=task_id
        )
        db.session.add(ai_chat)
        db.session.commit()
        
        # Add welcome message
        welcome_msg = AIChatMessage(
            ai_chat_id=ai_chat.id,
            role='system',
            message=f'AI Assistant initialized for task: {task.title}. I can help you with this task and have access to the group chat history.'
        )
        db.session.add(welcome_msg)
        db.session.commit()
    
    return jsonify(ai_chat.to_dict()), 200


@ai_chat_bp.route('/tasks/<int:task_id>/ai-chat/messages', methods=['GET'])
@token_required
def get_ai_messages(task_id, current_user_id=None):
    """
    Get AI chat message history
    ---
    GET /api/tasks/1/ai-chat/messages?limit=50
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    ai_chat = _get_ai_chat_with_access(task_id, current_user_id)
    
    limit = min(request.args.get('limit', 50, type=int), 200)
    
    messages = AIChatMessage.query.filter_by(
        ai_chat_id=ai_chat.id
    ).order_by(AIChatMessage.created_at.asc()).limit(limit).all()
    
    return jsonify({
        'messages': [msg.to_dict() for msg in messages],
        'total': len(messages)
    }), 200


@ai_chat_bp.route('/tasks/<int:task_id>/ai-chat/messages', methods=['POST'])
@token_required
def send_ai_message(task_id, current_user_id=None):
    """
    Send a message to the AI assistant
    ---
    POST /api/tasks/1/ai-chat/messages
    Headers: Authorization: Bearer <token>
    Body: {
        "message": "Can you summarize the group chat?",
        "include_group_context": true
    }
    """
    # Verify access
    ai_chat = _get_ai_chat_with_access(task_id, current_user_id)
    
    data = request.get_json()
    if not data or 'message' not in data:
        raise APIError('Message is required', 400)
    
    user_message = sanitize_string(data['message'])
    if not user_message or len(user_message.strip()) == 0:
        raise APIError('Message cannot be empty', 400)
    
    if len(user_message) > 5000:
        raise APIError('Message too long (max 5000 characters)', 400)
    
    include_group_context = data.get('include_group_context', True)
    
    # Save user message
    user_msg = AIChatMessage(
        ai_chat_id=ai_chat.id,
        role='user',
        message=user_message
    )
    db.session.add(user_msg)
    db.session.commit()
    
    # Get group chat context if requested
    group_context = None
    if include_group_context:
        group_context = _get_group_chat_context(task_id)
    
    # Build conversation history for AI
    conversation_history = _build_conversation_history(ai_chat)
    
    # Call AI API
    start_time = time.time()
    ai_response, model_used, tokens = _call_ai_with_context(
        user_message,
        conversation_history,
        group_context,
        ai_chat.task
    )
    response_time = time.time() - start_time
    
    # Save AI response
    ai_msg = AIChatMessage(
        ai_chat_id=ai_chat.id,
        role='assistant',
        message=ai_response,
        model=model_used,
        tokens_used=tokens,
        response_time=response_time,
        group_chat_context=group_context
    )
    db.session.add(ai_msg)
    
    # Update AI chat
    ai_chat.updated_at = datetime.utcnow()
    if group_context:
        ai_chat.last_sync_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'user_message': user_msg.to_dict(),
        'ai_response': ai_msg.to_dict()
    }), 201


@ai_chat_bp.route('/tasks/<int:task_id>/ai-chat/sync', methods=['POST'])
@token_required
def sync_group_context(task_id, current_user_id=None):
    """
    Manually sync group chat context for AI
    ---
    POST /api/tasks/1/ai-chat/sync
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    ai_chat = _get_ai_chat_with_access(task_id, current_user_id)
    
    # Get group chat context
    group_context = _get_group_chat_context(task_id)
    
    if not group_context:
        return jsonify({
            'message': 'No group chat messages to sync',
            'synced': False
        }), 200
    
    # Generate summary
    summary = _generate_context_summary(group_context)
    
    ai_chat.context_summary = summary
    ai_chat.last_sync_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Group chat context synced successfully',
        'synced': True,
        'message_count': len(group_context.get('messages', [])),
        'last_sync_at': ai_chat.last_sync_at.isoformat()
    }), 200


@ai_chat_bp.route('/tasks/<int:task_id>/ai-chat/context', methods=['GET'])
@token_required
def get_ai_context(task_id, current_user_id=None):
    """
    Get AI's understanding of the group chat
    ---
    GET /api/tasks/1/ai-chat/context
    Headers: Authorization: Bearer <token>
    """
    # Verify access
    ai_chat = _get_ai_chat_with_access(task_id, current_user_id)
    
    group_context = _get_group_chat_context(task_id)
    
    return jsonify({
        'context_summary': ai_chat.context_summary,
        'last_sync_at': ai_chat.last_sync_at.isoformat() if ai_chat.last_sync_at else None,
        'group_message_count': len(group_context.get('messages', [])) if group_context else 0,
        'has_context': bool(group_context)
    }), 200


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


def _get_ai_chat_with_access(task_id, user_id):
    """Get AI chat and verify user has access"""
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task not found')
    
    if not _user_has_task_access(user_id, task):
        raise AuthorizationError('You do not have access to this task')
    
    ai_chat = AIChat.query.filter_by(
        user_id=user_id,
        task_id=task_id
    ).first()
    
    if not ai_chat:
        raise NotFoundError('AI chat not found. Create one first.')
    
    return ai_chat


def _get_group_chat_context(task_id, limit=50):
    """Get recent group chat messages for context"""
    task_chat = TaskChat.query.filter_by(task_id=task_id).first()
    
    if not task_chat:
        return None
    
    messages = ChatMessage.query.filter_by(
        chat_id=task_chat.id,
        is_deleted=False
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    if not messages:
        return None
    
    return {
        'chat_id': task_chat.id,
        'message_count': len(messages),
        'messages': [
            {
                'id': msg.id,
                'user': msg.user.name if msg.user else 'Unknown',
                'message': msg.message,
                'created_at': msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in reversed(messages)  # Chronological order
        ]
    }


def _build_conversation_history(ai_chat, limit=10):
    """Build conversation history for AI context"""
    messages = AIChatMessage.query.filter_by(
        ai_chat_id=ai_chat.id
    ).order_by(AIChatMessage.created_at.desc()).limit(limit).all()
    
    return [
        {
            'role': msg.role,
            'content': msg.message
        }
        for msg in reversed(messages)
    ]


def _generate_context_summary(group_context):
    """Generate a summary of group chat context"""
    if not group_context or not group_context.get('messages'):
        return None
    
    messages = group_context['messages']
    summary_parts = []
    
    summary_parts.append(f"Group chat has {len(messages)} recent messages.")
    
    # Get unique participants
    participants = set(msg['user'] for msg in messages)
    summary_parts.append(f"Participants: {', '.join(participants)}")
    
    # Get recent topics (simple keyword extraction)
    recent_messages = messages[-5:] if len(messages) > 5 else messages
    summary_parts.append(f"Recent discussion: {' | '.join([msg['message'][:50] + '...' if len(msg['message']) > 50 else msg['message'] for msg in recent_messages])}")
    
    return ' '.join(summary_parts)


def _call_ai_with_context(user_message, conversation_history, group_context, task):
    """Call AI API with full context"""
    ai_api_url = os.getenv('AI_API_URL', 'http://localhost:11434/api/generate')
    ai_model = os.getenv('AI_MODEL', 'phi3')
    
    # Build system prompt with context
    system_prompt = f"""You are an AI assistant helping with the task: "{task.title}".
Task description: {task.description or 'No description provided'}
Task status: {task.status}
"""
    
    if group_context:
        system_prompt += f"\n\nGroup Chat Context ({group_context['message_count']} messages):\n"
        for msg in group_context['messages'][-10:]:  # Last 10 messages
            system_prompt += f"- {msg['user']}: {msg['message']}\n"
    
    system_prompt += "\nProvide helpful, context-aware assistance based on the task and group chat history."
    
    # Build full prompt
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
    
    try:
        response = requests.post(
            ai_api_url,
            json={
                'model': ai_model,
                'prompt': full_prompt,
                'stream': False
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        ai_response = result.get('response', 'No response from AI')
        
        # Estimate tokens (rough approximation)
        tokens = len(full_prompt.split()) + len(ai_response.split())
        
        return ai_response, ai_model, tokens
        
    except requests.exceptions.Timeout:
        return "AI service timed out. Please try again.", ai_model, 0
    except requests.exceptions.ConnectionError:
        return "AI service unavailable. Please ensure Ollama is running.", ai_model, 0
    except requests.exceptions.HTTPError as e:
        return f"AI service error: {e.response.status_code}", ai_model, 0
    except requests.exceptions.RequestException as e:
        return f"AI request failed: {str(e)}", ai_model, 0

