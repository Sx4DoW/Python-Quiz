"""Seed database with quiz questions from JSON files"""
from app import app
from db.tables import db, Question
import json
import os
from pathlib import Path


def load_questions_from_json():
    """Load all quiz questions from JSON files in quiz_data folder"""
    quiz_data_dir = Path('quiz_data')
    
    if not quiz_data_dir.exists():
        print(f"Error: {quiz_data_dir} folder not found")
        return []
    
    all_questions = []
    
    for json_file in quiz_data_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                all_questions.extend(questions)
                print(f"Loaded {len(questions)} questions from {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
    
    return all_questions


def seed_questions():
    """Add quiz questions from JSON files to the database"""
    with app.app_context():
        existing = Question.query.first()
        if existing:
            print("Questions already exist in database.")
            response = input("Do you want to clear existing questions and reload? (yes/no): ")
            if response.lower() == 'yes':
                Question.query.delete()
                db.session.commit()
                print("Existing questions cleared.")
            else:
                print("Skipping seed.")
                return
        
        questions_data = load_questions_from_json()
        
        if not questions_data:
            print("No questions found to load.")
            return
        
        for q_data in questions_data:
            question = Question()
            question.prompt = q_data['prompt']
            question.option_a = q_data['option_a']
            question.option_b = q_data['option_b']
            question.option_c = q_data['option_c']
            question.option_d = q_data['option_d']
            question.correct_option = q_data['correct_option']
            
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully added {len(questions_data)} questions to the database!")


if __name__ == '__main__':
    seed_questions()
