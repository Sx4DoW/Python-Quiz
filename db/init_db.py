from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def init_db(app):
    """Initialize database tables"""
    with app.app_context():
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if db_path and not os.path.exists(db_path):
            db.create_all()
            print(f"Database created: {db_path}")
        else:
            db.create_all()


