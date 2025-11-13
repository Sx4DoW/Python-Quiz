from db.tables import db, User, Question, Score
from sqlalchemy import func
import random


def get_question_by_id(question_id):
    """Get a specific question by ID"""
    return Question.query.get(question_id)


def get_random_question(user_id=None):
    """Get a random question, preferring unanswered ones if user is logged in"""
    if user_id:
        answered_ids = db.session.query(Score.question_id).filter_by(user_id=user_id).distinct().all()
        answered_ids = [q[0] for q in answered_ids]
        
        unanswered = Question.query.filter(~Question.id.in_(answered_ids)).all()
        if unanswered:
            return random.choice(unanswered)
    
    questions = Question.query.all()
    if not questions:
        return None
    
    return random.choice(questions)


def submit_answer(user_id, question_id, answer):
    """Submit an answer and calculate points"""
    question = Question.query.get(question_id)
    if not question:
        return False, 'Question not found', None
    
    user = User.query.get(user_id)
    if not user:
        return False, 'User not found', None
    
    is_correct = question.is_correct(answer)
    points = 10 if is_correct else 0
    
    previously_correct = Score.query.filter_by(
        user_id=user_id,
        question_id=question_id,
        correct=True
    ).first() is not None
    
    if is_correct and not previously_correct:
        user.total_score += 10
    
    score = Score()
    score.user_id = user_id
    score.question_id = question_id
    score.correct = is_correct
    score.points = points
    
    try:
        db.session.add(score)
        db.session.commit()
        return True, None, {
            'correct': is_correct,
            'points': points,
            'total_score': user.total_score,
            'already_answered': previously_correct
        }
    except Exception as e:
        db.session.rollback()
        return False, 'Failed to save answer', None
