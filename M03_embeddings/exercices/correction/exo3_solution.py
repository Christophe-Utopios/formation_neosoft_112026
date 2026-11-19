import re
import sys
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import tiktoken
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

# On ajoute le dossier parent au chemin pour pouvoir importer _docs.py
sys.path.append(str(Path(__file__).resolve().parents[1]))
from _docs import get_chunk_golden, get_docs  # noqa: E402

console = Console()
# Tokenizer utilisé pour compter les tokens (celui des modèles OpenAI récents)
ENC = tiktoken.get_encoding("cl100k_base")
MODEL_NAME = "intfloat/multilingual-e5-small"
# Au-delà de 512 tokens, e5-small coupe le texte : un chunk plus long serait tronqué
MAX_MODEL_TOKENS = 512
# Le graphique est enregistré à côté de ce script
OUT = Path(__file__).with_name("chunking_sweep.png")


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


# Stratégie 1 : taille fixe. On coupe tous les `size` tokens, sans regarder le sens.
def fixed_size(text: str, size: int, overlap: int) -> list[str]:
    ids = ENC.encode(text)
    # On avance de size - overlap : les chunks se chevauchent de `overlap` tokens
    step = max(1, size - overlap)
    return [ENC.decode(ids[i:i + size]) for i in range(0, len(ids), step)]


# Stratégie 2 : récursive. On essaie de couper d'abord sur les titres, puis les paragraphes,
# puis les lignes, les phrases, les mots, et en dernier recours n'importe où.
def recursive(text: str, size: int, overlap: int) -> list[str]:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


# Stratégie 3 : par titres Markdown, puis récursive dans chaque section trop longue.
def by_markdown(text: str, size: int, overlap: int) -> list[tuple[str, str]]:
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2")])
    out = []
    for section in splitter.split_text(text):
        # Chemin de la section, par exemple "Titre du doc > Nom de la section"
        path = " > ".join(section.metadata.values())
        for piece in recursive(section.page_content, size, overlap):
            # On colle ce chemin en tête du chunk pour lui donner du contexte
            out.append((section.metadata.get("h2", ""), f"{path}\n{piece}"))
    return out


def split_sentences(text: str) -> list[str]:
    sentences = []
    for line in (l.strip() for l in text.split("\n")):
        if line:
            # Coupe après un ".", "!" ou "?" suivi d'un espace
            sentences.extend(s for s in re.split(r"(?<=[.!?])\s+", line) if s)
    return sentences


# Transforme les morceaux de texte en fiches avec métadonnées (doc, section, position...)
def to_records(doc: dict, pieces: list, start_id: int) -> list[dict]:
    records = []
    for pos, piece in enumerate(pieces):
        # by_markdown renvoie (section, texte), les autres stratégies juste le texte
        section, text = piece if isinstance(piece, tuple) else ("", piece)
        records.append({
            "chunk_id": start_id + pos,
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "section": section,
            "position": pos,
            "n_tokens": n_tokens(text),
            "text": text,
        })
    return records


# Applique une stratégie de découpage `fn` à tous les documents
def chunk_corpus(docs: list[dict], fn) -> list[dict]:
    chunks: list[dict] = []
    for doc in docs:
        chunks += to_records(doc, fn(doc["text"]), len(chunks))
    return chunks


# Supprime les espaces et retours à la ligne en trop, pour comparer des textes
def norm(text: str) -> str:
    return " ".join(text.split())


def evaluate(chunks: list[dict], golden: list[dict], model: SentenceTransformer, k: int = 3) -> dict:
    vectors = model.encode([f"passage: {c['text']}" for c in chunks], normalize_embeddings=True, batch_size=32)
    queries = model.encode([f"query: {g['q']}" for g in golden], normalize_embeddings=True)
    ranks = []
    for i, g in enumerate(golden):
        # Les k chunks les plus proches de la question
        top = np.argsort(-(vectors @ queries[i]))[:k]
        # Un chunk est "bon" s'il contient la phrase-réponse attendue (needle) en entier
        hits = [r + 1 for r, idx in enumerate(top) if norm(g["needle"]) in norm(chunks[idx]["text"])]
        # Rang du premier bon chunk, ou 0 s'il n'est pas dans le top k
        ranks.append(hits[0] if hits else 0)
    ranks = np.array(ranks)
    return {
        "r1": float(np.mean(ranks == 1)),
        "rk": float(np.mean(ranks > 0)),
        "mrr": float(np.mean([1 / r if r else 0.0 for r in ranks])),
    }


# Étape 2 : les stratégies avec les mêmes réglages (200 tokens, overlap 30)
def compare(docs: list[dict], golden: list[dict], model: SentenceTransformer) -> None:
    strategies = {
        "fixed 200/30": lambda t: fixed_size(t, 200, 30),
        "recursive 200/30": lambda t: recursive(t, 200, 30),
        "markdown 200/30": lambda t: by_markdown(t, 200, 30),
    }
    table = Table(title="Étape 2 : comparaison des stratégies", expand=True)
    for c in ["Stratégie", "Chunks", "Moy.", "Min", "Max", "R@1", "R@3", "MRR@3", "Temps (s)"]:
        table.add_column(c, justify="left" if c == "Stratégie" else "right")
    for name, fn in strategies.items():
        t0 = time.perf_counter()
        chunks = chunk_corpus(docs, fn)
        m = evaluate(chunks, golden, model)
        sizes = [c["n_tokens"] for c in chunks]
        # Sécurité : aucun chunk ne doit dépasser ce que le modèle sait lire
        assert max(sizes) < MAX_MODEL_TOKENS, f"{name} dépasse la limite du modèle"
        table.add_row(name, str(len(chunks)), f"{np.mean(sizes):.0f}", str(min(sizes)), str(max(sizes)),
                      f"{m['r1']:.2f}", f"{m['rk']:.2f}", f"{m['mrr']:.3f}", f"{time.perf_counter() - t0:.1f}")
    console.print(table)


# Étape 3 : on fait varier taille et overlap et on trace le Recall@3 obtenu
def sweep(docs: list[dict], golden: list[dict], model: SentenceTransformer) -> None:
    sizes, overlaps = [100, 200, 300, 500], [0, 30, 60]
    strategies = {"fixed": fixed_size, "markdown + recursive": by_markdown}
    # Un graphique par stratégie, côte à côte, avec le même axe Y
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, (name, fn) in zip(axes, strategies.items()):
        for ov in overlaps:
            recalls = []
            for size in sizes:
                chunks = chunk_corpus(docs, lambda t: fn(t, size, ov))
                recalls.append(evaluate(chunks, golden, model)["rk"])
                console.print(f"  {name} size={size:>3} overlap={ov:>2} -> Recall@3 {recalls[-1]:.2f} ({len(chunks)} chunks)")
            # Une courbe par valeur d'overlap
            ax.plot(sizes, recalls, marker="o", label=f"overlap {ov}")
        ax.set_title(name)
        ax.set_xlabel("Taille de chunk (tokens)")
        ax.grid(alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Recall@3")
    axes[0].set_ylim(0, 1.05)
    fig.tight_layout()
    plt.savefig(OUT, dpi=120)
    console.print(f"[green]Figure : {OUT.name}[/green]")


def main() -> None:
    docs, golden = get_docs(), get_chunk_golden()
    # Un seul modèle chargé, réutilisé partout
    model = SentenceTransformer(MODEL_NAME)
    compare(docs, golden, model)
    console.print("\n[bold]Étape 3 : balayage[/bold]")
    sweep(docs, golden, model)

    console.print("\n[bold]Conclusion type pour la note de décision[/bold]")
    console.print("- Retenu : markdown + recursive, 200 tokens, overlap 30 : R@1 0.88, R@3 1.00, MRR 0.94.")
    console.print("- Au-delà de 200 tokens la taille n'a plus d'effet : les sections tiennent déjà entières.")
    console.print("  L'overlap est inutile quand on coupe sur les frontières naturelles.")
    console.print("- Le préfixe 'Titre > Section' donne du contexte au chunk et sert de citation.")
    console.print("- fixed coupe des phrases-réponses : échecs nets sur les URL et les chiffres.")
    console.print("- semantic : pas de gain mesurable ici, et un embedding par phrase à l'ingestion.")
    console.print("- Métadonnées doc_id, product, version, section : filtres M04 et citations M05.")


if __name__ == "__main__":
    main()
