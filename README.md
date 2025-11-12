
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

2. Install dependencies (create `requirements.txt` later):

```bash
pip install flask flask_sqlalchemy flask_wtf werkzeug requests
```

3. Configure environment variables for development (example):

```bash
export FLASK_APP=app
export FLASK_ENV=development
# optionally set a SECRET_KEY and WEATHER_API_KEY
```

4. Initialize the database and run the app (once implemented):

```bash
flask db init   # if using Flask-Migrate
flask db migrate
flask db upgrade
flask run
```

## Testing

- Add unit tests for auth, quiz logic, and leaderboard calculations.
- Create a small integration test that registers a user, simulates quiz answers, and checks leaderboard updates.

## Deployment (PythonAnywhere)

1. Create a PythonAnywhere account and a new web app.
2. Upload or clone this repository to your account.
3. Configure the web app to use the Flask WSGI entry point.
4. Set environment variables (SECRET_KEY, WEATHER_API_KEY) in the PythonAnywhere web app settings.

## Security and edge cases

- Hash passwords with a secure algorithm (Werkzeug/Passlib).
- Validate and sanitize user input (forms, city names).
- Rate-limit weather API calls and cache results for a short time to avoid hitting API quotas.
- Handle duplicate usernames/nicknames gracefully and show helpful validation messages.

## Next steps I can implement for you

- Scaffold the Flask app (project structure, routes, basic templates).
- Add authentication (register/login/logout) and user model with SQLite.
- Implement the quiz engine with randomized questions and leaderboard updates.
- Integrate a public weather API and build the 3-day forecast widget.

Tell me which task you'd like me to start with and I'll scaffold it now.