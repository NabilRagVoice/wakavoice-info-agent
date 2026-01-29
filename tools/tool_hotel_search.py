# tools/tool_hotel_search.py
"""
Outil de recherche d'hôtels via Amadeus API
Permet de rechercher des hôtels disponibles avec prix et disponibilité
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")
AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "test.api.amadeus.com")


def get_amadeus_token():
    """
    Obtient un token d'accès OAuth2 pour l'API Amadeus.
    
    Returns:
        str: Token d'accès ou None en cas d'erreur
    """
    try:
        url = f"https://{AMADEUS_BASE_URL}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_API_KEY,
            "client_secret": AMADEUS_API_SECRET
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code != 200:
            return None
        
        token_data = response.json()
        return token_data.get("access_token")
        
    except Exception as e:
        print(f"Erreur obtention token Amadeus: {e}")
        return None


def get_tool_definition():
    """Retourne la définition du tool search_hotels"""
    return {
        "type": "function",
        "name": "search_hotels",
        "description": """OUTIL PRIORITAIRE pour rechercher des HÔTELS avec prix et disponibilité en temps réel.
        
UTILISATION OBLIGATOIRE pour toute demande concernant:
- Hôtels, hébergements, chambres d'hôtel
- Où dormir, où loger, où séjourner
- Réserver un hôtel, trouver un hôtel
- Hôtels pas chers, hôtels de luxe

NE JAMAIS utiliser search_web pour les hôtels - toujours utiliser cet outil.

CODES DE VILLES (IATA - 3 lettres majuscules):
Afrique de l'Ouest:
- OUA = Ouagadougou (Burkina Faso)
- ABJ = Abidjan (Côte d'Ivoire)
- DKR = Dakar (Sénégal)
- ACC = Accra (Ghana)
- LOS = Lagos (Nigeria)
- BKO = Bamako (Mali)
- NIM = Niamey (Niger)
- LFW = Lomé (Togo)
- COO = Cotonou (Bénin)

Europe:
- PAR = Paris (France) - utilise PAR, pas CDG pour les hôtels
- LON = Londres (UK)
- MAD = Madrid (Espagne)
- ROM = Rome (Italie)
- BER = Berlin (Allemagne)

Si tu ne connais pas le code IATA d'une ville, devine les 3 premières lettres du nom de la ville en majuscules.""",
        "parameters": {
            "type": "object",
            "properties": {
                "city_code": {
                    "type": "string",
                    "description": """Code IATA de la VILLE où chercher des hôtels (exactement 3 lettres majuscules).
                    
IMPORTANT: Pour les hôtels, utilise le code de VILLE, pas d'aéroport!
- Pour Paris: utilise "PAR" (pas "CDG")
- Pour Londres: utilise "LON" (pas "LHR")
- Pour Ouagadougou: utilise "OUA"

EXEMPLES VALIDES:
- "OUA" pour Ouagadougou
- "PAR" pour Paris
- "ABJ" pour Abidjan
- "DKR" pour Dakar

CONVERSION depuis langage naturel:
- "hôtel à Ouagadougou" → "OUA"
- "dormir à Paris" → "PAR"
- "hébergement à Abidjan" → "ABJ"

FORMAT ATTENDU: Exactement 3 lettres majuscules (ex: "OUA", pas "Ouagadougou" ni "oua")"""
                },
                "check_in_date": {
                    "type": "string",
                    "description": """Date d'ARRIVÉE à l'hôtel (check-in) au format YYYY-MM-DD.
                    
EXEMPLES VALIDES:
- "2025-12-15" pour le 15 décembre 2025
- "2025-11-25" pour le 25 novembre 2025
- "2026-01-10" pour le 10 janvier 2026

CONVERSION depuis langage naturel:
- "demain" → calcule la date de demain au format YYYY-MM-DD
- "le 15 décembre" → "2025-12-15"
- "dans 5 jours" → calcule J+5 au format YYYY-MM-DD
- "lundi prochain" → calcule le prochain lundi
- "ce weekend" → calcule le prochain samedi

FORMAT ATTENDU: YYYY-MM-DD avec zéros (ex: "2025-01-05", pas "2025-1-5" ni "15/12/2025")"""
                },
                "check_out_date": {
                    "type": "string",
                    "description": """Date de DÉPART de l'hôtel (check-out) au format YYYY-MM-DD.
                    
EXEMPLES VALIDES:
- "2025-12-20" pour le 20 décembre 2025
- "2025-11-30" pour le 30 novembre 2025

REMARQUES IMPORTANTES:
- La date de check-out doit être APRÈS la date de check-in
- Minimum 1 nuit de séjour
- Si l'utilisateur dit "3 nuits", calcule: check_out = check_in + 3 jours

CONVERSION depuis langage naturel:
- "pour 2 nuits" → check_in + 2 jours
- "du 15 au 20 décembre" → check_in="2025-12-15", check_out="2025-12-20"
- "une semaine" → check_in + 7 jours

FORMAT ATTENDU: YYYY-MM-DD avec zéros (ex: "2025-12-20", pas "20/12/2025")"""
                },
                "adults": {
                    "type": "integer",
                    "description": """Nombre d'ADULTES par chambre.
                    
EXEMPLES VALIDES:
- 1 (par défaut - une personne seule)
- 2 (couple ou deux personnes)
- 3 (trois adultes)

CONVERSION depuis langage naturel:
- "pour moi seul" → 1
- "pour deux personnes" → 2
- "couple" → 2
- "nous sommes 4" → 4 (mais pense aussi à augmenter le nombre de chambres si nécessaire)

REMARQUE: Si l'utilisateur dit "nous sommes 4 personnes", tu peux:
- Soit mettre 4 adultes dans 1 chambre (chambre familiale)
- Soit mettre 2 adultes et rooms=2 (deux chambres doubles)
Demande clarification si ambigu.

LIMITES: Entre 1 et 9 adultes par chambre.

FORMAT ATTENDU: Nombre entier (ex: 2, pas "deux" ni "2.0")""",
                    "default": 1
                },
                "rooms": {
                    "type": "integer",
                    "description": """Nombre de CHAMBRES à réserver.
                    
EXEMPLES VALIDES:
- 1 (par défaut - une seule chambre)
- 2 (deux chambres)
- 3 (trois chambres)

CONVERSION depuis langage naturel:
- "une chambre" → 1
- "deux chambres" → 2
- "chambre double" → 1 chambre avec adults=2
- "famille de 4" → 1 chambre avec adults=4 OU 2 chambres avec adults=2

REMARQUE: 
- Pour un couple: rooms=1, adults=2
- Pour deux couples: rooms=2, adults=2
- Pour une famille de 5: soit rooms=1 avec adults=5, soit rooms=2 avec adults=2 et 3

LIMITES: Entre 1 et 9 chambres maximum.

FORMAT ATTENDU: Nombre entier (ex: 2, pas "deux" ni "2.0")""",
                    "default": 1
                },
                "max_results": {
                    "type": "integer",
                    "description": """Nombre maximum d'hôtels à retourner dans les résultats.
                    
EXEMPLES:
- 10 (par défaut - retourne les 10 meilleures options)
- 5 (pour une liste plus courte)
- 20 (pour un maximum de choix)

CONVERSION depuis langage naturel:
- "quelques hôtels" → 5
- "beaucoup d'options" → 15
- "les meilleurs hôtels" → 10
- Aucune mention → 10 (par défaut)

LIMITES: Entre 1 et 20 résultats maximum.

FORMAT ATTENDU: Nombre entier entre 1 et 20 (ex: 10, pas "dix" ni "10.0")""",
                    "default": 10
                }
            },
            "required": ["city_code", "check_in_date", "check_out_date"]
        }
    }


def search_hotels(city_code, check_in_date, check_out_date, adults=1, rooms=1, max_results=10):
    """
    Recherche des hôtels via Amadeus Hotel Search API.
    
    Args:
        city_code: Code IATA de la ville (3 lettres)
        check_in_date: Date d'arrivée YYYY-MM-DD
        check_out_date: Date de départ YYYY-MM-DD
        adults: Nombre d'adultes par chambre (1-9)
        rooms: Nombre de chambres (1-9)
        max_results: Nombre max de résultats (1-20)
    
    Returns:
        dict: Résultats de recherche avec liste des hôtels
    """
    try:
        # Valider les paramètres
        if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
            return {
                "status": "error",
                "message": "Clés API Amadeus manquantes. Configurez AMADEUS_API_KEY et AMADEUS_API_SECRET dans .env"
            }
        
        city_code = city_code.upper().strip()
        
        if len(city_code) != 3:
            return {
                "status": "error",
                "message": "Le code IATA de ville doit faire 3 lettres (ex: OUA, PAR, ABJ)"
            }
        
        adults = max(1, min(adults, 9))
        rooms = max(1, min(rooms, 9))
        max_results = max(1, min(max_results, 20))
        
        # Valider le format des dates
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            
            if check_out <= check_in:
                return {
                    "status": "error",
                    "message": "La date de départ doit être après la date d'arrivée"
                }
        except ValueError:
            return {
                "status": "error",
                "message": "Format de date invalide. Utilisez YYYY-MM-DD (ex: 2025-12-15)"
            }
        
        # 1. Obtenir le token d'accès
        token = get_amadeus_token()
        
        if not token:
            return {
                "status": "error",
                "message": "Impossible d'obtenir le token Amadeus. Vérifiez vos credentials."
            }
        
        # 2. ÉTAPE 1: Récupérer la liste des hôtels dans la ville (Hotel List API)
        hotels_list_url = f"https://{AMADEUS_BASE_URL}/v1/reference-data/locations/hotels/by-city"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        hotels_list_params = {
            "cityCode": city_code,
            "radius": 50,  # 50 km autour de la ville
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
        
        hotels_list_response = requests.get(hotels_list_url, headers=headers, params=hotels_list_params, timeout=30)
        
        if hotels_list_response.status_code != 200:
            return {
                "status": "error",
                "message": f"Impossible de récupérer la liste des hôtels pour {city_code} (code {hotels_list_response.status_code})"
            }
        
        hotels_data = hotels_list_response.json()
        hotel_list = hotels_data.get("data", [])
        
        if not hotel_list:
            return {
                "status": "success",
                "message": f"Aucun hôtel trouvé dans la ville {city_code}",
                "hotels": []
            }
        
        # Extraire les IDs d'hôtels (limiter au nombre demandé)
        hotel_ids = [h.get("hotelId") for h in hotel_list[:max_results] if h.get("hotelId")]
        
        if not hotel_ids:
            return {
                "status": "error",
                "message": "Aucun ID d'hôtel trouvé dans la liste"
            }
        
        # 3. ÉTAPE 2: Rechercher les offres pour ces hôtels (Hotel Offers API)
        url = f"https://{AMADEUS_BASE_URL}/v3/shopping/hotel-offers"
        params = {
            "hotelIds": ",".join(hotel_ids),  # Liste d'IDs séparés par virgule
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "roomQuantity": rooms,
            "currency": "EUR",
            "paymentPolicy": "NONE",
            "bestRateOnly": "true"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 400:
            error_data = response.json()
            errors = error_data.get("errors", [])
            if errors:
                error_msg = errors[0].get("detail", "Paramètres invalides")
                return {
                    "status": "error",
                    "message": f"Erreur Amadeus: {error_msg}"
                }
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Erreur API Amadeus (code {response.status_code})"
            }
        
        data = response.json()
        hotel_offers = data.get("data", [])
        
        if not hotel_offers:
            return {
                "status": "success",
                "message": f"Aucun hôtel trouvé à {city_code} pour {check_in_date} - {check_out_date}",
                "hotels": []
            }
        
        # Limiter au nombre demandé
        hotel_offers = hotel_offers[:max_results]
        
        # 3. Formater les résultats
        hotels = []
        for offer in hotel_offers:
            hotel_data = offer.get("hotel", {})
            offers_list = offer.get("offers", [])
            
            # Prendre la meilleure offre
            best_offer = offers_list[0] if offers_list else {}
            price = best_offer.get("price", {})
            room = best_offer.get("room", {})
            
            hotel_info = {
                "hotel_id": hotel_data.get("hotelId"),
                "name": hotel_data.get("name", "Hôtel sans nom"),
                "chain_code": hotel_data.get("chainCode", "N/A"),
                "rating": hotel_data.get("rating", "N/A"),
                "address": {
                    "city": hotel_data.get("address", {}).get("cityName", city_code),
                    "country": hotel_data.get("address", {}).get("countryCode", "")
                },
                "contact": {
                    "phone": hotel_data.get("contact", {}).get("phone", ""),
                    "email": hotel_data.get("contact", {}).get("email", "")
                },
                "best_offer": {
                    "offer_id": best_offer.get("id"),
                    "price": f"{price.get('total', 'N/A')} {price.get('currency', 'EUR')}",
                    "price_amount": float(price.get("total", 0)),
                    "currency": price.get("currency", "EUR"),
                    "room_type": room.get("typeEstimated", {}).get("category", "N/A"),
                    "beds": room.get("typeEstimated", {}).get("beds", 0),
                    "bed_type": room.get("typeEstimated", {}).get("bedType", "N/A")
                },
                "amenities": hotel_data.get("amenities", []),
                "available": True
            }
            
            hotels.append(hotel_info)
        
        return {
            "status": "success",
            "search_params": {
                "city_code": city_code,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "adults": adults,
                "rooms": rooms
            },
            "total_results": len(hotels),
            "hotels": hotels
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche d'hôtels: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    city_code = arguments.get("city_code", "")
    check_in_date = arguments.get("check_in_date", "")
    check_out_date = arguments.get("check_out_date", "")
    adults = arguments.get("adults", 1)
    rooms = arguments.get("rooms", 1)
    max_results = arguments.get("max_results", 10)
    
    return search_hotels(city_code, check_in_date, check_out_date, adults, rooms, max_results)
