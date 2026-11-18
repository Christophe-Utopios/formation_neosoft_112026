from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

console = Console()

MODEL_NAME = "intfloat/multilingual-e5-small"
Q_PREFIX = "query: "

# TODO étape 1 : au moins 12 cas (famille, ancre, positif, négatif)
CASES: list[tuple[str, str, str, str]] = [
    ("paraphrase", "réinitialiser mon mot de passe", "j'ai oublié mes identifiants", "changer le logo"),
]


def run_cases(model: SentenceTransformer, cases: list, prefix: str = Q_PREFIX) -> None:
    # TODO : pour chaque cas, cos(ancre, positif), cos(ancre, négatif), marge, statut
    raise NotImplementedError


def storage_table(dims: list[int], n_chunks: list[int]) -> None:
    # TODO étape 3 : taille en Go pour float32, float16, int8 + tient en 64 Go ?
    raise NotImplementedError


def main() -> None:
    run_cases(SentenceTransformer(MODEL_NAME), CASES)
    storage_table([384, 768, 1024, 3072], [1_000_000, 10_000_000])


if __name__ == "__main__":
    main()
