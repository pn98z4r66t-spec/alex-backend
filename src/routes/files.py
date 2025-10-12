"""
File Storage Routes
Handles file upload, download, preview, and AI integration
"""
from flask import Blueprint, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import mimetypes
import hashlib
from datetime import datetime
from pathlib import Path
import magic  # python-magic for file type detection
from PIL import Image
import PyPDF2
import docx
import json

from ..models.models import db, File, User
from ..middleware.auth import token_required, optional_token
from ..utils.validation import validate_request, FileUploadSchema
from ..utils.errors import APIError

files_bp = Blueprint('files', __name__)

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB default
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'md', 'rtf'},
    'spreadsheets': {'xls', 'xlsx', 'csv'},
    'presentations': {'ppt', 'pptx'},
    'archives': {'zip', 'tar', 'gz', 'rar'},
    'code': {'py', 'js', 'html', 'css', 'json', 'xml', 'yaml', 'yml'},
    'media': {'mp3', 'mp4', 'wav', 'avi', 'mov'}
}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'thumbnails'), exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return any(ext in exts for exts in ALLOWED_EXTENSIONS.values())


def get_file_category(filename):
    """Determine file category based on extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'other'


def calculate_file_hash(file_path):
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_thumbnail(file_path, thumbnail_path, size=(200, 200)):
    """Generate thumbnail for image files"""
    try:
        with Image.open(file_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'PNG')
            return True
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return False


def extract_text_from_file(file_path, file_type):
    """Extract text content from various file types for AI processing"""
    try:
        if file_type == 'pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
                return text[:10000]  # Limit to first 10k chars
        
        elif file_type in ['doc', 'docx']:
            doc = docx.Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text[:10000]
        
        elif file_type in ['txt', 'md', 'json', 'xml', 'yaml', 'yml', 'py', 'js', 'html', 'css']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:10000]
        
        return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


@files_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """Upload a file to the server"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            raise APIError('No file provided', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            raise APIError('No file selected', 400)
        
        if not allowed_file(file.filename):
            raise APIError('File type not allowed', 400)
        
        # Get optional metadata
        description = request.form.get('description', '')
        task_id = request.form.get('task_id')
        is_public = request.form.get('is_public', 'false').lower() == 'true'
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}_{current_user.id}{ext}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            raise APIError(f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB', 400)
        
        file_hash = calculate_file_hash(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        category = get_file_category(filename)
        
        # Generate thumbnail for images
        thumbnail_path = None
        if category == 'images':
            thumbnail_filename = f"thumb_{unique_filename}.png"
            thumbnail_full_path = os.path.join(UPLOAD_FOLDER, 'thumbnails', thumbnail_filename)
            if generate_thumbnail(file_path, thumbnail_full_path):
                thumbnail_path = f"thumbnails/{thumbnail_filename}"
        
        # Extract text for AI processing
        extracted_text = extract_text_from_file(file_path, ext[1:])
        
        # Create database record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=unique_filename,
            file_size=file_size,
            mime_type=mime_type,
            file_hash=file_hash,
            category=category,
            thumbnail_path=thumbnail_path,
            description=description,
            extracted_text=extracted_text,
            uploaded_by=current_user.id,
            task_id=int(task_id) if task_id else None,
            is_public=is_public
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_record.to_dict()
        }), 201
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error uploading file: {str(e)}', 500)


@files_bp.route('/list', methods=['GET'])
@token_required
def list_files(current_user):
    """List all files accessible to the user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        task_id = request.args.get('task_id', type=int)
        search = request.args.get('search')
        
        # Base query - user's files or public files
        query = File.query.filter(
            (File.uploaded_by == current_user.id) | (File.is_public == True)
        )
        
        # Apply filters
        if category:
            query = query.filter(File.category == category)
        
        if task_id:
            query = query.filter(File.task_id == task_id)
        
        if search:
            query = query.filter(
                (File.filename.ilike(f'%{search}%')) |
                (File.description.ilike(f'%{search}%'))
            )
        
        # Order by most recent
        query = query.order_by(File.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'files': [f.to_dict() for f in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        raise APIError(f'Error listing files: {str(e)}', 500)


@files_bp.route('/<int:file_id>', methods=['GET'])
@optional_token
def get_file_info(file_id, current_user=None):
    """Get file information"""
    try:
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and (not current_user or file.uploaded_by != current_user.id):
            raise APIError('Access denied', 403)
        
        return jsonify(file.to_dict(include_uploader=True)), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error getting file info: {str(e)}', 500)


@files_bp.route('/download/<int:file_id>', methods=['GET'])
@optional_token
def download_file(file_id, current_user=None):
    """Download a file"""
    try:
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and (not current_user or file.uploaded_by != current_user.id):
            raise APIError('Access denied', 403)
        
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(file_path):
            raise APIError('File not found on server', 404)
        
        # Update download count
        file.download_count += 1
        file.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file.original_filename,
            mimetype=file.mime_type
        )
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error downloading file: {str(e)}', 500)


@files_bp.route('/preview/<int:file_id>', methods=['GET'])
@optional_token
def preview_file(file_id, current_user=None):
    """Preview a file (inline display)"""
    try:
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access permissions
        if not file.is_public and (not current_user or file.uploaded_by != current_user.id):
            raise APIError('Access denied', 403)
        
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(file_path):
            raise APIError('File not found on server', 404)
        
        # Update access tracking
        file.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return send_file(
            file_path,
            mimetype=file.mime_type
        )
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error previewing file: {str(e)}', 500)


@files_bp.route('/thumbnail/<int:file_id>', methods=['GET'])
def get_thumbnail(file_id):
    """Get file thumbnail"""
    try:
        file = File.query.get(file_id)
        
        if not file or not file.thumbnail_path:
            raise APIError('Thumbnail not found', 404)
        
        thumbnail_path = os.path.join(UPLOAD_FOLDER, file.thumbnail_path)
        
        if not os.path.exists(thumbnail_path):
            raise APIError('Thumbnail not found on server', 404)
        
        return send_file(thumbnail_path, mimetype='image/png')
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error getting thumbnail: {str(e)}', 500)


@files_bp.route('/<int:file_id>', methods=['DELETE'])
@token_required
def delete_file(file_id, current_user):
    """Delete a file"""
    try:
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check permissions
        if file.uploaded_by != current_user.id:
            raise APIError('You do not have permission to delete this file', 403)
        
        # Delete physical file
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete thumbnail if exists
        if file.thumbnail_path:
            thumbnail_path = os.path.join(UPLOAD_FOLDER, file.thumbnail_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error deleting file: {str(e)}', 500)


@files_bp.route('/<int:file_id>/ai-analyze', methods=['POST'])
@token_required
def ai_analyze_file(file_id, current_user):
    """Use AI to analyze file content"""
    try:
        file = File.query.get(file_id)
        
        if not file:
            raise APIError('File not found', 404)
        
        # Check access
        if not file.is_public and file.uploaded_by != current_user.id:
            raise APIError('Access denied', 403)
        
        if not file.extracted_text:
            raise APIError('File content cannot be analyzed (no text extracted)', 400)
        
        # Get analysis type from request
        data = request.get_json() or {}
        analysis_type = data.get('type', 'summary')  # summary, keywords, sentiment, etc.
        
        # Prepare AI request
        import requests
        ai_api_url = os.getenv('AI_API_URL', 'http://localhost:11434/api/generate')
        ai_model = os.getenv('AI_MODEL', 'phi3')
        
        prompts = {
            'summary': f"Summarize the following document in 3-5 sentences:\n\n{file.extracted_text}",
            'keywords': f"Extract the top 10 keywords from this document:\n\n{file.extracted_text}",
            'sentiment': f"Analyze the sentiment and tone of this document:\n\n{file.extracted_text}",
            'questions': f"Generate 5 important questions that this document answers:\n\n{file.extracted_text}"
        }
        
        prompt = prompts.get(analysis_type, prompts['summary'])
        
        # Call AI API
        response = requests.post(
            ai_api_url,
            json={'model': ai_model, 'prompt': prompt, 'stream': False},
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json().get('response', 'No response from AI')
        else:
            ai_response = f"AI analysis unavailable (using fallback)"
        
        return jsonify({
            'file_id': file_id,
            'filename': file.filename,
            'analysis_type': analysis_type,
            'result': ai_response
        }), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error analyzing file: {str(e)}', 500)


@files_bp.route('/bulk-upload', methods=['POST'])
@token_required
def bulk_upload(current_user):
    """Upload multiple files at once"""
    try:
        if 'files' not in request.files:
            raise APIError('No files provided', 400)
        
        files = request.files.getlist('files')
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                if file.filename == '' or not allowed_file(file.filename):
                    errors.append(f"{file.filename}: Invalid file")
                    continue
                
                # Process each file (similar to single upload)
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}_{current_user.id}{ext}"
                
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                
                file_size = os.path.getsize(file_path)
                if file_size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    errors.append(f"{filename}: File too large")
                    continue
                
                file_hash = calculate_file_hash(file_path)
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                category = get_file_category(filename)
                
                file_record = File(
                    filename=filename,
                    original_filename=file.filename,
                    file_path=unique_filename,
                    file_size=file_size,
                    mime_type=mime_type,
                    file_hash=file_hash,
                    category=category,
                    uploaded_by=current_user.id
                )
                
                db.session.add(file_record)
                uploaded_files.append(file_record.to_dict())
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Uploaded {len(uploaded_files)} files',
            'files': uploaded_files,
            'errors': errors
        }), 201
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error in bulk upload: {str(e)}', 500)

