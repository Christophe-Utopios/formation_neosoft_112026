from __future__ import annotations

import os
import json

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

import _neoflow as neo

load_dotenv()
console = Console()
LLM_MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "trouver_collaborateur",
        "description": "Recherche un collaborateur NeoFlow par nom ou login",
        "input_schema": {"type": "object", "properties": {"nom": {"type": "string"}}, "required": ["nom"]},
    },
    {
        "name": "compter_demandes",
        "description": "Compte les demandes d'un collaborateur pour un statut donné, SOUMISE par défaut. Statuts : BROUILLON (pas encore envoyée), SOUMISE (en attente de validation), VALIDEE, REFUSEE, CLOTUREE",
        "input_schema": {"type": "object", "properties": {"login": {"type": "string"}, "statut": {"type": "string"}}, "required": ["login"]},
    },
    {
        "name": "lister_demandes",
        "description": "Liste les demandes d'un collaborateur pour un statut donné. Statuts : BROUILLON (pas encore envoyée), SOUMISE (en attente de validation), VALIDEE, REFUSEE, CLOTUREE",
        "input_schema": {
            "type": "object",
            "properties": {"login": {"type": "string"}, "statut": {"type": "string"}},
            "required": ["login"],
        },
    },
]

TOOL_FNS = {
    "trouver_collaborateur": lambda **kw: neo.trouver_collaborateur(kw["nom"]),
    "compter_demandes": lambda **kw: neo.compter_demandes(kw["login"], kw.get("statut", "SOUMISE")),
    "lister_demandes": lambda **kw: neo.lister_demandes(kw["login"], kw.get("statut", "SOUMISE")),
}


def run_agent(question: str, llm: Anthropic, max_iter: int = 6) -> str:
    """Agent ReAct natif : boucle Thought → Action → Observation."""
    messages = [{"role": "user", "content": question}]
    iteration = 0

    while iteration < max_iter:
        iteration += 1
        console.print(f"\n[bold cyan]── Itération {iteration} ──[/bold cyan]")

        # Appel au LLM : raisonnement (Thought) + décision d'action (Action)
        response = llm.messages.create(
            model=LLM_MODEL, max_tokens=1024,
            tools=TOOLS, messages=messages,
        )

        # Affichage du raisonnement et des actions demandées
        for block in response.content:
            if hasattr(block, "text") and block.text:
                console.print(Panel(block.text, title="Thought / Réponse", border_style="orange3"))
            elif block.type == "tool_use":
                console.print(f"[bold yellow]🔧 Action : {block.name}({json.dumps(block.input)})[/bold yellow]")

        # Si réponse finale, on termine
        if response.stop_reason == "end_turn":
            console.print("[green]✓ Final answer atteint[/green]")
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            return text.strip()

        # Exécution des outils (Observation) et préparation du prochain tour
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                fn = TOOL_FNS.get(block.name)
                result = fn(**block.input) if fn else {"error": f"unknown tool {block.name}"}
                console.print(f"[dim]   Observation : {result}[/dim]")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        # Injection des observations pour le prochain raisonnement
        messages.append({"role": "user", "content": tool_results})

    return "Max iterations atteint sans final answer"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY manquant[/red]")
        return

    console.print("\n[bold orange3]Demo 02 — ReAct natif Anthropic[/bold orange3]\n")
    llm = Anthropic()

    question = "Pour Alice Martin, donne-moi son département, le nombre de demandes en attente de validation, et la liste de ses brouillons."
    console.print(Panel(question, title="Question utilisateur", border_style="cyan"))

    final = run_agent(question, llm)
    console.print(Panel(final, title="🎯 Réponse finale", border_style="green"))


if __name__ == "__main__":
    main()
