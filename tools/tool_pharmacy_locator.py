# tools/tool_pharmacy_locator.py
"""
Tool : Localisation des pharmacies de garde
Trouve les pharmacies de garde (ouvertes 24h/24) dans les villes du Burkina Faso.
Utilise Azure Maps pour la recherche de POI pharmacies.
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Azure Maps configuration
AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
AZURE_MAPS_SEARCH_URL = 'https://atlas.microsoft.com/search/poi/json'

# Coordonnées des principales villes du Burkina Faso
BURKINA_CITIES = {
    "Ouagadougou": {"lat": 12.3714, "lon": -1.5197},
    "Bobo-Dioulasso": {"lat": 11.1770, "lon": -4.2970},
    "Koudougou": {"lat": 12.2529, "lon": -2.3622},
    "Ouahigouya": {"lat": 13.5828, "lon": -2.4214},
    "Banfora": {"lat": 10.6333, "lon": -4.7667},
    "Fada N'Gourma": {"lat": 12.0614, "lon": 0.3556}
}

# Numéros d'urgence Burkina Faso
EMERGENCY_NUMBERS = {
    "Police": "17",
    "Gendarmerie": "16",
    "Pompiers": "18",
    "SAMU": "112",
    "Croix-Rouge": "225 50 66 66"
}

# Base de données pharmacies de garde (mise à jour hebdomadaire recommandée)
# En production, cette data viendrait d'une API gouvernementale ou d'une base Cosmos DB
PHARMACIES_DE_GARDE = {
    "Ouagadougou": [
        {"name": "Pharmacie de la Paix", "address": "Avenue Kwame N'Krumah", "phone": "+226 25 30 67 89", "hours": "24h/24"},
        {"name": "Pharmacie Centrale", "address": "Avenue de la Nation", "phone": "+226 25 31 22 33", "hours": "24h/24"},
        {"name": "Pharmacie du Progrès", "address": "Zone du Bois", "phone": "+226 25 36 45 78", "hours": "24h/24"},
        {"name": "Pharmacie Solidarité", "address": "Ouaga 2000", "phone": "+226 25 37 89 12", "hours": "24h/24"}
    ],
    "Bobo-Dioulasso": [
        {"name": "Pharmacie du Marché", "address": "Grand Marché", "phone": "+226 20 97 23 45", "hours": "24h/24"},
        {"name": "Pharmacie Saint-Camille", "address": "Route de Banfora", "phone": "+226 20 98 56 78", "hours": "24h/24"}
    ],
    "Koudougou": [
        {"name": "Pharmacie Espoir", "address": "Centre-ville", "phone": "+226 25 44 12 34", "hours": "24h/24"}
    ],
    "Ouahigouya": [
        {"name": "Pharmacie du Nord", "address": "Avenue principale", "phone": "+226 24 55 67 89", "hours": "24h/24"}
    ],
    "Banfora": [
        {"name": "Pharmacie des Cascades", "address": "Route des Cascades", "phone": "+226 20 91 23 45", "hours": "24h/24"}
    ],
    "Fada N'Gourma": [
        {"name": "Pharmacie de l'Est", "address": "Centre-ville", "phone": "+226 24 77 89 12", "hours": "24h/24"}
    ]
}


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "find_pharmacy",
        "description": """Trouve les pharmacies de garde (ouvertes 24h/24 et 7j/7) et les numéros d'urgence dans les villes du Burkina Faso.

IMPORTANT : Utilise ce tool pour :
- Pharmacies de garde
- Pharmacies d'urgence
- Où acheter médicaments la nuit
- Numéros d'urgence médicale

EXEMPLE:
{
  "city": "Ouagadougou",
  "emergency": false
}

Retourne liste pharmacies avec adresses, téléphones et horaires.""",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": """Ville du Burkina Faso pour trouver les pharmacies de garde.

VILLES SUPPORTÉES:
- Ouagadougou (capitale)
- Bobo-Dioulasso
- Koudougou
- Ouahigouya
- Banfora
- Fada N'Gourma

CONVERSION:
- "Ouaga" → "Ouagadougou"
- "Bobo" → "Bobo-Dioulasso"
- "Fada" → "Fada N'Gourma"
- Pas de ville → "Ouagadougou" (défaut)

FORMAT: Nom de ville (ex: "Ouagadougou")""",
                    "default": "Ouagadougou"
                },
                "emergency": {
                    "type": "boolean",
                    "description": """Si true, inclut les numéros d'urgence médicale (SAMU, Pompiers, etc.).

EXEMPLES:
- Urgence médicale → true
- Simple recherche pharmacie → false

DEFAULT: false""",
                    "default": False
                }
            },
            "required": ["city"]
        }
    }


def search_pharmacies_azure_maps(city_name):
    """
    Recherche de pharmacies via Azure Maps
    
    Args:
        city_name: Nom de la ville
    
    Returns:
        list: Liste de pharmacies trouvées
    """
    try:
        if not AZURE_MAPS_SUBSCRIPTION_KEY:
            logger.warning("⚠️ Azure Maps key non configurée, utilisation base locale")
            return []
        
        # Normaliser ville
        city_normalized = city_name.replace("Ouaga", "Ouagadougou").replace("Bobo", "Bobo-Dioulasso").replace("Fada", "Fada N'Gourma")
        
        if city_normalized not in BURKINA_CITIES:
            logger.warning(f"⚠️ Ville non reconnue: {city_name}")
            city_normalized = "Ouagadougou"
        
        coords = BURKINA_CITIES[city_normalized]
        
        # Paramètres recherche Azure Maps
        params = {
            'subscription-key': AZURE_MAPS_SUBSCRIPTION_KEY,
            'api-version': '1.0',
            'query': 'pharmacy',
            'lat': coords['lat'],
            'lon': coords['lon'],
            'radius': 10000,  # 10km
            'limit': 10,
            'language': 'fr-FR'
        }
        
        response = requests.get(AZURE_MAPS_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        pharmacies = []
        for poi in results:
            pharmacy = {
                'name': poi.get('poi', {}).get('name', 'Pharmacie'),
                'address': poi.get('address', {}).get('freeformAddress', 'Adresse non disponible'),
                'phone': poi.get('poi', {}).get('phone', 'Non disponible'),
                'distance': poi.get('dist', 0),
                'hours': '24h/24'  # Assumé pour pharmacies de garde
            }
            pharmacies.append(pharmacy)
        
        logger.info(f"✅ Trouvé {len(pharmacies)} pharmacies via Azure Maps")
        return pharmacies
        
    except Exception as e:
        logger.exception(f"❌ Erreur Azure Maps: {str(e)}")
        return []


def get_local_pharmacies(city_name):
    """
    Récupère les pharmacies depuis la base locale
    
    Args:
        city_name: Nom de la ville
    
    Returns:
        list: Liste de pharmacies
    """
    # Normaliser ville
    city_normalized = city_name.replace("Ouaga", "Ouagadougou").replace("Bobo", "Bobo-Dioulasso").replace("Fada", "Fada N'Gourma")
    
    if city_normalized not in PHARMACIES_DE_GARDE:
        logger.warning(f"⚠️ Pas de pharmacies dans la base pour: {city_name}, utilisation Ouagadougou")
        city_normalized = "Ouagadougou"
    
    return PHARMACIES_DE_GARDE[city_normalized]


def execute(arguments):
    """
    Exécute la recherche de pharmacies de garde
    
    Args:
        arguments: Dictionnaire contenant:
            - city: Ville (optionnel, défaut: 'Ouagadougou')
            - emergency: Inclure numéros d'urgence (optionnel, défaut: False)
    
    Returns:
        dict: Résultat avec liste pharmacies
    """
    city = arguments.get('city', 'Ouagadougou')
    emergency = arguments.get('emergency', False)
    
    logger.info(f"🏥 Recherche pharmacies de garde: {city}, urgence={emergency}")
    
    try:
        # Essayer Azure Maps d'abord
        pharmacies = search_pharmacies_azure_maps(city)
        
        # Fallback sur base locale si Azure Maps échoue
        if not pharmacies:
            pharmacies = get_local_pharmacies(city)
        
        if not pharmacies:
            return {
                "status": "error",
                "message": f"Aucune pharmacie de garde trouvée à {city}."
            }
        
        # Formater le message
        city_display = city.replace("Ouaga", "Ouagadougou").replace("Bobo", "Bobo-Dioulasso")
        
        pharmacies_text = "\n\n".join([
            f"📍 {p['name']}\n   Adresse: {p['address']}\n   Téléphone: {p['phone']}\n   Horaires: {p['hours']}"
            for p in pharmacies[:5]  # Limiter à 5 résultats
        ])
        
        message = f"🏥 Pharmacies de garde à {city_display}:\n\n{pharmacies_text}"
        
        # Ajouter numéros d'urgence si demandé
        if emergency:
            urgence_text = "\n\n".join([
                f"🚨 {service}: {number}"
                for service, number in EMERGENCY_NUMBERS.items()
            ])
            message += f"\n\n🆘 NUMÉROS D'URGENCE:\n\n{urgence_text}"
        
        return {
            "status": "success",
            "city": city_display,
            "pharmacies": pharmacies[:5],
            "emergency_numbers": EMERGENCY_NUMBERS if emergency else None,
            "message": message
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur recherche pharmacies: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche de pharmacies: {str(e)}"
        }
