# tools/tool_search_web.py
"""
Outil de recherche web via Tavily AI
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BING_API_KEY = os.getenv("BING_API_KEY", "")


def get_tool_definition():
    """Retourne la définition du tool search_web"""
    return {
        "type": "function",
        "name": "search_web",
        "description": """OUTIL DE DERNIER RECOURS - Recherche générale sur Internet.
        
À utiliser UNIQUEMENT quand AUCUN outil spécialisé ne correspond:
- Météo → utilise get_weather_forecast (PAS search_web)
- Hôtels → utilise search_hotels (PAS search_web)
- Vols → utilise search_flights (PAS search_web)
- Actualités → utilise get_news (PAS search_web)
- Traduction → utilise translate_text (PAS search_web)
- Devises → utilise convert_currency (PAS search_web)

Utilise search_web pour:
- Informations générales ("qui est...", "qu'est-ce que...")
- Recherches encyclopédiques
- Données historiques, scientifiques
- Sujets non couverts par les outils spécialisés

Extrait automatiquement le contenu complet des pages web.

EXEMPLE:
{
  "query": "Ibrahim Traoré biographie",
  "count": 5
}""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """REQUÊTE de recherche (mots-clés ou question).
                    
EXEMPLES VALIDES:
Questions:
- "Qui est Ibrahim Traoré?"
- "Qu'est-ce que le PNDES?"
- "Comment fonctionne la photosynthse?"

Mots-clés:
- "Burkina Faso histoire"
- "Thomas Sankara discours"
- "recette tiga degéna"
- "distance Ouagadougou Bobo-Dioulasso"

Recherches factuelles:
- "capitale du Ghana"
- "population du Burkina Faso 2024"
- "plus haut sommet d'Afrique"

CONSEILS:
- Sois précis et spécifique
- Utilise des mots-clés pertinents
- Pour personnalités: "prénom nom + contexte" (ex: "Ibrahim Traoré président")
- Pour lieux: "nom lieu + pays" (ex: "Nazinga Burkina Faso")

FORMAT: Texte libre, question ou mots-clés séparés par espaces"""
                },
                "count": {
                    "type": "integer",
                    "description": """Nombre de RÉSULTATS à retourner (entre 1 et 10).
                    
EXEMPLES:
- 7 (par défaut - bon équilibre)
- 3 (réponse rapide)
- 10 (recherche approfondie)

CONVERSION:
- "quelques résultats" → 3
- "recherche complète" → 10
- Aucune mention → 7 (défaut)

FORMAT: Nombre entier entre 1 et 10 (ex: 7, pas "sept")""",
                    "default": 7
                }
            },
            "required": ["query"]
        }
    }


def search_web(query, count=7, extract_content=True):
    """
    Recherche web via Tavily AI avec extraction automatique du contenu.
    
    Args:
        query: Terme de recherche
        count: Nombre de résultats (défaut: 7)
        extract_content: Si True, extrait le contenu complet de chaque page (défaut: True)
    
    Retourne les résultats avec titre, snippet, url et contenu complet extrait.
    """
    try:
        if not TAVILY_API_KEY:
            return {
                "status": "error",
                "message": "Clé API Tavily manquante. Configurez TAVILY_API_KEY dans .env"
            }
        
        # API Tavily
        endpoint = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": count,
            "include_raw_content": extract_content,
            "include_answer": True,
            "search_depth": "advanced" if extract_content else "basic"
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Erreur API Tavily: {response.status_code}"
            }
        
        data = response.json()
        
        # Formater les résultats
        results = []
        tavily_results = data.get("results", [])
        
        for item in tavily_results:
            result_item = {
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": item.get("url", "")
            }
            
            # Tavily fournit déjà le contenu extrait si demandé
            if extract_content:
                raw_content = item.get("raw_content", "")
                if raw_content:
                    # Limiter à 2000 caractères
                    result_item["content"] = raw_content[:2000] + ("..." if len(raw_content) > 2000 else "")
                    result_item["content_length"] = len(raw_content)
                else:
                    result_item["content"] = item.get("content", "Contenu non disponible")
            
            results.append(result_item)
        
        # Compter les succès d'extraction
        successful_extractions = sum(1 for r in results if r.get("content") and len(r.get("content", "")) > 100)
        
        # Inclure la réponse AI de Tavily si disponible
        ai_answer = data.get("answer", "")
        
        return {
            "status": "success",
            "query": query,
            "ai_answer": ai_answer if ai_answer else None,
            "results": results,
            "source": "Tavily AI Search",
            "count": len(results),
            "content_extracted": extract_content,
            "extraction_summary": f"{successful_extractions}/{len(results)} pages extraites avec succès" if extract_content else "Extraction désactivée"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur recherche web Tavily: {str(e)}"
        }


def execute(arguments):
    """Point d'entrée pour l'exécution du tool"""
    query = arguments.get("query", "")
    count = arguments.get("count", 7)
    
    return search_web(query, count)
