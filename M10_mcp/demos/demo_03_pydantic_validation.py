from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator
from rich.console import Console
from rich.panel import Panel

console = Console()

# Types de demandes NeoFlow (énumération TypeDemande du socle)
TypeDemande = Literal[
    "GENERIQUE", "CONGES", "NOTE_DE_FRAIS", "MATERIEL_IT", "RESERVATION_SALLE", "FORMATION",
    "ACCES_APPLICATIF", "DEPLACEMENT", "ACHAT", "INCIDENT", "ONBOARDING",
]


# Modèles d'entrée typés
class CreerDemandeInput(BaseModel):
    login: str = Field(pattern=r"^[a-z]+$")
    type: TypeDemande
    titre: str = Field(min_length=3, max_length=120)
    montant: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    urgent: bool = False


class RechercheDemandesInput(BaseModel):
    date_debut: date
    date_fin: date
    statut: Literal["BROUILLON", "SOUMISE", "VALIDEE", "REFUSEE", "CLOTUREE"]
    size: int = Field(default=20, ge=1, le=100)

    @field_validator("date_fin")
    @classmethod
    def check_range(cls, v: date, info):
        sd = info.data.get("date_debut")
        if sd is None:
            return v
        if v < sd:
            raise ValueError("date_fin doit être ≥ date_debut")
        if (v - sd).days > 365:
            raise ValueError("Période > 365 jours interdite")
        return v


def try_input(label: str, model, payload: dict) -> None:
    console.print(f"\n[bold cyan]{label}[/bold cyan]")
    console.print(f"[dim]Input : {payload}[/dim]")
    try:
        validated = model(**payload)
        console.print(Panel(str(validated.model_dump()),
                            title="✓ Validation OK", border_style="green"))
    except ValidationError as e:
        # Premières erreurs uniquement (lisibilité)
        errors = "\n".join(f"  • [{err['loc'][0]}] {err['msg']}" for err in e.errors())
        console.print(Panel(errors, title="✗ ValidationError", border_style="red"))


def main() -> None:
    console.print("\n[bold orange3]Demo 03 — Validation Pydantic stricte[/bold orange3]\n")

    # CreerDemandeInput
    try_input(
        "Cas A — demande valide",
        CreerDemandeInput,
        {"login": "alice", "type": "NOTE_DE_FRAIS", "titre": "Déjeuner client Lyon", "montant": "86.40"},
    )

    try_input(
        "Cas B — login malformé",
        CreerDemandeInput,
        {"login": "Alice Martin", "type": "NOTE_DE_FRAIS", "titre": "Déjeuner client Lyon", "montant": "86.40"},
    )

    try_input(
        "Cas C — type hors enum",
        CreerDemandeInput,
        {"login": "alice", "type": "REMBOURSEMENT", "titre": "Taxi", "montant": "32.50"},
    )

    try_input(
        "Cas D — montant négatif et trop de décimales",
        CreerDemandeInput,
        {"login": "alice", "type": "NOTE_DE_FRAIS", "titre": "Taxi gare", "montant": "-32.505"},
    )

    # RechercheDemandesInput — règle métier
    try_input(
        "Cas E — recherche sur 30 jours OK",
        RechercheDemandesInput,
        {"date_debut": "2026-10-01", "date_fin": "2026-10-31", "statut": "SOUMISE"},
    )

    try_input(
        "Cas F — fin avant début → refus",
        RechercheDemandesInput,
        {"date_debut": "2026-11-01", "date_fin": "2026-10-01", "statut": "SOUMISE"},
    )

    try_input(
        "Cas G — période > 365 jours → refus",
        RechercheDemandesInput,
        {"date_debut": "2024-01-01", "date_fin": "2026-01-01", "statut": "VALIDEE"},
    )

    try_input(
        "Cas H — size hors range (l'API NeoFlow accepte 1 à 100)",
        RechercheDemandesInput,
        {"date_debut": "2026-10-01", "date_fin": "2026-10-31", "statut": "SOUMISE", "size": 500},
    )

    console.print("\n[bold]À retenir :[/bold]")
    console.print("• Pydantic capture les types, enums, patterns, ranges en une déclaration")
    console.print("• Les validators custom (`@field_validator`) ajoutent la logique métier")
    console.print("• Les erreurs sont structurées (loc, msg, type) → facilement loggables\n")


if __name__ == "__main__":
    main()
