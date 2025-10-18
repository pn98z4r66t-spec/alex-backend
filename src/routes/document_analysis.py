"""
Document Analysis Routes
Advanced document parsing and AI-powered analysis
"""
from flask import Blueprint, request, jsonify
import os
import logging

from ..models.models import db, File
from ..middleware.auth import token_required
from ..utils.errors import APIError
from ..services.document_parsers import DocumentParserService
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

document_analysis_bp = Blueprint('document_analysis', __name__)

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')


@document_analysis_bp.route('/parse/<int:file_id>', methods=['POST'])
@token_required
def parse_document(file_id, current_user_id=None):
    """
    Parse a document and extract structured content
    
    POST /api/documents/parse/<file_id>
    
    Returns:
        - Full parsed content
        - Metadata
        - Statistics
        - Summary
    """
    try:
        # Get file from database
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and file.uploaded_by != current_user_id:
            raise APIError('Access denied', 403)
        
        # Get file path
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(file_path):
            raise APIError('File not found on server', 404)
        
        # Parse the document
        parsed_data = DocumentParserService.parse_document(file_path)
        
        if not parsed_data.get('success'):
            raise APIError(
                f"Failed to parse document: {parsed_data.get('error', 'Unknown error')}",
                400
            )
        
        # Update file record with extracted text if not already set
        if not file.extracted_text and parsed_data.get('text'):
            file.extracted_text = parsed_data['text'][:10000]  # Store first 10k chars
            db.session.commit()
        
        return jsonify({
            'file_id': file_id,
            'filename': file.filename,
            'file_type': parsed_data.get('file_type'),
            'summary': parsed_data.get('summary'),
            'metadata': parsed_data.get('metadata', {}),
            'statistics': parsed_data.get('statistics', {}),
            'content_preview': parsed_data.get('text', '')[:500],  # First 500 chars
            'full_content_length': len(parsed_data.get('text', '')),
            'parsed_successfully': True
        }), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error parsing document: {e}")
        raise APIError(f'Error parsing document: {str(e)}', 500)


@document_analysis_bp.route('/analyze/<int:file_id>', methods=['POST'])
@token_required
def analyze_document_with_ai(file_id, current_user_id=None):
    """
    Analyze document content using AI
    
    POST /api/documents/analyze/<file_id>
    {
        "analysis_type": "summary|keywords|questions|custom",
        "custom_prompt": "optional custom prompt"
    }
    
    Returns:
        AI-generated analysis of the document
    """
    try:
        # Get file from database
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and file.uploaded_by != current_user_id:
            raise APIError('Access denied', 403)
        
        # Get file path
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(file_path):
            raise APIError('File not found on server', 404)
        
        # Parse the document first
        parsed_data = DocumentParserService.parse_document(file_path)
        
        if not parsed_data.get('success'):
            raise APIError(
                f"Failed to parse document: {parsed_data.get('error', 'Unknown error')}",
                400
            )
        
        # Get analysis parameters
        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'summary')
        custom_prompt = data.get('custom_prompt')
        
        # Generate AI context from parsed document
        document_context = DocumentParserService.get_ai_context(parsed_data, max_length=8000)
        
        # Prepare AI prompts
        prompts = {
            'summary': f"Please provide a comprehensive summary of this document:\n\n{document_context}",
            'keywords': f"Extract and list the key topics, concepts, and keywords from this document:\n\n{document_context}",
            'questions': f"Generate 5-7 important questions that this document answers or addresses:\n\n{document_context}",
            'insights': f"Analyze this document and provide key insights, main points, and important takeaways:\n\n{document_context}",
            'action_items': f"Identify any action items, tasks, or recommendations mentioned in this document:\n\n{document_context}"
        }
        
        # Use custom prompt if provided
        if analysis_type == 'custom' and custom_prompt:
            prompt = f"{custom_prompt}\n\nDocument content:\n{document_context}"
        else:
            prompt = prompts.get(analysis_type, prompts['summary'])
        
        # Call AI service
        ai_service = AIService()
        ai_response = ai_service.generate_response(prompt)
        
        return jsonify({
            'file_id': file_id,
            'filename': file.filename,
            'file_type': parsed_data.get('file_type'),
            'analysis_type': analysis_type,
            'document_summary': parsed_data.get('summary'),
            'ai_analysis': ai_response,
            'metadata': parsed_data.get('metadata', {}),
            'statistics': parsed_data.get('statistics', {})
        }), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error analyzing document with AI: {e}")
        raise APIError(f'Error analyzing document: {str(e)}', 500)


@document_analysis_bp.route('/chat/<int:file_id>', methods=['POST'])
@token_required
def chat_about_document(file_id, current_user_id=None):
    """
    Have a conversation with AI about a specific document
    
    POST /api/documents/chat/<file_id>
    {
        "message": "What are the main findings in this document?",
        "conversation_history": []  # optional
    }
    
    Returns:
        AI response with document context
    """
    try:
        # Get file from database
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and file.uploaded_by != current_user_id:
            raise APIError('Access denied', 403)
        
        # Get file path
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(file_path):
            raise APIError('File not found on server', 404)
        
        # Parse the document
        parsed_data = DocumentParserService.parse_document(file_path)
        
        if not parsed_data.get('success'):
            raise APIError(
                f"Failed to parse document: {parsed_data.get('error', 'Unknown error')}",
                400
            )
        
        # Get chat parameters
        data = request.get_json()
        if not data or 'message' not in data:
            raise APIError('Message is required', 400)
        
        user_message = data['message']
        conversation_history = data.get('conversation_history', [])
        
        # Generate AI context from document
        document_context = DocumentParserService.get_ai_context(parsed_data, max_length=6000)
        
        # Build conversation prompt
        system_prompt = f"""You are an AI assistant helping analyze and discuss a document.

Document Information:
{parsed_data.get('summary', 'No summary available')}

Document Content:
{document_context}

Please answer questions about this document accurately and helpfully. If the answer is not in the document, say so."""
        
        # Build conversation with history
        conversation = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        for msg in conversation_history[-5:]:  # Last 5 messages
            conversation.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        # Add current user message
        conversation.append({"role": "user", "content": user_message})
        
        # Call AI service
        ai_service = AIService()
        ai_response = ai_service.chat(conversation)
        
        return jsonify({
            'file_id': file_id,
            'filename': file.filename,
            'message': user_message,
            'response': ai_response,
            'document_info': {
                'type': parsed_data.get('file_type'),
                'summary': parsed_data.get('summary'),
                'statistics': parsed_data.get('statistics', {})
            }
        }), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error in document chat: {e}")
        raise APIError(f'Error in document chat: {str(e)}', 500)


@document_analysis_bp.route('/supported-types', methods=['GET'])
def get_supported_types():
    """
    Get list of supported document types
    
    GET /api/documents/supported-types
    
    Returns:
        List of supported file extensions and descriptions
    """
    try:
        supported_types = DocumentParserService.get_supported_types()
        
        type_info = []
        for ext in supported_types:
            type_info.append({
                'extension': ext,
                'description': DocumentParserService.get_file_type_description(ext)
            })
        
        return jsonify({
            'supported_types': type_info,
            'count': len(type_info)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting supported types: {e}")
        raise APIError(f'Error getting supported types: {str(e)}', 500)

