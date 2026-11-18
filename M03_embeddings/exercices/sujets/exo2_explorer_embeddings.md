# TP 2 : Les angles morts d'un modèle d'embedding

**Durée** : 45 min
**Modalité** : individuel
**Prérequis** : TP 1 terminé (un modèle retenu)

## Contexte

Avant de mettre un modèle en production, l'équipe qualité de Velora veut une **suite de tests d'acceptation** : une liste de cas qui doivent toujours passer, à rejouer à chaque changement de modèle. Vous allez l'écrire, et découvrir au passage ce qu'un embedding ne sait pas faire.

## Étape 1 : Tests de similarité (15 min)

Dans `starters/exo2_starter.py`, complétez la liste `CASES`. Chaque cas est un triplet `(ancre, positif, négatif)` : le score `cos(ancre, positif)` doit être **strictement supérieur** à `cos(ancre, négatif)`.

Écrivez au moins **12 cas**, 2 par famille :

| Famille         | Exemple d'ancre                    | Positif                                  | Négatif                             |
| --------------- | ---------------------------------- | ---------------------------------------- | ----------------------------------- |
| Paraphrase      | « réinitialiser mon mot de passe » | « j'ai oublié mes identifiants »         | « changer le logo »                 |
| Cross-lingue    | « exporter en CSV »                | « export data as CSV »                   | « exporter en PDF »                 |
| Jargon métier   | « SSO »                            | « authentification unique via SAML »     | « envoi de SMS »                    |
| Négation        | « la MFA est obligatoire »         | « la double authentification est requise » | « la MFA n'est pas obligatoire »  |
| Nombre / code   | « erreur 401 »                     | « token expiré, non authentifié »        | « erreur 403 »                      |
| Version         | « SAML en version 3.2 »            | « SAML sur Velora 3.2 »               | « SAML en version 3.0 »             |

Implémentez `run_cases(model, cases)` : affiche chaque cas, les deux scores, la **marge** et un statut OK / FRAGILE (marge < 0.05) / KO.

## Étape 2 : Analyse (10 min)

Lancez la suite sur votre modèle du TP 1 et sur `all-MiniLM-L6-v2`. Répondez :

1. Quelles familles échouent, et sur quel modèle ?
2. Pour les cas qui passent, la marge est-elle confortable (> 0.05) ?
3. Qu'en déduire pour la recherche de codes d'erreur et de versions ? Quels mécanismes du M04 compensent ces faiblesses ?

## Étape 3 : Coût de stockage (10 min)

Implémentez `storage_table(dims, n_chunks)` pour 1 M et 10 M de chunks, avec 3 précisions :

- float32 (4 octets / dimension)
- float16 (2 octets)
- int8 (1 octet, quantization scalaire)

Pour les dimensions 384, 768, 1024, 3072. Ajoutez une colonne « tient en RAM sur un serveur de 64 Go ? ».

## Étape 4 : Matryoshka (10 min, bonus)

Certains modèles récents (`Qwen3-Embedding`, `text-embedding-3-*`, `jina-embeddings-v3`) sont entraînés en **Matryoshka** : on peut tronquer le vecteur aux N premières dimensions.

Avec `SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", truncate_dim=N)`, mesurez le MRR du golden set pour N = 1024, 256, 128, 64. Requêtes encodées avec `prompt_name="query"`, documents sans préfixe.

## Livrable

- `exo2_solution.py` : la suite de tests, le tableau de stockage
- 5 lignes de réponse aux questions de l'étape 2

## Critères de réussite

- Au moins 12 cas, les 6 familles couvertes
- La marge est affichée, pas seulement OK / KO
- Les faiblesses identifiées sont reliées à une solution (filtre de métadonnées, BM25, reranker)

## Pièges à éviter

- Écrire des négatifs trop faciles : un test qui passe toujours ne teste rien
- Oublier les préfixes du modèle
- Confondre Go et Gio, ou oublier l'index HNSW dans le calcul (compter environ +10 à 20 %)
