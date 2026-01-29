# tools/tool_prayer_times.py
"""
Tool : Horaires de prière islamique
Fournit les horaires des 5 prières quotidiennes pour les villes du Burkina Faso.
"""

import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# API Aladhan pour horaires de prière (gratuite)
ALADHAN_API_URL = 'http://api.aladhan.com/v1/timingsByCity'

# Coordonnées des principales villes du Burkina Faso
BURKINA_CITIES = {
    "Ouagadougou": {"country": "Burkina Faso", "latitude": 12.3714, "longitude": -1.5197},
    "Bobo-Dioulasso": {"country": "Burkina Faso", "latitude": 11.1770, "longitude": -4.2970},
    "Koudougou": {"country": "Burkina Faso", "latitude": 12.2529, "longitude": -2.3622},
    "Ouahigouya": {"country": "Burkina Faso", "latitude": 13.5828, "longitude": -2.4214},
    "Banfora": {"country": "Burkina Faso", "latitude": 10.6333, "longitude": -4.7667},
    "Fada N'Gourma": {"country": "Burkina Faso", "latitude": 12.0614, "longitude": 0.3556},
    "Kaya": {"country": "Burkina Faso", "latitude": 13.0916, "longitude": -1.0849},
    "Tenkodogo": {"country": "Burkina Faso", "latitude": 11.7833, "longitude": -0.3667},
    "Dédougou": {"country": "Burkina Faso", "latitude": 12.4631, "longitude": -3.4606},
    "Réo": {"country": "Burkina Faso", "latitude": 12.3167, "longitude": -2.4667}
}


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "get_prayer_times",
        "description": """Fournit les horaires des 5 prières quotidiennes islamiques (Fajr, Dhuhr, Asr, Maghrib, Isha) pour une ville du Burkina Faso.

IMPORTANT : Utilise ce tool uniquement pour les demandes concernant les horaires de prière islamique.

EXEMPLE:
{
  "city": "Ouagadougou",
  "date": "2025-11-17"
}

Retourne les 5 horaires de prière avec les noms en arabe et français.""",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": """Ville du Burkina Faso pour laquelle obtenir les horaires de prière.

VILLES SUPPORTÉES:
- Ouagadougou (capitale)
- Bobo-Dioulasso (2ème ville)
- Koudougou
- Ouahigouya
- Banfora
- Fada N'Gourma
- Kaya
- Tenkodogo
- Dédougou
- Réo

CONVERSION:
- "Ouaga" → "Ouagadougou"
- "Bobo" → "Bobo-Dioulasso"
- "Fada" → "Fada N'Gourma"
- Pas de ville mentionnée → "Ouagadougou" (défaut)

FORMAT: Nom de ville (ex: "Ouagadougou")""",
                    "default": "Ouagadougou"
                },
                "date": {
                    "type": "string",
                    "description": """Date pour laquelle obtenir les horaires (format YYYY-MM-DD).

EXEMPLES:
- "2025-11-17" (format ISO)
- Aujourd'hui → date du jour
- Demain → date du jour + 1
- Pas de date → aujourd'hui (défaut)

FORMAT: YYYY-MM-DD (ex: "2025-11-17")""",
                    "default": "today"
                }
            },
            "required": ["city"]
        }
    }


def get_prayer_times_from_api(city, date_str):
    """
    Récupère les horaires de prière depuis l'API Aladhan.
    
    Args:
        city: Nom de la ville
        date_str: Date au format YYYY-MM-DD ou "today"
    
    Returns:
        dict: Horaires de prière ou None si erreur
    """
    try:
        # Normaliser le nom de ville
        city_normalized = city.replace("Ouaga", "Ouagadougou").replace("Bobo", "Bobo-Dioulasso").replace("Fada", "Fada N'Gourma")
        
        if city_normalized not in BURKINA_CITIES:
            logger.warning(f"⚠️ Ville non reconnue: {city}, utilisation de Ouagadougou par défaut")
            city_normalized = "Ouagadougou"
        
        city_info = BURKINA_CITIES[city_normalized]
        
        # Date
        if date_str == "today" or not date_str:
            date_obj = datetime.now()
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Paramètres API
        params = {
            'city': city_normalized,
            'country': city_info['country'],
            'method': 2,  # ISNA (Islamic Society of North America)
            'date': date_obj.strftime('%d-%m-%Y')
        }
        
        # Requête API
        response = requests.get(ALADHAN_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') != 200:
            logger.error(f"❌ Erreur API Aladhan: {data}")
            return None
        
        timings = data['data']['timings']
        date_info = data['data']['date']
        
        # Extraire les 5 prières principales
        prayers = {
            'Fajr': {'name_fr': 'Fajr (Aube)', 'time': timings['Fajr'].split(' ')[0]},
            'Dhuhr': {'name_fr': 'Dhuhr (Midi)', 'time': timings['Dhuhr'].split(' ')[0]},
            'Asr': {'name_fr': 'Asr (Après-midi)', 'time': timings['Asr'].split(' ')[0]},
            'Maghrib': {'name_fr': 'Maghrib (Coucher du soleil)', 'time': timings['Maghrib'].split(' ')[0]},
            'Isha': {'name_fr': 'Isha (Nuit)', 'time': timings['Isha'].split(' ')[0]}
        }
        
        return {
            'city': city_normalized,
            'date': date_obj.strftime('%d/%m/%Y'),
            'date_hijri': f"{date_info['hijri']['day']} {date_info['hijri']['month']['en']} {date_info['hijri']['year']}",
            'prayers': prayers,
            'sunrise': timings.get('Sunrise', '').split(' ')[0],
            'sunset': timings.get('Sunset', '').split(' ')[0]
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur récupération horaires de prière: {str(e)}")
        return None


def execute(arguments):
    """
    Exécute la recherche des horaires de prière
    
    Args:
        arguments: Dictionnaire contenant:
            - city: Ville (optionnel, défaut: 'Ouagadougou')
            - date: Date (optionnel, défaut: 'today')
    
    Returns:
        dict: Résultat avec horaires de prière
    """
    city = arguments.get('city', 'Ouagadougou')
    date_str = arguments.get('date', 'today')
    
    logger.info(f"🕌 Récupération horaires de prière: {city}, {date_str}")
    
    try:
        result = get_prayer_times_from_api(city, date_str)
        
        if not result:
            return {
                "status": "error",
                "message": "Impossible de récupérer les horaires de prière. Veuillez réessayer."
            }
        
        # Formater le message
        prayers_text = "\n".join([
            f"• {prayer['name_fr']}: {prayer['time']}"
            for prayer in result['prayers'].values()
        ])
        
        return {
            "status": "success",
            "city": result['city'],
            "date": result['date'],
            "date_hijri": result['date_hijri'],
            "prayers": result['prayers'],
            "sunrise": result['sunrise'],
            "sunset": result['sunset'],
            "message": f"🕌 Horaires de prière à {result['city']} le {result['date']} ({result['date_hijri']}):\n\n{prayers_text}\n\n🌅 Lever du soleil: {result['sunrise']}\n🌇 Coucher du soleil: {result['sunset']}"
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur horaires de prière: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des horaires de prière: {str(e)}"
        }
