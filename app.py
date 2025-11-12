# Importing bleach to sanitize user input for possible xss attacks
import bleach

from flask import Flask, render_template, request
from api.services import get_weather_forecast
from api import api_bp

app = Flask(__name__)

app.register_blueprint(api_bp)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    forecast = None
    error = None
    city = None
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        city = bleach.clean(city, tags=[], strip=True)  # Strip all HTML
        force_refresh = request.form.get('force_refresh') == '1'
        
        # Sanitize input and validate length
        if city and len(city) <= 100:
            forecast = get_weather_forecast(city, force_refresh=force_refresh)
            if forecast is None:
                error = f"Impossible adding weather data for '{city}'"
        else:
            error = "Please enter a valid city name (1-100 characters)."
    
    return render_template('index.html', forecast=forecast, error=error, city=city)