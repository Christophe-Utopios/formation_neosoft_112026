from __future__ import annotations

import sqlite3
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_db() -> sqlite3.Connection:
    # Extrait simplifié de la table demande de NeoFlow (V2__donnees_demo.sql)
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE demande (
            id INTEGER PRIMARY KEY,
            demandeur TEXT,
            type TEXT,
            statut TEXT,
            montant REAL
        )
    """)
    cur.executemany(
        "INSERT INTO demande VALUES (?, ?, ?, ?, ?)",
        [
            (2, "alice", "NOTE_DE_FRAIS", "SOUMISE", 86.40),
            (6, "alice", "ACHAT", "SOUMISE", 1250.0),
            (3, "alice", "MATERIEL_IT", "VALIDEE", 329.0),
            (12, "alice", "NOTE_DE_FRAIS", "CLOTUREE", 412.50),
            (20, "bob", "NOTE_DE_FRAIS", "SOUMISE", 54.0),
            (21, "farid", "ACHAT", "VALIDEE", 4800.0),
        ],
    )
    conn.commit()
    return conn


# ANTI-PATTERN : SQL libre exposé comme tool
def unsafe_query(conn: sqlite3.Connection, sql: str) -> list[dict]:
    """Exécute du SQL fourni par le LLM. Dangereux."""
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in rows]


# BON PATTERN : tool métier avec requête paramétrée
def lister_demandes(
    conn: sqlite3.Connection,
    login: str,
    statut: Literal["BROUILLON", "SOUMISE", "VALIDEE", "REFUSEE", "CLOTUREE"] = "SOUMISE",
) -> list[dict]:
    """Liste les demandes d'un collaborateur par statut.

    Args:
        login: login NeoFlow (ex: 'alice')
        statut: BROUILLON, SOUMISE, VALIDEE, REFUSEE ou CLOTUREE

    Returns:
        Liste des demandes correspondantes (peut être vide).
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT id, demandeur, type, statut, montant FROM demande WHERE demandeur = ? AND statut = ?",
        (login, statut),
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# BON PATTERN avec analyse globale
def montant_valide_par_type(conn: sqlite3.Connection) -> list[dict]:
    """Montant total des demandes validées ou clôturées, par type."""
    cur = conn.cursor()
    cur.execute("""
        SELECT type, SUM(montant) AS total
        FROM demande
        WHERE statut IN ('VALIDEE', 'CLOTUREE')
        GROUP BY type
        ORDER BY total DESC
    """)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def main() -> None:
    console.print("\n[bold orange3]Demo 05 — SQL safe vs unsafe[/bold orange3]\n")
    conn = setup_db()

    # 1. Cas du SQL libre — démontrer l'injection
    console.print("[bold red] ANTI-PATTERN : SQL libre[/bold red]")
    malicious_input = "SELECT * FROM demande; DROP TABLE demande; --"
    console.print(f"[dim]LLM envoie : {malicious_input}[/dim]")
    try:
        # sqlite3 refuse les statements multiples par défaut, mais le concept est là
        result = unsafe_query(conn, malicious_input)
        console.print(f"[red]Résultat : {result}[/red]")
    except sqlite3.ProgrammingError as e:
        console.print(f"[red]Exception (sqlite refuse les multi-statements) : {e}[/red]")
    # Plus subtil : `1=1` qui retourne tout, y compris les demandes des autres
    bypass = "SELECT * FROM demande WHERE demandeur = 'alice' OR 1=1"
    result_bypass = unsafe_query(conn, bypass)
    console.print(f"[red]Bypass via 1=1 → {len(result_bypass)} lignes (alice n'en a que 4)[/red]\n")

    # 2. Bons patterns
    console.print("[bold green]✓ BON PATTERN : tool métier paramétré[/bold green]\n")

    table = Table(title="lister_demandes(alice, SOUMISE)", show_lines=False)
    table.add_column("id")
    table.add_column("type")
    table.add_column("montant", justify="right")
    for row in lister_demandes(conn, "alice", "SOUMISE"):
        table.add_row(str(row["id"]), row["type"], f"{row['montant']:.2f}")
    console.print(table)

    # Essai d'injection sur le tool métier
    console.print("\n[cyan]Tentative d'injection via login :[/cyan]")
    injection = "alice' OR '1'='1"
    result = lister_demandes(conn, injection, "SOUMISE")
    console.print(f"[green]→ {len(result)} ligne(s) (l'injection est traitée comme une chaîne)[/green]")

    # Analyse agrégée
    console.print("\n[bold]Tool d'analyse : montant_valide_par_type[/bold]")
    table2 = Table()
    table2.add_column("type")
    table2.add_column("total", justify="right")
    for row in montant_valide_par_type(conn):
        table2.add_row(row["type"], f"{row['total']:.2f}")
    console.print(table2)

    console.print("\n[bold]À retenir :[/bold]")
    console.print("• Le tool métier accepte des paramètres, pas du SQL")
    console.print("• Les paramètres sont passés à `?` placeholders → pas d'injection")
    console.print("• Le LLM ne voit jamais le SQL réel → moindre surface d'attaque\n")
    conn.close()


if __name__ == "__main__":
    main()
