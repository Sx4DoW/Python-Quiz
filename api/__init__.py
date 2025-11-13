from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from .weather import weather_routes
from .auth import auth_routes
from .profile import profile_routes
from .quiz import quiz_routes
from .leaderboard import leaderboard_routes

api_bp.register_blueprint(weather_routes)
api_bp.register_blueprint(auth_routes)
api_bp.register_blueprint(profile_routes)
api_bp.register_blueprint(quiz_routes)
api_bp.register_blueprint(leaderboard_routes)