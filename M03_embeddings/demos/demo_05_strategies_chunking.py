import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sentence_transformers import SentenceTransformer

from _chunkers import by_markdown, fixed_size, n_tokens, recursive, semantic
from _docs import get_docs

console = Console()
MODEL_NAME = "intfloat/multilingual-e5-small"


def main() -> None:
    doc = get_docs()[0]  # ticket NF-401 (congés)
    model = SentenceTransformer(MODEL_NAME)
    console.print(f"Document : [bold]{doc['title']}[/bold] ({n_tokens(doc['text'])} tokens)\n")

    strategies = {
        "fixed 200": fixed_size(doc["text"], 200),
        "fixed 200 / overlap 40": fixed_size(doc["text"], 200, 40),
        "recursive 200 / 30": recursive(doc["text"], 200, 30),
        "markdown + recursive": by_markdown(doc["text"], 200, 30),
        "semantic": semantic(doc["text"], model),
    }

    table = Table(title="Mêmes données, cinq découpages", expand=True)
    for col in ["Stratégie", "Nb chunks", "Tokens moyen", "Min", "Max"]:
        table.add_column(col, justify="right" if col != "Stratégie" else "left")
    for name, chunks in strategies.items():
        sizes = [n_tokens(c) for c in chunks]
        table.add_row(name, str(len(chunks)), f"{np.mean(sizes):.0f}", str(min(sizes)), str(max(sizes)))
    console.print(table)

    # Montrer les frontières : là où chaque stratégie coupe
    for name in ["fixed 200", "recursive 200 / 30", "markdown + recursive", "semantic"]:
        chunks = strategies[name]
        c = chunks[min(2, len(chunks) - 1)]
        console.print(Panel(c[:400] + ("..." if len(c) > 400 else ""),
                            title=f"{name} : chunk n°3", title_align="left"))

    console.print("[bold]À observer[/bold]")
    console.print("- fixed coupe au milieu d'un mot ou d'une URL : la phrase est perdue pour les deux chunks.")
    console.print("- recursive respecte paragraphes et phrases.")
    console.print("- markdown ajoute le chemin 'Titre > Section' : le chunk se comprend seul.")
    console.print("- semantic produit des tailles très variables, et coûte un embedding par phrase.")


if __name__ == "__main__":
    main()
