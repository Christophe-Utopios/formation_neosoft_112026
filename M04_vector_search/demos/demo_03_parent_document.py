from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.panel import Panel

console = Console()
COLLECTION = "demo_03_parent_doc"
MODEL_NAME = "intfloat/multilingual-e5-small"


# Document long (un guide complet, pas un FAQ chunk)
LONG_DOCUMENT = """# Guide : soumettre une demande dans NeoFlow

## Introduction
NeoFlow gère les demandes internes du Groupe Velmora : congés, notes de frais, matériel, accès, déplacements.
Ce guide explique le parcours complet d'une demande, du brouillon à la clôture, et les erreurs courantes.

## Prérequis
Avant de commencer, vous devez disposer des éléments suivants :
- Un compte avec le rôle DEMANDEUR, par exemple alice dans les données de démonstration.
- L'URL de l'API, par défaut http://localhost:8080/api, protégée par HTTP Basic.
- Le type de demande, parmi CONGES, NOTE_DE_FRAIS, MATERIEL_IT, ACCES_APPLICATIF, DEPLACEMENT, ACHAT.
- La date de début, et le montant si la demande est chiffrée (deux décimales au plus).

## Créer un brouillon
Envoyez POST /api/demandes avec le type, le titre et la date de début, qui sont obligatoires.
Le titre fait 120 caractères au plus. La demande est créée au statut BROUILLON et reste modifiable
par son auteur avec PUT /api/demandes/{id}. La modification d'un brouillon n'est pas journalisée.

## Soumettre et calculer le niveau
Envoyez POST /api/demandes/{id}/soumettre. NeoFlow calcule alors le niveau de validation, de 1 à 3,
avec le module legacy RegleValidationLegacy : type, montant, ancienneté, département et urgence.
Une note de frais passe au niveau 2 au-delà de 1 000 euros, au niveau 3 à partir de 5 000 euros.
Le vendredi à partir de 14 heures, toute demande chiffrée passe au niveau 2 minimum.

## Suivre la demande
Le valideur passe la demande en VALIDEE ou en REFUSEE, avec un motif obligatoire en cas de refus.
L'administrateur la passe ensuite en CLOTUREE. Chaque étape écrit une ligne dans le journal,
consultable avec GET /api/demandes/{id}/evenements.

## Dépannage
Si l'appel échoue, la réponse suit le format ProblemDetail. Les erreurs courantes sont :
- "Transition de statut invalide" (409) indique que la demande n'est plus au bon statut, par exemple déjà soumise.
- "Accès refusé" (403) indique que vous agissez sur la demande d'un autre utilisateur.
- "Règles métier non respectées" (422) liste dans la propriété erreurs les règles non respectées.

Pour une erreur interne (500), la réponse contient un traceId. Recherchez ce traceId dans les logs
au format ECS, ou ouvrez la trace correspondante dans Jaeger sur http://localhost:16686,
service neoflow-backend, pour retrouver l'appel en échec.
"""


def main() -> None:
    console.print("\n[bold orange3]Demo 05 — Parent-document retrieval[/bold orange3]\n")

    model = SentenceTransformer(MODEL_NAME)
    client = QdrantClient(url="http://localhost:6333")

    # 1. Découpage à deux niveaux : parents (sections) et enfants (petits chunks)
    # Parents : grands chunks de ~600 caractères (sections logiques)
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=0,
        separators=["\n## ", "\n# "],  # Découpe sur les titres de sections
    )
    parents = parent_splitter.split_text(LONG_DOCUMENT)
    console.print(f"[cyan]→ Document découpé en {len(parents)} parents (sections)[/cyan]\n")

    # Enfants : petits chunks de ~200 caractères pour la recherche précise
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        separators=["\n", ". ", " "],
    )

    # Création des embeddings : on indexe les enfants mais on garde le parent en payload
    points: list[PointStruct] = []
    point_id = 0
    for parent_id, parent in enumerate(parents):
        children = child_splitter.split_text(parent)
        for child in children:
            point_id += 1
            # L'embedding est créé sur le petit chunk (précis)
            child_emb = model.encode(f"passage: {child}", normalize_embeddings=True)
            points.append(PointStruct(
                id=point_id,
                vector=child_emb.tolist(),
                payload={
                    "child_content": child,
                    "parent_id": parent_id,
                    "parent_content": parent,  # On stocke le contexte complet
                },
            ))

    console.print(f"[cyan]→ {len(points)} petits chunks (children) générés[/cyan]")
    console.print(f"[cyan]→ Chaque petit chunk garde une référence vers son parent[/cyan]\n")

    # 2. Indexation dans Qdrant
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    dim = model.get_sentence_embedding_dimension()
    client.create_collection(COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))
    client.upsert(COLLECTION, points=points, wait=True)

    # 3. Rechercher
    query = "Que faire avec le traceId d'une erreur 500 ?"
    console.print(f"[bold cyan]Requête : {query}[/bold cyan]\n")

    query_emb = model.encode(f"query: {query}", normalize_embeddings=True)
    hits = client.query_points(COLLECTION, query=query_emb.tolist(), limit=10, with_payload=True).points

    # 4. Top-3 children sans déduplication
    console.print("[bold]Top-3 children (vue brute)[/bold]")
    for i, hit in enumerate(hits[:3], start=1):
        console.print(Panel(
            hit.payload["child_content"][:150] + "...",
            title=f"Child #{i} (score={hit.score:.3f}, parent={hit.payload['parent_id']})",
            border_style="orange3",
        ))

    # 5. Déduplication par parent → on retourne les sections complètes au LLM
    # Si plusieurs enfants matchent le même parent, on ne garde que le parent une fois
    seen_parents: set[int] = set()
    unique_parents: list[tuple[int, str, float]] = []
    for hit in hits:
        pid = hit.payload["parent_id"]
        if pid not in seen_parents:
            seen_parents.add(pid)
            unique_parents.append((pid, hit.payload["parent_content"], hit.score))
        if len(unique_parents) >= 2:
            break

    console.print("\n[bold orange3]Top-2 parents uniques (ce qui sera passé au LLM)[/bold orange3]")
    for pid, content, score in unique_parents:
        console.print(Panel(
            content,
            title=f"Parent #{pid} (meilleur score child={score:.3f})",
            border_style="green",
        ))

    console.print("\n[bold]Pourquoi c'est mieux :[/bold]")
    console.print("• Le retrieval est précis car on cherche sur des chunks courts (200 tok)")
    console.print("• Mais le LLM voit du contexte large (600+ tok) → meilleures réponses")
    console.print("• Si plusieurs children matchent le même parent, on déduplique automatiquement")
    console.print("• Pattern recommandé pour la documentation technique structurée\n")


if __name__ == "__main__":
    main()
