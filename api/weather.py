import os
from flask import Blueprint, request, jsonify, Response
from dotenv import load_dotenv
from .services import get_weather_forecast, search_cities_api

load_dotenv()

weather_routes = Blueprint('weather', __name__)

@weather_routes.route('/weather', methods=['POST'])
def get_weather() -> Response:
    """
    Endpoint API to obtain weather forecast.
    Accepts POST with JSON: {"city": "city_name"}
    Returns JSON with forecast or error.
    """
    data = request.get_json()
    
    if not data or 'city' not in data:
        response = jsonify({'error': 'Parameter <city> is required'})
        response.status_code = 400
        return response
    
    city_name = data['city']
    forecast = get_weather_forecast(city_name)
    
    if forecast is None:
        response = jsonify({'error': 'Could not retrieve weather data'})
        response.status_code = 500
        return response
    
    response = jsonify({'forecast': forecast})
    response.status_code = 200
    return response


@weather_routes.route('/search-cities', methods=['GET'])
def search_cities() -> Response:
    """
    Endpoint to search cities (autocomplete).
    Accepts GET with parameter ?q=query
    """
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        response = jsonify({'cities': []})
        response.status_code = 200
        return response
    
    api_key = os.getenv('WEATHER_API_KEY')
    results = search_cities_api(query, api_key)
    
    # Format results for autocomplete
    cities = [
        {
            'name': city['name'],
            'country': city['country'],
            'display': f"{city['name']}, {city['country']}"
        }
        for city in results[:5]  # Limit to 5 results
    ]
    
    response = jsonify({'cities': cities})
    response.status_code = 200
    return response
