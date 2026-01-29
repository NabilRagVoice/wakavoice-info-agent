# tools/tool_flight_booking.py
"""
Outil de réservation de vols via Amadeus API
Permet de réserver un vol sélectionné via search_flights
"""

import os
import requests
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
    """Retourne la définition du tool book_flight"""
    return {
        "type": "function",
        "name": "book_flight",
        "description": """Génère un lien de réservation pour un vol sélectionné via search_flights.
        
PROCESSUS EN 2 ÉTAPES:
1. D'abord utilise search_flights pour obtenir les offres de vols disponibles
2. Ensuite utilise book_flight avec l'ID de l'offre + infos du passager

MODE AFFILIATION: Génère un lien vers Skyscanner, Google Flights ou Kayak où l'utilisateur pourra:
- Comparer les prix en temps réel
- Choisir la meilleure offre
- Payer de manière 100% sécurisée
- Recevoir sa confirmation par email

EXEMPLE COMPLET:
{
  "flight_offer_id": "flight_12345_OUA_CDG_2025-12-15",
  "passenger": {
    "first_name": "Jean",
    "last_name": "Traore",
    "date_of_birth": "1985-03-20",
    "gender": "MALE",
    "email": "jean.traore@example.com",
    "phone": "+22670123456"
  }
}""",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_offer_id": {
                    "type": "string",
                    "description": """ID de l'offre de vol obtenu via search_flights.
                    
EXEMPLE: "flight_12345_OUA_CDG_2025-12-15"

Cet ID est retourné par search_flights. Si l'utilisateur dit "le vol Air France de 10h30", retrouve l'ID dans les résultats précédents."""
                },
                "passenger": {
                    "type": "object",
                    "description": """Informations du passager (6 champs OBLIGATOIRES).

EXEMPLE:
{
  "first_name": "Aminata",
  "last_name": "Ouedraogo",
  "date_of_birth": "1990-07-15",
  "gender": "FEMALE",
  "email": "aminata@gmail.com",
  "phone": "+22670987654"
}

CONVERSION:
- Prénom/nom: comme sur le passeport, sans accents
- Date: "15 juillet 1990" → "1990-07-15" (format YYYY-MM-DD)
- Genre: "Monsieur" → "MALE", "Madame" → "FEMALE"
- Tél: "70 12 34 56" → "+22670123456" (avec indicatif pays)

Indicatifs: Burkina +226, France +33, Sénégal +221, Côte d'Ivoire +225""",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "Prénom comme sur le passeport (ex: 'Aminata', pas d'accents)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Nom de famille comme sur le passeport (ex: 'Ouedraogo', pas d'accents)"
                        },
                        "date_of_birth": {
                            "type": "string",
                            "description": "Date de naissance format YYYY-MM-DD avec zéros (ex: '1990-07-15' pour 15 juillet 1990)"
                        },
                        "gender": {
                            "type": "string",
                            "description": "Genre: 'MALE' (Monsieur) ou 'FEMALE' (Madame) - en MAJUSCULES uniquement",
                            "enum": ["MALE", "FEMALE"]
                        },
                        "email": {
                            "type": "string",
                            "description": "Email valide pour confirmation (ex: 'passager@example.com')"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Téléphone avec indicatif pays (ex: '+22670123456' pour Burkina, '+33612345678' pour France)"
                        }
                    },
                    "required": ["first_name", "last_name", "date_of_birth", "gender", "email", "phone"]
                }
            },
            "required": ["flight_offer_id", "passenger"]
        }
    }


def book_flight(flight_offer_id, passenger):
    """
    Réserve un vol via Amadeus Flight Create Orders API.
    
    IMPORTANT: En mode TEST, cette fonction simule une réservation.
    Pour des réservations réelles, il faut utiliser l'API Production avec certification.
    
    Args:
        flight_offer_id: ID de l'offre de vol
        passenger: Dict avec first_name, last_name, date_of_birth, gender, email, phone
    
    Returns:
        dict: Confirmation de réservation ou erreur
    """
    try:
        # Valider les paramètres
        if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
            return {
                "status": "error",
                "message": "Clés API Amadeus manquantes. Configurez AMADEUS_API_KEY et AMADEUS_API_SECRET dans .env"
            }
        
        if not flight_offer_id:
            return {
                "status": "error",
                "message": "ID de vol manquant. Utilisez search_flights d'abord pour obtenir un ID de vol."
            }
        
        # Valider les informations passager
        required_fields = ["first_name", "last_name", "date_of_birth", "gender", "email", "phone"]
        for field in required_fields:
            if not passenger.get(field):
                return {
                    "status": "error",
                    "message": f"Champ passager manquant: {field}"
                }
        
        # 1. Obtenir le token d'accès
        token = get_amadeus_token()
        
        if not token:
            return {
                "status": "error",
                "message": "Impossible d'obtenir le token Amadeus. Vérifiez vos credentials."
            }
        
        # 2. Générer un lien de redirection vers des partenaires d'affiliation
        # Ces liens permettent de finaliser la réservation sur des plateformes de confiance
        
        # Extraire les informations de vol depuis l'ID
        # Format attendu: flight_XXXXX_OUA_CDG_2025-12-15
        parts = flight_offer_id.split('_')
        origin = parts[2] if len(parts) > 2 else "OUA"
        destination = parts[3] if len(parts) > 3 else "CDG"
        date = parts[4] if len(parts) > 4 else ""
        
        # Générer les liens d'affiliation avec les bons paramètres
        # Note: Remplacez les IDs d'affiliation par les vôtres après inscription aux programmes
        
        # Skyscanner - Programme d'affiliation gratuit (à inscrire sur skyscanner.com/affiliates)
        booking_url_skyscanner = f"https://www.skyscanner.net/transport/flights/{origin}/{destination}/{date}/?adultsv2=1&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0"
        
        # Google Flights - Pas de programme d'affiliation mais bon pour les utilisateurs
        booking_url_google = f"https://www.google.com/travel/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{date}"
        
        # Kayak - Programme d'affiliation (à inscrire sur kayak.com/affiliate)
        booking_url_kayak = f"https://www.kayak.com/flights/{origin}-{destination}/{date}?sort=bestflight_a"
        
        # Message personnalisé pour l'utilisateur
        passenger_name = f"{passenger['first_name']} {passenger['last_name']}"
        
        # On retourne les informations avec les liens de réservation
        return {
            "status": "ready_to_book",
            "message": f"✈️ Parfait {passenger_name} ! Votre vol est prêt à être réservé. Je vous envoie le lien pour finaliser votre réservation sur une plateforme sécurisée.",
            "booking_reference": f"WAKA-FL-{flight_offer_id[:8].upper()}",
            "flight_offer_id": flight_offer_id,
            "route": {
                "origin": origin,
                "destination": destination,
                "date": date
            },
            "passenger": {
                "name": passenger_name,
                "date_of_birth": passenger["date_of_birth"],
                "gender": passenger["gender"],
                "contact": {
                    "email": passenger["email"],
                    "phone": passenger["phone"]
                }
            },
            "booking_links": {
                "skyscanner": booking_url_skyscanner,
                "google_flights": booking_url_google,
                "kayak": booking_url_kayak
            },
            "recommended_link": booking_url_skyscanner,
            "instructions": (
                f"Pour finaliser votre réservation {origin} → {destination} :\n"
                f"1. Cliquez sur le lien Skyscanner ci-dessous\n"
                f"2. Comparez les prix des différentes compagnies\n"
                f"3. Choisissez le vol qui vous convient\n"
                f"4. Finalisez le paiement directement sur le site\n\n"
                f"Lien de réservation: {booking_url_skyscanner}"
            ),
            "note": "🔒 Paiement 100% sécurisé sur Skyscanner, l'une des plateformes de réservation les plus fiables au monde."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la réservation de vol: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    flight_offer_id = arguments.get("flight_offer_id", "")
    passenger = arguments.get("passenger", {})
    
    return book_flight(flight_offer_id, passenger)
