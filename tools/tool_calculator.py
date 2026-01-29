# tools/tool_calculator.py
"""
Tool : Calculatrice
Permet d'effectuer des calculs mathématiques.
"""

import logging
import math

logger = logging.getLogger(__name__)


def get_tool_definition():
    """
    Définition du tool pour OpenAI function calling
    """
    return {
        "type": "function",
        "name": "calculate",
        "description": "Effectue des calculs mathématiques. Supporte les opérations de base (+, -, *, /), puissances, racines carrées, pourcentages, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Expression mathématique à calculer (ex: '2+2', '10*5', 'sqrt(16)', '20% de 500')"
                }
            },
            "required": ["expression"]
        }
    }


def execute(arguments):
    """
    Exécute le calcul
    
    Args:
        arguments: Dictionnaire contenant:
            - expression: Expression mathématique
    
    Returns:
        dict: Résultat du calcul
    """
    expression = arguments.get('expression', '')
    
    logger.info(f"🔢 Calcul: '{expression}'")
    
    try:
        # Nettoyer l'expression
        expression = expression.strip()
        
        # Gérer les cas spéciaux
        # Pourcentage: "20% de 500"
        if '%' in expression and 'de' in expression.lower():
            parts = expression.lower().split('de')
            if len(parts) == 2:
                percent = float(parts[0].replace('%', '').strip())
                number = float(parts[1].strip())
                result = (percent / 100) * number
                return {
                    "status": "success",
                    "expression": expression,
                    "result": result,
                    "formatted": f"{percent}% de {number} = {result}",
                    "message": f"Le résultat est {result}"
                }
        
        # Remplacer les fonctions courantes
        expression = expression.replace('sqrt', 'math.sqrt')
        expression = expression.replace('pow', 'math.pow')
        expression = expression.replace('π', 'math.pi')
        expression = expression.replace('pi', 'math.pi')
        
        # Évaluer l'expression de manière sécurisée
        # Note: eval() est dangereux en production, utiliser une bibliothèque comme simpleeval
        allowed_names = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return {
            "status": "success",
            "expression": expression,
            "result": result,
            "formatted": f"{expression} = {result}",
            "message": f"Le résultat est {result}"
        }
        
    except ZeroDivisionError:
        return {
            "status": "error",
            "expression": expression,
            "message": "Erreur : Division par zéro impossible"
        }
    except Exception as e:
        logger.exception(f"❌ Erreur calcul: {str(e)}")
        return {
            "status": "error",
            "expression": expression,
            "message": f"Erreur lors du calcul : {str(e)}"
        }
