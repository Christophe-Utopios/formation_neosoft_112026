import numpy as np
import tiktoken
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

console = Console()

FR = "Le justificatif est obligatoire pour toutes les dépenses de la note de frais, sans exception."
EN = "A receipt is mandatory for every expense in the expense report, without exception."


def compare_tokenizers() -> None:
    # 1. Un même texte ne coûte pas le même nombre de tokens selon la langue et le tokenizer
    table = Table(title="Nombre de tokens selon le tokenizer", expand=True)
    table.add_column("Tokenizer")
    table.add_column("FR", justify="right")
    table.add_column("EN", justify="right")
    table.add_column("Ratio FR/EN", justify="right")

    for name in ["cl100k_base", "o200k_base"]:
        enc = tiktoken.get_encoding(name)
        fr, en = len(enc.encode(FR)), len(enc.encode(EN))
        table.add_row(f"tiktoken {name}", str(fr), str(en), f"{fr / en:.2f}")

    for model_name in ["sentence-transformers/all-MiniLM-L6-v2", "intfloat/multilingual-e5-small"]:
        tok = SentenceTransformer(model_name).tokenizer
        fr, en = len(tok.tokenize(FR)), len(tok.tokenize(EN))
        table.add_row(model_name.split("/")[1], str(fr), str(en), f"{fr / en:.2f}")
    console.print(table)


def show_pieces() -> None:
    # 2. Ce que "voit" le modèle : des sous-mots, pas des mots
    for model_name in ["sentence-transformers/all-MiniLM-L6-v2", "intfloat/multilingual-e5-small"]:
        tok = SentenceTransformer(model_name).tokenizer
        console.print(f"\n[bold]{model_name}[/bold]")
        console.print(tok.tokenize("Remboursement des indemnités kilométriques"))


def show_truncation() -> None:
    # 3. Au-delà de max_seq_length, le texte est coupé SANS erreur
    model = SentenceTransformer("intfloat/multilingual-e5-small")
    console.print(f"\nmax_seq_length = {model.max_seq_length} tokens")

    head = "passage: " + FR * 30  # déjà bien plus long que 512 tokens
    tail = " Information cruciale : les dépenses de plus de trois mois ne sont pas remboursées."
    n_tokens = len(model.tokenizer.tokenize(head + tail))
    console.print(f"Texte long : {n_tokens} tokens")

    v_head = model.encode(head, normalize_embeddings=True)
    v_full = model.encode(head + tail, normalize_embeddings=True)
    sim = float(np.dot(v_head, v_full))
    console.print(f"Similarité (texte) vs (texte + phrase finale) : [bold]{sim:.4f}[/bold]")
    console.print("[red]La phrase finale n'a eu aucun effet : elle a été tronquée silencieusement.[/red]")


def main() -> None:
    compare_tokenizers()
    show_pieces()
    show_truncation()


if __name__ == "__main__":
    main()
