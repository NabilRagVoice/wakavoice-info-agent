# tools/tool_weather.py
"""
Outil de prévisions météo via WeatherAPI
Fournit la météo actuelle et les prévisions sur plusieurs jours
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
DEFAULT_COUNTRY = "Burkina Faso"


def get_tool_definition():
    """Retourne la définition du tool get_weather_forecast"""
    return {
        "type": "function",
        "name": "get_weather_forecast",
        "description": "Prévisions météo pour une ville (température, pluie, vent).",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nom de la ville (ex: Ouagadougou, Paris)."
                },
                "country": {
                    "type": "string",
                    "description": "Pays (défaut: Burkina Faso).",
                    "default": "Burkina Faso"
                },
                "days": {
                    "type": "integer",
                    "description": "Nb jours prévisions (1-5, défaut 3).",
                    "default": 3
                }
            },
            "required": ["city"]
        }
    }


def get_weather_forecast(city, country=DEFAULT_COUNTRY, days=3):
    """
    Obtient les prévisions météo pour une ville avec WeatherAPI.
    
    Args:
        city: Nom de la ville
        country: Pays (optionnel)
        days: Nombre de jours de prévisions (1-5)
    
    Returns:
        dict: Résultat avec météo actuelle et prévisions
    """
    if not WEATHER_API_KEY:
        return {
            "status": "error",
            "message": "WEATHER_API_KEY non configuré dans le fichier .env"
        }
    
    try:
        # Limiter le nombre de jours (1-5)
        days = min(max(1, days), 5)
        
        # WeatherAPI.com - Forecast
        endpoint = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": f"{city},{country}",
            "days": days,
            "lang": "fr",
            "aqi": "no",
            "alerts": "no"
        }
        
        response = requests.get(endpoint, params=params, timeout=10)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Erreur API WeatherAPI: {response.status_code}",
                "details": response.text
            }
        
        data = response.json()
        
        # Météo actuelle
        current = {
            "temperature": data["current"]["temp_c"],
            "feels_like": data["current"]["feelslike_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"],
            "wind_dir": data["current"]["wind_dir"],
            "pressure_mb": data["current"]["pressure_mb"],
            "precipitation_mm": data["current"]["precip_mm"],
            "cloud": data["current"]["cloud"],
            "uv": data["current"]["uv"],
            "last_updated": data["current"]["last_updated"]
        }
        
        # Prévisions
        forecasts = []
        for day in data["forecast"]["forecastday"]:
            forecasts.append({
                "date": day["date"],
                "max_temp": day["day"]["maxtemp_c"],
                "min_temp": day["day"]["mintemp_c"],
                "avg_temp": day["day"]["avgtemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"],
                "total_precipitation_mm": day["day"]["totalprecip_mm"],
                "max_wind_kph": day["day"]["maxwind_kph"],
                "avg_humidity": day["day"]["avghumidity"],
                "uv": day["day"]["uv"],
                "sunrise": day["astro"]["sunrise"],
                "sunset": day["astro"]["sunset"]
            })
        
        return {
            "status": "success",
            "type": "forecast",
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "region": data["location"]["region"],
            "current": current,
            "days_count": len(forecasts),
            "forecasts": forecasts
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Timeout lors de l'appel à l'API météo. Veuillez réessayer."
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Erreur de connexion à l'API météo: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des prévisions météo: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    city = arguments.get("city", "")
    country = arguments.get("country", DEFAULT_COUNTRY)
    days = arguments.get("days", 3)
    
    return get_weather_forecast(city, country, days)
