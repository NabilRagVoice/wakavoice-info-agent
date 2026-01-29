# tools/tool_flight_search.py
"""
Outil de recherche de vols via Amadeus API
Permet de rechercher des vols disponibles avec prix et horaires
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
    """Retourne la définition du tool search_flights"""
    return {
        "type": "function",
        "name": "search_flights",
        "description": """OUTIL PRIORITAIRE pour rechercher des VOLS AÉRIENS avec prix et horaires en temps réel.
        
UTILISATION OBLIGATOIRE pour toute demande concernant:
- Vols, avions, billets d'avion
- Voyager en avion, aller à [destination] en avion
- Trouver un vol, chercher un vol
- Prix des vols, réserver un vol

NE JAMAIS utiliser search_web pour les vols - toujours utiliser cet outil.

CODES AÉROPORTS (IATA - 3 lettres majuscules):
Afrique de l'Ouest:
- OUA = Ouagadougou (Burkina Faso)
- ABJ = Abidjan (Côte d'Ivoire)
- DKR = Dakar (Sénégal)
- ACC = Accra (Ghana)
- LOS = Lagos (Nigeria)
- NIM = Niamey (Niger)
- LFW = Lomé (Togo)
- COO = Cotonou (Bénin)
- BKO = Bamako (Mali)

Europe:
- CDG = Paris Charles de Gaulle (France)
- ORY = Paris Orly (France)
- LHR = Londres Heathrow (UK)
- FRA = Francfort (Allemagne)
- AMS = Amsterdam (Pays-Bas)
- BCN = Barcelone (Espagne)
- FCO = Rome (Italie)

Si tu ne connais pas le code IATA d'un aéroport, demande au utilisateur ou devine le code probable (capitale + pays).""",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": """Code IATA de l'aéroport de DÉPART (exactement 3 lettres majuscules).
                    
EXEMPLES VALIDES:
- "OUA" pour Ouagadougou
- "CDG" pour Paris Charles de Gaulle
- "ABJ" pour Abidjan
- "DKR" pour Dakar

Si l'utilisateur dit "de Ouagadougou", utilise "OUA".
Si l'utilisateur dit "depuis Paris", utilise "CDG".
Si l'utilisateur dit "partir de Abidjan", utilise "ABJ".

FORMAT ATTENDU: Exactement 3 lettres majuscules (ex: "OUA", pas "Ouagadougou" ni "oua")"""
                },
                "destination": {
                    "type": "string",
                    "description": """Code IATA de l'aéroport d'ARRIVÉE (exactement 3 lettres majuscules).
                    
EXEMPLES VALIDES:
- "CDG" pour Paris
- "OUA" pour Ouagadougou
- "DKR" pour Dakar
- "ABJ" pour Abidjan

Si l'utilisateur dit "vers Paris", utilise "CDG".
Si l'utilisateur dit "à Dakar", utilise "DKR".
Si l'utilisateur dit "pour Londres", utilise "LHR".

FORMAT ATTENDU: Exactement 3 lettres majuscules (ex: "CDG", pas "Paris" ni "cdg")"""
                },
                "departure_date": {
                    "type": "string",
                    "description": """Date de DÉPART au format YYYY-MM-DD (année-mois-jour).
                    
EXEMPLES VALIDES:
- "2025-12-15" pour le 15 décembre 2025
- "2025-11-20" pour le 20 novembre 2025
- "2026-01-05" pour le 5 janvier 2026

CONVERSION depuis langage naturel:
- "demain" → calcule la date de demain au format YYYY-MM-DD
- "le 15 décembre" → "2025-12-15" (utilise l'année courante ou suivante)
- "dans 3 jours" → calcule J+3 au format YYYY-MM-DD
- "lundi prochain" → calcule le prochain lundi au format YYYY-MM-DD

FORMAT ATTENDU: Toujours YYYY-MM-DD avec des zéros (ex: "2025-01-05", pas "2025-1-5" ni "15/12/2025")"""
                },
                "return_date": {
                    "type": "string",
                    "description": """Date de RETOUR au format YYYY-MM-DD (OPTIONNEL - seulement pour un aller-retour).
                    
EXEMPLES VALIDES:
- "2025-12-22" pour un retour le 22 décembre 2025
- "" (chaîne vide) pour un aller simple
- Ne pas fournir ce paramètre pour un aller simple

QUAND UTILISER:
- Aller-retour: l'utilisateur dit "aller-retour", "round trip", "avec retour"
- Aller simple: l'utilisateur dit "aller simple", "one-way", pas de mention de retour

REMARQUE: La date de retour doit être APRÈS la date de départ.

FORMAT ATTENDU: YYYY-MM-DD ou chaîne vide "" (ex: "2025-12-22" ou "")""",
                    "default": ""
                },
                "adults": {
                    "type": "integer",
                    "description": """Nombre de passagers ADULTES (âge 12 ans et plus).
                    
EXEMPLES VALIDES:
- 1 (valeur par défaut - un seul passager)
- 2 (deux passagers)
- 4 (quatre passagers)

CONVERSION depuis langage naturel:
- "pour moi" → 1
- "pour deux personnes" → 2
- "nous sommes 4" → 4
- "moi et ma femme" → 2
- "famille de 5" → 5

LIMITES: Entre 1 et 9 passagers maximum.

FORMAT ATTENDU: Nombre entier entre 1 et 9 (ex: 2, pas "deux" ni "2.0")""",
                    "default": 1
                },
                "travel_class": {
                    "type": "string",
                    "description": """Classe de voyage souhaitée.
                    
VALEURS POSSIBLES (majuscules obligatoires):
- "ECONOMY" = Classe économique (la moins chère, par défaut)
- "PREMIUM_ECONOMY" = Économique premium (plus d'espace)
- "BUSINESS" = Classe affaires (confort supérieur)
- "FIRST" = Première classe (luxe)

CONVERSION depuis langage naturel:
- "classe éco", "économique", "pas cher" → "ECONOMY"
- "business", "affaires" → "BUSINESS"
- "première classe", "first class" → "FIRST"
- "premium" → "PREMIUM_ECONOMY"
- Aucune mention → "ECONOMY" (par défaut)

FORMAT ATTENDU: Exactement l'une de ces valeurs en MAJUSCULES (ex: "ECONOMY", pas "economy" ni "Economique")""",
                    "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
                    "default": "ECONOMY"
                },
                "max_results": {
                    "type": "integer",
                    "description": """Nombre maximum de vols à retourner dans les résultats.
                    
EXEMPLES:
- 5 (par défaut - retourne les 5 meilleures offres)
- 10 (pour plus de choix)
- 3 (pour une réponse rapide)

CONVERSION depuis langage naturel:
- "quelques options" → 5
- "beaucoup d'options" → 10
- "le moins cher" → 3 (pour avoir rapidement les options économiques)
- Aucune mention → 5 (par défaut)

LIMITES: Entre 1 et 10 résultats maximum.

FORMAT ATTENDU: Nombre entier entre 1 et 10 (ex: 5, pas "cinq" ni "5.0")""",
                    "default": 5
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    }


def search_flights(origin, destination, departure_date, return_date="", adults=1, travel_class="ECONOMY", max_results=5):
    """
    Recherche des vols via Amadeus Flight Offers Search API.
    
    Args:
        origin: Code IATA aéroport de départ (3 lettres)
        destination: Code IATA aéroport d'arrivée (3 lettres)
        departure_date: Date de départ YYYY-MM-DD
        return_date: Date de retour YYYY-MM-DD (optionnel)
        adults: Nombre d'adultes (1-9)
        travel_class: Classe de voyage (ECONOMY, BUSINESS, etc.)
        max_results: Nombre max de résultats (1-10)
    
    Returns:
        dict: Résultats de recherche avec liste des vols
    """
    try:
        # Valider les paramètres
        if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
            return {
                "status": "error",
                "message": "Clés API Amadeus manquantes. Configurez AMADEUS_API_KEY et AMADEUS_API_SECRET dans .env"
            }
        
        origin = origin.upper().strip()
        destination = destination.upper().strip()
        
        if len(origin) != 3 or len(destination) != 3:
            return {
                "status": "error",
                "message": "Les codes IATA doivent faire 3 lettres (ex: OUA, CDG, ABJ)"
            }
        
        adults = max(1, min(adults, 9))
        max_results = max(1, min(max_results, 10))
        
        # Valider le format des dates
        try:
            datetime.strptime(departure_date, "%Y-%m-%d")
            if return_date:
                datetime.strptime(return_date, "%Y-%m-%d")
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
        
        # 2. Rechercher les vols
        url = f"https://{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": travel_class,
            "max": max_results,
            "currencyCode": "EUR"  # Prix en euros
        }
        
        if return_date:
            params["returnDate"] = return_date
        
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
        flight_offers = data.get("data", [])
        
        if not flight_offers:
            return {
                "status": "success",
                "message": f"Aucun vol trouvé de {origin} à {destination} pour le {departure_date}",
                "flights": []
            }
        
        # 3. Formater les résultats
        flights = []
        for offer in flight_offers:
            price = offer.get("price", {})
            itineraries = offer.get("itineraries", [])
            
            flight_info = {
                "id": offer.get("id"),
                "price": f"{price.get('total', 'N/A')} {price.get('currency', 'EUR')}",
                "price_amount": float(price.get("total", 0)),
                "currency": price.get("currency", "EUR"),
                "number_of_bookable_seats": offer.get("numberOfBookableSeats", "N/A"),
                "outbound": None,
                "return": None
            }
            
            # Aller
            if len(itineraries) > 0:
                outbound = itineraries[0]
                segments = outbound.get("segments", [])
                
                if segments:
                    first_seg = segments[0]
                    last_seg = segments[-1]
                    
                    flight_info["outbound"] = {
                        "departure": {
                            "airport": first_seg.get("departure", {}).get("iataCode"),
                            "time": first_seg.get("departure", {}).get("at")
                        },
                        "arrival": {
                            "airport": last_seg.get("arrival", {}).get("iataCode"),
                            "time": last_seg.get("arrival", {}).get("at")
                        },
                        "duration": outbound.get("duration"),
                        "stops": len(segments) - 1,
                        "carriers": [seg.get("carrierCode") for seg in segments]
                    }
            
            # Retour
            if len(itineraries) > 1:
                return_flight = itineraries[1]
                segments = return_flight.get("segments", [])
                
                if segments:
                    first_seg = segments[0]
                    last_seg = segments[-1]
                    
                    flight_info["return"] = {
                        "departure": {
                            "airport": first_seg.get("departure", {}).get("iataCode"),
                            "time": first_seg.get("departure", {}).get("at")
                        },
                        "arrival": {
                            "airport": last_seg.get("arrival", {}).get("iataCode"),
                            "time": last_seg.get("arrival", {}).get("at")
                        },
                        "duration": return_flight.get("duration"),
                        "stops": len(segments) - 1,
                        "carriers": [seg.get("carrierCode") for seg in segments]
                    }
            
            flights.append(flight_info)
        
        return {
            "status": "success",
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date if return_date else None,
                "adults": adults,
                "travel_class": travel_class
            },
            "total_results": len(flights),
            "flights": flights
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche de vols: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    origin = arguments.get("origin", "")
    destination = arguments.get("destination", "")
    departure_date = arguments.get("departure_date", "")
    return_date = arguments.get("return_date", "")
    adults = arguments.get("adults", 1)
    travel_class = arguments.get("travel_class", "ECONOMY")
    max_results = arguments.get("max_results", 5)
    
    return search_flights(origin, destination, departure_date, return_date, adults, travel_class, max_results)
