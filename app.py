# Importing bleach to sanitize user input for possible xss attacks
import bleach
import os
import secrets
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api.services import get_weather_forecast
from api import api_bp
from db.tables import db
from db.init_db import init_db

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

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
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

# Apply rate limits to auth routes
limiter.limit("5 per hour")(api_bp.view_functions.get('auth.register'))
limiter.limit("10 per minute")(api_bp.view_functions.get('auth.login'))

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

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@app.route('/logout', methods=['GET'])
def logout_page():
    """Fallback logout route for non-JS clients: clear session and redirect to login."""
    session.clear()
    return redirect(url_for('login_page'))