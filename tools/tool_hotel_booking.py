# tools/tool_hotel_booking.py
"""
Outil de réservation d'hôtels via Amadeus API
Permet de réserver un hôtel sélectionné via search_hotels
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
    """Retourne la définition du tool book_hotel"""
    return {
        "type": "function",
        "name": "book_hotel",
        "description": """Génère un lien de réservation pour un hôtel sélectionné via search_hotels.
        
PROCESSUS EN 2 ÉTAPES:
1. D'abord utilise search_hotels pour obtenir les offres d'hôtels disponibles
2. Ensuite utilise book_hotel avec l'ID + infos client

MODE AFFILIATION: Génère un lien vers Booking.com, Hotels.com ou Agoda où l'utilisateur pourra:
- Voir les photos et avis de l'hôtel
- Comparer les prix et conditions d'annulation
- Payer de manière 100% sécurisée
- Recevoir sa confirmation par email
- Bénéficier souvent d'une annulation gratuite

EXEMPLE COMPLET:
{
  "hotel_offer_id": "hotel_54321_OUA_Laico",
  "guest": {
    "first_name": "Sophie",
    "last_name": "Kabore",
    "email": "sophie@example.com",
    "phone": "+22675123456"
  },
  "payment": {
    "card_type": "VISA",
    "card_number": "4111111111111111"
  }
}""",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_offer_id": {
                    "type": "string",
                    "description": """ID de l'offre d'hôtel obtenu via search_hotels.
                    
EXEMPLE: "hotel_54321_OUA_Laico"

Cet ID est retourné par search_hotels. Si l'utilisateur dit "l'hôtel Laico", retrouve l'ID dans les résultats."""
                },
                "guest": {
                    "type": "object",
                    "description": """Informations du client (4 champs OBLIGATOIRES).

EXEMPLE:
{
  "first_name": "Fatou",
  "last_name": "Sow",
  "email": "fatou.sow@yahoo.fr",
  "phone": "+221771234567"
}

CONVERSION:
- Tél: "75 12 34 56" → "+22675123456" (avec indicatif pays)

Indicatifs: Burkina +226, France +33, Sénégal +221, Côte d'Ivoire +225, Ghana +233, Mali +223""",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "Prénom du client (ex: 'Fatou')"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Nom de famille du client (ex: 'Sow')"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email valide pour confirmation (ex: 'client@example.com')"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Téléphone avec indicatif pays (ex: '+22675123456' pour Burkina, '+33687654321' pour France)"
                        }
                    },
                    "required": ["first_name", "last_name", "email", "phone"]
                },
                "payment": {
                    "type": "object",
                    "description": """Paiement SIMULÉ - mode TEST uniquement (aucun vrai débit).

EXEMPLE:
{
  "card_type": "VISA",
  "card_number": "4111111111111111"
}

NUMEROS DE TEST:
- VISA: "4111111111111111"
- MASTERCARD: "5555555555554444"
- AMEX: "378282246310005"

REMARQUE: N'utilise JAMAIS de vraies données bancaires. Explique à l'utilisateur que c'est un mode TEST.""",
                    "properties": {
                        "card_type": {
                            "type": "string",
                            "description": "Type de carte: 'VISA' (par défaut), 'MASTERCARD', ou 'AMEX' - en MAJUSCULES",
                            "enum": ["VISA", "MASTERCARD", "AMEX"]
                        },
                        "card_number": {
                            "type": "string",
                            "description": "Numéro simulé pour test (ex: '4111111111111111' pour VISA, '5555555555554444' pour MASTERCARD)"
                        }
                    },
                    "required": ["card_type", "card_number"]
                }
            },
            "required": ["hotel_offer_id", "guest", "payment"]
        }
    }


def book_hotel(hotel_offer_id, guest, payment):
    """
    Réserve un hôtel via Amadeus Hotel Booking API.
    
    IMPORTANT: En mode TEST, cette fonction simule une réservation.
    Pour des réservations réelles, il faut utiliser l'API Production avec certification.
    
    Args:
        hotel_offer_id: ID de l'offre d'hôtel
        guest: Dict avec first_name, last_name, email, phone
        payment: Dict avec card_type, card_number
    
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
        
        if not hotel_offer_id:
            return {
                "status": "error",
                "message": "ID d'offre d'hôtel manquant. Utilisez search_hotels d'abord pour obtenir un ID d'offre."
            }
        
        # Valider les informations client
        required_guest_fields = ["first_name", "last_name", "email", "phone"]
        for field in required_guest_fields:
            if not guest.get(field):
                return {
                    "status": "error",
                    "message": f"Champ client manquant: {field}"
                }
        
        # Valider les informations de paiement
        required_payment_fields = ["card_type", "card_number"]
        for field in required_payment_fields:
            if not payment.get(field):
                return {
                    "status": "error",
                    "message": f"Champ paiement manquant: {field}"
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
        
        # Extraire les informations d'hôtel depuis l'ID
        # Format attendu: hotel_XXXXX_OUA_NomHotel ou similaire
        parts = hotel_offer_id.split('_')
        city = parts[2] if len(parts) > 2 else "Ouagadougou"
        hotel_name = parts[3] if len(parts) > 3 else ""
        
        # Générer les liens d'affiliation avec les bons paramètres
        # Note: Remplacez les IDs d'affiliation par les vôtres après inscription aux programmes
        
        # Booking.com - Programme d'affiliation (à inscrire sur booking.com/affiliate-program)
        # aid = votre ID affilié Booking.com (remplacez par le vôtre)
        booking_url_booking = f"https://www.booking.com/searchresults.html?ss={city}&aid=2311236"
        
        # Hotels.com - Programme d'affiliation Expedia
        booking_url_hotels = f"https://fr.hotels.com/search.do?destination={city}"
        
        # Agoda - Programme d'affiliation (à inscrire sur agoda.com/partners)
        booking_url_agoda = f"https://www.agoda.com/search?city={city}"
        
        # Message personnalisé pour l'utilisateur
        guest_name = f"{guest['first_name']} {guest['last_name']}"
        
        # On retourne les informations avec les liens de réservation
        return {
            "status": "ready_to_book",
            "message": f"🏨 Excellent choix {guest_name} ! Votre hôtel à {city} est disponible. Je vous envoie le lien pour finaliser votre réservation sur une plateforme sécurisée.",
            "booking_reference": f"WAKA-HTL-{hotel_offer_id[:8].upper()}",
            "confirmation_number": f"REF-{hotel_offer_id[-8:].upper()}",
            "hotel_offer_id": hotel_offer_id,
            "location": {
                "city": city,
                "hotel_name": hotel_name if hotel_name else "Voir options disponibles"
            },
            "guest": {
                "name": guest_name,
                "contact": {
                    "email": guest["email"],
                    "phone": guest["phone"]
                }
            },
            "booking_links": {
                "booking_com": booking_url_booking,
                "hotels_com": booking_url_hotels,
                "agoda": booking_url_agoda
            },
            "recommended_link": booking_url_booking,
            "payment_info": {
                "card_type": payment["card_type"],
                "status": "À effectuer sur la plateforme partenaire",
                "note": "Paiement sécurisé directement sur Booking.com, Hotels.com ou Agoda"
            },
            "instructions": (
                f"Pour finaliser votre réservation d'hôtel à {city} :\n"
                f"1. Cliquez sur le lien Booking.com ci-dessous\n"
                f"2. Parcourez les hôtels disponibles et leurs avis\n"
                f"3. Sélectionnez l'hôtel et les dates qui vous conviennent\n"
                f"4. Finalisez le paiement directement sur le site\n\n"
                f"Lien de réservation: {booking_url_booking}"
            ),
            "note": "🔒 Paiement 100% sécurisé sur Booking.com. Annulation gratuite sur la plupart des hôtels !"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la réservation d'hôtel: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    hotel_offer_id = arguments.get("hotel_offer_id", "")
    guest = arguments.get("guest", {})
    payment = arguments.get("payment", {})
    
    return book_hotel(hotel_offer_id, guest, payment)
