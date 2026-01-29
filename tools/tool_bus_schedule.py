# tools/tool_bus_schedule.py
"""
Tool : Horaires des bus SOTRACO
Fournit les horaires des lignes de bus de la SOTRACO (Société de Transport en Commun) de Ouagadougou.
"""

import os
import logging
from datetime import datetime, time
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Horaires des lignes SOTRACO Ouagadougou
# Source: SOTRACO 2025 (horaires types)
# En production, ces données viendraient d'une API SOTRACO ou base Cosmos DB mise à jour
SOTRACO_LINES = {
    "1": {
        "name": "Ligne 1",
        "route": "Gare Routière ↔ Ouaga 2000",
        "stops": ["Gare Routière", "Avenue Kwame N'Krumah", "Place des Nations Unies", "Avenue Charles de Gaulle", "Ouaga 2000"],
        "first_departure": "05:30",
        "last_departure": "22:00",
        "frequency_peak": 15,  # minutes
        "frequency_offpeak": 30,
        "fare": 200,  # FCFA
        "operating_days": "Lundi-Dimanche"
    },
    "2": {
        "name": "Ligne 2",
        "route": "Zone du Bois ↔ Patte d'Oie",
        "stops": ["Zone du Bois", "Avenue de la Liberté", "Centre-ville", "Rond-Point des Nations Unies", "Patte d'Oie"],
        "first_departure": "05:45",
        "last_departure": "21:30",
        "frequency_peak": 20,
        "frequency_offpeak": 40,
        "fare": 200,
        "operating_days": "Lundi-Dimanche"
    },
    "3": {
        "name": "Ligne 3",
        "route": "Aéroport ↔ Université de Ouagadougou",
        "stops": ["Aéroport International", "Avenue de l'Indépendance", "Place des Cinéastes", "Université Joseph Ki-Zerbo"],
        "first_departure": "06:00",
        "last_departure": "20:00",
        "frequency_peak": 30,
        "frequency_offpeak": 60,
        "fare": 250,  # Supplément aéroport
        "operating_days": "Lundi-Samedi"
    },
    "4": {
        "name": "Ligne 4",
        "route": "Tampouy ↔ Gounghin",
        "stops": ["Tampouy", "Avenue Bassawarga", "Rond-Point Kennedy", "Gounghin"],
        "first_departure": "05:30",
        "last_departure": "21:00",
        "frequency_peak": 25,
        "frequency_offpeak": 45,
        "fare": 200,
        "operating_days": "Lundi-Dimanche"
    },
    "5": {
        "name": "Ligne 5",
        "route": "Pissy ↔ CHU Yalgado",
        "stops": ["Pissy", "Avenue Raoul Follereau", "Centre-ville", "CHU Yalgado Ouédraogo"],
        "first_departure": "06:00",
        "last_departure": "21:30",
        "frequency_peak": 20,
        "frequency_offpeak": 35,
        "fare": 200,
        "operating_days": "Lundi-Dimanche"
    }
}

# Lignes inter-urbaines (Ouagadougou - autres villes)
INTERURBAN_LINES = {
    "Ouagadougou-Bobo": {
        "route": "Ouagadougou ↔ Bobo-Dioulasso",
        "distance_km": 360,
        "duration_hours": 5.5,
        "departures": ["06:00", "09:00", "12:00", "15:00", "18:00"],
        "fare": 5000,
        "company": "TSR / STAF",
        "operating_days": "Tous les jours"
    },
    "Ouagadougou-Koudougou": {
        "route": "Ouagadougou ↔ Koudougou",
        "distance_km": 100,
        "duration_hours": 1.5,
        "departures": ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00"],
        "fare": 2000,
        "company": "Divers",
        "operating_days": "Tous les jours"
    },
    "Ouagadougou-Banfora": {
        "route": "Ouagadougou ↔ Banfora",
        "distance_km": 450,
        "duration_hours": 7,
        "departures": ["06:00", "08:00", "14:00"],
        "fare": 6000,
        "company": "TSR",
        "operating_days": "Tous les jours"
    }
}


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "get_bus_schedule",
        "description": """Fournit les horaires des bus SOTRACO à Ouagadougou et des lignes inter-urbaines au Burkina Faso.

IMPORTANT : Utilise ce tool pour :
- Horaires bus SOTRACO
- Quelle ligne de bus prendre
- Prix du bus
- Horaires bus inter-villes

EXEMPLE:
{
  "line_number": "1",
  "type": "urban"
}

Retourne horaires, arrêts, tarifs et fréquence de passage.""",
        "parameters": {
            "type": "object",
            "properties": {
                "line_number": {
                    "type": "string",
                    "description": """Numéro de ligne ou nom de trajet.

LIGNES URBAINES OUAGADOUGOU (SOTRACO):
- "1" : Gare Routière ↔ Ouaga 2000
- "2" : Zone du Bois ↔ Patte d'Oie
- "3" : Aéroport ↔ Université
- "4" : Tampouy ↔ Gounghin
- "5" : Pissy ↔ CHU Yalgado

LIGNES INTER-URBAINES:
- "Ouagadougou-Bobo" : Vers Bobo-Dioulasso
- "Ouagadougou-Koudougou" : Vers Koudougou
- "Ouagadougou-Banfora" : Vers Banfora

CONVERSION:
- "ligne 1" → "1"
- "ouaga bobo" → "Ouagadougou-Bobo"
- Pas de ligne → liste toutes les lignes

FORMAT: Numéro ou nom de trajet""",
                    "default": "all"
                },
                "type": {
                    "type": "string",
                    "description": """Type de transport.

TYPES:
- "urban" : Bus urbains SOTRACO (Ouagadougou)
- "interurban" : Bus inter-villes
- "all" : Tous les types

DEFAULT: "urban" """,
                    "default": "urban"
                }
            },
            "required": []
        }
    }


def get_current_time_category():
    """
    Détermine si on est en heure de pointe ou creuse
    
    Returns:
        str: "peak" ou "offpeak"
    """
    now = datetime.now().time()
    
    # Heures de pointe: 6h-9h et 16h-19h
    morning_peak = time(6, 0) <= now <= time(9, 0)
    evening_peak = time(16, 0) <= now <= time(19, 0)
    
    if morning_peak or evening_peak:
        return "peak"
    else:
        return "offpeak"


def calculate_next_departures(first_dep, last_dep, frequency_min, count=3):
    """
    Calcule les prochains départs
    
    Args:
        first_dep: Heure premier départ (HH:MM)
        last_dep: Heure dernier départ (HH:MM)
        frequency_min: Fréquence en minutes
        count: Nombre de départs à retourner
    
    Returns:
        list: Liste des heures de départ
    """
    now = datetime.now()
    current_time = now.time()
    
    # Convertir en datetime
    first_time = datetime.strptime(first_dep, "%H:%M").time()
    last_time = datetime.strptime(last_dep, "%H:%M").time()
    
    # Si après dernier départ, retourner premier départ du lendemain
    if current_time > last_time:
        return [f"{first_dep} (demain)"]
    
    # Si avant premier départ, retourner premiers départs
    if current_time < first_time:
        departures = []
        current = datetime.combine(now.date(), first_time)
        for _ in range(count):
            departures.append(current.strftime("%H:%M"))
            current = datetime.combine(now.date(), datetime.strptime(departures[-1], "%H:%M").time())
            current = current.replace(hour=current.hour, minute=current.minute + frequency_min)
            if current.time() > last_time:
                break
        return departures
    
    # Trouver prochain départ
    current = datetime.combine(now.date(), first_time)
    departures = []
    
    while current.time() <= last_time:
        if current.time() >= current_time:
            departures.append(current.strftime("%H:%M"))
            if len(departures) >= count:
                break
        current = current.replace(hour=current.hour, minute=current.minute + frequency_min)
    
    return departures if departures else [f"{first_dep} (demain)"]


def execute(arguments):
    """
    Exécute la recherche d'horaires de bus
    
    Args:
        arguments: Dictionnaire contenant:
            - line_number: Numéro de ligne (optionnel, défaut: 'all')
            - type: Type de transport (optionnel, défaut: 'urban')
    
    Returns:
        dict: Résultat avec horaires de bus
    """
    line_number = arguments.get('line_number', 'all')
    transport_type = arguments.get('type', 'urban')
    
    logger.info(f"🚌 Recherche horaires bus: ligne={line_number}, type={transport_type}")
    
    try:
        # Déterminer heure de pointe
        time_category = get_current_time_category()
        
        if transport_type == "urban" or transport_type == "all":
            if line_number == "all":
                # Lister toutes les lignes urbaines
                lines_text = "\n\n".join([
                    f"🚌 {info['name']}\n   Trajet: {info['route']}\n   Premier bus: {info['first_departure']} | Dernier: {info['last_departure']}\n   Fréquence: {info['frequency_peak']}min (pointe) / {info['frequency_offpeak']}min (normale)\n   Tarif: {info['fare']} FCFA"
                    for line, info in SOTRACO_LINES.items()
                ])
                
                message = f"🚌 LIGNES SOTRACO OUAGADOUGOU:\n\n{lines_text}"
                
                return {
                    "status": "success",
                    "type": "urban_all",
                    "lines": SOTRACO_LINES,
                    "message": message
                }
            
            elif line_number in SOTRACO_LINES:
                # Détails ligne spécifique
                line = SOTRACO_LINES[line_number]
                frequency = line['frequency_peak'] if time_category == "peak" else line['frequency_offpeak']
                next_buses = calculate_next_departures(line['first_departure'], line['last_departure'], frequency)
                
                stops_text = " → ".join(line['stops'])
                next_buses_text = ", ".join(next_buses)
                
                message = f"""🚌 {line['name']} - SOTRACO

📍 Trajet: {line['route']}

🛑 Arrêts: {stops_text}

⏰ Horaires:
• Premier départ: {line['first_departure']}
• Dernier départ: {line['last_departure']}
• Fréquence actuelle: {frequency} minutes
• Prochains bus: {next_buses_text}

💰 Tarif: {line['fare']} FCFA

📅 Service: {line['operating_days']}"""
                
                return {
                    "status": "success",
                    "type": "urban_line",
                    "line": line,
                    "next_departures": next_buses,
                    "message": message
                }
        
        if transport_type == "interurban" or transport_type == "all":
            if line_number == "all":
                # Lister toutes les lignes inter-urbaines
                lines_text = "\n\n".join([
                    f"🚍 {info['route']}\n   Durée: {info['duration_hours']}h | Distance: {info['distance_km']}km\n   Départs: {', '.join(info['departures'])}\n   Tarif: {info['fare']} FCFA\n   Compagnie: {info['company']}"
                    for route, info in INTERURBAN_LINES.items()
                ])
                
                message = f"🚍 LIGNES INTER-URBAINES:\n\n{lines_text}"
                
                return {
                    "status": "success",
                    "type": "interurban_all",
                    "lines": INTERURBAN_LINES,
                    "message": message
                }
            
            else:
                # Chercher ligne inter-urbaine
                matched_line = None
                for route, info in INTERURBAN_LINES.items():
                    if line_number.lower() in route.lower():
                        matched_line = info
                        break
                
                if matched_line:
                    # Trouver prochains départs
                    now = datetime.now().time()
                    next_deps = [dep for dep in matched_line['departures'] if datetime.strptime(dep, "%H:%M").time() >= now]
                    if not next_deps:
                        next_deps = [f"{matched_line['departures'][0]} (demain)"]
                    
                    departures_text = ", ".join(matched_line['departures'])
                    next_text = ", ".join(next_deps[:3])
                    
                    message = f"""🚍 {matched_line['route']}

📏 Distance: {matched_line['distance_km']} km
⏱️ Durée: {matched_line['duration_hours']} heures

⏰ Départs quotidiens: {departures_text}
🕐 Prochains départs: {next_text}

💰 Tarif: {matched_line['fare']} FCFA

🚌 Compagnie: {matched_line['company']}
📅 Service: {matched_line['operating_days']}

📍 Départ: Gare Routière de Ouagadougou"""
                    
                    return {
                        "status": "success",
                        "type": "interurban_line",
                        "line": matched_line,
                        "next_departures": next_deps,
                        "message": message
                    }
        
        return {
            "status": "error",
            "message": f"Ligne '{line_number}' non trouvée. Utilisez 'all' pour voir toutes les lignes disponibles."
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur horaires bus: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche d'horaires: {str(e)}"
        }
