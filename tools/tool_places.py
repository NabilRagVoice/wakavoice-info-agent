# tools/tool_places.py
"""
Tool : Recherche de lieux
Permet de rechercher des lieux, adresses, points d'intérêt via Azure Maps Search API.
"""

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration Azure Maps
AZURE_MAPS_KEY = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "search_places",
        "description": """Recherche des lieux, adresses ou points d'intérêt en temps réel via Azure Maps.

CAPACITÉS:
- Restaurants, cafés, bars
- Pharmacies, hôpitaux, cliniques
- Banques, distributeurs ATM
- Hôtels, hébergements
- Magasins, supermarchés
- Monuments, sites touristiques
- Stations-service, garages
- Écoles, universités

EXEMPLES D'UTILISATION:
- "restaurant italien Ouagadougou"
- "pharmacie Zone 4"
- "hôpital Bobo-Dioulasso"
- "banque près de moi"
- "supermarché Ouaga 2000"

RÉSULTATS INCLUENT:
- Nom et adresse complète
- Téléphone (si disponible)
- Coordonnées GPS (latitude/longitude)
- Distance depuis le centre-ville
- Catégorie du lieu""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Type de lieu à rechercher avec optionnellement le quartier/zone.
                    
EXEMPLES:
- "restaurant" → tous les restaurants
- "restaurant italien" → restaurants italiens uniquement
- "pharmacie Zone 4" → pharmacies dans la Zone 4
- "hôpital" → tous les hôpitaux
- "ATM Ouaga 2000" → distributeurs dans Ouaga 2000

CATÉGORIES POPULAIRES:
Restaurant, Café, Pharmacie, Hôpital, Banque, ATM, Hôtel, Supermarché, Station-service, Garage, École, Université"""
                },
                "location": {
                    "type": "string",
                    "description": """Ville ou localisation pour centrer la recherche.
                    
EXEMPLES:
- "Ouagadougou" (défaut)
- "Bobo-Dioulasso"
- "Koudougou"
- "Ouahigouya"

Si l'utilisateur mentionne une zone/quartier dans la query (ex: 'pharmacie Zone 4'), garde 'Ouagadougou' ici.""",
                    "default": "Ouagadougou"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Nombre maximum de lieux à retourner (1-10). Défaut: 5",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }


def search_places_azure_maps(query, location, max_results):
    """
    Recherche de lieux via Azure Maps Search API
    
    Documentation: https://learn.microsoft.com/en-us/rest/api/maps/search/get-search-fuzzy
    
    Args:
        query: Type de lieu à rechercher
        location: Ville de recherche
        max_results: Nombre max de résultats
        
    Returns:
        list: Liste de lieux trouvés
    """
    if not AZURE_MAPS_KEY:
        logger.error("❌ AZURE_MAPS_SUBSCRIPTION_KEY manquant dans .env")
        return []
    
    try:
        # Azure Maps Search API - Fuzzy Search
        url = "https://atlas.microsoft.com/search/fuzzy/json"
        
        # Coordonnées des principales villes du Burkina Faso
        city_coords = {
            "Ouagadougou": "12.3714,1.5197",
            "Bobo-Dioulasso": "11.1770,4.2970",
            "Koudougou": "12.2529,2.3622",
            "Ouahigouya": "13.5828,2.4214",
            "Banfora": "10.6333,4.7667",
            "Fada N'Gourma": "12.0614,0.3556"
        }
        
        # Obtenir les coordonnées de la ville
        lat_lon = city_coords.get(location, city_coords["Ouagadougou"])
        
        # Construire la requête complète
        search_query = f"{query}, {location}, Burkina Faso"
        
        params = {
            "subscription-key": AZURE_MAPS_KEY,
            "api-version": "1.0",
            "query": search_query,
            "lat": lat_lon.split(',')[0],
            "lon": lat_lon.split(',')[1],
            "radius": 50000,  # 50km de rayon
            "limit": max_results,
            "language": "fr-FR",
            "view": "Auto"
        }
        
        logger.info(f"🔍 Azure Maps Search: {search_query}")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"❌ Azure Maps API erreur {response.status_code}: {response.text}")
            return []
        
        data = response.json()
        results = data.get('results', [])
        
        places = []
        for result in results:
            place = {
                "name": result.get('poi', {}).get('name', result.get('address', {}).get('freeformAddress', 'Lieu sans nom')),
                "address": result.get('address', {}).get('freeformAddress', 'Adresse non disponible'),
                "phone": result.get('poi', {}).get('phone', 'Non renseigné'),
                "category": result.get('poi', {}).get('categories', ['Autre'])[0] if result.get('poi', {}).get('categories') else 'Autre',
                "position": {
                    "latitude": result.get('position', {}).get('lat'),
                    "longitude": result.get('position', {}).get('lon')
                },
                "distance_meters": result.get('dist', 0),
                "distance_km": round(result.get('dist', 0) / 1000, 2)
            }
            places.append(place)
        
        logger.info(f"✅ {len(places)} lieu(x) trouvé(s)")
        return places
        
    except Exception as e:
        logger.exception(f"❌ Erreur Azure Maps: {str(e)}")
        return []


def execute(arguments):
    """
    Exécute la recherche de lieux via Azure Maps
    
    Args:
        arguments: Dictionnaire contenant:
            - query: Type de lieu à rechercher
            - location: Ville (optionnel, défaut: 'Ouagadougou')
            - max_results: Nombre de résultats (optionnel, défaut: 5)
    
    Returns:
        dict: Résultat de la recherche
    """
    query = arguments.get('query', '')
    location = arguments.get('location', 'Ouagadougou')
    max_results = min(int(arguments.get('max_results', 5)), 10)
    
    logger.info(f"📍 Recherche lieux: '{query}' à {location} (max: {max_results})")
    
    if not query:
        return {
            "status": "error",
            "message": "Veuillez spécifier un type de lieu à rechercher (ex: 'restaurant', 'pharmacie', 'hôtel')"
        }
    
    try:
        # Recherche via Azure Maps
        places = search_places_azure_maps(query, location, max_results)
        
        if not places:
            return {
                "status": "no_results",
                "query": query,
                "location": location,
                "message": f"Aucun lieu trouvé pour '{query}' à {location}. Essayez une autre recherche.",
                "suggestions": [
                    "Utilisez des termes plus généraux (ex: 'restaurant' au lieu de 'restaurant italien')",
                    "Vérifiez l'orthographe de la ville",
                    "Essayez une autre ville proche"
                ]
            }
        
        return {
            "status": "success",
            "query": query,
            "location": location,
            "total_results": len(places),
            "places": places,
            "message": f"✅ {len(places)} lieu(x) trouvé(s) pour '{query}' à {location}",
            "note": "Résultats triés par proximité depuis le centre de la ville"
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur recherche lieux: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche de lieux: {str(e)}",
            "fallback": "Veuillez réessayer dans quelques instants"
        }
