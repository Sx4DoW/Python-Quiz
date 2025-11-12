from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from .weather import weather_routes
from .auth import auth_routes

# Register all sub-routes
api_bp.register_blueprint(weather_routes)
api_bp.register_blueprint(auth_routes)