# Exercice 1 : comparer plusieurs modèles d'embeddings sur le golden set Velora
# et choisir le meilleur compromis qualité / vitesse / stockage.

import sys
import time
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

# On ajoute le dossier parent au chemin pour pouvoir importer _corpus.py
sys.path.append(str(Path(__file__).resolve().parents[1]))
from _corpus import get_corpus, get_golden  # noqa: E402

console = Console()

# Modèles à comparer : (nom, préfixe des questions, préfixe des documents).
# Les modèles e5 ont été entraînés avec "query: " et "passage: ", il faut les remettre.
CANDIDATES = [
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "", ""),
    ("intfloat/multilingual-e5-small", "query: ", "passage: "),
    ("intfloat/multilingual-e5-base", "query: ", "passage: "),
    ("BAAI/bge-m3", "", ""),
]

# Questions en plus du golden set : (question, id du bon document).
# Fautes d'orthographe, anglais, codes d'erreur, et None = aucune réponse dans le corpus.
EXTRA_GOLDEN: list[tuple[str, int | None]] = [
    ("jarrive pa a me co avec le sso", 5),
    ("le raport du lundi est pa arivé", 19),
    ("cmt on paye par prelevement", 22),
    ("How can I export all my data as CSV?", 12),
    ("Where is my data hosted?", 29),
    ("What is the API rate limit per user?", 15),
    ("j'ai une erreur 429", 9),
    ("erreur 403 sur un dossier", 7),
    ("Quelle est la recette de la tarte tatin ?", None),
    ("Comment intégrer Velora à SAP ?", None),
]

# Les questions en anglais, pour calculer un score FR et un score EN séparés
EN_QUERIES = {
    "How do I enable two-factor authentication?",
    "Which events can trigger a webhook?",
    "How can I export all my data as CSV?",
    "Where is my data hosted?",
    "What is the API rate limit per user?",
}


def encode_corpus(model: SentenceTransformer, corpus: list[dict], prefix: str) -> np.ndarray:
    # Transforme chaque document en vecteur. normalize_embeddings=True donne des vecteurs
    # de longueur 1 : le produit scalaire devient alors la similarité cosinus.
    return model.encode([prefix + c["content"] for c in corpus], normalize_embeddings=True, batch_size=32)


def rank_of(scores: np.ndarray, ids: np.ndarray, expected: int) -> int:
    # Trie les documents du plus proche au moins proche (le "-" inverse l'ordre)
    ranking = ids[np.argsort(-scores)]
    # Position du bon document dans ce classement (1 = premier)
    return int(np.where(ranking == expected)[0][0]) + 1


def metrics(ranks: list[int]) -> tuple[float, float, float]:
    r = np.array(ranks)
    # R@1 : bon doc en 1re position. R@3 : dans le top 3. MRR : moyenne de 1/rang.
    return float(np.mean(r == 1)), float(np.mean(r <= 3)), float(np.mean(1 / r))


def evaluate(name: str, q_prefix: str, p_prefix: str, corpus: list[dict], golden: list) -> dict:
    console.print(f"[dim]{name}...[/dim]")
    model = SentenceTransformer(name)
    # Un premier appel "à vide" pour que le chargement ne fausse pas la mesure de latence
    model.encode(["warmup"])
    ids = np.array([c["id"] for c in corpus])
    docs = encode_corpus(model, corpus, p_prefix)

    ranks_fr, ranks_en, no_answer, top1_scores, latencies = [], [], [], [], []
    for q, expected in golden:
        t0 = time.perf_counter()
        qv = model.encode(q_prefix + q, normalize_embeddings=True)
        # Similarité de la question avec tous les documents d'un coup (produit matriciel)
        scores = docs @ qv
        latencies.append((time.perf_counter() - t0) * 1000)

        # Question sans réponse : on garde juste le meilleur score pour le comparer plus tard
        if expected is None:
            no_answer.append(float(scores.max()))
            continue
        top1_scores.append(float(scores.max()))
        # On range le rang du bon document dans la liste FR ou EN
        (ranks_en if q in EN_QUERIES else ranks_fr).append(rank_of(scores, ids, expected))

    r1, r3, mrr = metrics(ranks_fr + ranks_en)
    dim = model.get_sentence_embedding_dimension()
    return {
        "name": name.split("/")[1],
        "dim": dim,
        # Taille du modèle en millions de paramètres
        "params": sum(p.numel() for p in model.parameters()) / 1e6,
        "r1": r1, "r3": r3, "mrr": mrr,
        "mrr_fr": metrics(ranks_fr)[2],
        "mrr_en": metrics(ranks_en)[2],
        "latency": float(np.mean(latencies)),
        # Stockage pour 1 million de chunks : dimension x 4 octets (float32)
        "storage_gb": 1_000_000 * dim * 4 / 1e9,
        # Si ces deux scores sont proches, un seuil ne suffit pas à détecter "pas de réponse"
        "top1_answer": float(np.mean(top1_scores)),
        "top1_no_answer": float(np.mean(no_answer)),
    }


def main() -> None:
    corpus = get_corpus()
    golden = get_golden() + EXTRA_GOLDEN
    # On évalue chaque modèle candidat sur les mêmes questions
    results = [evaluate(n, qp, pp, corpus, golden) for n, qp, pp in CANDIDATES]

    # Affichage du tableau comparatif, trié du meilleur MRR au moins bon
    table = Table(title="Benchmark sur le golden set Velora (30 requêtes)", expand=True)
    cols = ["Modèle", "Dim", "Params (M)", "R@1", "R@3", "MRR", "MRR FR", "MRR EN",
            "Latence (ms)", "Stockage 1M (Go)", "Top-1 avec rép.", "Top-1 sans rép."]
    for c in cols:
        table.add_column(c, justify="left" if c == "Modèle" else "right")
    for r in sorted(results, key=lambda r: -r["mrr"]):
        table.add_row(r["name"], str(r["dim"]), f"{r['params']:.0f}", f"{r['r1']:.2f}", f"{r['r3']:.2f}",
                      f"{r['mrr']:.3f}", f"{r['mrr_fr']:.3f}", f"{r['mrr_en']:.3f}", f"{r['latency']:.1f}",
                      f"{r['storage_gb']:.1f}", f"{r['top1_answer']:.3f}", f"{r['top1_no_answer']:.3f}")
    console.print(table)

    # Réponse attendue à la question "quel modèle choisir ?"
    console.print("\n[bold]Recommandation type (chiffres mesurés sur CPU)[/bold]")
    console.print("- bge-m3 : meilleur MRR (0.95, 1.00 en anglais) et seul modèle qui sépare un peu")
    console.print("  les requêtes sans réponse (top-1 0.59 vs 0.47). Mais 8 fois plus lent que e5-small.")
    console.print("- multilingual-e5-base : bon compromis (MRR 0.89), 2 à 3 fois plus rapide que bge-m3.")
    console.print("- e5-small : MRR 0.82, choix par défaut si CPU ou latence contraints.")
    console.print("- Avec e5, top-1 avec / sans réponse quasi identiques (0.84 vs 0.83) : un seuil de score")
    console.print("  ne détecte pas 'pas de réponse', il faudra un reranker ou un LLM juge (M05).")
    console.print("- Assistant Velora : bge-m3 si un GPU est disponible (8192 tokens, vecteurs sparse natifs")
    console.print("  pour l'hybride du M04), sinon e5-base.")


if __name__ == "__main__":
    main()
