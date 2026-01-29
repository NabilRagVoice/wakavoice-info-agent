#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool: Dog Breeds Search (API Ninja)
Description: Recherche d'informations sur les races de chiens avec API Ninja
Documentation: https://api-ninjas.com/api/dogs
Gratuit: 50,000 requêtes/mois
"""

import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration API Ninja
NINJA_API_KEY = os.getenv("NINJA_API_KEY", "")
NINJA_BASE_URL = "https://api.api-ninjas.com/v1"


def get_tool_definition():
    """
    Retourne la définition du tool pour dog breeds.
    """
    return {
        "type": "function",
        "name": "search_dog_breeds",
        "description": """Recherche d'informations détaillées sur les races de chiens. 
            API Ninja Dogs - Gratuit 50k req/mois.
            Retourne: taille, poids, espérance de vie, tempérament, niveau d'énergie, 
            facilité de dressage, protection, toilettage, et compatibilité avec enfants/chiens.""",
        "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nom de la race (recherche partielle possible, ex: 'golden', 'labrador', 'bulldog')."
                    },
                    "min_height": {
                        "type": "number",
                        "description": "Hauteur minimale en pouces (ex: 10, 20, 30)."
                    },
                    "max_height": {
                        "type": "number",
                        "description": "Hauteur maximale en pouces."
                    },
                    "min_weight": {
                        "type": "number",
                        "description": "Poids minimal en livres (ex: 10, 50, 100)."
                    },
                    "max_weight": {
                        "type": "number",
                        "description": "Poids maximal en livres."
                    },
                    "min_life_expectancy": {
                        "type": "number",
                        "description": "Espérance de vie minimale en années (ex: 8, 10, 12)."
                    },
                    "max_life_expectancy": {
                        "type": "number",
                        "description": "Espérance de vie maximale en années."
                    },
                    "shedding": {
                        "type": "integer",
                        "description": "Niveau de perte de poils: 1 (faible) à 5 (élevé).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "energy": {
                        "type": "integer",
                        "description": "Niveau d'énergie: 1 (calme) à 5 (très énergique).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "protectiveness": {
                        "type": "integer",
                        "description": "Instinct de protection: 1 (faible) à 5 (élevé).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "trainability": {
                        "type": "integer",
                        "description": "Facilité de dressage: 1 (difficile) à 5 (facile).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "good_with_children": {
                        "type": "integer",
                        "description": "Compatibilité avec enfants: 1 (faible) à 5 (excellente).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "good_with_other_dogs": {
                        "type": "integer",
                        "description": "Compatibilité avec autres chiens: 1 (faible) à 5 (excellente).",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Nombre maximum de résultats (par défaut: 10, max: 20).",
                        "default": 10
                    }
                },
                "required": []
            }
    }


def search_dog_breeds(
    name=None,
    min_height=None,
    max_height=None,
    min_weight=None,
    max_weight=None,
    min_life_expectancy=None,
    max_life_expectancy=None,
    shedding=None,
    energy=None,
    protectiveness=None,
    trainability=None,
    good_with_children=None,
    good_with_other_dogs=None,
    max_results=10
):
    """
    Recherche des races de chiens avec filtres multiples.
    
    Args:
        name (str, optional): Nom de la race
        min_height, max_height (float): Hauteur en pouces
        min_weight, max_weight (float): Poids en livres
        min_life_expectancy, max_life_expectancy (int): Espérance de vie en années
        shedding (int): Perte de poils (1-5)
        energy (int): Niveau d'énergie (1-5)
        protectiveness (int): Protection (1-5)
        trainability (int): Facilité de dressage (1-5)
        good_with_children (int): Compatibilité enfants (1-5)
        good_with_other_dogs (int): Compatibilité autres chiens (1-5)
        max_results (int): Nombre max de résultats
    
    Returns:
        dict: Résultats de la recherche avec races trouvées
    """
    
    if not NINJA_API_KEY:
        return {
            "status": "error",
            "message": "❌ Clé API Ninja manquante. Ajoutez NINJA_API_KEY dans .env"
        }
    
    # Construction des paramètres
    params = {}
    if name:
        params["name"] = name
    if min_height is not None:
        params["min_height"] = min_height
    if max_height is not None:
        params["max_height"] = max_height
    if min_weight is not None:
        params["min_weight"] = min_weight
    if max_weight is not None:
        params["max_weight"] = max_weight
    if min_life_expectancy is not None:
        params["min_life_expectancy"] = min_life_expectancy
    if max_life_expectancy is not None:
        params["max_life_expectancy"] = max_life_expectancy
    if shedding is not None:
        params["shedding"] = shedding
    if energy is not None:
        params["energy"] = energy
    if protectiveness is not None:
        params["protectiveness"] = protectiveness
    if trainability is not None:
        params["trainability"] = trainability
    if good_with_children is not None:
        params["good_with_children"] = good_with_children
    if good_with_other_dogs is not None:
        params["good_with_other_dogs"] = good_with_other_dogs
    
    # Limite de résultats
    max_results = min(max(1, max_results), 20)
    
    try:
        # Appel API Ninja
        url = f"{NINJA_BASE_URL}/dogs"
        headers = {
            "X-Api-Key": NINJA_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        dogs_data = response.json()
        
        if not dogs_data or not isinstance(dogs_data, list):
            return {
                "status": "success",
                "total_results": 0,
                "message": "Aucune race trouvée avec ces critères.",
                "breeds": []
            }
        
        # Limiter les résultats
        dogs_data = dogs_data[:max_results]
        
        # Formatage des races
        breeds = []
        for dog in dogs_data:
            # Conversion pouces → cm et livres → kg
            min_height_cm = round(dog.get("min_height_male", 0) * 2.54, 1) if dog.get("min_height_male") else None
            max_height_cm = round(dog.get("max_height_male", 0) * 2.54, 1) if dog.get("max_height_male") else None
            min_weight_kg = round(dog.get("min_weight_male", 0) * 0.453592, 1) if dog.get("min_weight_male") else None
            max_weight_kg = round(dog.get("max_weight_male", 0) * 0.453592, 1) if dog.get("max_weight_male") else None
            
            breed = {
                "name": dog.get("name", "N/A"),
                "image_link": dog.get("image_link", ""),
                "size": {
                    "height_cm": f"{min_height_cm}-{max_height_cm} cm" if min_height_cm and max_height_cm else "N/A",
                    "weight_kg": f"{min_weight_kg}-{max_weight_kg} kg" if min_weight_kg and max_weight_kg else "N/A"
                },
                "life_expectancy": f"{dog.get('min_life_expectancy', 'N/A')}-{dog.get('max_life_expectancy', 'N/A')} ans",
                "characteristics": {
                    "shedding": f"{dog.get('shedding', 'N/A')}/5" if dog.get('shedding') else "N/A",
                    "grooming": f"{dog.get('grooming', 'N/A')}/5" if dog.get('grooming') else "N/A",
                    "energy": f"{dog.get('energy', 'N/A')}/5" if dog.get('energy') else "N/A",
                    "trainability": f"{dog.get('trainability', 'N/A')}/5" if dog.get('trainability') else "N/A",
                    "barking": f"{dog.get('barking', 'N/A')}/5" if dog.get('barking') else "N/A",
                    "protectiveness": f"{dog.get('protectiveness', 'N/A')}/5" if dog.get('protectiveness') else "N/A"
                },
                "compatibility": {
                    "good_with_children": f"{dog.get('good_with_children', 'N/A')}/5" if dog.get('good_with_children') else "N/A",
                    "good_with_other_dogs": f"{dog.get('good_with_other_dogs', 'N/A')}/5" if dog.get('good_with_other_dogs') else "N/A",
                    "good_with_strangers": f"{dog.get('good_with_strangers', 'N/A')}/5" if dog.get('good_with_strangers') else "N/A"
                }
            }
            breeds.append(breed)
        
        # Filtres appliqués pour résumé
        filters_applied = {}
        if name:
            filters_applied["name"] = name
        if shedding:
            filters_applied["shedding"] = f"{shedding}/5"
        if energy:
            filters_applied["energy"] = f"{energy}/5"
        if trainability:
            filters_applied["trainability"] = f"{trainability}/5"
        if good_with_children:
            filters_applied["good_with_children"] = f"{good_with_children}/5"
        
        return {
            "status": "success",
            "total_results": len(breeds),
            "filters_applied": filters_applied if filters_applied else "Aucun filtre",
            "breeds": breeds
        }
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {
                "status": "error",
                "message": "❌ Clé API Ninja invalide. Vérifiez NINJA_API_KEY dans .env"
            }
        elif e.response.status_code == 429:
            return {
                "status": "error",
                "message": "❌ Limite de requêtes API Ninja atteinte (50k/mois). Réessayez plus tard."
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Erreur API Ninja: {e.response.status_code} - {e.response.text}"
            }
    
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "❌ Délai d'attente dépassé. Vérifiez votre connexion."
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"❌ Erreur de connexion API Ninja: {str(e)}"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erreur inattendue: {str(e)}"
        }


def execute(params):
    """
    Point d'entrée pour l'exécution du tool.
    """
    return search_dog_breeds(
        name=params.get("name"),
        min_height=params.get("min_height"),
        max_height=params.get("max_height"),
        min_weight=params.get("min_weight"),
        max_weight=params.get("max_weight"),
        min_life_expectancy=params.get("min_life_expectancy"),
        max_life_expectancy=params.get("max_life_expectancy"),
        shedding=params.get("shedding"),
        energy=params.get("energy"),
        protectiveness=params.get("protectiveness"),
        trainability=params.get("trainability"),
        good_with_children=params.get("good_with_children"),
        good_with_other_dogs=params.get("good_with_other_dogs"),
        max_results=params.get("max_results", 10)
    )


# Test direct du script
if __name__ == "__main__":
    print("Test 1: Recherche Golden Retriever")
    print("-" * 60)
    result1 = search_dog_breeds(name="golden")
    
    import json
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    print("Test 2: Chiens bons avec enfants (5/5) et faciles à dresser")
    print("-" * 60)
    result2 = search_dog_breeds(good_with_children=5, trainability=5, max_results=5)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    print("Test 3: Petits chiens (poids max 10kg)")
    print("-" * 60)
    result3 = search_dog_breeds(max_weight=22, max_results=5)  # 22 lbs ≈ 10 kg
    print(json.dumps(result3, indent=2, ensure_ascii=False))
