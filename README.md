
# Python Quiz — AI & Python Learning Platform

A comprehensive Flask-based web application for learning Python and AI concepts through interactive quizzes. Features user authentication, persistent scoring, a dynamic leaderboard, weather forecasts, and a beautiful modern UI.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure registration and login system with password hashing
- **Profile Management**: View and update user profiles with statistics
- **Interactive Quizzes**: Multiple-choice questions on Python and AI topics
- **Smart Scoring System**: 
  - 10 points for correct first-time answers
  - 0 points for incorrect or repeated answers
  - Cumulative score tracking across all quizzes
- **Question Randomization**: Prioritizes unanswered questions for better learning experience
- **Quiz History**: Review previously answered questions from your profile
- **Global Leaderboard**: Paginated leaderboard showing all players ranked by score
- **Weather Widget**: 3-day weather forecast on the home page

### User Interface
- 🎨 Modern, responsive design that works on mobile, tablet, and desktop
- 🏅 Special styling for top 3 leaderboard positions with medal emojis
- ✨ Smooth animations and hover effects
- 🎯 Intuitive navigation with session-aware menu
- 📊 Visual feedback for correct/incorrect answers
- 💫 Gradient headers and card-based layouts

## 📁 Project Structure

```
Python_Quiz/
├── app.py                      # Main Flask application and routes
├── requirements.txt            # Python dependencies
├── seed_questions.py          # Database seeding script
├── cache_cities.json          # Cached city data for weather API
├── .env                       # Environment variables (create this)
│
├── api/                       # API layer and business logic
│   ├── __init__.py           # Blueprint registration
│   ├── auth.py               # Authentication API endpoints
│   ├── auth_service.py       # Authentication business logic
│   ├── profile.py            # Profile API endpoints
│   ├── profile_service.py    # Profile business logic
│   ├── quiz.py               # Quiz API endpoints
│   ├── quiz_service.py       # Quiz business logic
│   ├── leaderboard.py        # Leaderboard API endpoints
│   ├── leaderboard_service.py # Leaderboard business logic
│   ├── weather.py            # Weather API endpoints
│   └── services.py           # Shared service utilities
│
├── db/                        # Database layer
│   ├── init_db.py            # Database initialization
│   └── tables.py             # SQLAlchemy models (User, Question, Score)
│
├── templates/                 # Jinja2 HTML templates
│   ├── _nav.html             # Navigation header component
│   ├── _footer.html          # Footer component
│   ├── index.html            # Home page with weather widget
│   ├── register.html         # User registration page
│   ├── login.html            # User login page
│   ├── profile.html          # User profile and stats
│   ├── public_profile.html   # Public user profiles
│   ├── quiz.html             # Quiz interface
│   └── leaderboard.html      # Global leaderboard
│
├── static/                    # Static assets
│   ├── style/
│   │   └── main.css          # Main stylesheet (800+ lines)
│   └── js/
│       └── city-autocomplete.js # Weather city search
│
├── quiz_data/                 # Quiz questions in JSON format
│   ├── README.md             # Quiz data format documentation
│   ├── python_basics.json    # Basic Python questions (10)
│   ├── ai_development.json   # AI/ML fundamentals (10)
│   ├── computer_vision.json  # Computer vision concepts (10)
│   ├── nlp.json              # Natural Language Processing (10)
│   └── ai_applications.json  # AI application deployment (10)
│
└── instance/                  # Instance-specific files (auto-created)
    └── quiz.db               # SQLite database
```

## 🗄️ Database Schema

### User Model
```python
- id: Integer (Primary Key)
- username: String(80), Unique, Indexed
- nickname: String(80), Unique, Indexed
- password_hash: String(255)
- total_score: Integer (default: 0)
- created_at: DateTime
```

### Question Model
```python
- id: Integer (Primary Key)
- prompt: Text
- option_a: String(255)
- option_b: String(255)
- option_c: String(255)
- option_d: String(255)
- correct_option: String(1) ['a', 'b', 'c', 'd']
- created_at: DateTime
```

### Score Model
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key → users.id)
- question_id: Integer (Foreign Key → questions.id)
- correct: Boolean
- points: Integer
- timestamp: DateTime
```

## 🚀 Local Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd Python_Quiz
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file** in the root directory:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///instance/quiz.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Weather API Configuration
WEATHER_API_KEY=your-openweathermap-api-key-here
```

5. **Initialize the database**
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

6. **Seed quiz questions** (loads all JSON files from quiz_data/)
```bash
python seed_questions.py
```

7. **Run the application**
```bash
flask run
```

8. **Access the application**
```
Open your browser and navigate to: http://127.0.0.1:5000
```

## 📝 Adding New Quiz Questions

Quiz questions are stored in JSON format in the `quiz_data/` folder. Each file contains an array of question objects.

### Question Format
```json
{
    "prompt": "What is the correct way to create a function in Python?",
    "option_a": "function myFunc():",
    "option_b": "def myFunc():",
    "option_c": "create myFunc():",
    "option_d": "func myFunc():",
    "correct_option": "b"
}
```

### Adding Questions
1. Create a new `.json` file in `quiz_data/` (e.g., `quiz_data/python_advanced.json`)
2. Add your questions following the format above
3. Run `python seed_questions.py` to load them into the database
4. The script will ask for confirmation if questions already exist

## 🔐 Security Features

- **Password Hashing**: Uses `werkzeug.security` for secure password storage
- **CSRF Protection**: CSRF tokens on all forms
- **Session Management**: Secure session cookies with HttpOnly flag
- **Rate Limiting**: Request limiting on sensitive endpoints (login/register)
- **Input Sanitization**: Uses `bleach` library to sanitize user inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection attacks

## 🎯 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/logout` - User logout

### Profile
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update user profile

### Quiz
- `GET /api/quiz/question` - Get random quiz question
- `POST /api/quiz/answer` - Submit quiz answer

### Leaderboard
- `GET /api/leaderboard?page=1&per_page=50` - Get paginated leaderboard

### Weather
- `POST /api/weather` - Get weather forecast for a city

## 📱 Routes

### Public Routes
- `/` - Home page with weather widget
- `/register` - User registration
- `/login` - User login
- `/leaderboard` - Global leaderboard (paginated)
- `/profile/<nickname>` - Public user profiles

### Protected Routes (require authentication)
- `/profile` - User profile and statistics
- `/quiz` - Quiz interface
- `/quiz?id=<question_id>` - View specific question
- `/logout` - Logout

## 🎨 Customization

### Styling
- Main stylesheet: `static/style/main.css`
- CSS uses modern CSS variables for easy theme customization
- Responsive design with mobile-first approach

### Quiz Topics
Current topics (50 questions total):
- Python Basics (10 questions)
- AI Development (10 questions)
- Computer Vision (10 questions)
- Natural Language Processing (10 questions)
- AI Applications (10 questions)

Add more by creating new JSON files in `quiz_data/`

## 🌐 Deployment

### PythonAnywhere Deployment

1. **Create account** at https://www.pythonanywhere.com/

2. **Upload files** via Files tab or Git

3. **Create virtual environment**
```bash
mkvirtualenv --python=/usr/bin/python3.10 quizenv
workon quizenv
pip install -r requirements.txt
```

4. **Configure Web App**
   - Go to Web tab → Add a new web app
   - Choose Flask
   - Set source code directory
   - Set working directory
   - Configure WSGI file

5. **Set environment variables** in WSGI configuration file

6. **Initialize database**
```bash
cd /home/yourusername/Python_Quiz
python seed_questions.py
```

7. **Reload web app** and test

## 🛠️ Technologies Used

- **Backend**: Flask 3.0+
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (production)
- **Frontend**: Jinja2 templates, HTML5, CSS3, vanilla JavaScript
- **Authentication**: werkzeug.security (password hashing)
- **Security**: bleach (input sanitization), flask-limiter (rate limiting)
- **APIs**: OpenWeatherMap API for weather data
- **Styling**: Custom CSS with CSS variables, gradient backgrounds, animations

## 📊 Features Breakdown

### Scoring System
- First correct answer: **10 points**
- Wrong answer: **0 points**
- Already answered (repeat): **0 points**
- Points accumulate in user's `total_score`

### Question Selection
- Prioritizes unanswered questions for logged-in users
- Falls back to random selection when all questions answered
- Tracks attempts in Score table

### Leaderboard
- Shows all users ranked by total score
- Paginated (50 users per page)
- Highlights current user's row
- Shows medals (🥇🥈🥉) for top 3
- Displays current user's rank badge at top

### Profile Statistics
- Total score
- Average score per quiz
- Total quizzes taken
- Recent quiz history (clickable to review questions)

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
rm instance/quiz.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python seed_questions.py
```

### Missing Questions
```bash
# Reseed questions
python seed_questions.py
# Choose 'yes' when prompted to clear and reload
```

### Weather Widget Not Working
- Check `WEATHER_API_KEY` in `.env` file
- Verify API key at https://openweathermap.org/api
- Check browser console for errors

## 📄 License

This project is created for educational purposes as part of the Kodland Python Pro course.

## 👨‍💻 Development

Built with ❤️ for learning Python, Flask, and AI concepts through interactive quizzes.