"""
Pytest configuration and fixtures
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import create_app
from src.models.models import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing"""
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()


@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Register a test user
    response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'role': 'Developer'
    })
    
    # Cookies are set automatically in the client
    return {}  # No headers needed with cookie auth


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'SecurePassword123!',
        'role': 'Developer'
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'pending',
        'priority': 'high',
        'due_date': '2025-12-31'
    }
