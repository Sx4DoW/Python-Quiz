from flask import Blueprint, request, jsonify, session
from .quiz_service import get_random_question, submit_answer

quiz_routes = Blueprint('quiz', __name__)


@quiz_routes.route('/quiz/question', methods=['GET'])
def get_question():
    """Get a random quiz question"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    question = get_random_question(user_id)
    if not question:
        return jsonify({'error': 'No questions available'}), 404
    
    return jsonify({
        'id': question.id,
        'prompt': question.prompt,
        'options': {
            'a': question.option_a,
            'b': question.option_b,
            'c': question.option_c,
            'd': question.option_d
        }
    }), 200


@quiz_routes.route('/quiz/answer', methods=['POST'])
def submit_quiz_answer():
    """Submit an answer to a quiz question"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'question_id' not in data or 'answer' not in data:
        return jsonify({'error': 'Question ID and answer are required'}), 400
    
    question_id = data['question_id']
    answer = data['answer'].strip().lower()
    
    if answer not in ['a', 'b', 'c', 'd']:
        return jsonify({'error': 'Answer must be a, b, c, or d'}), 400
    
    success, error, result = submit_answer(user_id, question_id, answer)
    
    if not success:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'correct': result['correct'],
        'points': result['points'],
        'total_score': result['total_score'],
        'already_answered': result['already_answered']
    }), 200
