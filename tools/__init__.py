# tools/__init__.py
"""
Orchestrateur des outils pour Waka Agent AI
Importe tous les modules d'outils et fournit les fonctions centrales:
- get_tools_definition(): Retourne toutes les définitions d'outils
- get_tools_definition_compact(): Retourne des définitions compactes pour Voice Live
- execute_tool(tool_name, arguments): Exécute un outil spécifique
"""

# ⚡ OPTIMISATION: Imports lazy pour éviter le timeout 502
# Les imports sont déplacés dans les fonctions pour accélérer le chargement


def _truncate_description(text, max_length=200):
    """Tronque une description à une longueur maximale."""
    if not text:
        return text
    # Nettoyer les espaces multiples et retours à la ligne
    text = ' '.join(text.split())
    if len(text) <= max_length:
        return text
    # Couper au dernier espace avant la limite
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."


def _compact_tool_definition(tool):
    """Crée une version compacte d'une définition de tool pour Voice Live."""
    if 'function' in tool:
        func = tool['function']
        compact_func = {
            "name": func.get('name', ''),
            "description": _truncate_description(func.get('description', ''), 150),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        # Simplifier les paramètres
        params = func.get('parameters', {})
        if 'properties' in params:
            for key, value in params['properties'].items():
                compact_func['parameters']['properties'][key] = {
                    "type": value.get('type', 'string'),
                    "description": _truncate_description(value.get('description', ''), 80)
                }
                if 'default' in value:
                    compact_func['parameters']['properties'][key]['default'] = value['default']
        if 'required' in params:
            compact_func['parameters']['required'] = params['required']
        
        return {"type": "function", "function": compact_func}
    return tool


def _convert_to_realtime_format(tool):
    """
    Convertit un tool du format Chat Completions au format Realtime API.
    
    Format Chat Completions (entrée):
    {
        "type": "function",
        "function": {
            "name": "...",
            "description": "...",
            "parameters": {...}
        }
    }
    
    Format Realtime API (sortie):
    {
        "type": "function",
        "name": "...",
        "description": "...",
        "parameters": {...}
    }
    """
    if 'function' in tool:
        func = tool['function']
        return {
            "type": "function",
            "name": func.get('name', ''),
            "description": _truncate_description(func.get('description', ''), 150),
            "parameters": func.get('parameters', {"type": "object", "properties": {}})
        }
    # Si déjà au bon format ou format inconnu, retourner tel quel
    return tool


def get_tools_definition_realtime():
    """
    Retourne des définitions d'outils au format Realtime API (Voice Live).
    Ce format est différent du format Chat Completions.
    
    Returns:
        list: Liste des définitions au format RealtimeFunctionTool
    """
    chat_tools = get_tools_definition(compact=True)
    return [_convert_to_realtime_format(t) for t in chat_tools]


def get_tools_definition(compact=False):
    """
    Retourne la liste complète des définitions d'outils.
    Collecte les définitions de tous les modules de tools/.
    
    Args:
        compact: Si True, retourne des définitions compactes pour Voice Live
    
    Returns:
        list: Liste des définitions d'outils au format OpenAI function calling
    """
    # ⚡ Import lazy: charger les modules seulement quand nécessaire
    from . import tool_search_web
    from . import tool_email
    from . import tool_weather
    from . import tool_cv
    from . import tool_currency
    from . import tool_flight_search
    from . import tool_hotel_search
    from . import tool_flight_booking
    from . import tool_hotel_booking
    from . import tool_exercises
    from . import tool_dogs
    from . import tool_knowledge_base
    from . import tool_health_advice
    from . import tool_news
    from . import tool_places
    from . import tool_translator
    from . import tool_calculator
    # Tool de fin de conversation (sans sessions)
    from . import tool_end_conversation
    from . import tool_prayer_times
    from . import tool_pharmacy_locator
    from . import tool_taxi_estimate
    from . import tool_bus_schedule
    from . import tool_school_info
    from . import tool_government_services
    from . import tool_tax_calculator
    # Outils campagne de recouvrement
    from . import tool_send_confirmation_email
    from . import tool_send_sms_disconnection
    from . import tool_send_sms_payment_promise
    from . import tool_send_sms_extension_confirm
    from . import tool_schedule_callback
    # tool_end_call_status supprimé
    # Brain tool pour gestion dynamique des instructions
    from . import tool_conversation_brain
    # Outils de génération et analyse de documents
    from utils.tools.document_generator import DOCUMENT_GENERATION_TOOL
    from utils.tools.document_analyzer import DOCUMENT_ANALYZER_TOOL
    # Outil de création de configuration d'agent
    from . import tool_create_agent_config
    # Outil pour lister les voix Azure
    from . import tool_list_azure_voices

    raw_tools = [
        tool_search_web.get_tool_definition(),
        tool_email.get_tool_definition(),
        tool_weather.get_tool_definition(),
        tool_cv.get_tool_definition(),
        tool_currency.get_tool_definition(),
        tool_flight_search.get_tool_definition(),
        tool_hotel_search.get_tool_definition(),
        tool_flight_booking.get_tool_definition(),
        tool_hotel_booking.get_tool_definition(),
        tool_exercises.get_tool_definition(),
        tool_dogs.get_tool_definition(),
        tool_knowledge_base.get_tool_definition(),
        tool_health_advice.get_tool_definition(),
        tool_news.get_tool_definition(),
        tool_places.get_tool_definition(),
        tool_translator.get_tool_definition(),
        tool_calculator.get_tool_definition(),
        tool_end_conversation.get_tool_definition(),
        tool_prayer_times.get_tool_definition(),
        tool_pharmacy_locator.get_tool_definition(),
        tool_taxi_estimate.get_tool_definition(),
        tool_bus_schedule.get_tool_definition(),
        tool_school_info.get_tool_definition(),
        tool_government_services.get_tool_definition(),
        tool_tax_calculator.get_tool_definition(),
        # Outils campagne de recouvrement
        tool_send_confirmation_email.get_tool_definition(),
        tool_send_sms_disconnection.get_tool_definition(),
        tool_send_sms_payment_promise.get_tool_definition(),
        tool_send_sms_extension_confirm.get_tool_definition(),
        tool_schedule_callback.get_tool_definition(),
        # Brain tool
        tool_conversation_brain.get_tool_definition(),
        # Outils de génération et analyse de documents
        DOCUMENT_GENERATION_TOOL,
        DOCUMENT_ANALYZER_TOOL,
        # Outil de création de configuration d'agent
        tool_create_agent_config.get_tool_definition(),
        # Outil pour lister les voix Azure
        tool_list_azure_voices.get_tool_definition()
    ]
    
    # Correction automatique du format pour compatibilité OpenAI
    formatted_tools = []
    for tool in raw_tools:
        # Si le format est déjà correct (avec clé 'function'), on le garde tel quel
        if 'function' in tool:
            formatted_tools.append(tool)
        # Si le format est plat (name, description au niveau racine), on l'enveloppe
        elif 'name' in tool and 'description' in tool:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool['name'],
                    "description": tool['description'],
                    "parameters": tool.get('parameters', {})
                }
            })
        else:
            formatted_tools.append(tool)
    
    # Si mode compact demandé, réduire les descriptions
    if compact:
        formatted_tools = [_compact_tool_definition(t) for t in formatted_tools]
            
    return formatted_tools


def get_tools_definition_compact():
    """
    Retourne des définitions d'outils compactes pour Voice Live.
    Les descriptions sont tronquées pour réduire la taille du payload.
    """
    return get_tools_definition(compact=True)


def execute_tool(tool_name, arguments):
    """
    Exécute un outil spécifique avec les arguments fournis.
    
    Args:
        tool_name: Nom de l'outil à exécuter
        arguments: Dictionnaire des arguments pour l'outil
    
    Returns:
        dict: Résultat de l'exécution de l'outil
    """
    # ⚡ Import lazy: charger seulement le module nécessaire
    from . import tool_search_web
    from . import tool_email
    from . import tool_weather
    from . import tool_cv
    from . import tool_currency
    from . import tool_flight_search
    from . import tool_hotel_search
    from . import tool_flight_booking
    from . import tool_hotel_booking
    from . import tool_exercises
    from . import tool_dogs
    from . import tool_knowledge_base
    from . import tool_health_advice
    from . import tool_news
    from . import tool_places
    from . import tool_translator
    from . import tool_calculator
    # Tool de fin de conversation (sans sessions)
    from . import tool_end_conversation
    from . import tool_prayer_times
    from . import tool_pharmacy_locator
    from . import tool_taxi_estimate
    from . import tool_bus_schedule
    from . import tool_school_info
    from . import tool_government_services
    from . import tool_tax_calculator
    from . import tool_conversation_brain
    # Outils de génération et analyse de documents
    from utils.tools import document_generator
    from utils.tools import document_analyzer
    # Outil de création de configuration d'agent
    from . import tool_create_agent_config
    # Outil pour lister les voix Azure
    from . import tool_list_azure_voices
    # Outils campagne de recouvrement
    from . import tool_schedule_callback
    from . import tool_send_confirmation_email
    from . import tool_send_sms_disconnection
    from . import tool_send_sms_payment_promise
    from . import tool_send_sms_extension_confirm
    # tool_end_call_status supprimé
    
    # Mapping des noms d'outils vers leurs modules
    tool_map = {
        "search_web": tool_search_web,
        "send_email": tool_email,
        "get_weather_forecast": tool_weather,
        "create_cv": tool_cv,
        "convert_currency": tool_currency,
        "search_flights": tool_flight_search,
        "search_hotels": tool_hotel_search,
        "book_flight": tool_flight_booking,
        "book_hotel": tool_hotel_booking,
        "search_exercises": tool_exercises,
        "search_dog_breeds": tool_dogs,
        "search_knowledge_base": tool_knowledge_base,
        "get_health_advice": tool_health_advice,
        "get_news": tool_news,
        "search_places": tool_places,
        "translate_text": tool_translator,
        "calculate": tool_calculator,
        "end_conversation": tool_end_conversation,
        "get_prayer_times": tool_prayer_times,
        "find_pharmacy": tool_pharmacy_locator,
        "estimate_taxi_fare": tool_taxi_estimate,
        "get_bus_schedule": tool_bus_schedule,
        "get_school_info": tool_school_info,
        "get_government_service_info": tool_government_services,
        "calculate_tax": tool_tax_calculator,
        "get_next_instruction": tool_conversation_brain,
        # Outils campagne de recouvrement
        "schedule_callback": tool_schedule_callback,
        "send_confirmation_email": tool_send_confirmation_email,
        "send_sms_disconnection": tool_send_sms_disconnection,
        "send_sms_payment_promise": tool_send_sms_payment_promise,
        "send_sms_extension_confirm": tool_send_sms_extension_confirm,
        # Outils de génération et analyse de documents
        "generate_document": document_generator,
        "analyze_document": document_analyzer,
        # Outil de création de configuration d'agent
        "create_agent_config": tool_create_agent_config,
        # Outil pour lister les voix Azure
        "list_azure_voices": tool_list_azure_voices
    }
    
    # Chercher le module correspondant
    tool_module = tool_map.get(tool_name)
    
    if not tool_module:
        return {
            "status": "error",
            "message": f"Outil '{tool_name}' non trouvé. Outils disponibles: {', '.join(tool_map.keys())}"
        }
    
    try:
        # Cas spéciaux pour les outils de documents (utilisent handle_* au lieu de execute)
        if tool_name == "generate_document":
            result = tool_module.handle_document_generation_tool_call(arguments)
            return {"status": "success", "result": result}
        elif tool_name == "analyze_document":
            result = tool_module.handle_document_analyzer_tool_call(
                file_content=arguments.get('file_content', ''),
                filename=arguments.get('filename', ''),
                analysis_type=arguments.get('analysis_type', 'extract_text'),
                specific_question=arguments.get('specific_question')
            )
            return {"status": "success", "result": result}

        # Exécuter l'outil via sa fonction execute()
        result = tool_module.execute(arguments)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de l'exécution de l'outil '{tool_name}': {str(e)}"
        }


# Export des fonctions principales
__all__ = ['get_tools_definition', 'execute_tool']
