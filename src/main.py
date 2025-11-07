"""
Alex Backend - Main Application
Improved version with security, authentication, and error handling
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.config.config import config
from src.config.env_validator import validate_environment
from src.models.models import db, User, Task, Email, ReferenceFile, Message
from src.routes.auth import auth_bp
from src.routes.tasks import tasks_bp
from src.routes.ai import ai_bp
from src.routes.task_sharing import task_sharing_bp
from src.routes.task_instance import task_instance_bp
from src.routes.files import files_bp
from src.routes.email import email_bp
from src.routes.team import team_bp
from src.routes.task_chat import task_chat_bp
from src.routes.ai_chat import ai_chat_bp
from src.routes.users import users_bp
from src.routes.document_analysis import document_analysis_bp
from src.routes.memory import memory_bp
from src.utils.errors import register_error_handlers
from src.middleware.security import register_security_middleware


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Validate environment variables
    if config_name == 'production':
        validate_environment('production')
    else:
        validate_environment('development')
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup CORS with restrictions
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # Setup JWT
    jwt = JWTManager(app)
    
    # Setup rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register security middleware
    register_security_middleware(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(task_sharing_bp, url_prefix='/api/tasks')
    
    app.register_blueprint(task_instance_bp, url_prefix="/api")
    app.register_blueprint(files_bp, url_prefix="/api/files")
    app.register_blueprint(email_bp, url_prefix="/api")
    app.register_blueprint(team_bp, url_prefix="/api")
    app.register_blueprint(task_chat_bp, url_prefix="/api")
    app.register_blueprint(ai_chat_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(document_analysis_bp, url_prefix="/api/documents")
    app.register_blueprint(memory_bp, url_prefix="/api/memory")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'alex-backend',
            'version': '2.0.0'
        }), 200
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': 'Alex Workspace API',
            'version': '2.0.0',
            'description': 'AI-powered workspace backend with authentication',
            'endpoints': {
                'auth': '/api/auth',
                'tasks': '/api/tasks',
                'ai': '/api/ai',
                'health': '/health'
            },
            'documentation': '/api/docs'  # Add Swagger docs later
        }), 200
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT tokens"""
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please refresh your token'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid JWT tokens"""
        return jsonify({
            'error': 'Invalid token',
            'message': 'Please provide a valid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing JWT tokens"""
        return jsonify({
            'error': 'Missing authorization token',
            'message': 'Please provide an access token'
        }), 401
    
    # Initialize database
    with app.app_context():
        db.create_all()
        seed_database()
    
    return app


def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Alex Backend startup')


def seed_database():
    """Seed database with initial data"""
    from datetime import datetime, timedelta
    
    # Check if already seeded
    if User.query.count() > 0:
        return
    
    print("Seeding database...")
    
    # Create users
    users_data = [
        {'name': 'Admin User', 'email': 'admin@alex.local', 'password': 'admin123', 'role': 'Manager'},
        {'name': 'Sarah Johnson', 'email': 'sarah.j@alex.local', 'password': 'password123', 'role': 'Manager'},
        {'name': 'Mike Chen', 'email': 'mike.c@alex.local', 'password': 'password123', 'role': 'Developer'},
        {'name': 'Anna Smith', 'email': 'anna.s@alex.local', 'password': 'password123', 'role': 'Designer'},
        {'name': 'John Davis', 'email': 'john.d@alex.local', 'password': 'password123', 'role': 'Analyst'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            role=user_data['role'],
            online=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    
    # Create tasks
    tasks_data = [
        {
            'title': 'Complete Q4 Financial Report',
            'description': 'Prepare comprehensive financial report for Q4',
            'status': 'in-progress',
            'urgent': True,
            'deadline': datetime.utcnow() + timedelta(hours=5),
            'assignee_id': 1,
            'supervisor_id': 2,
            'collaborators': '3,4'
        },
        {
            'title': 'Review Marketing Campaign',
            'description': 'Review and approve new marketing materials',
            'status': 'todo',
            'urgent': False,
            'deadline': datetime.utcnow() + timedelta(days=1),
            'assignee_id': 3,
            'supervisor_id': 2,
            'collaborators': '1'
        },
        {
            'title': 'Client Presentation Prep',
            'description': 'Prepare slides for client meeting',
            'status': 'in-progress',
            'urgent': True,
            'deadline': datetime.utcnow() + timedelta(hours=3),
            'assignee_id': 4,
            'supervisor_id': 2,
            'collaborators': '1,3'
        },
    ]
    
    for task_data in tasks_data:
        task = Task(**task_data)
        db.session.add(task)
    
    # Create emails
    emails_data = [
        {
            'sender': 'john.smith@client.com',
            'subject': 'Q4 Budget Review',
            'body': 'Please review the attached Q4 budget proposal.',
            'priority': 'priority',
            'user_id': 1
        },
        {
            'sender': 'newsletter@company.com',
            'subject': 'Weekly Newsletter',
            'body': 'Check out this week\'s updates...',
            'priority': 'normal',
            'user_id': 1
        },
    ]
    
    for email_data in emails_data:
        email = Email(**email_data)
        db.session.add(email)
    
    # Create reference files
    files_data = [
        {'name': 'Company Guidelines', 'file_type': 'pdf'},
        {'name': 'Project Templates', 'file_type': 'doc'},
        {'name': 'Standing Orders', 'file_type': 'txt'},
    ]
    
    for file_data in files_data:
        ref_file = ReferenceFile(**file_data)
        db.session.add(ref_file)
    
    db.session.commit()
    
    print("Database seeded successfully!")
    print("\nDefault login credentials:")
    print("Email: admin@alex.local")
    print("Password: admin123")


# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

