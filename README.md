
# Python Quiz — Application README

This repository contains the Flask-based "Python Quiz" application: a web quiz platform with user accounts, persistent scoring, randomized questions, a leaderboard, and a weather widget on the home page. The README below describes the app architecture, features, local setup, and deployment notes.

## Application overview

Core features:

- User registration and authentication with unique usernames and nicknames.
- Persistent user profiles that store cumulative quiz scores.
- A multi-question quiz interface that presents one question at a time with 4 answer options.
- Randomized question order and an endless quiz loop (questions repeat in randomized order).
- Leaderboard showing top players by total score.
- Home page weather widget: enter a city and see a 3-day forecast (today, tomorrow, day-after) including day names and day/night temperatures.

## Architecture and key components

- Flask app: routes for auth, quiz flow, leaderboard, and API endpoints.
- Templates: Jinja2 templates for pages (home, register, login, quiz, leaderboard).
- Static assets: CSS and client-side JavaScript for interactivity (weather widget, quiz UI).
- Database: SQLite (development) via SQLAlchemy models for Users, Questions, and Scores.

Data model (high level):

- User: id, username (unique), nickname (unique), password_hash, total_score, created_at
- Question: id, prompt, option_a..option_d, correct_option, created_at
- Score/Attempt (optional): id, user_id, question_id, correct(bool), points, timestamp

## Local setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Configure environment variables for development:

```bash
WEATHER_API_KEY=YOUR-API-KEY
SECRET_KEY=YOUR-SECRET-KEY
SQLALCHEMY_DATABASE_URI=sqlite:///path-to-your-db.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

1. Initialize the database and run the app:

```bash
flask run
```