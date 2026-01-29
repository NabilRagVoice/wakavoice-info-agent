#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool: Exercises Search (API Ninja)
Description: Recherche d'exercices de fitness par muscle, type, difficulté avec API Ninja
Documentation: https://api-ninjas.com/api/exercises
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
    Retourne la définition du tool pour exercises.
    """
    return {
        "type": "function",
        "name": "search_exercises",
        "description": """Recherche d'exercices de fitness avec filtres avancés. 
            API Ninja Exercises - Gratuit 50k req/mois.
            Filtres disponibles: muscle (biceps, triceps, chest, back, legs, etc.), 
            type (cardio, strength, stretching, plyometrics), 
            difficulty (beginner, intermediate, expert).""",
        "parameters": {
                "type": "object",
                "properties": {
                    "muscle": {
                        "type": "string",
                        "description": """Muscle ciblé. Options: abdominals, abductors, adductors, 
                        biceps, calves, chest, forearms, glutes, hamstrings, lats, lower_back, 
                        middle_back, neck, quadriceps, traps, triceps.""",
                        "enum": [
                            "abdominals", "abductors", "adductors", "biceps", "calves", 
                            "chest", "forearms", "glutes", "hamstrings", "lats", 
                            "lower_back", "middle_back", "neck", "quadriceps", 
                            "traps", "triceps"
                        ]
                    },
                    "type": {
                        "type": "string",
                        "description": "Type d'exercice: cardio, olympicWeightlifting, plyometrics, powerlifting, strength, stretching, strongman.",
                        "enum": [
                            "cardio", "olympicWeightlifting", "plyometrics", 
                            "powerlifting", "strength", "stretching", "strongman"
                        ]
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "Niveau de difficulté: beginner, intermediate, expert.",
                        "enum": ["beginner", "intermediate", "expert"]
                    },
                    "name": {
                        "type": "string",
                        "description": "Nom de l'exercice (recherche partielle possible, ex: 'push' pour push-ups)."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Nombre maximum de résultats (par défaut: 10, max: 30).",
                        "default": 10
                    }
                },
                "required": []
            }
    }


def search_exercises(muscle=None, type=None, difficulty=None, name=None, max_results=10):
    """
    Recherche des exercices de fitness avec filtres.
    
    Args:
        muscle (str, optional): Muscle ciblé (biceps, chest, legs, etc.)
        type (str, optional): Type d'exercice (cardio, strength, stretching, etc.)
        difficulty (str, optional): Niveau (beginner, intermediate, expert)
        name (str, optional): Nom de l'exercice (recherche partielle)
        max_results (int): Nombre maximum de résultats (défaut: 10, max: 30)
    
    Returns:
        dict: Résultats de la recherche avec exercices trouvés
    """
    
    if not NINJA_API_KEY:
        return {
            "status": "error",
            "message": "❌ Clé API Ninja manquante. Ajoutez NINJA_API_KEY dans .env"
        }
    
    # Construction des paramètres
    params = {}
    if muscle:
        params["muscle"] = muscle
    if type:
        params["type"] = type
    if difficulty:
        params["difficulty"] = difficulty
    if name:
        params["name"] = name
    
    # Limite de résultats
    max_results = min(max(1, max_results), 30)
    params["offset"] = 0
    
    try:
        # Appel API Ninja
        url = f"{NINJA_BASE_URL}/exercises"
        headers = {
            "X-Api-Key": NINJA_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        exercises_data = response.json()
        
        if not exercises_data or not isinstance(exercises_data, list):
            return {
                "status": "success",
                "total_results": 0,
                "message": "Aucun exercice trouvé avec ces critères.",
                "exercises": []
            }
        
        # Limiter les résultats
        exercises_data = exercises_data[:max_results]
        
        # Formatage des exercices
        exercises = []
        for ex in exercises_data:
            exercise = {
                "name": ex.get("name", "N/A"),
                "type": ex.get("type", "N/A"),
                "muscle": ex.get("muscle", "N/A"),
                "equipment": ex.get("equipment", "N/A"),
                "difficulty": ex.get("difficulty", "N/A"),
                "instructions": ex.get("instructions", "Aucune instruction disponible.")
            }
            exercises.append(exercise)
        
        return {
            "status": "success",
            "total_results": len(exercises),
            "filters_applied": {
                "muscle": muscle or "Tous",
                "type": type or "Tous",
                "difficulty": difficulty or "Tous",
                "name": name or "Tous"
            },
            "exercises": exercises
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
    muscle = params.get("muscle")
    type_ex = params.get("type")
    difficulty = params.get("difficulty")
    name = params.get("name")
    max_results = params.get("max_results", 10)
    
    return search_exercises(
        muscle=muscle,
        type=type_ex,
        difficulty=difficulty,
        name=name,
        max_results=max_results
    )


# Test direct du script
if __name__ == "__main__":
    print("Test 1: Exercices pour biceps (débutant)")
    print("-" * 60)
    result1 = search_exercises(muscle="biceps", difficulty="beginner", max_results=5)
    
    import json
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    print("Test 2: Exercices de cardio")
    print("-" * 60)
    result2 = search_exercises(type="cardio", max_results=3)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    print("Test 3: Recherche par nom 'push'")
    print("-" * 60)
    result3 = search_exercises(name="push", max_results=5)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
