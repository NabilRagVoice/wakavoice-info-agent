# tools/tool_translator.py
"""
Tool : Traduction de texte
Permet de traduire du texte d'une langue à une autre via Azure Translator.
"""

import os
import logging
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration Azure Translator
AZURE_TRANSLATOR_KEY = os.getenv('AZURE_TRANSLATOR_KEY', '')
AZURE_TRANSLATOR_ENDPOINT = os.getenv('AZURE_TRANSLATOR_ENDPOINT', 'https://usageinterne-0509-resource.cognitiveservices.azure.com/')
AZURE_TRANSLATOR_REGION = os.getenv('AZURE_TRANSLATOR_REGION', 'eastus2')


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "translate_text",
        "description": """Traduit un texte d'une langue source vers une langue cible.
        
Supporte de nombreuses langues internationales et africaines.

EXEMPLE:
{
  "text": "Bonjour, comment allez-vous?",
  "source_language": "fr",
  "target_language": "en"
}

Résultat: Hello, how are you?""",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": """TEXTE à traduire (peut être un mot, une phrase ou un paragraphe).
                    
EXEMPLES:
Mots simples:
- "bonjour"
- "merci"
- "au revoir"

Phrases:
- "Comment allez-vous?"
- "Je m'appelle Jean"
- "Où est l'aéroport?"

Paragraphes:
- Plusieurs phrases complètes
- Textes longs (emails, messages)

FORMAT: Texte libre de toute longueur"""
                },
                "source_language": {
                    "type": "string",
                    "description": """CODE de la langue SOURCE (langue du texte à traduire).
                    
CODES INTERNATIONAUX (ISO 639-1):
- "fr" = Français
- "en" = Anglais (English)
- "es" = Espagnol (Español)
- "ar" = Arabe (العربية)
- "pt" = Portugais (Português)
- "de" = Allemand (Deutsch)
- "it" = Italien (Italiano)
- "zh" = Chinois (中文)
- "ja" = Japonais (日本語)
- "ru" = Russe (Русский)

LANGUES AFRICAINES:
- "moore" = Mooré (Burkina Faso)
- "dioula" = Dioula (Burkina Faso, Côte d'Ivoire, Mali)
- "bambara" = Bambara (Mali)
- "wolof" = Wolof (Sénégal)
- "fulfulde" = Peul (Afrique de l'Ouest)
- "hausa" = Haoussa (Niger, Nigeria)
- "swahili" = Swahili (Afrique de l'Est)

DÉTECTION AUTOMATIQUE:
- "auto" = Détecte automatiquement la langue source (par défaut)

CONVERSION:
- "depuis le français" → "fr"
- "de l'anglais" → "en"
- "du mooré" → "moore"
- Aucune mention → "auto" (défaut)

FORMAT: Code ISO 639-1 en minuscules (ex: "fr") ou nom complet pour langues africaines (ex: "moore")""",
                    "default": "auto"
                },
                "target_language": {
                    "type": "string",
                    "description": """CODE de la langue CIBLE (langue vers laquelle traduire) - OBLIGATOIRE.
                    
CODES INTERNATIONAUX (ISO 639-1):
- "fr" = Français
- "en" = Anglais (English)
- "es" = Espagnol (Español)
- "ar" = Arabe (العربية)
- "pt" = Portugais (Português)
- "de" = Allemand (Deutsch)
- "it" = Italien (Italiano)
- "zh" = Chinois (中文)
- "ja" = Japonais (日本語)
- "ru" = Russe (Русский)

LANGUES AFRICAINES:
- "moore" = Mooré (Burkina Faso)
- "dioula" = Dioula (Burkina Faso, Côte d'Ivoire, Mali)
- "bambara" = Bambara (Mali)
- "wolof" = Wolof (Sénégal)
- "fulfulde" = Peul (Afrique de l'Ouest)
- "hausa" = Haoussa (Niger, Nigeria)
- "swahili" = Swahili (Afrique de l'Est)

EXEMPLES D'USAGE:
- Français → Anglais: target_language="en"
- Anglais → Mooré: target_language="moore"
- Dioula → Français: target_language="fr"

CONVERSION:
- "en français" → "fr"
- "vers l'anglais" → "en"
- "en mooré" → "moore"
- "traduire en dioula" → "dioula"

FORMAT: Code ISO 639-1 en minuscules (ex: "en") ou nom complet pour langues africaines (ex: "moore")"""
                }
            },
            "required": ["text", "target_language"]
        }
    }


def translate_with_azure(text, source_lang, target_lang):
    """
    Traduit un texte via Azure Translator API
    
    Args:
        text: Texte à traduire
        source_lang: Code langue source ('auto' pour détection)
        target_lang: Code langue cible
    
    Returns:
        tuple: (translated_text, detected_source_lang)
    """
    if not AZURE_TRANSLATOR_KEY:
        logger.error("❌ AZURE_TRANSLATOR_KEY manquant dans .env")
        raise Exception("Configuration Azure Translator manquante")
    
    # Endpoint de traduction
    path = '/translate'
    constructed_url = AZURE_TRANSLATOR_ENDPOINT.rstrip('/') + path
    
    # Paramètres
    params = {
        'api-version': '3.0',
        'to': target_lang
    }
    
    # Ajouter langue source si spécifiée (sinon détection auto)
    if source_lang and source_lang != 'auto':
        params['from'] = source_lang
    
    # Headers
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    
    # Body
    body = [{'text': text}]
    
    # Requête
    response = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    
    if result and len(result) > 0:
        translation = result[0]
        translated_text = translation['translations'][0]['text']
        detected_lang = translation.get('detectedLanguage', {}).get('language', source_lang)
        
        return translated_text, detected_lang
    else:
        raise Exception("Réponse vide de l'API Azure Translator")


def execute(arguments):
    """
    Exécute la traduction via Azure Translator
    
    Args:
        arguments: Dictionnaire contenant:
            - text: Texte à traduire
            - source_language: Langue source (optionnel, défaut: 'auto')
            - target_language: Langue cible
    
    Returns:
        dict: Résultat de la traduction
    """
    text = arguments.get('text', '')
    source_lang = arguments.get('source_language', 'auto')
    target_lang = arguments.get('target_language', 'fr')
    
    if not text:
        return {
            "status": "error",
            "message": "Le texte à traduire est requis"
        }
    
    logger.info(f"🌍 Traduction Azure: '{text[:50]}...' de {source_lang} vers {target_lang}")
    
    try:
        # Appel à Azure Translator
        translated_text, detected_lang = translate_with_azure(text, source_lang, target_lang)
        
        # Nom complet de la langue détectée
        language_names = {
            'fr': 'Français',
            'en': 'Anglais',
            'es': 'Espagnol',
            'ar': 'Arabe',
            'pt': 'Portugais',
            'de': 'Allemand',
            'it': 'Italien',
            'zh-Hans': 'Chinois',
            'ja': 'Japonais',
            'ru': 'Russe'
        }
        
        source_name = language_names.get(detected_lang, detected_lang)
        target_name = language_names.get(target_lang, target_lang)
        
        return {
            "status": "success",
            "original_text": text,
            "translated_text": translated_text,
            "source_language": detected_lang,
            "source_language_name": source_name,
            "target_language": target_lang,
            "target_language_name": target_name,
            "message": f"✅ Texte traduit de {source_name} vers {target_name}"
        }
        
    except Exception as e:
        logger.exception(f"❌ Erreur traduction Azure: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la traduction: {str(e)}"
        }
