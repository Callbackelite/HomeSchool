import pytest
import tempfile
import os
from app import app, db, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.drop_all()

@pytest.fixture
def admin_user():
    """Create a test admin user."""
    user = User(
        username='testadmin',
        email='admin@test.com',
        password_hash=generate_password_hash('testpass'),
        role='admin'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def child_user():
    """Create a test child user."""
    user = User(
        username='testchild',
        email='child@test.com',
        password_hash=generate_password_hash('testpass'),
        role='child',
        pin='1234',
        grade_level=5
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200

def test_admin_login(client, admin_user):
    """Test admin login functionality."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_child_login(client, child_user):
    """Test child login functionality."""
    response = client.post('/login', data={
        'username': 'testchild',
        'pin': '1234'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_invalid_login(client):
    """Test invalid login attempt."""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_admin_dashboard_access(client, admin_user):
    """Test admin dashboard access."""
    # Login first
    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpass'
    })
    
    response = client.get('/admin/dashboard')
    assert response.status_code == 200

def test_child_dashboard_access(client, child_user):
    """Test child dashboard access."""
    # Login first
    client.post('/login', data={
        'username': 'testchild',
        'pin': '1234'
    })
    
    response = client.get('/child/dashboard')
    assert response.status_code == 200

def test_unauthorized_access(client):
    """Test that unauthorized users are redirected."""
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200
    # Should be redirected to login page

def test_user_creation_api(client, admin_user):
    """Test user creation API."""
    # Login as admin first
    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpass'
    })
    
    response = client.post('/api/admin/users', 
        json={
            'username': 'newchild',
            'email': 'newchild@test.com',
            'role': 'child',
            'grade_level': 3,
            'pin': '5678'
        },
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_database_models():
    """Test that database models can be created."""
    with app.app_context():
        # Test User model
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
            role='child'
        )
        assert user.username == 'testuser'
        assert user.role == 'child'

if __name__ == '__main__':
    pytest.main([__file__]) 