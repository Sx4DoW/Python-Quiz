from flask import Blueprint, request, jsonify, session, current_app, Response
from werkzeug.security import generate_password_hash, check_password_hash
from db.tables import db, User
from datetime import datetime
import bleach

auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/register', methods=['POST'])
def register() -> Response:
    """
    Endpoint for user registration.
    Accepts POST with JSON: {"username": "...", "nickname": "...", "password": "...", "confirm_password": "..."}
    """
    data = request.get_json()
    
    # Input validation
    required_fields = ['username', 'nickname', 'password', 'confirm_password']
    if not data or not all(field in data for field in required_fields):
        response = jsonify({'error': 'All fields are required'})
        response.status_code = 400
        return response
    
    if data['password'] != data['confirm_password']:
        response = jsonify({'error': 'Passwords do not match'})
        response.status_code = 400
        return response
    
    # Sanitize inputs
    username = bleach.clean(data['username'].strip(), tags=[], strip=True)
    nickname = bleach.clean(data['nickname'].strip(), tags=[], strip=True)
    password = data['password']
    
    # Validate input lengths
    if not (3 <= len(username) <= 80):
        response = jsonify({'error': 'Username must be 3-80 characters'})
        response.status_code = 400
        return response
    if not (3 <= len(nickname) <= 80):
        response = jsonify({'error': 'Nickname must be 3-80 characters'})
        response.status_code = 400
        return response
    if len(password) < 6:
        response = jsonify({'error': 'Password must be at least 6 characters'})
        response.status_code = 400
        return response
    
    # Verify username and nickname uniqueness in the database
    if User.query.filter_by(username=username).first():
        response = jsonify({'error': 'Username already exists'})
        response.status_code = 409
        return response
    if User.query.filter_by(nickname=nickname).first():
        response = jsonify({'error': 'Nickname already exists'})
        response.status_code = 409
        return response
    
    # Create new user in the database with hashed password
    new_user = User(username=username, nickname=nickname)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        response = jsonify({
            'message': 'User registered successfully',
            'username': username
        })
        response.status_code = 201
        return response
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': 'Registration failed'})
        response.status_code = 500
        return response


@auth_routes.route('/login', methods=['POST'])
def login() -> Response:
    """
    Endpoint for user login.
    Accepts POST with JSON: {"username": "...", "password": "..."}
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        response = jsonify({'error': 'Username and password are required'})
        response.status_code = 400
        return response
    
    # Sanitize input
    username = bleach.clean(data['username'].strip(), tags=[], strip=True)
    password = data['password']
    
    # Verify credentials in the database
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        response = jsonify({'error': 'Invalid username or password'})
        response.status_code = 401
        return response
    
    # Create user session
    session['user_id'] = user.id
    session['username'] = user.username
    session['nickname'] = user.nickname
    
    response = jsonify({
        'message': 'Login successful',
        'username': user.username,
        'nickname': user.nickname
    })
    response.status_code = 200
    return response


@auth_routes.route('/logout', methods=['POST'])
def logout() -> Response:
    """
    Endpoint for user logout.
    """
    # CSRF protection: require X-CSRF-Token header to match session token
    token = request.headers.get('X-CSRF-Token')
    if not token or token != session.get('csrf_token'):
        response = jsonify({'error': 'Invalid CSRF token'})
        response.status_code = 403
        return response

    # Delete user session
    session.clear()

    response = jsonify({'message': 'Logout successful'})
    response.status_code = 200
    return response
