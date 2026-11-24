from __future__ import annotations

import os
import sqlite3
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

import _setup  # noqa: F401
from _setup import neo  # noqa

load_dotenv()
console = Console()
DB_PATH = "demo_03_hil.db"


class State(TypedDict):
    user_request: str
    draft_action: Optional[dict]
    result: Optional[str]
    cancelled: bool


def draft_action(state: State) -> dict:
    """Prépare une action sensible à partir de la requête utilisateur."""
    request = state["user_request"]
    # Dans la vraie vie : LLM analyse la requête.
    # Ici on simplifie et on construit une action de refus de demande NeoFlow.
    if "refuse" in request.lower():
        # Extraire le numéro de la demande
        import re
        m = re.search(r"demande (\d+)", request)
        target = neo.DEMANDES.get(int(m.group(1))) if m else None
        if target and target["statut"] == "SOUMISE":
            return {
                "draft_action": {
                    "tool": "refuser_demande",
                    "args": {"id": target["id"], "titre": target["titre"]},
                    "reason": "budget dépassé",
                },
            }
    return {"draft_action": None}


def execute_action(state: State) -> dict:
    """Exécute l'action après approbation humaine."""
    if state.get("cancelled"):
        return {"result": "Action annulée par l'humain."}
    action = state.get("draft_action")
    if not action:
        return {"result": "Aucune action proposée."}

    if action["tool"] == "refuser_demande":
        demande = neo.DEMANDES.get(action["args"]["id"])
        if demande and demande["statut"] == "SOUMISE":
            # POST /api/demandes/{id}/refuser : transition irréversible, motif obligatoire
            demande["statut"] = "REFUSEE"
            demande["motif_refus"] = action["reason"]
            return {"result": f"Demande {demande['id']} ({demande['titre']}) refusée, motif : {action['reason']}."}
    return {"result": "Tool inconnu, aucune action."}


def build_graph(checkpointer):
    g = StateGraph(State)
    g.add_node("draft", draft_action)
    g.add_node("execute", execute_action)
    g.add_edge(START, "draft")
    g.add_edge("draft", "execute")
    g.add_edge("execute", END)
    return g.compile(checkpointer=checkpointer, interrupt_before=["execute"])


def main() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    console.print("\n[bold orange3]Demo 03 — Human-in-the-Loop[/bold orange3]\n")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    agent = build_graph(checkpointer)

    config = {"configurable": {"thread_id": "hil_session_1"}}
    request = "Refuse la demande 6, les licences IntelliJ dépassent le budget"
    console.print(Panel(request, title="Requête utilisateur", border_style="cyan"))

    # 1. Lancer — s'arrête avant execute
    state_after_draft = agent.invoke({"user_request": request, "cancelled": False}, config=config)

    proposed = state_after_draft.get("draft_action")
    if not proposed:
        console.print("[yellow]Aucune action proposée[/yellow]")
        return

    console.print(Panel(
        f"Tool : {proposed['tool']}\n"
        f"Args : {proposed['args']}\n"
        f"Motif : {proposed['reason']}",
        title="⏸ Action en attente d'approbation",
        border_style="yellow",
    ))

    # 2. Demander approbation (DEMO_AUTO=a|r|m permet de scripter en CI / démo enregistrée)
    auto = os.environ.get("DEMO_AUTO")
    if auto in {"a", "r", "m"}:
        decision = auto
        console.print(f"[dim](mode auto via DEMO_AUTO={auto})[/dim]")
    else:
        decision = Prompt.ask(
            "Approuver (a), Rejeter (r), Modifier le motif (m) ?",
            choices=["a", "r", "m"], default="a",
        )

    if decision == "r":
        agent.update_state(config, {"cancelled": True})
        console.print("[red]Action rejetée par l'humain.[/red]")
    elif decision == "m":
        new_reason = Prompt.ask("Nouveau motif ?", default="à reproposer au budget 2027")
        modified = {**proposed, "reason": new_reason}
        agent.update_state(config, {"draft_action": modified})
        console.print(f"[blue]Motif modifié → '{new_reason}'[/blue]")
    else:
        console.print("[green]Action approuvée.[/green]")

    # 3. Reprendre l'exécution
    final = agent.invoke(None, config=config)
    console.print(Panel(final["result"], title="Résultat final", border_style="orange3"))

    console.print(f"\n[bold]État final de la demande 6 :[/bold] statut = {neo.DEMANDES[6]['statut']}")
    console.print("\n[bold]À retenir :[/bold]")
    console.print("• `interrupt_before=['execute']` suspend avant ce node")
    console.print("• `update_state` modifie l'état avant la reprise")
    console.print("• `invoke(None, config)` reprend l'exécution là où elle s'est arrêtée\n")
    conn.close()


if __name__ == "__main__":
    main()
