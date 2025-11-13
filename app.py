# Importing bleach to sanitize user input for possible xss attacks
import bleach
import os
import secrets
import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api.services import get_weather_forecast
from api import api_bp
from db.tables import db, User, Score
from db.init_db import init_db
from sqlalchemy import func

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Session security settings
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Set SECURE flag to True in production (requires HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

# Rate limiting configuration (disabled in development)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"] if os.getenv('FLASK_ENV') == 'production' else [],
    storage_uri="memory://",
    enabled=os.getenv('FLASK_ENV') == 'production'
)

# Initialize database
db.init_app(app)

# Auto-create tables on first run
init_db(app)


# CSRF token: ensure each session has a token and expose it to templates
@app.before_request
def ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)


@app.context_processor
def inject_csrf_token():
    return {'csrf_token': session.get('csrf_token')}

# Register blueprints
app.register_blueprint(api_bp)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    forecast = None
    error = None
    city = None
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        city = bleach.clean(city, tags=[], strip=True)  # Sanitize input
        force_refresh = request.form.get('force_refresh') == '1'
        
        # Validate city input
        if city and len(city) <= 100:
            forecast = get_weather_forecast(city, force_refresh=force_refresh)
            if forecast is None:
                error = f"Impossible adding weather data for '{city}'"
        else:
            error = "Please enter a valid city name (1-100 characters)."
    
    return render_template('index.html', forecast=forecast, error=error, city=city)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    from api.auth import login as api_login
    from flask import g
    
    original_get_json = request.get_json
    request.get_json = lambda: {
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }
    
    # Call API function directly (shares session)
    response = api_login()
    data = response.get_json()
    
    # Restore original get_json
    request.get_json = original_get_json
    
    if response.status_code == 200:
        return redirect(url_for('profile_page'))
    else:
        return render_template('login.html', error=data.get('error', 'Login failed'))
    

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Call API endpoint directly (shares session)
    from api.auth import register as api_register
    
    # Temporarily override get_json to return form data
    original_get_json = request.get_json
    request.get_json = lambda: {
        'username': request.form.get('username'),
        'nickname': request.form.get('nickname'),
        'password': request.form.get('password'),
        'confirm_password': request.form.get('confirm_password')
    }
    
    response = api_register()
    data = response.get_json()
    
    # Restore original get_json
    request.get_json = original_get_json
    
    if response.status_code == 201:
        return render_template('login.html', message='Registration successful! Please login.')
    else:
        return render_template('register.html', error=data.get('error', 'Registration failed'))


@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    """Display and update the profile page for the logged-in user"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login_page'))
    
    message = None
    error = None

    # Handle profile update via POST
    if request.method == 'POST':
        from api.profile import update_profile as api_update_profile
        
        # Temporarily override get_json and headers
        original_get_json = request.get_json
        original_headers = request.headers
        
        request.get_json = lambda: {'nickname': request.form.get('nickname')}
        
        # Add CSRF token to headers
        class HeadersWithCSRF:
            def __init__(self, original_headers, csrf_token):
                self._original = original_headers
                self._csrf = csrf_token
            
            def get(self, key, default=None):
                if key == 'X-CSRF-Token':
                    return self._csrf
                return self._original.get(key, default)
        
        request.headers = HeadersWithCSRF(original_headers, session.get('csrf_token'))
        
        response = api_update_profile()
        data = response.get_json()
        
        # Restore originals
        request.get_json = original_get_json
        request.headers = original_headers
        
        if response.status_code == 200:
            message = 'Profile updated successfully!'
            # Refresh user data
            user = User.query.get(user_id)
        else:
            error = data.get('error', 'Failed to update profile')

    # Get profile data from API
    from api.profile import get_profile as api_get_profile
    response = api_get_profile()
    profile_data = response.get_json()
    
    return render_template('profile.html', 
                         user=user, 
                         average_score=profile_data.get('average_score', 0),
                         total_quizzes=profile_data.get('total_quizzes', 0),
                         quizzes=[{
                             'question_id': q['question_id'],
                             'points': q['points'],
                             'correct': q['correct'],
                             'timestamp': datetime.datetime.fromisoformat(q['timestamp'])
                         } for q in profile_data.get('quizzes', [])],
                         message=message,
                         error=error)


@app.route('/profile/<nickname>')
def view_profile(nickname):
    """View another user's public profile by nickname"""
    from api.profile import get_profile as api_get_profile
    
    # Temporarily override request.args to include nickname parameter
    from werkzeug.datastructures import ImmutableMultiDict
    original_args = request.args
    request.args = ImmutableMultiDict([('nickname', nickname)])
    
    response = api_get_profile()
    
    # Restore original args
    request.args = original_args
    
    if response.status_code == 404:
        return render_template('public_profile.html', error='User not found')
    
    profile_data = response.get_json()
    
    # For public profiles, create a minimal user object
    class PublicUser:
        def __init__(self, nickname, total_score, created_at):
            self.nickname = nickname
            self.total_score = total_score
            self.created_at = datetime.datetime.fromisoformat(created_at) if created_at else None
    
    public_user = PublicUser(
        profile_data.get('nickname'),
        profile_data.get('total_score', 0),
        profile_data.get('created_at')
    )
    
    return render_template('public_profile.html', user=public_user)


@app.route('/logout', methods=['GET'])
def logout_page():
    """Fallback logout route for non-JS clients: clear session and redirect to login."""
    session.clear()
    return redirect(url_for('login_page'))