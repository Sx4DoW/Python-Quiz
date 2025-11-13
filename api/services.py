import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

_weather_cache = {}
WEATHER_CACHE_TTL_HOURS = 6

CITIES_CACHE_FILE = 'cache_cities.json'
CITIES_CACHE_TTL_DAYS = 30


def _load_cities_cache():
    """Load city cache from disk"""
    if os.path.exists(CITIES_CACHE_FILE):
        try:
            with open(CITIES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_cities_cache(cache_data):
    """Save city cache to disk"""
    try:
        with open(CITIES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error saving city cache: {e}")


_cities_cache = _load_cities_cache()


def _get_from_weather_cache(key):
    """Get weather from cache if still valid"""
    if key in _weather_cache:
        data, timestamp = _weather_cache[key]
        if datetime.now() - timestamp < timedelta(hours=WEATHER_CACHE_TTL_HOURS):
            return data
        else:
            del _weather_cache[key]
    return None


def _set_weather_cache(key, value):
    """Save weather to cache"""
    _weather_cache[key] = (value, datetime.now())


def _get_from_cities_cache(key):
    """Get city from cache if still valid"""
    if key in _cities_cache:
        data, timestamp_str = _cities_cache[key]
        timestamp = datetime.fromisoformat(timestamp_str)
        if datetime.now() - timestamp < timedelta(days=CITIES_CACHE_TTL_DAYS):
            return data
        else:
            del _cities_cache[key]
            _save_cities_cache(_cities_cache)
    return None


def _set_cities_cache(key, value):
    """Save city to cache"""
    _cities_cache[key] = (value, datetime.now().isoformat())
    _save_cities_cache(_cities_cache)


def search_cities_api(query, api_key=None):
    """Search cities using WeatherAPI.com with caching"""
    if not query or len(query) < 2:
        return []
    
    cache_key = f"search_{query.lower()}"
    cached = _get_from_cities_cache(cache_key)
    if cached is not None:
        return cached
    
    if api_key is None:
        api_key = os.getenv('WEATHER_API_KEY')
    
    base_url = "http://api.weatherapi.com/v1/search.json"
    params = {'key': api_key, 'q': query}
    
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        response.encoding = 'utf-8'
        results = response.json()
        
        _set_cities_cache(cache_key, results)
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error searching cities: {e}")
        return []


def get_weather_forecast(city_name, api_key=None, force_refresh=False):
    """Retrieve 3-day weather forecast using WeatherAPI.com"""
    if not city_name or not city_name.strip():
        return None
    
    city_name = city_name.strip()
    
    if not all(c.isalnum() or c.isspace() or c in '-,.' for c in city_name):
        return None

    if api_key is None:
        api_key = os.getenv('WEATHER_API_KEY')
    
    search_results = search_cities_api(city_name, api_key)
    
    if not search_results:
        print(f"City not found: {city_name}")
        return None
    
    validated_city = search_results[0]['name']
    
    cache_key = f"weather_{validated_city.lower()}"
    if not force_refresh:
        cached = _get_from_weather_cache(cache_key)
        if cached is not None:
            return cached
    
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': validated_city,
        'days': 3,
        'lang': 'it'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        data = response.json()
        
        forecast_list = []
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in data['forecast']['forecastday']:
            dt = datetime.strptime(day['date'], '%Y-%m-%d')
            
            forecast_list.append({
                'date': day['date'],
                'day_name': day_names[dt.weekday()],
                'day_temp': round(day['day']['maxtemp_c']),
                'night_temp': round(day['day']['mintemp_c'])
            })
        
        _set_weather_cache(cache_key, forecast_list)
        return forecast_list
        
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing data: {e}")
        return None
