import os
from flask import Blueprint, request, jsonify, Response
from dotenv import load_dotenv
from .services import get_weather_forecast, search_cities_api

load_dotenv()

weather_routes = Blueprint('weather', __name__)


@weather_routes.route('/weather', methods=['POST'])
def get_weather():
    """API endpoint to get weather forecast"""
    data = request.get_json()
    
    if not data or 'city' not in data:
        return jsonify({'error': 'Parameter <city> is required'}), 400
    
    city_name = data['city']
    forecast = get_weather_forecast(city_name)
    
    if forecast is None:
        return jsonify({'error': 'Could not retrieve weather data'}), 500
    
    return jsonify({'forecast': forecast}), 200


@weather_routes.route('/search-cities', methods=['GET'])
def search_cities():
    """City search endpoint for autocomplete"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'cities': []}), 200
    
    api_key = os.getenv('WEATHER_API_KEY')
    results = search_cities_api(query, api_key)
    
    cities = [
        {
            'name': city['name'],
            'country': city['country'],
            'display': f"{city['name']}, {city['country']}"
        }
        for city in results[:5]
    ]
    
    return jsonify({'cities': cities}), 200
