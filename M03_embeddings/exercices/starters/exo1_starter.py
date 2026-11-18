import sys
import time
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _corpus import get_corpus, get_golden  # noqa: E402

console = Console()

# TODO étape 1 : vos 4 candidats (nom HF, préfixe requête, préfixe passage)
CANDIDATES: list[tuple[str, str, str]] = [
    ("intfloat/multilingual-e5-small", "query: ", "passage: "),
]

# TODO étape 2 : 10 requêtes supplémentaires (id attendu, ou None si pas de réponse)
EXTRA_GOLDEN: list[tuple[str, int | None]] = []

EN_QUERIES: set[str] = set()  # TODO : les requêtes en anglais, pour le score par langue


def encode_corpus(model: SentenceTransformer, corpus: list[dict], prefix: str) -> np.ndarray:
    # TODO : encoder les chunks avec le préfixe, vecteurs normalisés
    raise NotImplementedError


def rank_of(scores: np.ndarray, ids: np.ndarray, expected: int) -> int:
    # TODO : position (1 = premier) du chunk attendu dans le classement par score décroissant
    raise NotImplementedError


def evaluate(name: str, q_prefix: str, p_prefix: str, corpus: list[dict], golden: list) -> dict:
    # TODO : charger le modèle, warmup, encoder, calculer Recall@1, Recall@3, MRR,
    # latence moyenne par requête, et le score top-1 des requêtes sans réponse
    raise NotImplementedError


def main() -> None:
    corpus = get_corpus()
    golden = get_golden() + EXTRA_GOLDEN
    results = [evaluate(n, qp, pp, corpus, golden) for n, qp, pp in CANDIDATES]
    # TODO : tableau rich comparatif + scores FR / EN
    console.print(results)


if __name__ == "__main__":
    main()
