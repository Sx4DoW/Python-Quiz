from flask import Blueprint, request, jsonify, session, Response
from db.tables import db, User, Score
from sqlalchemy import func, desc
import bleach

profile_routes = Blueprint('profile', __name__)


@profile_routes.route('/api/profile', methods=['GET'])
def get_profile() -> Response:
    """
    Get profile data for current user or by nickname parameter
    If nickname parameter is provided, get that user's public profile
    Otherwise, get current user's full profile
    """
    user_id = session.get('user_id')
    
    # Get nickname parameter for viewing other profiles
    nickname = request.args.get('nickname')
    
    if nickname:
        # Public profile view
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 404
            return response
        
        response = jsonify({
            'nickname': user.nickname,
            'total_score': user.total_score,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
        response.status_code = 200
        return response
    
    # Own profile view - requires authentication
    if not user_id:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    
    user = User.query.get(user_id)
    if not user:
        response = jsonify({'error': 'User not found'})
        response.status_code = 404
        return response
    
    # Compute statistics
    total_quizzes = len(user.scores)
    average_score = 0
    if total_quizzes > 0:
        total_points = db.session.query(func.sum(Score.points)).filter_by(user_id=user_id).scalar() or 0
        average_score = round(total_points / total_quizzes, 1)
    
    # Get recent quiz attempts
    recent_quizzes = Score.query.filter_by(user_id=user_id)\
        .order_by(Score.timestamp.desc())\
        .limit(10)\
        .all()
    
    response = jsonify({
        'username': user.username,
        'nickname': user.nickname,
        'total_score': user.total_score,
        'average_score': average_score,
        'total_quizzes': total_quizzes,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'quizzes': [
            {
                'question_id': quiz.question_id,
                'points': quiz.points,
                'correct': quiz.correct,
                'timestamp': quiz.timestamp.isoformat()
            }
            for quiz in recent_quizzes
        ]
    })
    response.status_code = 200
    return response


@profile_routes.route('/api/profile/update', methods=['POST'])
def update_profile() -> Response:
    """Update user profile information"""
    user_id = session.get('user_id')
    if not user_id:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    
    # CSRF protection
    token = request.headers.get('X-CSRF-Token')
    if not token or token != session.get('csrf_token'):
        response = jsonify({'error': 'Invalid CSRF token'})
        response.status_code = 403
        return response
    
    user = User.query.get(user_id)
    if not user:
        response = jsonify({'error': 'User not found'})
        response.status_code = 404
        return response
    
    data = request.get_json()
    if not data:
        response = jsonify({'error': 'No data provided'})
        response.status_code = 400
        return response
    
    # Update nickname if provided
    if 'nickname' in data:
        nickname = bleach.clean(data['nickname'].strip(), tags=[], strip=True)
        if not (3 <= len(nickname) <= 80):
            response = jsonify({'error': 'Nickname must be 3-80 characters'})
            response.status_code = 400
            return response
        
        # Check if nickname is already taken by another user
        existing = User.query.filter_by(nickname=nickname).first()
        if existing and existing.id != user_id:
            response = jsonify({'error': 'Nickname already taken'})
            response.status_code = 409
            return response
        
        user.nickname = nickname
        session['nickname'] = nickname
    
    try:
        db.session.commit()
        response = jsonify({
            'message': 'Profile updated successfully',
            'nickname': user.nickname,
        })
        response.status_code = 200
        return response
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': 'Failed to update profile'})
        response.status_code = 500
        return response
