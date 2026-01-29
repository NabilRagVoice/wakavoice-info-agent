# tools/tool_news.py
"""
Tool : Recherche d'actualités
Permet de rechercher les dernières actualités via NewsData.io API.
"""

import os
import logging
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration NewsData.io
NEWSDATA_API_KEY = os.getenv('NewsData_Key', '')
NEWSDATA_BASE_URL = 'https://newsdata.io/api/1/news'


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "get_news",
        "description": """Recherche les dernières actualités sur un sujet donné.
        
Retourne articles de presse récents avec titre, source et résumé.

EXEMPLE:
{
  "query": "Burkina Faso politique",
  "language": "fr",
  "max_results": 5
}""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """Sujet ou MOT-CLÉ pour rechercher les actualités.
                    
EXEMPLES VALIDES:
Sujets généraux:
- "Burkina Faso" (actualités du pays)
- "politique" (actualités politiques)
- "sport" (actualités sportives)
- "technologie" (actualités tech)
- "économie" (actualités économiques)

Sujets spécifiques:
- "Burkina Faso politique" (politique burkinabè)
- "football africain" (foot en Afrique)
- "sécurité Sahel" (sécurité au Sahel)
- "Covid-19 Afrique" (pandémie en Afrique)
- "JO 2024 Paris" (Jeux Olympiques)

Personnalités/organisations:
- "Ibrahim Traoré" (président)
- "CEDEAO" (organisation régionale)
- "Elon Musk" (entrepreneur)

CONVERSION depuis langage naturel:
- "quoi de neuf au Burkina" → "Burkina Faso"
- "actualités sportives" → "sport"
- "dernières news politique" → "politique"
- "infos sur la CEDEAO" → "CEDEAO"

CONSEILS:
- Utilise des mots-clés clairs et spécifiques
- Combine pays + thème pour cibler (ex: "Burkina Faso économie")
- Évite les phrases complètes, préfère les mots-clés

FORMAT: Texte libre, mots-clés séparés par espaces (ex: "Burkina Faso politique")"""
                },
                "language": {
                    "type": "string",
                    "description": """CODE de langue pour filtrer les résultats (ISO 639-1).
                    
CODES COURANTS:
- "fr" = Français (par défaut)
- "en" = Anglais (English)
- "es" = Espagnol (Español)
- "ar" = Arabe (العربية)
- "pt" = Portugais (Português)
- "de" = Allemand (Deutsch)
- "it" = Italien (Italiano)

CONVERSION:
- "en français" → "fr"
- "en anglais" → "en"
- "articles en espagnol" → "es"
- Aucune mention → "fr" (défaut)

REMARQUE: Filtre les articles écrits dans cette langue, pas la langue du sujet.

FORMAT: Code ISO 639-1 de 2 lettres en minuscules (ex: "fr", pas "FR" ni "francais")""",
                    "default": "fr"
                },
                "max_results": {
                    "type": "integer",
                    "description": """Nombre MAXIMUM d'articles à retourner (entre 1 et 10).
                    
EXEMPLES:
- 5 (par défaut - les 5 articles les plus récents)
- 3 (résumé rapide)
- 10 (maximum d'informations)

CONVERSION:
- "quelques articles" → 3
- "principales actualités" → 5
- "toutes les news" → 10
- Aucune mention → 5 (défaut)

FORMAT: Nombre entier entre 1 et 10 (ex: 5, pas "cinq" ni "5.0")""",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }


def execute(arguments):
    """
    Exécute la recherche d'actualités
    
    Args:
        arguments: Dictionnaire contenant:
            - query: Sujet à rechercher
            - language: Code langue (optionnel, défaut: 'fr')
            - max_results: Nombre de résultats (optionnel, défaut: 5)
    
    Returns:
        dict: Résultat de la recherche
    """
    query = arguments.get('query', '')
    language = arguments.get('language', 'fr')
    max_results = min(int(arguments.get('max_results', 5)), 10)
    
    if not query:
        return {
            "status": "error",
            "message": "Le sujet de recherche est requis"
        }
    
    logger.info(f"📰 Recherche actualités NewsData.io: '{query}' (langue: {language}, max: {max_results})")
    
    try:
        if not NEWSDATA_API_KEY:
            logger.error("❌ NewsData_Key manquant dans .env")
            return {
                "status": "error",
                "message": "Configuration NewsData.io manquante"
            }
        
        # Paramètres de recherche NewsData.io
        params = {
            'apikey': NEWSDATA_API_KEY,
            'q': query,
            'language': language,
            'size': max_results
        }
        
        # Requête API
        response = requests.get(NEWSDATA_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'success':
            logger.error(f"❌ Erreur NewsData.io: {data}")
            return {
                "status": "error",
                "message": "Erreur lors de la récupération des actualités"
            }
        
        results = data.get('results', [])
        
        if not results:
            return {
                "status": "success",
                "query": query,
                "language": language,
                "total_results": 0,
                "articles": [],
                "message": f"Aucune actualité trouvée pour '{query}'"
            }
        
        # Formater les articles
        articles = []
        for article in results[:max_results]:
            # Formater la date
            pub_date = article.get('pubDate', '')
            try:
                if pub_date:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%d/%m/%Y %H:%M')
                else:
                    formatted_date = 'Date inconnue'
            except:
                formatted_date = pub_date
            
            articles.append({
                "title": article.get('title', 'Sans titre'),
                "source": article.get('source_id', 'Source inconnue'),
                "published_at": pub_date,
                "formatted_date": formatted_date,
                "summary": article.get('description', 'Aucun résumé disponible') or article.get('content', 'Aucun contenu')[:200] + '...',
                "url": article.get('link', ''),
                "image_url": article.get('image_url', ''),
                "category": article.get('category', [])
            })
        
        return {
            "status": "success",
            "query": query,
            "language": language,
            "total_results": len(articles),
            "articles": articles,
            "message": f"✅ {len(articles)} article(s) récent(s) trouvé(s) sur '{query}'"
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur recherche actualités: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la recherche d'actualités: {str(e)}"
        }
