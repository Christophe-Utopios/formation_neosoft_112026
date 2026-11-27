from __future__ import annotations

import functools
import json
import logging
import time
import uuid
from typing import Callable

from rich.console import Console

console = Console()

# Configurer un logger JSON dédié à l'audit
audit_logger = logging.getLogger("mcp.audit")
audit_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(handler)


def audit_tool(tool_name: str):
    """Decorator qui audite chaque appel d'un tool MCP."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(actor_id: str, **kwargs):
            trace_id = str(uuid.uuid4())
            started_at = time.perf_counter()
            log_entry = {
                "event": "tool_call",
                "tool": tool_name,
                "trace_id": trace_id,
                "actor_id": actor_id,
                "args": kwargs,
            }
            try:
                result = fn(actor_id=actor_id, **kwargs)
                log_entry.update({
                    "result": "success",
                    "duration_ms": int((time.perf_counter() - started_at) * 1000),
                    "output_keys": list(result.keys()) if isinstance(result, dict) else None,
                })
                audit_logger.info(json.dumps(log_entry))
                return result
            except Exception as e:
                log_entry.update({
                    "result": "error",
                    "error_type": type(e).__name__,
                    "error_msg": str(e),
                    "duration_ms": int((time.perf_counter() - started_at) * 1000),
                })
                audit_logger.info(json.dumps(log_entry))
                raise
        return wrapper
    return decorator


# Mock data
DEMANDES = {7: {"id": 7, "demandeur": "alice", "titre": "Mission client Nantes", "statut": "BROUILLON"}}


@audit_tool("supprimer_brouillon")
def supprimer_brouillon(actor_id: str, demande_id: int) -> dict:
    """Supprime un brouillon de demande NeoFlow (mock)."""
    if demande_id not in DEMANDES:
        raise ValueError(f"Demande {demande_id} introuvable")
    del DEMANDES[demande_id]
    return {"deleted": demande_id}


@audit_tool("detail_demande")
def detail_demande(actor_id: str, demande_id: int) -> dict:
    return DEMANDES.get(demande_id) or {"error": "not_found"}


def main() -> None:
    console.print("\n[bold orange3]Demo 06 — Audit logs JSON[/bold orange3]\n")

    # Quelques appels
    console.print("[bold]Lecture de logs JSON (1 ligne par event) :[/bold]\n")

    detail_demande(actor_id="assistant_alice", demande_id=7)
    detail_demande(actor_id="assistant_alice", demande_id=999)  # not found

    try:
        supprimer_brouillon(actor_id="assistant_alice", demande_id=999)  # erreur
    except ValueError:
        pass

    supprimer_brouillon(actor_id="assistant_alice", demande_id=7)  # succès

    console.print("\n[bold]Pourquoi JSON-only :[/bold]")
    console.print("• Parsable directement par Logstash, Vector, Promtail")
    console.print("• trace_id = corrélation avec l'agent et les autres serveurs MCP")
    console.print("• Pas de PII dans les args (anonymisation si nécessaire)")
    console.print("• Rétention 12-24 mois selon le secteur (RGPD, DORA, etc.)\n")


if __name__ == "__main__":
    main()
