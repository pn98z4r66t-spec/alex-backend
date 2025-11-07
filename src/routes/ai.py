"""
AI integration routes - Refactored to use AIService
"""
from flask import Blueprint, request, jsonify
from src.middleware.auth import token_required
from src.utils.validation import validate_request, AIPromptSchema
from src.utils.errors import APIError
from src.services.ai_service import get_ai_service
import logging

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/chat', methods=['POST'])
@token_required
@validate_request(AIPromptSchema)
def chat_with_ai(current_user_id=None):
    """
    Chat with AI assistant
    ---
    POST /api/ai/chat
    Headers: Authorization: Bearer <token>
    {
        "message": "Hello, how can you help me?"
    }
    """
    data = request.validated_data
    user_message = data.get('message', '')
    session_id = data.get('session_id')  # Optional session ID for conversation continuity
    
    try:
        ai_service = get_ai_service()
        
        # Use memory-aware chat if user is authenticated
        if current_user_id:
            response = ai_service.chat_with_memory(
                user_id=current_user_id,
                message=user_message,
                session_id=session_id
            )
        else:
            # Fallback to regular chat without memory
            response = ai_service.chat(user_message)
        
        return jsonify({
            'message': response.get('message', response.get('response', '')),
            'model': response.get('model', 'unknown'),
            'provider': response.get('provider', 'unknown'),
            'session_id': session_id,
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'message': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/agents/<agent_name>', methods=['POST'])
@token_required
def execute_agent(agent_name, current_user_id=None):
    """
    Execute specialized AI agent
    ---
    POST /api/ai/agents/benchmarking
    Headers: Authorization: Bearer <token>
    {
        "context": "Compare our Q4 performance..."
    }
    """
    data = request.json or {}
    context = data.get('context', '')
    
    if not context:
        return jsonify({'error': 'Context is required'}), 400
    
    try:
        ai_service = get_ai_service()
        response = ai_service.execute_agent(agent_name, context)
        
        return jsonify({
            'agent': agent_name,
            'message': response.get('response', ''),
            'model': response.get('model', 'unknown'),
            'status': 'completed',
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'agent': agent_name,
            'message': e.message,
            'status': 'error',
            'success': False
        }), e.status_code


@ai_bp.route('/agents', methods=['GET'])
@token_required
def list_agents(current_user_id=None):
    """
    List available AI agents
    ---
    GET /api/ai/agents
    Headers: Authorization: Bearer <token>
    """
    try:
        ai_service = get_ai_service()
        agents = ai_service.get_available_agents()
        
        return jsonify({
            'agents': agents,
            'count': len(agents),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f'Error listing agents: {str(e)}')
        return jsonify({
            'error': 'Failed to list agents',
            'success': False
        }), 500


@ai_bp.route('/summarize', methods=['POST'])
@token_required
def summarize_content(current_user_id=None):
    """
    Summarize text content
    ---
    POST /api/ai/summarize
    Headers: Authorization: Bearer <token>
    {
        "content": "Long text to summarize..."
    }
    """
    data = request.json or {}
    content = data.get('content', '')
    
    try:
        ai_service = get_ai_service()
        response = ai_service.summarize(content)
        
        return jsonify({
            'summary': response.get('response', ''),
            'model': response.get('model', 'unknown'),
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'error': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_content(current_user_id=None):
    """
    Analyze content
    ---
    POST /api/ai/analyze
    Headers: Authorization: Bearer <token>
    {
        "content": "Content to analyze..."
    }
    """
    data = request.json or {}
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    try:
        ai_service = get_ai_service()
        response = ai_service.analyze(content)
        
        return jsonify({
            'analysis': response.get('response', ''),
            'model': response.get('model', 'unknown'),
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'error': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/status', methods=['GET'])
@token_required
def ai_status(current_user_id=None):
    """
    Get AI service status
    ---
    GET /api/ai/status
    Headers: Authorization: Bearer <token>
    """
    try:
        ai_service = get_ai_service()
        is_available = ai_service.is_available()
        cache_stats = ai_service.get_cache_stats()
        
        return jsonify({
            'available': is_available,
            'provider': ai_service.provider_name,
            'cache': cache_stats,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f'Error checking AI status: {str(e)}')
        return jsonify({
            'available': False,
            'error': str(e),
            'success': False
        }), 500


@ai_bp.route('/cache/clear', methods=['POST'])
@token_required
def clear_cache(current_user_id=None):
    """
    Clear AI response cache
    ---
    POST /api/ai/cache/clear
    Headers: Authorization: Bearer <token>
    """
    try:
        ai_service = get_ai_service()
        ai_service.clear_cache()
        
        return jsonify({
            'message': 'Cache cleared successfully',
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f'Error clearing cache: {str(e)}')
        return jsonify({
            'error': 'Failed to clear cache',
            'success': False
        }), 500

