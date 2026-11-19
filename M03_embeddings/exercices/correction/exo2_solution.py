# Exercice 2 : trouver les limites des embeddings (négation, chiffres, versions...)
# et calculer ce que coûte le stockage des vecteurs.

import sys
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer

# On ajoute le dossier parent au chemin pour pouvoir importer _corpus.py
sys.path.append(str(Path(__file__).resolve().parents[1]))
from _corpus import get_corpus, get_golden  # noqa: E402

console = Console()

# Deux modèles : un multilingue (e5) et un entraîné surtout en anglais (all-MiniLM)
MODELS = [
    ("intfloat/multilingual-e5-small", "query: "),
    ("sentence-transformers/all-MiniLM-L6-v2", ""),
]

# Cas de test : (famille, ancre, positif, négatif).
# Le positif a le même sens que l'ancre, le négatif lui ressemble mais dit autre chose.
# Un bon modèle doit placer le positif plus près de l'ancre que le négatif.
CASES = [
    ("paraphrase", "réinitialiser mon mot de passe", "j'ai oublié mes identifiants", "changer le logo"),
    ("paraphrase", "le rapport hebdo n'arrive pas", "je ne reçois plus le mail du lundi", "créer un nouveau rapport"),
    ("cross-lingue", "exporter en CSV", "export data as CSV", "exporter en PDF"),
    ("cross-lingue", "où sont hébergées les données ?", "where is the data hosted?", "where is the support team?"),
    ("jargon", "SSO", "authentification unique via SAML", "envoi de SMS"),
    ("jargon", "CMK", "clés de chiffrement gérées par le client", "clés USB autorisées"),
    ("négation", "la MFA est obligatoire", "la double authentification est requise", "la MFA n'est pas obligatoire"),
    ("négation", "le virement est accepté", "on peut payer par virement", "le virement n'est pas accepté"),
    ("nombre / code", "erreur 401", "token expiré, non authentifié", "erreur 403"),
    ("nombre / code", "limite de 100 requêtes par minute", "100 appels par minute maximum", "limite de 1000 requêtes par minute"),
    ("version", "SAML en version 3.2", "SAML sur Velora 3.2", "SAML en version 3.0"),
    ("version", "Android 12 minimum", "nécessite au moins Android 12", "nécessite au moins Android 8"),
]


def run_cases(model: SentenceTransformer, cases: list, prefix: str) -> dict[str, int]:
    table = Table(expand=True)
    for c in ["Famille", "Ancre", "Positif", "Négatif", "cos+", "cos-", "Marge", ""]:
        table.add_column(c, overflow="fold")
    failures: dict[str, int] = {}
    for family, anchor, pos, neg in cases:
        # On encode les 3 phrases d'un coup ; vecteurs normalisés donc "@" = cosinus
        a, p, n = model.encode([prefix + anchor, prefix + pos, prefix + neg], normalize_embeddings=True)
        sp, sn = float(a @ p), float(a @ n)
        # Marge positive = le modèle a raison. Plus elle est grande, plus il est sûr.
        margin = sp - sn
        ok = margin > 0
        if not ok:
            # On compte les échecs par famille pour voir où le modèle est faible
            failures[family] = failures.get(family, 0) + 1
        # OK si marge nette, FRAGILE si juste au-dessus de 0, KO si le modèle se trompe
        status = "OK" if ok and margin > 0.05 else ("FRAGILE" if ok else "KO")
        table.add_row(family, anchor, pos, neg, f"{sp:.3f}", f"{sn:.3f}", f"{margin:+.3f}", status)
    console.print(table)
    return failures


def storage_table(dims: list[int], n_chunks: list[int]) -> None:
    table = Table(title="Stockage des vecteurs (hors index HNSW, +10 à 20 %)", expand=True)
    for c in ["Chunks", "Dim", "float32 (Go)", "float16 (Go)", "int8 (Go)", "float32 tient en 64 Go ?"]:
        table.add_column(c, justify="right")
    for n in n_chunks:
        for d in dims:
            # Taille = nb de chunks x dimension x octets par nombre (4, 2 ou 1)
            sizes = [n * d * b / 1e9 for b in (4, 2, 1)]
            # On ajoute 20 % pour l'index et on regarde si ça tient dans 64 Go de RAM
            fits = "oui" if sizes[0] * 1.2 < 64 else "non"
            table.add_row(f"{n:,}", str(d), *(f"{s:.1f}" for s in sizes), fits)
    console.print(table)


def matryoshka() -> None:
    corpus, golden = get_corpus(), get_golden()
    ids = np.array([c["id"] for c in corpus])
    # Qwen3-Embedding est entraîné en Matryoshka : on peut tronquer ses 1024 dimensions
    # On mesure combien de qualité (MRR) on perd en gardant moins de dimensions
    for dim in [1024, 256, 128, 64]:
        model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", truncate_dim=dim)
        docs = model.encode([c["content"] for c in corpus], normalize_embeddings=True)
        # prompt_name="query" : Qwen ajoute lui-même l'instruction prévue pour les questions
        qs = model.encode([q for q, _ in golden], prompt_name="query", normalize_embeddings=True)
        rr = []
        for i, (_, exp) in enumerate(golden):
            # Classement des documents pour la question i, puis 1 / rang du bon document
            ranking = ids[np.argsort(-(docs @ qs[i]))]
            rr.append(1 / (int(np.where(ranking == exp)[0][0]) + 1))
        console.print(f"  Qwen3-Embedding Matryoshka dim={dim:>4} -> MRR {np.mean(rr):.3f}")


def main() -> None:
    # Étape 1 : les cas pièges sur chaque modèle
    for name, prefix in MODELS:
        console.print(f"\n[bold]{name}[/bold]")
        failures = run_cases(SentenceTransformer(name), CASES, prefix)
        console.print(f"Échecs par famille : {failures or 'aucun'}")

    # Étape 2 : coût du stockage pour 1 et 10 millions de chunks
    storage_table([384, 768, 1024, 3072], [1_000_000, 10_000_000])

    # Bonus, seulement si on lance le script avec --matryoshka (gros modèle à télécharger)
    if "--matryoshka" in sys.argv:
        console.print("\n[bold]Bonus Matryoshka[/bold]")
        matryoshka()

    console.print("\n[bold]Réponses type[/bold]")
    console.print("- e5-small échoue sur négation, nombres / codes, une version et un jargon (SSO).")
    console.print("- Cross-lingue passe mais de justesse (+0.004 sur 'exporter en CSV') : FRAGILE.")
    console.print("- all-MiniLM échoue en plus sur la paraphrase française : il ne connaît que l'anglais.")
    console.print("- Compensations (M04 / M05) : filtres de métadonnées pour version et produit,")
    console.print("  BM25 / hybride pour les codes exacts, reranker cross-encoder pour la négation.")


if __name__ == "__main__":
    main()
