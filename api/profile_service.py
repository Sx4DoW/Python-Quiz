"""Profile business logic - shared between API and web routes"""
from db.tables import db, User, Score
from sqlalchemy import func
from flask import session
import bleach


def get_user_profile(user_id=None, nickname=None):
    """
    Get user profile data
    Returns: (success: bool, error_message: str or None, profile_data: dict or None)
    """
    if nickname:
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            return False, 'User not found', None
        
        return True, None, {
            'nickname': user.nickname,
            'total_score': user.total_score,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    
    if not user_id:
        user_id = session.get('user_id')
    
    if not user_id:
        return False, 'Unauthorized', None
    
    user = User.query.get(user_id)
    if not user:
        return False, 'User not found', None
    
    total_quizzes = len(user.scores)
    average_score = 0
    if total_quizzes > 0:
        total_points = db.session.query(func.sum(Score.points)).filter_by(user_id=user_id).scalar() or 0
        average_score = round(total_points / total_quizzes, 1)
    
    recent_quizzes = Score.query.filter_by(user_id=user_id)\
        .order_by(Score.timestamp.desc())\
        .limit(10)\
        .all()
    
    return True, None, {
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
    }


def update_user_profile(user_id, nickname, csrf_token):
    """
    Update user profile
    Returns: (success: bool, error_message: str or None)
    """
    if not user_id:
        return False, 'Unauthorized'
    
    if not csrf_token or csrf_token != session.get('csrf_token'):
        return False, 'Invalid CSRF token'
    
    user = User.query.get(user_id)
    if not user:
        return False, 'User not found'
    
    nickname = bleach.clean(nickname.strip(), tags=[], strip=True)
    if not (3 <= len(nickname) <= 80):
        return False, 'Nickname must be 3-80 characters'
    
    existing = User.query.filter_by(nickname=nickname).first()
    if existing and existing.id != user_id:
        return False, 'Nickname already taken'
    
    user.nickname = nickname
    session['nickname'] = nickname
    
    try:
        db.session.commit()
        return True, None
    except Exception:
        db.session.rollback()
        return False, 'Failed to update profile'
