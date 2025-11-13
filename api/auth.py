from flask import Blueprint, request, jsonify, session
from .auth_service import authenticate_user, register_user

auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    success, error, user = register_user(
        data.get('username', ''),
        data.get('nickname', ''),
        data.get('password', ''),
        data.get('confirm_password', '')
    )
    
    if success:
        return jsonify({
            'message': 'User registered successfully',
            'username': user.username
        }), 201
    else:
        status_code = 409 if 'already exists' in error or 'already taken' in error else 400
        return jsonify({'error': error}), status_code


@auth_routes.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    success, error, user = authenticate_user(
        data.get('username', ''),
        data.get('password', '')
    )
    
    if success:
        return jsonify({
            'message': 'Login successful',
            'username': user.username,
            'nickname': user.nickname
        }), 200
    else:
        status_code = 401 if 'Invalid' in error else 400
        return jsonify({'error': error}), status_code


@auth_routes.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint with CSRF protection"""
    token = request.headers.get('X-CSRF-Token')
    if not token or token != session.get('csrf_token'):
        return jsonify({'error': 'Invalid CSRF token'}), 403

    session.clear()
    return jsonify({'message': 'Logout successful'}), 200
