from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from db.tables import db, User
import bleach

auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/register', methods=['POST'])
def register():
    """
    Endpoint for user registration.
    Accepts POST with JSON: {"username": "...", "nickname": "...", "password": "...", "confirm_password": "..."}
    """
    data = request.get_json()
    
    # Input validation
    required_fields = ['username', 'nickname', 'password', 'confirm_password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'All fields are required'}), 400
    
    if data['password'] != data['confirm_password']:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Sanitize inputs
    username = bleach.clean(data['username'].strip(), tags=[], strip=True)
    nickname = bleach.clean(data['nickname'].strip(), tags=[], strip=True)
    password = data['password']
    
    # Validate input lengths
    if not (3 <= len(username) <= 80):
        return jsonify({'error': 'Username must be 3-80 characters'}), 400
    if not (3 <= len(nickname) <= 80):
        return jsonify({'error': 'Nickname must be 3-80 characters'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Verify username and nickname uniqueness in the database
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(nickname=nickname).first():
        return jsonify({'error': 'Nickname already exists'}), 409
    
    # Create new user in the database with hashed password
    new_user = User(username=username, nickname=nickname)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'username': username
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Endpoint for user login.
    Accepts POST with JSON: {"username": "...", "password": "..."}
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Sanitize input
    username = bleach.clean(data['username'].strip(), tags=[], strip=True)
    password = data['password']
    
    # Verify credentials in the database
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create user session
    session['user_id'] = user.id
    session['username'] = user.username
    session['nickname'] = user.nickname
    
    return jsonify({
        'message': 'Login successful',
        'username': user.username,
        'nickname': user.nickname
    }), 200


@auth_routes.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint for user logout.
    """
    # CSRF protection: require X-CSRF-Token header to match session token
    token = request.headers.get('X-CSRF-Token')
    if not token or token != session.get('csrf_token'):
        return jsonify({'error': 'Invalid CSRF token'}), 403

    # Delete user session
    session.clear()

    return jsonify({'message': 'Logout successful'}), 200