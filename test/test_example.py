import pytest
from app import app, db, User
from flask import flash

from models import User  # Replace with the correct path to the User model

# Fixture to create a test client
# Fixture to create a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Initialize the database schema
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests

# Helper function to create a user with password hashing
def create_user(username="defaultuser", password="defaultpassword"):
    with app.app_context():
        user = User(username=username)
        user.set_password(password)  # Ensure password is hashed
        db.session.add(user)
        db.session.commit()

# Test: Home Page
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello" in response.data or b"<html" in response.data  # At least returns a page

"""  # Adjust this according to the actual content of your home page
# Test: Register a New User
def test_register(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration Successful!" in response.data
    assert b"newuser" in response.data  # Check that the user is added in some page content

# Test: Register with an already taken username
def test_register_with_taken_username(client):
    create_user(username="newuser")  # Create a user with 'newuser'
    response = client.post('/register', data={
        'username': 'newuser',  # Trying to register with the same username
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username already exists. Try another one!" in response.data  # Flash message or error

# Test: Login with Correct Credentials
def test_login_success(client):
    create_user(username="testuser", password="testpassword")
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back, testuser!" in response.data  # Adjust this according to the actual message displayed

# Test: Login with Incorrect Credentials
def test_login_failure(client):
    create_user(username="testuser", password="testpassword")
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials! Try again." in response.data

  # Adjust this according to the actual message displayed

  # Adjust this according to the actual message displayed
# Test: Access Dashboard without Login (Should Redirect)
def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 302  # Should redirect to login
    assert response.location.endswith('/login')  # Check if it redirects to the login page

# Test: Access Dashboard after Login
def test_dashboard_after_login(client):
    create_user()
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"testuser" in response.data  # Ensure logged-in username is displayed

# Test: Logout
def test_logout(client):
    create_user()
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert b"logged out" in response.data  # Make sure the user sees "logged out"

# Test: Play Game Access Without Login
def test_play_game_requires_login(client):
    response = client.get('/play/easy', follow_redirects=True)
    assert response.status_code == 302  # Should redirect to login
    assert response.location.endswith('/login')  # Check if it redirects to the login page

# Test: Register with Empty Username or Password
def test_register_empty_fields(client):
    response = client.post('/register', data={
        'username': '',  # Empty username
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username is required" in response.data  # Error for empty username

    response = client.post('/register', data={
        'username': 'testuser',
        'password': ''  # Empty password
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Password is required" in response.data  # Error for empty password

# Test: Login with Empty Username or Password
def test_login_empty_fields(client):
    create_user()
    response = client.post('/login', data={
        'username': '',  # Empty username
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username is required" in response.data  # Error for empty username

    response = client.post('/login', data={
        'username': 'testuser',
        'password': ''  # Empty password
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Password is required" in response.data  # Error for empty password

# Test: Password Hashing (Ensure password is hashed and not stored in plain text)
def test_password_hashing(client):
    user = create_user(username="testuser", password="testpassword")
    assert user.check_password("testpassword") is True  # Password should match
    assert user.password != "testpassword"  # Password should not be stored in plain text

    
"""  # Adjust this according to the actual message displayed