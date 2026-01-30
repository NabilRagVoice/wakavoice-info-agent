#!/usr/bin/env python3
"""
MCP Server: info-agent
Serveur MCP pour les outils d'information et utilitaires

Compatible avec Azure Voice Live API (MCP natif)

Outils:
- get_weather_forecast: Prévisions météo
- get_news: Actualités
- search_web: Recherche web (Tavily)
- convert_currency: Conversion devises
- calculate: Calculatrice
- get_prayer_times: Horaires de prière

Auteur: WakaCore Team
Date: 2026-01-30
"""

import os
import json
from datetime import datetime, timezone
from flask import Flask, Response, request, jsonify
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# MCP SERVER BASE
# =============================================================================

class MCPServer:
    def __init__(self, name: str, description: str, version: str = "2.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.tools = {}
        self.app = Flask(__name__)
        self._setup_routes()
    
    def tool(self, name: str, description: str, parameters: dict):
        """Décorateur pour enregistrer un outil MCP"""
        def decorator(func):
            self.tools[name] = {
                "name": name,
                "description": description,
                "inputSchema": {
                    "type": "object",
                    "properties": parameters.get("properties", {}),
                    "required": parameters.get("required", [])
                },
                "handler": func
            }
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _setup_routes(self):
        @self.app.route("/mcp", methods=["POST"])
        def mcp_endpoint():
            return self._handle_mcp_request()
        
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({
                "status": "ok",
                "server": self.name,
                "version": self.version,
                "tools_count": len(self.tools)
            })
        
        @self.app.route("/tools", methods=["GET"])
        def list_tools():
            tools_list = [{"name": t["name"], "description": t["description"]} for t in self.tools.values()]
            return jsonify({"tools": tools_list, "count": len(tools_list)})
        
        @self.app.route("/", methods=["GET"])
        def index():
            return jsonify({
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "endpoints": {
                    "mcp": "/mcp (POST)",
                    "health": "/health",
                    "tools": "/tools"
                },
                "tools_count": len(self.tools)
            })
    
    def _handle_mcp_request(self):
        data = request.get_json()
        if not data:
            return jsonify({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), 400
        
        request_id = data.get("id")
        method = data.get("method", "")
        params = data.get("params", {})
        
        if method == "initialize":
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": self.name, "version": self.version},
                    "capabilities": {"tools": {"listChanged": False}}
                }
            })
        
        elif method == "tools/list":
            tools_list = [{
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"]
            } for t in self.tools.values()]
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_list}
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                })
            
            try:
                result = self.tools[tool_name]["handler"](**arguments)
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, default=str)}]
                    }
                })
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": str(e)}
                })
        
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
    
    def run(self, host="0.0.0.0", port=8000):
        self.app.run(host=host, port=port, threaded=True)


# =============================================================================
# CRÉATION DU SERVEUR
# =============================================================================

server = MCPServer(
    name="info-agent",
    description="Agent d'information - Météo, actualités, recherche web, devises, calculatrice",
    version="2.0.0"
)

# Import des modules tools
from tools import tool_weather, tool_news, tool_search_web
from tools import tool_currency, tool_calculator, tool_prayer_times


# =============================================================================
# MÉTÉO
# =============================================================================

@server.tool(
    name="get_weather_forecast",
    description="""Prévisions météo pour une ville (température, pluie, vent).

VILLES COURANTES:
Burkina: Ouagadougou, Bobo-Dioulasso, Koudougou, Ouahigouya
France: Paris, Lyon, Marseille

Retourne météo actuelle et prévisions sur plusieurs jours.""",
    parameters={
        "properties": {
            "city": {"type": "string", "description": "Nom de la ville (ex: 'Ouagadougou')"},
            "country": {"type": "string", "description": "Pays (défaut: 'Burkina Faso')"},
            "days": {"type": "integer", "description": "Nombre de jours de prévision (1-5)"}
        },
        "required": ["city"]
    }
)
def get_weather_forecast(city: str, country: str = "Burkina Faso", days: int = 3):
    return tool_weather.get_weather_forecast(city=city, country=country, days=days)


# =============================================================================
# ACTUALITÉS
# =============================================================================

@server.tool(
    name="get_news",
    description="""Recherche les dernières actualités sur un sujet via NewsData.io.

EXEMPLES DE REQUÊTES:
- "Burkina Faso" (actualités du pays)
- "football africain" (sport)
- "CEDEAO" (organisation régionale)

Retourne liste d'articles avec titre, source et résumé.""",
    parameters={
        "properties": {
            "query": {"type": "string", "description": "Sujet ou mots-clés de recherche"},
            "language": {"type": "string", "description": "Code langue (fr, en, es)"},
            "max_results": {"type": "integer", "description": "Nombre d'articles (1-10)"}
        },
        "required": ["query"]
    }
)
def get_news(query: str, language: str = "fr", max_results: int = 5):
    return tool_news.execute({"query": query, "language": language, "max_results": max_results})


# =============================================================================
# RECHERCHE WEB
# =============================================================================

@server.tool(
    name="search_web",
    description="""Recherche web générale via Tavily AI.

À UTILISER EN DERNIER RECOURS quand aucun outil spécialisé ne convient.

EXEMPLES:
- "Qui est Ibrahim Traoré?"
- "Thomas Sankara discours"
- "capitale du Ghana"

Retourne résultats de recherche avec extraits de pages.""",
    parameters={
        "properties": {
            "query": {"type": "string", "description": "Question ou mots-clés de recherche"},
            "count": {"type": "integer", "description": "Nombre de résultats (1-10)"}
        },
        "required": ["query"]
    }
)
def search_web(query: str, count: int = 5):
    return tool_search_web.search_web(query=query, count=count)


# =============================================================================
# CONVERSION DE DEVISES
# =============================================================================

@server.tool(
    name="convert_currency",
    description="""Convertit un montant entre devises avec taux en temps réel.

DEVISES COURANTES:
- XOF: Franc CFA (Burkina, Côte d'Ivoire, Sénégal)
- EUR: Euro
- USD: Dollar américain
- GHS: Cedi ghanéen

EXEMPLE: 100000 XOF → EUR""",
    parameters={
        "properties": {
            "amount": {"type": "number", "description": "Montant à convertir (positif)"},
            "from_currency": {"type": "string", "description": "Code devise source (ex: 'XOF')"},
            "to_currency": {"type": "string", "description": "Code devise cible (ex: 'EUR')"}
        },
        "required": ["amount", "from_currency", "to_currency"]
    }
)
def convert_currency(amount: float, from_currency: str, to_currency: str):
    return tool_currency.convert_currency(amount=amount, from_currency=from_currency, to_currency=to_currency)


# =============================================================================
# CALCULATRICE
# =============================================================================

@server.tool(
    name="calculate",
    description="""Effectue des calculs mathématiques.

OPÉRATIONS SUPPORTÉES:
- Basiques: +, -, *, /
- Pourcentages: "20% de 500"
- Racines: sqrt(16)
- Puissances: 2**3

EXEMPLES: "2 + 2", "100 * 0.19", "sqrt(144)" """,
    parameters={
        "properties": {
            "expression": {"type": "string", "description": "Expression mathématique à calculer"}
        },
        "required": ["expression"]
    }
)
def calculate(expression: str):
    return tool_calculator.execute({"expression": expression})


# =============================================================================
# HORAIRES DE PRIÈRE
# =============================================================================

@server.tool(
    name="get_prayer_times",
    description="""Horaires des 5 prières quotidiennes islamiques (Fajr, Dhuhr, Asr, Maghrib, Isha).

VILLES BURKINA SUPPORTÉES:
- Ouagadougou (capitale)
- Bobo-Dioulasso
- Koudougou
- Ouahigouya
- Banfora""",
    parameters={
        "properties": {
            "city": {"type": "string", "description": "Ville du Burkina Faso (défaut: Ouagadougou)"},
            "date": {"type": "string", "description": "Date spécifique (YYYY-MM-DD) ou aujourd'hui par défaut"}
        },
        "required": []
    }
)
def get_prayer_times(city: str = "Ouagadougou", date: str = None):
    return tool_prayer_times.execute({"city": city, "date": date})


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    print("📰 Démarrage du serveur MCP info-agent v2.0.0...")
    server.run(host="0.0.0.0", port=8000)
