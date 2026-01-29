# tools/tool_end_conversation.py
"""
Tool : Fin de conversation
Permet au modèle de détecter la fin d'une conversation et de déclencher
une fin d'échange propre côté assistant.

Ce tool est appelé par le modèle quand il détecte que l'utilisateur souhaite
terminer la conversation (au revoir, merci, fin d'échange, etc.)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_tool_definition() -> Dict[str, Any]:
    """
    Définition du tool pour OpenAI function calling.
    Ce tool est conçu pour être détecté automatiquement par le modèle
    quand la conversation arrive à sa fin naturelle.
    """
    return {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": """Termine la conversation en cours.

QUAND APPELER CE TOOL:
- L'utilisateur dit au revoir, bonne journée, à bientôt, merci et au revoir
- L'utilisateur indique qu'il n'a plus de questions
- L'utilisateur demande explicitement de terminer l'appel
- La conversation arrive à sa conclusion naturelle
- L'utilisateur remercie et semble satisfait
- Phrases de fin détectées: "c'est tout", "je n'ai plus besoin", "merci beaucoup", etc.

IMPORTANT: 
- Toujours appeler ce tool avant de dire au revoir à l'utilisateur
- Fournir un message d'au revoir approprié et personnalisé""",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": """Raison de la fin de conversation.

VALEURS POSSIBLES:
- "user_goodbye" : L'utilisateur a dit au revoir
- "user_satisfied" : L'utilisateur est satisfait, n'a plus de questions
- "task_completed" : La tâche demandée est terminée
- "user_request" : L'utilisateur demande explicitement de terminer
- "natural_end" : La conversation arrive à sa fin naturelle
- "timeout" : Inactivité prolongée (utilisé par le système)
- "error" : Erreur technique nécessitant une clôture

EXEMPLE: "user_goodbye" """
                    },
                    "farewell_message": {
                        "type": "string",
                        "description": """Message d'au revoir personnalisé à envoyer à l'utilisateur.
Doit être chaleureux, approprié au contexte et dans la langue de la conversation.

EXEMPLES:
- "Au revoir et bonne journée!"
- "Merci pour cet échange, à bientôt!"
- "N'hésitez pas à me recontacter si vous avez d'autres questions!"
- "Ce fut un plaisir de vous aider, prenez soin de vous!"

NOTE: Adapter le ton selon le contexte et la relation établie."""
                    },
                    "user_sentiment": {
                        "type": "string",
                        "enum": ["positive", "neutral", "negative", "mixed"],
                        "description": """Sentiment perçu de l'utilisateur à la fin de la conversation.

VALEURS:
- "positive" : Utilisateur satisfait, content, reconnaissant
- "neutral" : Échange professionnel, ni positif ni négatif
- "negative" : Utilisateur insatisfait, frustré, mécontent
- "mixed" : Sentiments mélangés au cours de la conversation

Cette évaluation sera comparée avec l'analyse automatique."""
                    },
                    "conversation_summary": {
                        "type": "string",
                        "description": """Résumé bref de la conversation (2-3 phrases).
Optionnel - un résumé automatique sera généré si non fourni.

CONTENU RECOMMANDÉ:
- Sujet principal abordé
- Actions effectuées ou informations fournies
- Résolution ou état final

EXEMPLE: "L'utilisateur a demandé des informations sur les vols Paris-Dakar. 
J'ai fourni les options disponibles et les prix. L'utilisateur a choisi de réfléchir." """
                    }
                },
                "required": ["reason", "farewell_message"]
            }
        }
    }


def execute(arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Exécute la clôture de la conversation.
    
    Note: Les fonctionnalités de "session" et de clôture/persistance associées
    ont été supprimées. Ce tool renvoie uniquement un signal de fin.
    
    Args:
        arguments: Paramètres du tool (reason, farewell_message, etc.)
        context: Contexte optionnel (session_id, agent_id, etc.)
    
    Returns:
        Dict avec signal de fin et métadonnées
    """
    reason = arguments.get("reason", "natural_end")
    farewell_message = arguments.get("farewell_message", "Au revoir!")
    user_sentiment = arguments.get("user_sentiment", "neutral")
    conversation_summary = arguments.get("conversation_summary", "")
    
    logger.info(f"🔚 Tool end_conversation appelé - Raison: {reason}")
    logger.info(f"   Message d'au revoir: {farewell_message[:50]}...")
    
    return {
        "success": True,
        "status": "success",
        "action": "end_conversation",
        "signal_end_conversation": True,
        "reason": reason,
        "farewell_message": farewell_message,
        "model_assessment": {
            "user_sentiment": user_sentiment,
            "summary_hint": conversation_summary
        },
        "message": f"Conversation terminée. Raison: {reason}",
        "instructions": "Dis au revoir à l'utilisateur avec le message fourni dans farewell_message."
    }


async def execute_async(arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Version asynchrone de execute() pour les contextes async."""
    return execute(arguments, context)


# Alias pour compatibilité
def handle_end_conversation(arguments: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Alias pour execute() - compatibilité avec anciens handlers."""
    return execute(arguments, kwargs)


# Export pour utilisation directe
__all__ = [
    'get_tool_definition',
    'execute',
    'execute_async',
    'handle_end_conversation'
]
