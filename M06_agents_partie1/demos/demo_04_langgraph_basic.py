import os
from typing import Optional, TypedDict

from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from rich.console import Console
from rich.panel import Panel

import _neoflow as neo

load_dotenv()
console = Console()
LLM_MODEL = "claude-haiku-4-5-20251001"


# State partagé : structure de données passée entre tous les nodes du graphe
# NB : Optional[X] (et non `X | None`) pour compat Python 3.9 lors de
# l'évaluation des type hints par LangGraph.
class AgentState(TypedDict):
    question: str
    nom_collaborateur: Optional[str]
    collaborateur: Optional[dict]
    n_demandes: Optional[int]
    answer: Optional[str]


def extract_collaborateur(state: AgentState) -> dict:
    """
    Node 1 : extraire le nom du collaborateur depuis la question.
    Retourne un dict partiel qui met à jour le State.
    """
    llm = Anthropic()
    msg = llm.messages.create(
        model=LLM_MODEL, max_tokens=50,
        messages=[{"role": "user", "content": f"Voici la question d'un utilisateur de NeoFlow. Extrais le nom de la personne dont elle parle. Réponds uniquement avec ce nom, sans phrase.\n\nQuestion : {state['question']}"}],
    )
    name = msg.content[0].text.strip()
    console.print(f"[dim]→ extract_collaborateur : '{name}'[/dim]")
    return {"nom_collaborateur": name}  # Mise à jour partielle du State


def fetch_demandes(state: AgentState) -> dict:
    """
    Node 2 : appeler l'API NeoFlow pour récupérer le collaborateur et ses demandes en attente.
    Utilise nom_collaborateur du State pour faire les appels API.
    """
    if not state.get("nom_collaborateur"):
        return {"collaborateur": None, "n_demandes": 0}
    collab = neo.trouver_collaborateur(state["nom_collaborateur"])
    if not collab:
        console.print(f"[dim]→ fetch_demandes : collaborateur introuvable[/dim]")
        return {"collaborateur": None, "n_demandes": 0}
    n = neo.compter_demandes(collab["login"], "SOUMISE")
    console.print(f"[dim]→ fetch_demandes : {collab['nom']}, {n} demandes en attente[/dim]")
    return {"collaborateur": collab, "n_demandes": n}


def generate_answer(state: AgentState) -> dict:
    """
    Node 3 : générer la réponse finale.
    Synthétise toutes les données du State en réponse utilisateur.
    """
    llm = Anthropic()
    if not state.get("collaborateur"):
        return {"answer": f"Je n'ai pas trouvé le collaborateur '{state.get('nom_collaborateur', 'inconnu')}'."}

    context = f"Collaborateur : {state['collaborateur']}\nDemandes en attente de validation : {state['n_demandes']}"
    msg = llm.messages.create(
        model=LLM_MODEL, max_tokens=200,
        messages=[{"role": "user", "content": f"Question : {state['question']}\nContexte : {context}\n\nRéponse concise :"}],
    )
    answer = msg.content[0].text.strip()
    console.print(f"[dim]→ generate_answer : {len(answer)} chars[/dim]")
    return {"answer": answer}


def build_graph():
    """
    Construction du graphe LangGraph : définit les nodes et les edges (flux linéaire).
    """
    graph = StateGraph(AgentState)
    # Ajout des 3 nodes de traitement
    graph.add_node("extract", extract_collaborateur)
    graph.add_node("fetch", fetch_demandes)
    graph.add_node("generate", generate_answer)

    # Définition du flux linéaire : START → extract → fetch → generate → END
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "fetch")
    graph.add_edge("fetch", "generate")
    graph.add_edge("generate", END)

    return graph.compile()  # Compilation du graphe pour exécution


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY manquant[/red]")
        return

    console.print("\n[bold orange3]Demo 04 — Premier graphe LangGraph[/bold orange3]\n")
    agent = build_graph()

    # Visualisation ASCII du graphe pour comprendre la structure
    console.print("[bold]Graphe ASCII :[/bold]")
    try:
        console.print(agent.get_graph().draw_ascii())
    except Exception as e:
        console.print(f"[dim]ASCII rendering: {e}[/dim]")
        # Fallback : afficher structure
        for node in agent.get_graph().nodes:
            console.print(f"  • {node}")

    # Exécution
    questions = [
        "Combien de demandes Alice Martin a-t-elle en attente de validation ?",
        "Et Bob Durand ?",
        "Et Zoé Lambert ?",  # n'existe pas
    ]

    for q in questions:
        console.print(f"\n[bold cyan]Question : {q}[/bold cyan]")
        # invoke() : exécute le graphe avec un State initial et retourne le State final
        result = agent.invoke({"question": q})
        console.print(Panel(result["answer"], title="Réponse", border_style="orange3"))

    console.print("\n[bold]À retenir :[/bold]")
    console.print("• Le State est passé entre les nodes, chacun renvoie un dict de mises à jour")
    console.print("• Le graphe est compilé une fois, exécuté plusieurs fois (.invoke)")
    console.print("• La trace dans le state permet le debugging\n")


if __name__ == "__main__":
    main()
