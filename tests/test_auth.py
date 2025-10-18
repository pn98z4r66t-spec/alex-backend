"""
Authentication endpoint tests
"""
import pytest


@pytest.mark.auth
class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json=sample_user_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert data['user']['name'] == sample_user_data['name']
        assert 'access_token' not in data  # Tokens should be in cookies
        
        # Check cookies are set
        assert 'access_token' in response.headers.get('Set-Cookie', '')
        assert 'refresh_token' in response.headers.get('Set-Cookie', '')
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post('/api/auth/register', json=sample_user_data)
        
        # Try to register again with same email
        response = client.post('/api/auth/register', json=sample_user_data)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        response = client.post('/api/auth/register', json={
            'name': 'Test',
            'email': 'invalid-email',  # Invalid email format
            'password': '123'  # Too short
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post('/api/auth/register', json=sample_user_data)
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['message'] == 'Login successful'
        
        # Check cookies are set
        assert 'access_token' in response.headers.get('Set-Cookie', '')
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post('/api/auth/register', json=sample_user_data)
        
        # Try to login with wrong password
        response = client.post('/api/auth/login', json={
            'email': sample_user_data['email'],
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'email' in data
        assert 'name' in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_logout(self, client, auth_headers):
        """Test logout"""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'
        
        # Verify cookies are cleared
        set_cookie = response.headers.get('Set-Cookie', '')
        assert 'access_token=' in set_cookie
        assert 'expires' in set_cookie.lower() or 'max-age=0' in set_cookie.lower()
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile"""
        response = client.put('/api/auth/me', json={
            'name': 'Updated Name',
            'role': 'Senior Developer'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['name'] == 'Updated Name'
        assert data['user']['role'] == 'Senior Developer'
