from flask import Blueprint, request, jsonify, session
from .profile_service import get_user_profile, update_user_profile

profile_routes = Blueprint('profile', __name__)


@profile_routes.route('/profile', methods=['GET'])
def get_profile():
    """Get profile data for current user or by nickname parameter"""
    nickname = request.args.get('nickname')
    user_id = session.get('user_id')
    
    success, error, profile_data = get_user_profile(user_id=user_id, nickname=nickname)
    
    if success:
        return jsonify(profile_data), 200
    else:
        status_code = 401 if error == 'Unauthorized' else 404
        return jsonify({'error': error}), status_code


@profile_routes.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile information"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    csrf_token = request.headers.get('X-CSRF-Token')
    nickname = data.get('nickname', '')
    
    success, error = update_user_profile(user_id, nickname, csrf_token)
    
    if success:
        return jsonify({'message': 'Profile updated successfully', 'nickname': nickname}), 200
    else:
        status_code = 401 if error == 'Unauthorized' else (403 if 'CSRF' in error else (409 if 'taken' in error else 400))
        return jsonify({'error': error}), status_code
