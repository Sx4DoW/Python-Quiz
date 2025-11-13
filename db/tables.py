from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db.init_db import db

class User(db.Model):
    """User model for authentication and scoring"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    total_score = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    
    # Relationship with scores
    scores = db.relationship('Score', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Question(db.Model):
    """Quiz question model"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'a', 'b', 'c', or 'd'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with scores
    scores = db.relationship('Score', backref='question', lazy=True)
    
    def is_correct(self, answer):
        """Check if the provided answer is correct"""
        return answer.lower() == self.correct_option.lower()
    
    def __repr__(self):
        return f'<Question {self.id}: {self.prompt[:50]}...>'


class Score(db.Model):
    """Individual quiz attempt/score record"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Score user_id={self.user_id} question_id={self.question_id} correct={self.correct}>'
