from __future__ import annotations

import re

import numpy as np
import tiktoken
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Toutes les tailles sont exprimées en tokens (cl100k), pas en caractères
ENC = tiktoken.get_encoding("cl100k_base")


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def fixed_size(text: str, size: int = 200, overlap: int = 0) -> list[str]:
    # Découpe aveugle tous les `size` tokens, quitte à couper un mot ou une phrase
    ids = ENC.encode(text)
    step = size - overlap
    return [ENC.decode(ids[i:i + size]) for i in range(0, len(ids), step)]


def recursive(text: str, size: int = 200, overlap: int = 30) -> list[str]:
    # Essaie de couper sur les paragraphes, puis les lignes, puis les phrases, puis les mots
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def by_markdown(text: str, size: int = 200, overlap: int = 30, title: str = "") -> list[str]:
    # Coupe sur la structure (titres), puis recursive si une section est trop longue.
    # Chaque chunk est préfixé par son chemin "Titre > Section" pour garder le contexte.
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2")])
    chunks = []
    for section in header_splitter.split_text(text):
        path = " > ".join(v for k, v in section.metadata.items())
        for piece in recursive(section.page_content, size, overlap):
            chunks.append(f"{path}\n{piece}" if path else piece)
    return chunks


def split_sentences(text: str) -> list[str]:
    # Découpage simple en phrases (suffisant pour la démo)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sentences = []
    for line in lines:
        sentences.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip())
    return sentences


def semantic(text: str, model, percentile: float = 20, max_size: int = 300) -> list[str]:
    # Coupe là où deux phrases consécutives sont sémantiquement éloignées
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return sentences
    vectors = model.encode([f"passage: {s}" for s in sentences], normalize_embeddings=True)
    sims = np.sum(vectors[:-1] * vectors[1:], axis=1)
    threshold = np.percentile(sims, percentile)

    chunks, current = [], [sentences[0]]
    for sentence, sim in zip(sentences[1:], sims):
        too_long = n_tokens(" ".join(current + [sentence])) > max_size
        if sim < threshold or too_long:
            chunks.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)
    chunks.append(" ".join(current))
    return chunks
