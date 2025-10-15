"""
Routes package initialization
"""
from src.routes.auth import auth_bp
from src.routes.tasks import tasks_bp
from src.routes.ai import ai_bp
from src.routes.task_sharing import task_sharing_bp
from src.routes.task_instance import task_instance_bp
from src.routes.files import files_bp

__all__ = [
    'auth_bp',
    'tasks_bp',
    'ai_bp',
    'task_sharing_bp',
    'task_instance_bp',
    'files_bp',
]

