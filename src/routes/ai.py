"""
AI integration routes with proper error handling
"""
from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from src.middleware.auth import token_required
from src.utils.validation import validate_request, AIPromptSchema
from src.utils.errors import APIError
import logging

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)


def call_ollama_api(prompt, model=None, timeout=30):
    """
    Call Ollama API with error handling
    """
    api_url = current_app.config.get('AI_API_URL', 'http://localhost:11434/api/generate')
    ai_model = model or current_app.config.get('AI_MODEL', 'phi3')
    
    try:
        response = requests.post(
            api_url,
            json={
                "model": ai_model,
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.error(f'AI API timeout after {timeout}s')
        raise APIError('AI service timeout. Please try again.', 504)
    except requests.exceptions.ConnectionError:
        logger.error('Cannot connect to AI service')
        raise APIError('AI service unavailable. Please ensure Ollama is running.', 503)
    except requests.exceptions.RequestException as e:
        logger.error(f'AI API error: {str(e)}')
        raise APIError(f'AI service error: {str(e)}', 500)


@ai_bp.route('/chat', methods=['POST'])
@token_required
@validate_request(AIPromptSchema)
def chat_with_ai():
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
    
    try:
        # Call AI API
        ai_response = call_ollama_api(user_message)
        
        return jsonify({
            'message': ai_response.get('response', 'No response'),
            'model': ai_response.get('model', 'unknown'),
            'timestamp': ai_response.get('created_at', ''),
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'message': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/agents/<agent_name>', methods=['POST'])
@token_required
def execute_agent(agent_name):
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
    
    # Agent-specific prompts
    agent_prompts = {
        'benchmarking': f'''You are a benchmarking specialist. Analyze and compare the following data against industry standards. Provide specific metrics and recommendations.

Context: {context}

Please provide:
1. Key performance indicators
2. Industry comparisons
3. Recommendations for improvement''',
        
        'persona_generation': f'''You are an expert in creating detailed user personas. Generate a comprehensive persona based on the following information.

Context: {context}

Please provide:
1. Demographics
2. Goals and motivations
3. Pain points
4. Behavioral patterns''',
        
        'data_analysis': f'''You are a data analyst. Analyze the following data and provide actionable insights.

Context: {context}

Please provide:
1. Key findings
2. Trends and patterns
3. Statistical insights
4. Recommendations''',
        
        'report_writing': f'''You are a professional report writer. Create a comprehensive, well-structured report on the following topic.

Context: {context}

Please provide:
1. Executive summary
2. Detailed analysis
3. Conclusions
4. Recommendations'''
    }
    
    agent_key = agent_name.lower().replace(' ', '_')
    
    if agent_key not in agent_prompts:
        return jsonify({
            'error': f'Agent "{agent_name}" not found',
            'available_agents': list(agent_prompts.keys())
        }), 404
    
    prompt = agent_prompts[agent_key]
    
    try:
        # Call AI API
        ai_response = call_ollama_api(prompt, timeout=60)
        
        return jsonify({
            'agent': agent_name,
            'message': ai_response.get('response', ''),
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


@ai_bp.route('/summarize', methods=['POST'])
@token_required
def summarize_content():
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
    
    if not content or len(content) < 10:
        return jsonify({'error': 'Content is required and must be at least 10 characters'}), 400
    
    if len(content) > 50000:
        return jsonify({'error': 'Content is too long (max 50,000 characters)'}), 400
    
    prompt = f'''Please provide a concise summary of the following text. Focus on the main points and key takeaways.

Text to summarize:
{content}

Summary:'''
    
    try:
        ai_response = call_ollama_api(prompt, timeout=45)
        
        return jsonify({
            'original_length': len(content),
            'summary': ai_response.get('response', ''),
            'model': current_app.config.get('AI_MODEL', 'phi3'),
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'error': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_content():
    """
    Analyze content with AI
    ---
    POST /api/ai/analyze
    Headers: Authorization: Bearer <token>
    {
        "content": "Content to analyze...",
        "type": "sentiment"
    }
    """
    data = request.json or {}
    content = data.get('content', '')
    analysis_type = data.get('type', 'general')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    analysis_prompts = {
        'sentiment': f'Analyze the sentiment of the following text. Provide a detailed sentiment analysis including tone, emotions, and overall sentiment score:\n\n{content}',
        'general': f'Provide a comprehensive analysis of the following content:\n\n{content}',
        'technical': f'Provide a technical analysis of the following content, focusing on technical aspects and implementation details:\n\n{content}',
        'business': f'Provide a business analysis of the following content, focusing on business value, ROI, and strategic implications:\n\n{content}'
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts['general'])
    
    try:
        ai_response = call_ollama_api(prompt, timeout=45)
        
        return jsonify({
            'type': analysis_type,
            'analysis': ai_response.get('response', ''),
            'model': current_app.config.get('AI_MODEL', 'phi3'),
            'success': True
        }), 200
        
    except APIError as e:
        return jsonify({
            'error': e.message,
            'success': False
        }), e.status_code


@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """
    Check AI service health
    ---
    GET /api/ai/health
    """
    try:
        # Try a simple request
        response = requests.get(
            'http://localhost:11434/api/tags',
            timeout=5
        )
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                'status': 'healthy',
                'service': 'ollama',
                'available_models': [m.get('name') for m in models],
                'configured_model': current_app.config.get('AI_MODEL', 'phi3')
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Ollama service returned non-200 status'
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Please ensure Ollama is running'
        }), 503

