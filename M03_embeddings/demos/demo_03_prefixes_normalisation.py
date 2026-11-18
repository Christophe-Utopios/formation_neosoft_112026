import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

from _corpus import get_corpus, get_golden

console = Console()
MODELS = ["intfloat/multilingual-e5-small", "intfloat/multilingual-e5-base"]
# Modèle sans couche Normalize : ses vecteurs n'ont pas une norme de 1
RAW_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def evaluate(model, corpus, golden, q_prefix: str, p_prefix: str) -> tuple[float, float]:
    # Recall@1 et MRR sur le golden set
    docs = model.encode([p_prefix + c["content"] for c in corpus], normalize_embeddings=True)
    queries = model.encode([q_prefix + q for q, _ in golden], normalize_embeddings=True)
    ids = np.array([c["id"] for c in corpus])

    scores = queries @ docs.T
    hits, rr = 0, 0.0
    for i, (_, expected) in enumerate(golden):
        ranking = ids[np.argsort(-scores[i])]
        rank = int(np.where(ranking == expected)[0][0]) + 1
        hits += rank == 1
        rr += 1 / rank
    return hits / len(golden), rr / len(golden)


def prefixes(corpus, golden) -> None:
    # 1. Les modèles e5 sont entraînés avec "query: " / "passage: "
    table = Table(title="Impact des préfixes", expand=True)
    table.add_column("Modèle")
    table.add_column("Configuration")
    table.add_column("Recall@1", justify="right")
    table.add_column("MRR", justify="right")
    configs = [
        ("query: / passage: (attendu)", "query: ", "passage: "),
        ("aucun préfixe", "", ""),
        ("passage: des deux côtés", "passage: ", "passage: "),
    ]
    for name in MODELS:
        model = SentenceTransformer(name)
        for label, qp, pp in configs:
            r1, mrr = evaluate(model, corpus, golden, qp, pp)
            table.add_row(name.split("/")[1], label, f"{r1:.2f}", f"{mrr:.3f}")
    console.print(table)
    console.print("[dim]L'effet dépend du modèle et du jeu de test : la model card dit quoi faire,"
                  " le golden set dit combien ça coûte de ne pas le faire.[/dim]")


def normalisation() -> None:
    # 2. Sans normalisation, le produit scalaire favorise les vecteurs "longs"
    model = SentenceTransformer(RAW_MODEL)
    console.print(f"\nModèle : {RAW_MODEL}")
    texts = [
        "Le repas est plafonné à 25,50 € dans le barème de remboursement.",
        "Repas, repas, frais. Note, note. Congés, achat, devis, badge, salle, incident.",
    ]
    raw = model.encode(texts, normalize_embeddings=False)
    norm = model.encode(texts, normalize_embeddings=True)
    q_raw = model.encode("Combien est remboursé un déjeuner ?", normalize_embeddings=False)
    q_norm = model.encode("Combien est remboursé un déjeuner ?", normalize_embeddings=True)

    console.print("\n[bold]Normes des vecteurs bruts[/bold]")
    for t, v in zip(texts, raw):
        console.print(f"  {np.linalg.norm(v):.3f}  <- {t[:50]}...")

    console.print("\nProduit scalaire brut   :", np.round(raw @ q_raw, 3))
    console.print("Produit scalaire normé  :", np.round(norm @ q_norm, 3), "(= cosinus)")
    console.print("[dim]Règle : normaliser à l'indexation ET à la requête, puis utiliser cosinus"
                  " (ou dot, équivalent sur vecteurs normés).[/dim]")


def main() -> None:
    corpus, golden = get_corpus(), get_golden()
    prefixes(corpus, golden)
    normalisation()


if __name__ == "__main__":
    main()
