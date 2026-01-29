# tools/tool_government_services.py
"""
Tool : Démarches administratives et services gouvernementaux
Fournit des informations sur les démarches administratives au Burkina Faso.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Services administratifs et démarches
ADMINISTRATIVE_SERVICES = {
    "Passeport": {
        "service": "Direction Générale de la Police Nationale - Service des Passeports",
        "location": "Ouagadougou, Bobo-Dioulasso, autres villes",
        "documents_required": [
            "Acte de naissance (original + 2 copies)",
            "Certificat de nationalité burkinabè",
            "2 photos d'identité récentes",
            "Justificatif de domicile",
            "Ancien passeport (si renouvellement)"
        ],
        "duration": "15 à 30 jours",
        "cost": "Ordinaire: 25,000 FCFA | Urgent (7 jours): 50,000 FCFA",
        "validity": "5 ans",
        "procedure": [
            "1. Constituer le dossier complet",
            "2. Déposer au commissariat de police de votre secteur",
            "3. Retrait de récépissé",
            "4. Retrait du passeport après délai annoncé"
        ],
        "contact": "Tél: +226 25 30 62 71"
    },
    "Carte d'identité nationale (CNIB)": {
        "service": "Office National d'Identification (ONI)",
        "location": "Bureaux ONI dans toutes les provinces",
        "documents_required": [
            "Acte de naissance (original + 2 copies)",
            "Certificat de nationalité",
            "2 photos d'identité récentes",
            "Justificatif de domicile"
        ],
        "duration": "30 à 45 jours",
        "cost": "Première demande: 2,500 FCFA | Renouvellement: 2,500 FCFA | Duplicata: 5,000 FCFA",
        "validity": "10 ans",
        "procedure": [
            "1. Retirer formulaire au bureau ONI",
            "2. Remplir et joindre pièces requises",
            "3. Dépôt du dossier et prise de photo biométrique",
            "4. Retrait après SMS de disponibilité"
        ],
        "contact": "Hotline: 80 00 11 45 | Site: www.oni.bf"
    },
    "Permis de conduire": {
        "service": "Direction Générale des Transports Terrestres et Maritimes",
        "location": "Centres d'examen dans les villes principales",
        "documents_required": [
            "Acte de naissance ou CNIB",
            "Certificat médical d'aptitude",
            "4 photos d'identité",
            "Attestation de formation auto-école",
            "Justificatif de domicile"
        ],
        "duration": "Après réussite examen (3 à 6 mois de formation)",
        "cost": "Formation: 150,000 à 250,000 FCFA | Frais examen: 15,000 FCFA | Confection permis: 10,000 FCFA",
        "validity": "5 ans (puis renouvellement)",
        "categories": "A (moto), B (voiture), C (poids lourd), D (transport en commun)",
        "procedure": [
            "1. S'inscrire dans auto-école agréée",
            "2. Formation théorique et pratique",
            "3. Examen code + conduite",
            "4. Retrait du permis après réussite"
        ],
        "contact": "Direction des Transports: +226 25 31 25 89"
    },
    "Acte de naissance": {
        "service": "Mairie / Centre d'État Civil",
        "location": "Mairie de votre commune",
        "documents_required": [
            "Déclaration de naissance (dans les 30 jours)",
            "Certificat d'accouchement (hôpital/maternité)",
            "CNIB des parents",
            "Acte de mariage des parents (si mariés)"
        ],
        "duration": "Immédiat à 7 jours",
        "cost": "Gratuit (première copie) | 500 FCFA (copies supplémentaires)",
        "validity": "Permanent",
        "procedure": [
            "1. Se présenter à la mairie avec documents",
            "2. Remplir formulaire de déclaration",
            "3. Enregistrement dans registre d'état civil",
            "4. Délivrance de l'acte"
        ],
        "note": "Déclaration obligatoire dans les 30 jours suivant naissance"
    },
    "Certificat de nationalité": {
        "service": "Tribunal d'Instance / Mairie",
        "location": "Tribunal de votre province",
        "documents_required": [
            "Acte de naissance du demandeur",
            "Acte de naissance des parents",
            "CNIB des parents",
            "Certificat de résidence",
            "Timbre fiscal (1,000 FCFA)"
        ],
        "duration": "1 à 3 mois",
        "cost": "5,000 à 10,000 FCFA (selon tribunal)",
        "validity": "Permanent",
        "procedure": [
            "1. Constituer dossier complet",
            "2. Dépôt au greffe du tribunal",
            "3. Enquête sur nationalité",
            "4. Délivrance certificat après validation"
        ]
    },
    "Casier judiciaire": {
        "service": "Tribunal de Grande Instance",
        "location": "Ouagadougou, Bobo-Dioulasso, chefs-lieux de province",
        "documents_required": [
            "CNIB ou passeport",
            "Demande manuscrite",
            "Timbre fiscal (500 FCFA)",
            "1 photo d'identité"
        ],
        "duration": "3 à 7 jours",
        "cost": "2,000 FCFA",
        "validity": "3 mois",
        "procedure": [
            "1. Retirer formulaire au greffe",
            "2. Remplir et joindre pièces",
            "3. Paiement des frais",
            "4. Retrait après délai annoncé"
        ],
        "types": "Bulletin n°3 (demandes administratives, emploi)"
    },
    "Immatriculation véhicule": {
        "service": "Direction Générale des Transports Terrestres - Service des Mines",
        "location": "Bureaux DGTTM dans les provinces",
        "documents_required": [
            "Carte grise originale",
            "Facture d'achat du véhicule",
            "CNIB du propriétaire",
            "Quittance assurance",
            "Certificat de visite technique",
            "Quittance taxe différentielle"
        ],
        "duration": "7 à 15 jours",
        "cost": "Variable selon cylindrée (20,000 à 100,000 FCFA)",
        "validity": "Permanent (renouvellement carte grise si changement propriétaire)",
        "procedure": [
            "1. Faire visite technique du véhicule",
            "2. Souscrire assurance",
            "3. Constituer dossier et déposer à la DGTTM",
            "4. Paiement taxes",
            "5. Retrait carte grise et plaque"
        ]
    }
}

# Contacts utiles administrations
GOVERNMENT_CONTACTS = {
    "Présidence du Faso": {
        "phone": "+226 25 30 66 33",
        "website": "www.presidencedufaso.bf"
    },
    "Primature": {
        "phone": "+226 25 32 48 00",
        "website": "www.primature.gov.bf"
    },
    "Ministère de la Justice": {
        "phone": "+226 25 32 47 41"
    },
    "Ministère de l'Intérieur": {
        "phone": "+226 25 32 47 61"
    },
    "Office National d'Identification (ONI)": {
        "phone": "80 00 11 45",
        "website": "www.oni.bf"
    },
    "Direction Générale des Impôts": {
        "phone": "+226 25 32 44 82",
        "website": "www.impots.gov.bf"
    },
    "Caisse Nationale de Sécurité Sociale (CNSS)": {
        "phone": "+226 25 31 29 00",
        "website": "www.cnss.bf"
    }
}


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "get_government_service_info",
        "description": """Fournit des informations sur les démarches administratives et services gouvernementaux au Burkina Faso.

IMPORTANT : Utilise ce tool pour :
- Comment obtenir passeport, CNIB, permis
- Documents requis pour démarches
- Coûts et délais administratifs
- Contacts administrations

EXEMPLE:
{
  "service": "passeport"
}

Retourne procédure, documents, coûts, délais et contacts.""",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": """Service administratif ou démarche recherché.

SERVICES DISPONIBLES:
- "passeport" : Obtention/renouvellement passeport
- "cnib" ou "carte identité" : Carte Nationale d'Identité Burkinabè
- "permis conduire" ou "permis" : Permis de conduire
- "acte naissance" : Acte de naissance
- "certificat nationalité" : Certificat de nationalité
- "casier judiciaire" : Extrait casier judiciaire
- "immatriculation" : Immatriculation véhicule
- "all" : Liste tous les services

CONVERSION:
- "id card" → "cnib"
- "passport" → "passeport"
- "license" → "permis conduire"

FORMAT: Nom du service (texte libre)""",
                    "default": "all"
                }
            },
            "required": []
        }
    }


def search_service(query):
    """
    Recherche service administratif
    
    Args:
        query: Terme de recherche
    
    Returns:
        dict: Services correspondants
    """
    query_lower = query.lower()
    
    # Normalisation
    if "cnib" in query_lower or "carte" in query_lower and "identité" in query_lower:
        query_lower = "carte d'identité nationale (cnib)"
    elif "permis" in query_lower:
        query_lower = "permis de conduire"
    elif "passeport" in query_lower:
        query_lower = "passeport"
    elif "acte" in query_lower and "naissance" in query_lower:
        query_lower = "acte de naissance"
    elif "nationalité" in query_lower:
        query_lower = "certificat de nationalité"
    elif "casier" in query_lower:
        query_lower = "casier judiciaire"
    elif "immatriculation" in query_lower or "carte grise" in query_lower:
        query_lower = "immatriculation véhicule"
    
    # Recherche
    results = {}
    for name, info in ADMINISTRATIVE_SERVICES.items():
        if query_lower == "all" or query_lower in name.lower():
            results[name] = info
    
    return results


def execute(arguments):
    """
    Exécute la recherche d'informations administratives
    
    Args:
        arguments: Dictionnaire contenant:
            - service: Service recherché (optionnel, défaut: 'all')
    
    Returns:
        dict: Résultat avec informations administratives
    """
    service_query = arguments.get('service', 'all')
    
    logger.info(f"🏛️ Recherche service administratif: {service_query}")
    
    try:
        services = search_service(service_query)
        
        if not services:
            return {
                "status": "error",
                "message": f"Service '{service_query}' non trouvé. Utilisez 'all' pour voir tous les services disponibles."
            }
        
        # Si un seul service, donner détails complets
        if len(services) == 1:
            name, info = list(services.items())[0]
            
            docs_text = "\n".join([f"   • {doc}" for doc in info['documents_required']])
            proc_text = "\n".join([f"   {step}" for step in info['procedure']])
            
            message = f"""🏛️ {name.upper()}

🏢 Service: {info['service']}
📍 Où: {info['location']}

📋 DOCUMENTS REQUIS:
{docs_text}

📝 PROCÉDURE:
{proc_text}

⏱️ Délai: {info['duration']}
💰 Coût: {info['cost']}
⏳ Validité: {info['validity']}

📞 Contact: {info.get('contact', 'Voir service local')}"""
            
            if 'note' in info:
                message += f"\n\n⚠️ NOTE: {info['note']}"
            
            if 'categories' in info:
                message += f"\n\n📌 Catégories: {info['categories']}"
            
            return {
                "status": "success",
                "type": "single_service",
                "service_name": name,
                "data": info,
                "message": message
            }
        
        # Liste de services
        services_text = "\n\n".join([
            f"🏛️ {name}\n   Service: {info['service']}\n   Coût: {info['cost']}\n   Délai: {info['duration']}"
            for name, info in services.items()
        ])
        
        message = f"🏛️ SERVICES ADMINISTRATIFS DISPONIBLES ({len(services)}):\n\n{services_text}\n\n💡 Demandez un service spécifique pour plus de détails."
        
        return {
            "status": "success",
            "type": "service_list",
            "count": len(services),
            "data": services,
            "message": message
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur recherche service administratif: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche: {str(e)}"
        }
