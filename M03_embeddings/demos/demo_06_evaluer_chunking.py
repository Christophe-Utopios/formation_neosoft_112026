import time

import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

from _chunkers import by_markdown, fixed_size, n_tokens, recursive, semantic
from _docs import get_chunk_golden, get_docs

console = Console()
MODEL_NAME = "intfloat/multilingual-e5-small"


def norm(text: str) -> str:
    return " ".join(text.split())


def build_chunks(strategy, docs: list[dict]) -> list[dict]:
    chunks = []
    for d in docs:
        for piece in strategy(d):
            chunks.append({"doc_id": d["doc_id"], "text": piece})
    return chunks


def evaluate(chunks: list[dict], golden: list[dict], model, k: int = 3) -> dict:
    vectors = model.encode([f"passage: {c['text']}" for c in chunks], normalize_embeddings=True, batch_size=32)
    queries = model.encode([f"query: {g['q']}" for g in golden], normalize_embeddings=True)
    ranks = []
    for i, g in enumerate(golden):
        top = np.argsort(-(vectors @ queries[i]))[:k]
        # Un hit = un des chunks retournés contient la réponse complète
        found = [r + 1 for r, idx in enumerate(top) if norm(g["needle"]) in norm(chunks[idx]["text"])]
        ranks.append(found[0] if found else 0)
    ranks = np.array(ranks)
    return {
        "r1": float(np.mean(ranks == 1)),
        "rk": float(np.mean(ranks > 0)),
        "mrr": float(np.mean([1 / r if r else 0 for r in ranks])),
    }


def main() -> None:
    docs, golden = get_docs(), get_chunk_golden()
    model = SentenceTransformer(MODEL_NAME)
    total = sum(n_tokens(d["text"]) for d in docs)
    console.print(f"{len(docs)} documents ({total} tokens), {len(golden)} questions\n")

    strategies = {
        "fixed 100": lambda d: fixed_size(d["text"], 100),
        "fixed 400": lambda d: fixed_size(d["text"], 400),
        "fixed 200 / overlap 40": lambda d: fixed_size(d["text"], 200, 40),
        "recursive 200 / 30": lambda d: recursive(d["text"], 200, 30),
        "markdown + recursive": lambda d: by_markdown(d["text"], 200, 30),
        "semantic": lambda d: semantic(d["text"], model),
        "document entier": lambda d: [d["text"]],
    }

    table = Table(title="Quel découpage retrouve la bonne réponse ?", expand=True)
    for col in ["Stratégie", "Chunks", "Tokens moy.", "Recall@1", "Recall@3", "MRR@3", "Temps (s)"]:
        table.add_column(col, justify="right" if col != "Stratégie" else "left")

    for name, strategy in strategies.items():
        t0 = time.perf_counter()
        chunks = build_chunks(strategy, docs)
        m = evaluate(chunks, golden, model)
        elapsed = time.perf_counter() - t0
        mean_tok = np.mean([n_tokens(c["text"]) for c in chunks])
        table.add_row(name, str(len(chunks)), f"{mean_tok:.0f}", f"{m['r1']:.2f}", f"{m['rk']:.2f}",
                      f"{m['mrr']:.3f}", f"{elapsed:.1f}")
    console.print(table)

    console.print("\n[bold]Lecture[/bold]")
    console.print("- 'document entier' reste compétitif : les tickets sont courts (environ 600 tokens).")
    console.print("  Mais le LLM recevrait 1 800 tokens pour une réponse d'une phrase, et un document")
    console.print("  long serait tronqué à 512 tokens par e5 : sa fin deviendrait introuvable.")
    console.print("- fixed 100 : chunks trop petits, phrases coupées, le Recall@3 s'effondre.")
    console.print("- Trop petit : le chunk perd son contexte. Trop gros : le vecteur est 'moyen' et dilué.")
    console.print("- Le choix se fait sur un golden set, pas à l'intuition.")


if __name__ == "__main__":
    main()
