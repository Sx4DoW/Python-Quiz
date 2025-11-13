"""API endpoints for leaderboard"""
from flask import Blueprint, jsonify, request
from api.leaderboard_service import get_leaderboard


leaderboard_routes = Blueprint('leaderboard_routes', __name__)


@leaderboard_routes.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    """Get leaderboard with users by score (paginated)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    if page < 1:
        return jsonify({'error': 'Page must be >= 1'}), 400
    
    if per_page < 1 or per_page > 100:
        return jsonify({'error': 'per_page must be between 1 and 100'}), 400
    
    leaderboard_data = get_leaderboard(page, per_page)
    return jsonify(leaderboard_data)
