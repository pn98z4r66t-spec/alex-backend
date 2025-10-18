"""
Task API endpoint tests
"""
import pytest


@pytest.mark.api
class TestTasks:
    """Test task endpoints"""
    
    def test_create_task(self, client, auth_headers, sample_task_data):
        """Test creating a new task"""
        response = client.post('/api/tasks', json=sample_task_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'task' in data
        assert data['task']['title'] == sample_task_data['title']
        assert data['task']['status'] == sample_task_data['status']
    
    def test_create_task_unauthorized(self, client, sample_task_data):
        """Test creating task without authentication"""
        response = client.post('/api/tasks', json=sample_task_data)
        
        assert response.status_code == 401
    
    def test_get_all_tasks(self, client, auth_headers, sample_task_data):
        """Test getting all tasks"""
        # Create a task first
        client.post('/api/tasks', json=sample_task_data)
        
        # Get all tasks
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tasks' in data
        assert len(data['tasks']) > 0
    
    def test_get_task_by_id(self, client, auth_headers, sample_task_data):
        """Test getting a specific task"""
        # Create a task
        create_response = client.post('/api/tasks', json=sample_task_data)
        task_id = create_response.get_json()['task']['id']
        
        # Get the task
        response = client.get(f'/api/tasks/{task_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'task' in data
        assert data['task']['id'] == task_id
    
    def test_update_task(self, client, auth_headers, sample_task_data):
        """Test updating a task"""
        # Create a task
        create_response = client.post('/api/tasks', json=sample_task_data)
        task_id = create_response.get_json()['task']['id']
        
        # Update the task
        update_data = {'title': 'Updated Task Title', 'status': 'in_progress'}
        response = client.put(f'/api/tasks/{task_id}', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['task']['title'] == 'Updated Task Title'
        assert data['task']['status'] == 'in_progress'
    
    def test_delete_task(self, client, auth_headers, sample_task_data):
        """Test deleting a task"""
        # Create a task
        create_response = client.post('/api/tasks', json=sample_task_data)
        task_id = create_response.get_json()['task']['id']
        
        # Delete the task
        response = client.delete(f'/api/tasks/{task_id}')
        
        assert response.status_code == 200
        
        # Verify task is deleted
        get_response = client.get(f'/api/tasks/{task_id}')
        assert get_response.status_code == 404
    
    def test_update_task_status(self, client, auth_headers, sample_task_data):
        """Test updating task status"""
        # Create a task
        create_response = client.post('/api/tasks', json=sample_task_data)
        task_id = create_response.get_json()['task']['id']
        
        # Update status
        response = client.patch(f'/api/tasks/{task_id}/status', json={'status': 'completed'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['task']['status'] == 'completed'
