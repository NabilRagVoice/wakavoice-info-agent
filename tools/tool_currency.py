# tools/tool_currency.py
"""
Outil de conversion de devises gratuit
Utilise l'API exchangerate-api.com (gratuite, sans clé API)
"""

import requests


def get_tool_definition():
    """Retourne la définition du tool convert_currency"""
    return {
        "type": "function",
        "name": "convert_currency",
        "description": """Convertit un montant d'une devise à une autre avec taux de change en temps réel.
        
Supporte toutes les devises internationales (codes ISO 4217).

EXEMPLE:
{
  "amount": 100000,
  "from_currency": "XOF",
  "to_currency": "EUR"
}

Résultat: 100 000 XOF = 152.45 EUR""",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": """MONTANT à convertir (nombre positif).
                    
EXEMPLES:
- 100 (cent unités)
- 1000 (mille unités)
- 50.50 (cinquante et demi)
- 100000 (cent mille)

CONVERSION:
- "cent euros" → 100
- "mille dollars" → 1000
- "50 euros et 50 centimes" → 50.50
- "cent mille francs CFA" → 100000

FORMAT: Nombre décimal positif (ex: 100, 1000.50, pas "cent" ni "-50")"""
                },
                "from_currency": {
                    "type": "string",
                    "description": """Code ISO 4217 de la DEVISE SOURCE (3 lettres majuscules).
                    
DEVISES AFRIQUE DE L'OUEST:
- "XOF" = Franc CFA BCEAO (Burkina Faso, Côte d'Ivoire, Sénégal, Mali, Niger, Togo, Bénin)
- "GHS" = Cedi ghanéen (Ghana)
- "NGN" = Naira nigérian (Nigeria)
- "GMD" = Dalasi gambien (Gambie)
- "SLL" = Leone sierra-léonais (Sierra Leone)

DEVISES AFRIQUE CENTRALE:
- "XAF" = Franc CFA BEAC (Cameroun, Gabon, Congo, Tchad, RCA, Guinée équatoriale)

DEVISES INTERNATIONALES MAJEURES:
- "EUR" = Euro (Zone euro)
- "USD" = Dollar américain (États-Unis)
- "GBP" = Livre sterling (Royaume-Uni)
- "CHF" = Franc suisse (Suisse)
- "JPY" = Yen japonais (Japon)
- "CNY" = Yuan chinois (Chine)
- "CAD" = Dollar canadien (Canada)
- "AUD" = Dollar australien (Australie)

AUTRES DEVISES AFRICAINES:
- "MAD" = Dirham marocain (Maroc)
- "TND" = Dinar tunisien (Tunisie)
- "EGP" = Livre égyptienne (Égypte)
- "ZAR" = Rand sud-africain (Afrique du Sud)
- "KES" = Shilling kényan (Kenya)

CONVERSION:
- "francs CFA" → "XOF"
- "euros" → "EUR"
- "dollars" → "USD"
- "livres sterling" → "GBP"
- "cedi" → "GHS"

FORMAT: Exactement 3 lettres MAJUSCULES (ex: "XOF", pas "xof" ni "Franc CFA")"""
                },
                "to_currency": {
                    "type": "string",
                    "description": """Code ISO 4217 de la DEVISE CIBLE (3 lettres majuscules).
                    
DEVISES AFRIQUE DE L'OUEST:
- "XOF" = Franc CFA BCEAO (Burkina, Côte d'Ivoire, Sénégal, Mali, Niger, Togo, Bénin)
- "GHS" = Cedi ghanéen (Ghana)
- "NGN" = Naira nigérian (Nigeria)

DEVISES INTERNATIONALES:
- "EUR" = Euro (Zone euro)
- "USD" = Dollar américain (États-Unis)
- "GBP" = Livre sterling (Royaume-Uni)
- "CHF" = Franc suisse (Suisse)
- "JPY" = Yen japonais (Japon)
- "CNY" = Yuan chinois (Chine)

EXEMPLES D'USAGE:
- XOF → EUR: to_currency="EUR" (francs CFA vers euros)
- USD → XOF: to_currency="XOF" (dollars vers francs CFA)
- EUR → GBP: to_currency="GBP" (euros vers livres sterling)

CONVERSION:
- "en euros" → "EUR"
- "vers dollars" → "USD"
- "en francs CFA" → "XOF"
- "en livres" → "GBP"

FORMAT: Exactement 3 lettres MAJUSCULES (ex: "EUR", pas "eur" ni "Euro")"""
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    }


def convert_currency(amount, from_currency, to_currency):
    """
    Convertit un montant d'une devise à une autre.
    
    Args:
        amount: Montant à convertir
        from_currency: Code devise source (ex: USD)
        to_currency: Code devise cible (ex: EUR)
    
    Returns:
        dict: Résultat avec montant converti et taux de change
    """
    try:
        # Valider les entrées
        if amount <= 0:
            return {
                "status": "error",
                "message": "Le montant doit être supérieur à 0"
            }
        
        # Normaliser les codes de devise (majuscules)
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()
        
        # API gratuite exchangerate-api.com (pas de clé requise)
        endpoint = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        
        response = requests.get(endpoint, timeout=10)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Erreur API: code {response.status_code}. Vérifiez le code de devise source '{from_currency}'."
            }
        
        data = response.json()
        
        # Vérifier que la devise cible existe
        if to_currency not in data.get("rates", {}):
            available = ", ".join(list(data.get("rates", {}).keys())[:10])
            return {
                "status": "error",
                "message": f"Devise cible '{to_currency}' non trouvée. Exemples de devises disponibles: {available}, ..."
            }
        
        # Calculer la conversion
        exchange_rate = data["rates"][to_currency]
        converted_amount = amount * exchange_rate
        
        # Devises courantes pour affichage
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "XOF": "CFA",
            "XAF": "CFA",
            "CAD": "C$",
            "CHF": "CHF",
            "CNY": "¥"
        }
        
        from_symbol = currency_symbols.get(from_currency, from_currency)
        to_symbol = currency_symbols.get(to_currency, to_currency)
        
        return {
            "status": "success",
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": exchange_rate,
            "converted_amount": round(converted_amount, 2),
            "formatted": f"{amount:,.2f} {from_symbol} = {converted_amount:,.2f} {to_symbol}",
            "rate_date": data.get("date", "N/A")
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Timeout lors de l'appel à l'API de conversion. Veuillez réessayer."
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Erreur de connexion à l'API: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la conversion: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    amount = arguments.get("amount", 0)
    from_currency = arguments.get("from_currency", "")
    to_currency = arguments.get("to_currency", "")
    
    return convert_currency(amount, from_currency, to_currency)
