import bleach
import os
import secrets
import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api import api_bp
from api.auth_service import authenticate_user, register_user
from api.profile_service import get_user_profile, update_user_profile
from api.quiz_service import get_random_question, submit_answer, get_question_by_id
from api.leaderboard_service import get_leaderboard, get_user_rank
from db.tables import db, User, Score
from db.init_db import init_db

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"] if os.getenv('FLASK_ENV') == 'production' else [],
    storage_uri="memory://",
    enabled=os.getenv('FLASK_ENV') == 'production'
)

db.init_app(app)
init_db(app)


@app.before_request
def ensure_csrf_token():
    """Generate CSRF token for each session"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)


@app.context_processor
def inject_csrf_token():
    """Make CSRF token available in templates"""
    return {'csrf_token': session.get('csrf_token')}


app.register_blueprint(api_bp)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    """Home page with weather forecast form"""
    forecast = None
    error = None
    city = None
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        city = bleach.clean(city, tags=[], strip=True)
        force_refresh = request.form.get('force_refresh') == '1'
        
        if city and len(city) <= 100:
            api_url = f"{request.host_url}api/weather"
            try:
                response = requests.post(api_url, json={'city': city}, timeout=15)
                if response.status_code == 200:
                    forecast = response.json().get('forecast')
                else:
                    error = f"Could not retrieve weather data for '{city}'"
            except requests.exceptions.RequestException:
                error = f"Error connecting to weather service"
        else:
            error = "Please enter a valid city name (1-100 characters)."
    
    return render_template('index.html', forecast=forecast, error=error, city=city)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login_page():
    """Login page and authentication"""
    if request.method == 'GET':
        return render_template('login.html')

    success, error, user = authenticate_user(
        request.form.get('username', ''),
        request.form.get('password', '')
    )
    
    if success:
        return redirect(url_for('profile_page'))
    else:
        return render_template('login.html', error=error)
    

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register_page():
    """Registration page and user creation"""
    if request.method == 'GET':
        return render_template('register.html')
    
    success, error, user = register_user(
        request.form.get('username', ''),
        request.form.get('nickname', ''),
        request.form.get('password', ''),
        request.form.get('confirm_password', '')
    )
    
    if success:
        return render_template('login.html', message='Registration successful! Please login.')
    else:
        return render_template('register.html', error=error)


@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    """Display and update the profile page for the logged-in user"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    
    message = None
    error = None

    if request.method == 'POST':
        success, err = update_user_profile(
            user_id,
            request.form.get('nickname', ''),
            session.get('csrf_token')
        )
        
        if success:
            message = 'Profile updated successfully!'
        else:
            error = err
    
    success, err, profile_data = get_user_profile(user_id=user_id)
    
    if success:
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('login_page'))
        
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
    else:
        return redirect(url_for('login_page'))


@app.route('/profile/<nickname>')
def view_profile(nickname):
    """View another user's public profile by nickname"""
    success, error, profile_data = get_user_profile(nickname=nickname)
    
    if success:
        user = User.query.filter_by(nickname=nickname).first()
        return render_template('public_profile.html', user=user)
    else:
        return render_template('public_profile.html', error='User not found')


@app.route('/quiz', methods=['GET', 'POST'])
def quiz_page():
    """Quiz page - get question and submit answer"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    
    result = None
    error = None
    
    if request.method == 'POST':
        question_id = request.form.get('question_id')
        answer = request.form.get('answer', '').strip().lower()
        
        if question_id and answer:
            success, err, result = submit_answer(user_id, int(question_id), answer)
            if not success:
                error = err
    
    # Check if a specific question ID is requested
    question_id = request.args.get('id', type=int)
    if question_id:
        question = get_question_by_id(question_id)
        if not question:
            error = 'Question not found'
            question = get_random_question(user_id)
    else:
        question = get_random_question(user_id)
    
    if not question:
        return render_template('quiz.html', error='No questions available')
    
    return render_template('quiz.html', question=question, result=result, error=error)


@app.route('/leaderboard')
def leaderboard_page():
    """Leaderboard page showing users by score with pagination"""
    page = request.args.get('page', 1, type=int)
    
    leaderboard_data = get_leaderboard(page=page, per_page=50)
    
    user_rank = None
    user_id = session.get('user_id')
    if user_id:
        user_rank = get_user_rank(user_id)
    
    return render_template('leaderboard.html', 
                         leaderboard=leaderboard_data['leaderboard'],
                         pagination=leaderboard_data,
                         user_rank=user_rank)


@app.route('/logout', methods=['GET'])
def logout_page():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login_page'))