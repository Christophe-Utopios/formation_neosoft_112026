from __future__ import annotations

import os
import time

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import _neoflow as neo

load_dotenv()
console = Console()
LLM_MODEL = "claude-haiku-4-5-20251001"


# === CHAÎNE FIXE ===
def fixed_chain(question: str, llm: Anthropic) -> dict:
    """Chaîne hard-codée : séquence prédéfinie d'étapes (pas de décision dynamique)."""
    # Étape 1 : extraction du nom du collaborateur par LLM
    extract = llm.messages.create(
        model=LLM_MODEL, max_tokens=50,
        messages=[{"role": "user", "content": f"Voici la question d'un utilisateur de NeoFlow. Extrais le nom de la personne dont elle parle. Réponds uniquement avec ce nom, sans phrase.\n\nQuestion : {question}"}],
    )
    nom = extract.content[0].text.strip()

    # Étape 2 : appels NeoFlow (toujours les mêmes, pas d'adaptation)
    collab = neo.trouver_collaborateur(nom)
    if not collab:
        return {"answer": f"Collaborateur '{nom}' introuvable.", "n_calls": 1}
    n_soumises = neo.compter_demandes(collab["login"], "SOUMISE")

    # Étape 3 : génération de la réponse finale
    answer = llm.messages.create(
        model=LLM_MODEL, max_tokens=200,
        messages=[{"role": "user", "content": f"Question : {question}\nDonnées : collaborateur={collab}, demandes_en_attente={n_soumises}\n\nRéponse :"}],
    )
    return {"answer": answer.content[0].text.strip(), "n_calls": 2}


# === AGENT ReAct (boucle libre) ===
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


def react_agent(question: str, llm: Anthropic, max_iter: int = 6) -> dict:
    """Agent ReAct : boucle autonome où le LLM décide quels outils utiliser."""
    messages = [{"role": "user", "content": question}]
    n_calls = 0
    for _ in range(max_iter):
        # Le LLM raisonne et décide de l'action suivante (tool ou réponse finale)
        response = llm.messages.create(
            model=LLM_MODEL, max_tokens=1024,
            tools=TOOLS, messages=messages,
        )
        n_calls += 1
        # Si le LLM produit une réponse finale (pas d'outil), on termine
        if response.stop_reason == "end_turn":
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            return {"answer": text.strip(), "n_calls": n_calls}

        # Exécution des outils demandés par le LLM
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                fn = TOOL_FNS.get(block.name)
                result = fn(**block.input) if fn else {"error": "unknown tool"}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        # Injection des résultats d'outils pour le prochain tour
        messages.append({"role": "user", "content": tool_results})

    return {"answer": "Max iterations atteint", "n_calls": n_calls}


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY manquant[/red]")
        return

    console.print("\n[bold orange3]Demo 01 — Chaîne vs Agent[/bold orange3]\n")
    llm = Anthropic()

    questions = [
        ("Cas A — simple", "Combien de demandes Alice Martin a-t-elle en attente de validation ?"),
        ("Cas B — multi-step", "Pour Alice Martin, donne-moi : le nombre de demandes en attente, leurs titres, et leur niveau de validation."),
    ]

    table = Table(title="Comparaison sur 2 cas", show_lines=True)
    table.add_column("Cas", style="cyan")
    table.add_column("Approche")
    table.add_column("LLM calls", justify="right")
    table.add_column("Latence (s)", justify="right")
    table.add_column("Réponse OK ?", justify="center")

    for label, question in questions:
        console.print(f"\n[bold cyan]{label} : {question}[/bold cyan]")

        # Chaîne
        t0 = time.perf_counter()
        chain_result = fixed_chain(question, llm)
        t_chain = time.perf_counter() - t0
        console.print(Panel(chain_result["answer"], title="Chaîne", border_style="orange3"))

        # Agent
        t0 = time.perf_counter()
        agent_result = react_agent(question, llm)
        t_agent = time.perf_counter() - t0
        console.print(Panel(agent_result["answer"], title="Agent ReAct", border_style="orange3"))

        table.add_row(label, "Chaîne", str(chain_result["n_calls"]), f"{t_chain:.1f}", "?")
        table.add_row(label, "Agent", str(agent_result["n_calls"]), f"{t_agent:.1f}", "?")

    console.print("\n")
    console.print(table)
    console.print("\n[bold]Observation :[/bold]")
    console.print("• Cas A : la chaîne suffit, l'agent surconsomme")
    console.print("• Cas B : l'agent gère naturellement les multi-steps que la chaîne fixe ne couvre pas")
    console.print("• → Choisir l'agent uniquement quand le pattern le justifie\n")


if __name__ == "__main__":
    main()
