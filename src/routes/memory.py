"""
Memory Management Routes
API endpoints for managing AI memory and context
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from src.middleware.auth import token_required
from src.services.ai_service import AIService
from src.utils.errors import APIError

memory_bp = Blueprint('memory', __name__)

def get_ai_service(current_user_id=None):
    """Get AI service instance"""
    return AIService()


@memory_bp.route('/history', methods=['GET'])
@token_required
def get_conversation_history(current_user_id=None):
    """Get conversation history"""
    try:
        user_id = current_user_id
        limit = request.args.get('limit', 20, type=int)
        session_id = request.args.get('session_id')
        
        ai_service = get_ai_service()
        history = ai_service.get_conversation_history(user_id, limit, session_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        raise APIError(f'Failed to get conversation history: {str(e)}', 500)


@memory_bp.route('/history/<session_id>', methods=['DELETE'])
@token_required
def clear_session_history(session_id):
    """Clear conversation history for a session"""
    try:
        user_id = current_user_id
        
        ai_service = get_ai_service()
        ai_service.clear_conversation_history(user_id, session_id)
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        }), 200
        
    except Exception as e:
        raise APIError(f'Failed to clear conversation history: {str(e)}', 500)


@memory_bp.route('/memories', methods=['GET'])
@token_required
def get_memories(current_user_id=None):
    """Get all user memories"""
    try:
        user_id = current_user_id
        
        ai_service = get_ai_service()
        memories = ai_service.get_user_memories(user_id)
        
        return jsonify({
            'success': True,
            'memories': memories
        }), 200
        
    except Exception as e:
        raise APIError(f'Failed to get memories: {str(e)}', 500)


@memory_bp.route('/memories', methods=['POST'])
@token_required
def save_memory(current_user_id=None):
    """Save a user memory"""
    try:
        user_id = current_user_id
        data = request.get_json()
        
        memory_type = data.get('memory_type')
        key = data.get('key')
        value = data.get('value')
        
        if not all([memory_type, key, value]):
            raise APIError('Missing required fields: memory_type, key, value', 400)
        
        if memory_type not in ['preference', 'pattern', 'insight', 'goal']:
            raise APIError('Invalid memory_type. Must be one of: preference, pattern, insight, goal', 400)
        
        ai_service = get_ai_service()
        memory = ai_service.save_user_memory(user_id, memory_type, key, value)
        
        return jsonify({
            'success': True,
            'message': 'Memory saved',
            'memory': memory.to_dict()
        }), 201
        
    except APIError:
        raise
    except Exception as e:
        raise APIError(f'Failed to save memory: {str(e)}', 500)


@memory_bp.route('/memories/<int:memory_id>', methods=['DELETE'])
@token_required
def delete_memory(memory_id):
    """Delete a specific memory"""
    try:
        user_id = current_user_id
        
        ai_service = get_ai_service()
        success = ai_service.memory_service.delete_memory(user_id, memory_id)
        
        if not success:
            raise APIError('Memory not found', 404)
        
        return jsonify({
            'success': True,
            'message': 'Memory deleted'
        }), 200
        
    except APIError:
        raise
    except Exception as e:
        raise APIError(f'Failed to delete memory: {str(e)}', 500)


@memory_bp.route('/stats', methods=['GET'])
@token_required
def get_memory_stats(current_user_id=None):
    """Get memory statistics"""
    try:
        user_id = current_user_id
        
        ai_service = get_ai_service()
        stats = ai_service.get_memory_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        raise APIError(f'Failed to get memory stats: {str(e)}', 500)


@memory_bp.route('/search', methods=['POST'])
@token_required
def search_memories(current_user_id=None):
    """Search memories by keyword"""
    try:
        user_id = current_user_id
        data = request.get_json()
        
        query = data.get('query')
        limit = data.get('limit', 10)
        
        if not query:
            raise APIError('Missing required field: query', 400)
        
        ai_service = get_ai_service()
        memories = ai_service.memory_service.search_memories(user_id, query, limit)
        
        return jsonify({
            'success': True,
            'memories': memories,
            'count': len(memories)
        }), 200
        
    except APIError:
        raise
    except Exception as e:
        raise APIError(f'Failed to search memories: {str(e)}', 500)


@memory_bp.route('/export', methods=['GET'])
@token_required
def export_memories(current_user_id=None):
    """Export all user data (GDPR compliance)"""
    try:
        user_id = current_user_id
        
        # Get all data
        ai_service = get_ai_service()
        memories = ai_service.get_user_memories(user_id)
        ai_service = get_ai_service()
        history = ai_service.get_conversation_history(user_id, limit=1000)
        ai_service = get_ai_service()
        stats = ai_service.get_memory_stats(user_id)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.utcnow().isoformat(),
            'memories': memories,
            'conversation_history': history,
            'statistics': stats
        }
        
        return jsonify({
            'success': True,
            'data': export_data
        }), 200
        
    except Exception as e:
        raise APIError(f'Failed to export data: {str(e)}', 500)


@memory_bp.route('/clear-all', methods=['DELETE'])
@token_required
def clear_all_data(current_user_id=None):
    """Clear all user memory data (GDPR right to be forgotten)"""
    try:
        user_id = current_user_id
        
        # Clear all conversations
        from src.models.models import db, ConversationHistory, UserMemory, ContextSummary
        
        ConversationHistory.query.filter_by(user_id=user_id).delete()
        UserMemory.query.filter_by(user_id=user_id).delete()
        ContextSummary.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All memory data cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        raise APIError(f'Failed to clear data: {str(e)}', 500)

