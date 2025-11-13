"""Service for leaderboard operations"""
from db.tables import db, User


def get_leaderboard(page=1, per_page=50):
    """
    Get users by total score with pagination
    
    Args:
        page: Page number (1-indexed)
        per_page: Number of users per page (default 50)
    
    Returns:
        Dictionary with leaderboard data and pagination info
    """
    pagination = User.query.order_by(User.total_score.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Calculate starting rank for this page
    start_rank = (page - 1) * per_page + 1
    
    leaderboard = []
    for idx, user in enumerate(pagination.items):
        leaderboard.append({
            'rank': start_rank + idx,
            'nickname': user.nickname,
            'score': user.total_score,
            'user_id': user.id
        })
    
    return {
        'leaderboard': leaderboard,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    }


def get_user_rank(user_id):
    """
    Get the rank of a specific user
    
    Args:
        user_id: User's ID
    
    Returns:
        Dictionary with rank and user info, or None if user not found
    """
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Count users with higher score
    higher_count = User.query.filter(User.total_score > user.total_score).count()
    rank = higher_count + 1
    
    return {
        'rank': rank,
        'nickname': user.nickname,
        'score': user.total_score,
        'user_id': user.id
    }
