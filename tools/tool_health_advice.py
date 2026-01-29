# tools/tool_health_advice.py
"""
Outil de conseils santé via Infermedica API
Analyse les symptômes et fournit des conseils médicaux, remèdes et recommandations
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

INFERMEDICA_APP_ID = os.getenv("INFERMEDICA_APP_ID", "")
INFERMEDICA_APP_KEY = os.getenv("INFERMEDICA_APP_KEY", "")
INFERMEDICA_API_URL = "https://api.infermedica.com/v3"


def get_tool_definition():
    """Retourne la définition du tool get_health_advice"""
    return {
        "type": "function",
        "name": "get_health_advice",
        "description": "Analyse des symptômes et fourniture de conseils santé, remèdes naturels et recommandations médicales. Indique quand consulter un médecin. Supporte les symptômes courants (ballonnement, maux de tête, fièvre, toux, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "string",
                    "description": "Description des symptômes ressentis (ex: 'ballonnement et douleur abdominale', 'maux de tête et fièvre', 'toux sèche')"
                },
                "age": {
                    "type": "integer",
                    "description": "Âge de la personne (optionnel, pour des conseils plus précis)",
                    "default": 30
                },
                "sex": {
                    "type": "string",
                    "description": "Sexe de la personne: 'male' ou 'female' (optionnel)",
                    "enum": ["male", "female"]
                }
            },
            "required": ["symptoms"]
        }
    }


def get_health_advice(symptoms, age=30, sex="male"):
    """
    Analyse les symptômes et fournit des conseils santé.
    
    Args:
        symptoms: Description des symptômes
        age: Âge de la personne
        sex: Sexe ('male' ou 'female')
    
    Returns:
        dict: Conseils santé, remèdes et recommandations
    """
    try:
        # Valider les paramètres
        if not INFERMEDICA_APP_ID or not INFERMEDICA_APP_KEY:
            # Mode fallback: conseils génériques sans API
            return get_generic_health_advice(symptoms)
        
        if not symptoms or len(symptoms.strip()) == 0:
            return {
                "status": "error",
                "message": "Veuillez décrire vos symptômes"
            }
        
        # 1. Parser les symptômes en utilisant l'API de parsing
        headers = {
            "App-Id": INFERMEDICA_APP_ID,
            "App-Key": INFERMEDICA_APP_KEY,
            "Content-Type": "application/json"
        }
        
        parse_payload = {
            "text": symptoms,
            "age": {"value": age},
            "sex": sex
        }
        
        parse_response = requests.post(
            f"{INFERMEDICA_API_URL}/parse",
            json=parse_payload,
            headers=headers,
            timeout=15
        )
        
        if parse_response.status_code != 200:
            return get_generic_health_advice(symptoms)
        
        parsed_data = parse_response.json()
        mentioned_symptoms = parsed_data.get("mentions", [])
        
        if not mentioned_symptoms:
            return get_generic_health_advice(symptoms)
        
        # 2. Préparer les symptômes pour le diagnostic
        evidence = []
        for mention in mentioned_symptoms:
            if mention.get("choice_id") == "present":
                evidence.append({
                    "id": mention.get("id"),
                    "choice_id": "present",
                    "source": "initial"
                })
        
        # 3. Obtenir le diagnostic
        diagnosis_payload = {
            "sex": sex,
            "age": {"value": age},
            "evidence": evidence
        }
        
        diagnosis_response = requests.post(
            f"{INFERMEDICA_API_URL}/diagnosis",
            json=diagnosis_payload,
            headers=headers,
            timeout=15
        )
        
        if diagnosis_response.status_code != 200:
            return get_generic_health_advice(symptoms)
        
        diagnosis_data = diagnosis_response.json()
        conditions = diagnosis_data.get("conditions", [])
        
        # 4. Formater les résultats
        possible_conditions = []
        for condition in conditions[:3]:  # Top 3 conditions
            possible_conditions.append({
                "name": condition.get("common_name", "Condition inconnue"),
                "probability": round(condition.get("probability", 0) * 100, 1)
            })
        
        # 5. Générer des conseils basés sur les conditions
        advice = generate_advice_from_conditions(symptoms, possible_conditions)
        
        return {
            "status": "success",
            "symptoms": symptoms,
            "patient_info": {
                "age": age,
                "sex": sex
            },
            "possible_conditions": possible_conditions,
            "advice": advice,
            "disclaimer": "⚠️ Ces conseils sont informatifs. Consultez un médecin pour un diagnostic précis."
        }
        
    except Exception as e:
        # En cas d'erreur, utiliser les conseils génériques
        return get_generic_health_advice(symptoms)


def get_generic_health_advice(symptoms):
    """
    Fournit des conseils santé génériques basés sur des mots-clés.
    Utilisé en fallback quand l'API n'est pas disponible.
    """
    symptoms_lower = symptoms.lower()
    
    # Base de connaissances locale
    advice_database = {
        "ballonnement": {
            "possible_causes": ["Excès de gaz intestinaux", "Indigestion", "Constipation", "Syndrome de l'intestin irritable"],
            "remedies": [
                "Boire une tisane de gingembre ou de menthe",
                "Masser doucement l'abdomen dans le sens des aiguilles d'une montre",
                "Éviter les aliments gazeux (choux, haricots, boissons gazeuses)",
                "Marcher 15-20 minutes après les repas",
                "Charbon actif (disponible en pharmacie)"
            ],
            "when_to_see_doctor": "Si douleur intense, fièvre, vomissements ou symptômes persistant plus de 3 jours",
            "natural_remedies": ["Tisane de fenouil", "Eau chaude citronnée", "Yaourt probiotique"]
        },
        "maux de tête": {
            "possible_causes": ["Tension", "Déshydratation", "Fatigue", "Stress", "Migraine"],
            "remedies": [
                "Repos dans un endroit calme et sombre",
                "Boire beaucoup d'eau (1-2 litres)",
                "Compresse froide sur le front",
                "Paracétamol 500mg (si nécessaire)",
                "Massage des tempes avec huile essentielle de menthe"
            ],
            "when_to_see_doctor": "Si très intense, soudain, accompagné de fièvre, confusion ou raideur de la nuque",
            "natural_remedies": ["Tisane de camomille", "Huile essentielle de lavande", "Repos"]
        },
        "fièvre": {
            "possible_causes": ["Infection virale", "Infection bactérienne", "Inflammation"],
            "remedies": [
                "Repos complet",
                "Boire beaucoup de liquides (eau, jus, bouillon)",
                "Paracétamol 1g toutes les 6h (adulte)",
                "Compresses tièdes pour faire baisser la température",
                "Vêtements légers"
            ],
            "when_to_see_doctor": "Si fièvre >39°C persistante, difficulté à respirer, confusion ou convulsions",
            "natural_remedies": ["Tisane de citronnelle", "Eau de coco", "Bain tiède"]
        },
        "toux": {
            "possible_causes": ["Rhume", "Grippe", "Allergie", "Irritation des voies respiratoires"],
            "remedies": [
                "Miel + citron dans de l'eau chaude",
                "Inhalation de vapeur d'eau",
                "Repos vocal",
                "Hydratation abondante",
                "Éviter les irritants (fumée, poussière)"
            ],
            "when_to_see_doctor": "Si toux avec sang, fièvre élevée, essoufflement ou durée >2 semaines",
            "natural_remedies": ["Sirop de miel et gingembre", "Tisane de thym", "Inhalation d'eucalyptus"]
        },
        "diarrhée": {
            "possible_causes": ["Infection intestinale", "Intoxication alimentaire", "Stress"],
            "remedies": [
                "Réhydratation orale (SRO) - eau + sel + sucre",
                "Riz blanc, banane, compote de pomme",
                "Éviter produits laitiers et aliments gras",
                "Repos",
                "Probiotiques naturels (yaourt après amélioration)"
            ],
            "when_to_see_doctor": "Si sang dans les selles, déshydratation sévère, fièvre élevée ou durée >3 jours",
            "natural_remedies": ["Eau de riz", "Tisane de menthe", "Charbon actif"]
        }
    }
    
    # Chercher dans la base de connaissances
    matched_advice = None
    for keyword, advice in advice_database.items():
        if keyword in symptoms_lower:
            matched_advice = advice
            break
    
    if not matched_advice:
        # Conseils génériques par défaut
        return {
            "status": "success",
            "symptoms": symptoms,
            "advice": {
                "general_advice": [
                    "Repos et hydratation",
                    "Surveiller l'évolution des symptômes",
                    "Consulter un médecin si les symptômes persistent ou s'aggravent",
                    "Éviter l'automédication prolongée"
                ],
                "when_to_see_doctor": "Si symptômes graves, persistants (>3 jours) ou inquiétants",
                "emergency_signs": [
                    "Douleur intense soudaine",
                    "Difficulté à respirer",
                    "Perte de conscience",
                    "Fièvre très élevée (>40°C)",
                    "Saignement important"
                ]
            },
            "disclaimer": "⚠️ Ces conseils sont généraux. Consultez un professionnel de santé pour un diagnostic précis.",
            "note": "Pour des conseils plus précis, configurez INFERMEDICA_APP_ID et INFERMEDICA_APP_KEY dans .env"
        }
    
    return {
        "status": "success",
        "symptoms": symptoms,
        "possible_causes": matched_advice["possible_causes"],
        "advice": {
            "remedies": matched_advice["remedies"],
            "natural_remedies": matched_advice["natural_remedies"],
            "when_to_see_doctor": matched_advice["when_to_see_doctor"]
        },
        "emergency_signs": [
            "Douleur intense soudaine",
            "Difficulté à respirer",
            "Perte de conscience",
            "Saignement important"
        ],
        "disclaimer": "⚠️ Ces conseils sont informatifs. Consultez un médecin si les symptômes persistent ou s'aggravent."
    }


def generate_advice_from_conditions(symptoms, conditions):
    """Génère des conseils basés sur les conditions identifiées"""
    advice = {
        "general_recommendations": [
            "Repos et hydratation",
            "Surveiller l'évolution des symptômes",
            "Tenir un journal des symptômes"
        ],
        "remedies": [],
        "when_to_see_doctor": "Si les symptômes persistent plus de 48-72 heures ou s'aggravent",
        "emergency_signs": [
            "Douleur intense soudaine",
            "Difficulté à respirer",
            "Fièvre très élevée (>40°C)",
            "Perte de conscience"
        ]
    }
    
    # Ajouter des remèdes basés sur les symptômes courants
    symptoms_lower = symptoms.lower()
    
    if "ballonnement" in symptoms_lower or "gaz" in symptoms_lower:
        advice["remedies"].extend([
            "Tisane de gingembre ou menthe",
            "Éviter les aliments gazeux",
            "Marche légère après les repas"
        ])
    
    if "douleur" in symptoms_lower:
        advice["remedies"].extend([
            "Repos dans une position confortable",
            "Compresse chaude ou froide selon le type de douleur"
        ])
    
    if "fièvre" in symptoms_lower:
        advice["remedies"].extend([
            "Paracétamol selon dosage approprié",
            "Hydratation abondante",
            "Repos complet"
        ])
    
    if not advice["remedies"]:
        advice["remedies"] = [
            "Repos et hydratation",
            "Alimentation légère et équilibrée",
            "Éviter le stress et les efforts intenses"
        ]
    
    return advice


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    symptoms = arguments.get("symptoms", "")
    age = arguments.get("age", 30)
    sex = arguments.get("sex", "male")
    
    return get_health_advice(symptoms, age, sex)
