import time

import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

from _corpus import get_corpus, get_golden

console = Console()

# (nom HF, préfixe requête, préfixe passage)
CANDIDATES = [
    ("sentence-transformers/all-MiniLM-L6-v2", "", ""),
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "", ""),
    ("intfloat/multilingual-e5-small", "query: ", "passage: "),
    ("intfloat/multilingual-e5-base", "query: ", "passage: "),
    # Plus lourd (2,2 Go) : décommenter si la machine le permet
    # ("BAAI/bge-m3", "", ""),
]


def rank_of(scores: np.ndarray, ids: np.ndarray, expected: int) -> int:
    ranking = ids[np.argsort(-scores)]
    return int(np.where(ranking == expected)[0][0]) + 1


def benchmark(name: str, qp: str, pp: str, corpus: list[dict], golden: list) -> dict:
    model = SentenceTransformer(name)
    ids = np.array([c["id"] for c in corpus])

    # Warmup pour ne pas mesurer le chargement
    model.encode(["warmup"])

    t0 = time.perf_counter()
    docs = model.encode([pp + c["content"] for c in corpus], normalize_embeddings=True, batch_size=32)
    index_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    queries = model.encode([qp + q for q, _ in golden], normalize_embeddings=True)
    query_ms = (time.perf_counter() - t0) * 1000 / len(golden)

    ranks = [rank_of(queries[i] @ docs.T, ids, exp) for i, (_, exp) in enumerate(golden)]
    ranks = np.array(ranks)
    n_params = sum(p.numel() for p in model.parameters()) / 1e6
    return {
        "name": name.split("/")[1],
        "dim": model.get_sentence_embedding_dimension(),
        "max_len": model.max_seq_length,
        "params": n_params,
        "r1": float(np.mean(ranks == 1)),
        "r3": float(np.mean(ranks <= 3)),
        "mrr": float(np.mean(1 / ranks)),
        "index_ms": index_ms,
        "query_ms": query_ms,
    }


def main() -> None:
    corpus, golden = get_corpus(), get_golden()
    console.print(f"Corpus : {len(corpus)} chunks, golden set : {len(golden)} requêtes (dont 2 en anglais)\n")

    results = []
    for name, qp, pp in CANDIDATES:
        console.print(f"[dim]Évaluation de {name}...[/dim]")
        results.append(benchmark(name, qp, pp, corpus, golden))

    table = Table(title="Choisir un modèle d'embedding sur SES données", expand=True)
    for col in ["Modèle", "Dim", "Max tokens", "Params (M)", "Recall@1", "Recall@3", "MRR",
                "Index 50 chunks (ms)", "Requête (ms)"]:
        table.add_column(col, justify="right" if col != "Modèle" else "left")
    for r in sorted(results, key=lambda r: -r["mrr"]):
        table.add_row(r["name"], str(r["dim"]), str(r["max_len"]), f"{r['params']:.0f}",
                      f"{r['r1']:.2f}", f"{r['r3']:.2f}", f"{r['mrr']:.3f}",
                      f"{r['index_ms']:.0f}", f"{r['query_ms']:.1f}")
    console.print(table)

    console.print("\n[bold]Lecture[/bold]")
    console.print("- all-MiniLM-L6-v2 est entraîné en anglais : rapide, mais faible sur du français.")
    console.print("- Le classement MTEB donne une short-list, seul un test sur vos données tranche.")
    console.print("- Dimension et taille du modèle = coût de stockage et de latence en production.")


if __name__ == "__main__":
    main()
