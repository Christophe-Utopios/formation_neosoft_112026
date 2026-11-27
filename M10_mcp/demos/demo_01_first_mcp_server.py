"""
Test interactif :
    npx @modelcontextprotocol/inspector python demo_01_first_mcp_server.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Réutilise la maquette de l'API NeoFlow du M6
M6_DEMOS = Path(__file__).resolve().parent.parent.parent / "M06_agents_partie1" / "demos"
sys.path.insert(0, str(M6_DEMOS))
import _neoflow as neo

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-neoflow-server")


@mcp.tool()
def trouver_collaborateur(nom: str) -> dict:
    """Recherche un collaborateur NeoFlow par son nom ou son login (exact ou contenant).

    Utiliser quand : on connaît le nom de la personne (ex: 'Alice Martin', 'Bob').
    Ne PAS utiliser pour : lister des demandes (utiliser lister_demandes à la place).

    Args:
        nom: nom partiel ou complet, ou login.

    Returns:
        Dict {login, nom, departement, date_entree} ou {"error": "not_found"}.
    """
    c = neo.trouver_collaborateur(nom)
    return c if c else {"error": "not_found", "query": nom}


@mcp.tool()
def compter_demandes(login: str, statut: str = "SOUMISE") -> dict:
    """Compte les demandes d'un collaborateur pour un statut donné.

    Statuts possibles : BROUILLON, SOUMISE (en attente de validation), VALIDEE, REFUSEE, CLOTUREE.

    Args:
        login: login NeoFlow du collaborateur (ex: 'alice').
        statut: statut des demandes à compter, SOUMISE par défaut.
    """
    if login not in neo.COLLABORATEURS:
        return {"error": "collaborateur_not_found", "login": login}
    return {"login": login, "statut": statut, "count": neo.compter_demandes(login, statut)}


@mcp.tool()
def lister_demandes(login: str, statut: str = "SOUMISE") -> list[dict]:
    """Liste les demandes d'un collaborateur filtrées par statut.

    Args:
        login: login NeoFlow du collaborateur.
        statut: BROUILLON, SOUMISE (par défaut), VALIDEE, REFUSEE ou CLOTUREE.

    Returns:
        Liste de dicts {id, type, titre, montant, statut, niveau_validation} (vide si rien trouvé).
    """
    return neo.lister_demandes(login, statut)


if __name__ == "__main__":
    # Mode stdio : lancement par le client MCP
    mcp.run()
