import sys
from pathlib import Path

import numpy as np
import tiktoken
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from rich.console import Console
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _docs import get_chunk_golden, get_docs  # noqa: E402

console = Console()
ENC = tiktoken.get_encoding("cl100k_base")
MODEL_NAME = "intfloat/multilingual-e5-small"  # TODO : votre modèle du TP 1


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def fixed_size(text: str, size: int, overlap: int) -> list[str]:
    # TODO : fenêtre glissante sur les tokens
    raise NotImplementedError


def recursive(text: str, size: int, overlap: int) -> list[str]:
    # TODO : RecursiveCharacterTextSplitter.from_tiktoken_encoder
    raise NotImplementedError


def by_markdown(text: str, size: int, overlap: int) -> list[tuple[str, str]]:
    # TODO : renvoie des couples (section, texte préfixé par "Titre > Section")
    raise NotImplementedError


def semantic(text: str, model: SentenceTransformer, percentile: float = 20, max_size: int = 300) -> list[str]:
    # TODO : phrases -> embeddings -> coupure sous le percentile de similarité
    raise NotImplementedError


def to_records(doc: dict, pieces: list, start_id: int) -> list[dict]:
    # TODO : dicts avec chunk_id, doc_id, title, section, position, n_tokens, text
    raise NotImplementedError


def evaluate(chunks: list[dict], golden: list[dict], model: SentenceTransformer, k: int = 3) -> dict:
    # TODO : Recall@1, Recall@k, MRR@k (hit = needle contenu dans le chunk)
    raise NotImplementedError


def main() -> None:
    docs, golden = get_docs(), get_chunk_golden()
    model = SentenceTransformer(MODEL_NAME)
    # TODO étape 2 : tableau comparatif des 4 stratégies
    # TODO étape 3 : balayage size x overlap + chunking_sweep.png


if __name__ == "__main__":
    main()
