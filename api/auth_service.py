"""Authentication business logic - shared between API and web routes"""
from werkzeug.security import check_password_hash
from db.tables import db, User
from flask import session
import bleach


def authenticate_user(username, password) -> tuple:
    """
    Authenticate user and create session
    Returns: (success: bool, error_message: str or None, user: User or None)
    """
    username = bleach.clean(username.strip(), tags=[], strip=True)
    
    if not username or not password:
        return False, 'Username and password are required', None
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return False, 'Invalid username or password', None
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['nickname'] = user.nickname
    
    return True, None, user


def register_user(username, nickname, password, confirm_password):
    """
    Register new user
    Returns: (success: bool, error_message: str or None, user: User or None)
    """
    if not all([username, nickname, password, confirm_password]):
        return False, 'All fields are required', None
    
    if password != confirm_password:
        return False, 'Passwords do not match', None
    
    username = bleach.clean(username.strip(), tags=[], strip=True)
    nickname = bleach.clean(nickname.strip(), tags=[], strip=True)
    
    if not (3 <= len(username) <= 80):
        return False, 'Username must be 3-80 characters', None
    
    if not (3 <= len(nickname) <= 80):
        return False, 'Nickname must be 3-80 characters', None
    
    if len(password) < 8:
        return False, 'Password must be at least 8 characters', None
    
    if User.query.filter_by(username=username).first():
        return False, 'Username already exists', None
    
    if User.query.filter_by(nickname=nickname).first():
        return False, 'Nickname already exists', None
    
    new_user = User()
    new_user.username = username
    new_user.nickname = nickname
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return True, None, new_user
    except Exception:
        db.session.rollback()
        return False, 'Registration failed', None
