import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

console = Console()
MODEL_NAME = "intfloat/multilingual-e5-small"

# Paires choisies pour montrer ce que l'embedding capte... et ce qu'il rate
PAIRS = [
    ("Paraphrase", "Comment poser mes congés ?", "Je voudrais prendre des jours de vacances"),
    ("Traduction FR/EN", "Comment poser mes congés ?", "How do I request time off?"),
    ("Même mots, sens différent", "Le manager valide la note de frais", "La note du manager sur les frais de validation"),
    ("Sans rapport", "Comment poser mes congés ?", "Le fournisseur doit être référencé par les achats"),
    ("Négation", "Le justificatif est obligatoire", "Le justificatif n'est pas obligatoire"),
    ("Nombre", "Validation de niveau 2 au-delà de 1 000 €", "Validation de niveau 2 au-delà de 5 000 €"),
    ("Version", "NeoFlow version 1.0", "NeoFlow version 1.1"),
]


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    console.print(f"Modèle : {MODEL_NAME}, dimension {model.get_sentence_embedding_dimension()}\n")

    # Un embedding = un vecteur de floats
    v = model.encode("query: Bonjour", normalize_embeddings=True)
    console.print(f"Exemple de vecteur : {np.round(v[:6], 3)} \n")

    table = Table(title="Similarité cosinus entre deux phrases", expand=True)
    table.add_column("Cas", width=24)
    table.add_column("Phrase A", overflow="fold")
    table.add_column("Phrase B", overflow="fold")
    table.add_column("Cosinus", justify="right", width=8)

    for label, a, b in PAIRS:
        va, vb = model.encode([f"query: {a}", f"query: {b}"], normalize_embeddings=True)
        # Vecteurs normalisés : cosinus = produit scalaire
        table.add_row(label, a, b, f"{float(va @ vb):.3f}")
    console.print(table)

    console.print("\n[bold]À retenir[/bold]")
    console.print("- Les scores absolus dépendent du modèle : e5 donne rarement moins de 0.7.")
    console.print("  On compare des scores entre eux (classement), pas à un seuil universel.")
    console.print("- Négation, nombres et versions restent très proches : l'embedding capte le sujet,")
    console.print("  pas les détails. D'où les filtres de métadonnées et la recherche hybride (M04).")


if __name__ == "__main__":
    main()
