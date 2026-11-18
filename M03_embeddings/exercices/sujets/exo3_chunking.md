# TP 3 : Choisir et justifier une stratégie de chunking

**Durée** : 1h
**Modalité** : binôme
**Prérequis** : TP 1 terminé (un modèle retenu), `langchain-text-splitters` et `tiktoken` installés

## Contexte

La base de connaissances Velora est faite de **guides longs** en Markdown (SSO, API, facturation, sécurité, rapports, mobile). Avant d'indexer, l'équipe doit **comparer fixed-size, recursive, structure et semantic**, puis **justifier le choix retenu** par une mesure.

Vous disposez de `exercices/_docs.py` :

- `get_docs()` : 6 guides Markdown avec métadonnées (`doc_id`, `title`, `product`, `version`)
- `get_chunk_golden()` : 24 questions, chacune associée à une **phrase-réponse exacte** (`needle`) présente dans un guide

**Métrique** : une question est réussie si un des k chunks retournés **contient la phrase-réponse en entier**. Un chunk qui coupe la réponse en deux est donc un échec : c'est exactement ce qui arrive en production.

## Étape 1 : Implémenter 4 chunkers (25 min)

Dans `starters/exo3_starter.py`, toutes les tailles sont en **tokens** (`tiktoken`, encodage `cl100k_base`) :

1. `fixed_size(text, size, overlap)` : fenêtre glissante sur les tokens
2. `recursive(text, size, overlap)` : `RecursiveCharacterTextSplitter.from_tiktoken_encoder`, séparateurs adaptés au Markdown
3. `by_markdown(text, size, overlap)` : découpe par titres `#` / `##` (`MarkdownHeaderTextSplitter`), puis `recursive` dans les sections trop longues ; **préfixer chaque chunk par son chemin** `Titre > Section`
4. `semantic(text, model, percentile)` : découpe en phrases, embedding de chaque phrase, coupure là où la similarité entre deux phrases consécutives passe sous le percentile choisi ; taille maximale 300 tokens

Chaque chunk produit doit être un dict avec : `chunk_id`, `doc_id`, `title`, `section` (si connue), `position` (rang dans le doc), `n_tokens`, `text`.

## Étape 2 : Évaluer (15 min)

Implémentez `evaluate(chunks, golden, model, k)` : Recall@1, Recall@3, MRR@3.

Lancez les 4 stratégies avec `size=200`, `overlap=30` et affichez un tableau : nombre de chunks, tokens moyens, min, max, Recall@1, Recall@3, MRR@3, temps de calcul.

## Étape 3 : Balayage des paramètres (10 min)

Pour `fixed` et pour la meilleure stratégie de l'étape 2 :

- `size` dans {100, 200, 300, 500}
- `overlap` dans {0, 30, 60}

Tracez (matplotlib) le Recall@3 en fonction de `size`, une courbe par `overlap`, un graphique par stratégie. Laquelle est la plus sensible aux paramètres, et pourquoi ? Enregistrez `chunking_sweep.png`.

## Étape 4 : Décision (10 min)

Rédigez une note de décision `decision_chunking.md` (10 à 15 lignes) :

- la stratégie et les paramètres retenus, **chiffres à l'appui**
- le coût : nombre de chunks (donc de vecteurs) et temps d'ingestion
- les métadonnées conservées et à quoi elles serviront (filtres M04, citations M05)
- ce que vous testeriez avec plus de temps (contextual retrieval, parent-document, late chunking)

## Livrable

- `exo3_solution.py` : les 4 chunkers, l'évaluation, le balayage
- `chunking_sweep.png`
- la note `decision_chunking.md`

## Critères de réussite

- Tailles mesurées en tokens, jamais en caractères
- Chaque chunk porte `doc_id`, `section` et `position`
- Le choix est justifié par le tableau, pas par une intuition
- La limite de 512 tokens du modèle est vérifiée : aucun chunk ne la dépasse

## Pièges à éviter

- Mesurer en caractères alors que le modèle compte en tokens : en français, 200 caractères font environ 50 tokens
- Oublier que le chunk le plus pertinent pour l'embedding n'est pas forcément le plus utile pour le LLM : un chunk de 50 tokens est précis mais pauvre en contexte
- Un overlap trop grand duplique l'information : le top-3 renvoie trois fois le même passage
- Le semantic chunking n'est pas toujours meilleur : il coûte un embedding par phrase et produit des tailles très irrégulières
