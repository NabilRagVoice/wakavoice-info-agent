#!/usr/bin/env python3
"""
MCP Server: info-agent
Serveur MCP pour les outils d'information et utilitaires

Outils:
- get_weather_forecast: Prévisions météo
- get_news: Actualités
- search_web: Recherche web (Tavily)
- convert_currency: Conversion devises
- calculate: Calculatrice
- get_prayer_times: Horaires de prière

Auteur: WakaCore Team
Date: 2026-01-29
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le chemin parent pour importer les tools
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

# Import des modules tools
from tools import tool_weather, tool_news, tool_search_web
from tools import tool_currency, tool_calculator, tool_prayer_times

# Créer le serveur MCP
mcp = FastMCP(
    "info-agent",
    instructions="Agent d'information - Météo, actualités, recherche web, devises, calculatrice",
    host="0.0.0.0",
    port=8000
)


# =============================================================================
# MÉTÉO
# =============================================================================

@mcp.tool()
def get_weather_forecast(
    city: str,
    country: str = "Burkina Faso",
    days: int = 3
) -> dict:
    """
    Prévisions météo pour une ville (température, pluie, vent).
    
    VILLES COURANTES:
    Burkina: Ouagadougou, Bobo-Dioulasso, Koudougou, Ouahigouya
    France: Paris, Lyon, Marseille
    
    Args:
        city: Nom de la ville (ex: "Ouagadougou")
        country: Pays (défaut: "Burkina Faso")
        days: Nombre de jours de prévision (1-5)
    
    Returns:
        dict: Météo actuelle et prévisions
    """
    return tool_weather.get_weather_forecast(
        city=city,
        country=country,
        days=days
    )


# =============================================================================
# ACTUALITÉS
# =============================================================================

@mcp.tool()
def get_news(
    query: str,
    language: str = "fr",
    max_results: int = 5
) -> dict:
    """
    Recherche les dernières actualités sur un sujet via NewsData.io.
    
    EXEMPLES DE REQUÊTES:
    - "Burkina Faso" (actualités du pays)
    - "Burkina Faso politique" (actualités politiques)
    - "football africain" (sport)
    - "CEDEAO" (organisation régionale)
    
    Args:
        query: Sujet ou mots-clés de recherche
        language: Code langue (fr, en, es)
        max_results: Nombre d'articles (1-10)
    
    Returns:
        dict: Liste d'articles avec titre, source et résumé
    """
    return tool_news.execute({
        "query": query,
        "language": language,
        "max_results": max_results
    })


# =============================================================================
# RECHERCHE WEB
# =============================================================================

@mcp.tool()
def search_web(
    query: str,
    count: int = 5
) -> dict:
    """
    Recherche web générale via Tavily AI.
    
    À UTILISER EN DERNIER RECOURS quand aucun outil spécialisé ne convient.
    
    EXEMPLES:
    - "Qui est Ibrahim Traoré?"
    - "Thomas Sankara discours"
    - "capitale du Ghana"
    - "recette tô burkinabè"
    
    Args:
        query: Question ou mots-clés de recherche
        count: Nombre de résultats (1-10)
    
    Returns:
        dict: Résultats de recherche avec extraits de pages
    """
    return tool_search_web.search_web(
        query=query,
        count=count
    )


# =============================================================================
# CONVERSION DE DEVISES
# =============================================================================

@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> dict:
    """
    Convertit un montant entre devises avec taux en temps réel.
    
    DEVISES COURANTES:
    - XOF: Franc CFA (Burkina, Côte d'Ivoire, Sénégal)
    - EUR: Euro
    - USD: Dollar américain
    - GHS: Cedi ghanéen
    - NGN: Naira nigérian
    
    EXEMPLE: 100000 XOF → EUR
    
    Args:
        amount: Montant à convertir (positif)
        from_currency: Code devise source (ex: "XOF")
        to_currency: Code devise cible (ex: "EUR")
    
    Returns:
        dict: Montant converti et taux de change
    """
    return tool_currency.convert_currency(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency
    )


# =============================================================================
# CALCULATRICE
# =============================================================================

@mcp.tool()
def calculate(
    expression: str
) -> dict:
    """
    Effectue des calculs mathématiques.
    
    OPÉRATIONS SUPPORTÉES:
    - Basiques: +, -, *, /
    - Pourcentages: "20% de 500"
    - Racines: sqrt(16)
    - Puissances: 2**3
    
    EXEMPLES:
    - "2 + 2"
    - "100 * 0.19"
    - "20% de 500"
    - "sqrt(144)"
    
    Args:
        expression: Expression mathématique à calculer
    
    Returns:
        dict: Résultat du calcul
    """
    return tool_calculator.execute({"expression": expression})


# =============================================================================
# HORAIRES DE PRIÈRE
# =============================================================================

@mcp.tool()
def get_prayer_times(
    city: str = "Ouagadougou",
    date: str = None
) -> dict:
    """
    Horaires des 5 prières quotidiennes islamiques (Fajr, Dhuhr, Asr, Maghrib, Isha).
    
    VILLES BURKINA SUPPORTÉES:
    - Ouagadougou (capitale)
    - Bobo-Dioulasso
    - Koudougou
    - Ouahigouya
    - Banfora
    - Fada N'Gourma
    
    Args:
        city: Ville du Burkina Faso (défaut: Ouagadougou)
        date: Date spécifique (YYYY-MM-DD) ou aujourd'hui par défaut
    
    Returns:
        dict: Horaires des 5 prières avec noms en arabe et français
    """
    return tool_prayer_times.execute({
        "city": city,
        "date": date
    })


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    print("📰 Démarrage du serveur MCP info-agent...")
    # Mode HTTP/SSE pour Container Apps
    mcp.run(transport="sse")
