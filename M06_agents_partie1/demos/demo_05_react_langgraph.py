from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from rich.console import Console

import _neoflow as neo

load_dotenv()
console = Console()
LLM_MODEL = "claude-sonnet-4-6"


# Déclaration des outils disponibles avec le décorateur @tool de LangChain
# Chaque docstring décrit l'outil pour le LLM

@tool
def trouver_collaborateur(nom: str) -> dict:
    """Recherche un collaborateur NeoFlow par nom ou login (exact ou contenant)."""
    c = neo.trouver_collaborateur(nom)
    return c if c else {"error": f"Collaborateur '{nom}' introuvable"}


@tool
def compter_demandes(login: str, statut: str = "SOUMISE") -> dict:
    """Compte les demandes d'un collaborateur pour un statut, SOUMISE par défaut. Statuts : BROUILLON (pas encore envoyée), SOUMISE (en attente de validation), VALIDEE, REFUSEE, CLOTUREE."""
    return {"count": neo.compter_demandes(login, statut)}


@tool
def lister_demandes(login: str, statut: str = "SOUMISE") -> list[dict]:
    """Liste les demandes d'un collaborateur filtrées par statut. Statuts : BROUILLON (pas encore envoyée), SOUMISE (en attente de validation), VALIDEE, REFUSEE, CLOTUREE."""
    return neo.lister_demandes(login, statut)


@tool
def creer_brouillon(login: str, type_demande: str, titre: str, montant: float | None = None) -> dict:
    """Crée une demande au statut BROUILLON (type : CONGES, NOTE_DE_FRAIS, DEPLACEMENT, ACHAT...)."""
    return neo.creer_brouillon(login, type_demande, titre, montant)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY manquant[/red]")
        return

    console.print("\n[bold orange3]Demo 05 — Agent ReAct LangGraph[/bold orange3]\n")

    llm = ChatAnthropic(model=LLM_MODEL)
    tools = [trouver_collaborateur, compter_demandes, lister_demandes, creer_brouillon]

    # create_react_agent : helper LangGraph qui crée automatiquement un graphe ReAct complet
    # (boucle raisonnement → action → observation → raisonnement)
    agent = create_react_agent(llm, tools=tools)

    question = ("Pour Alice Martin, donne-moi son département, le nombre de demandes en attente "
                "et la liste de ses brouillons avec leur montant. "
                "Ensuite crée un brouillon de note de frais 'Taxi gare de Nantes' de 32,50 €.")

    console.print(f"[bold cyan]Question :[/bold cyan]\n{question}\n")

    # Streaming des étapes : permet de suivre en temps réel le raisonnement de l'agent
    console.print("[bold]Streaming des étapes :[/bold]\n")

    for chunk in agent.stream(
        {"messages": [("user", question)]},
        stream_mode="values",  # Retourne le State complet à chaque étape
    ):
        msg = chunk["messages"][-1]
        if msg.type == "ai":
            if msg.tool_calls:
                # L'agent a décidé d'appeler un outil
                for call in msg.tool_calls:
                    console.print(f"[yellow]🔧 {call['name']}({call['args']})[/yellow]")
            elif msg.content:
                # L'agent raisonne ou répond
                console.print(f"[orange3]🤖 {msg.content}[/orange3]")
        elif msg.type == "tool":
            # Résultat de l'exécution de l'outil
            content = str(msg.content)[:200]
            console.print(f"[dim]   ↩ {content}[/dim]")

    console.print("\n[bold]À retenir :[/bold]")
    console.print("• create_react_agent encapsule la boucle ReAct standard")
    console.print("• Le streaming permet d'afficher les étapes en temps réel à l'utilisateur")
    console.print("• Chaque tool reçoit ses arguments validés via Pydantic\n")


if __name__ == "__main__":
    main()