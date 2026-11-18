# TP 1 : Choisir un modèle d'embedding pour l'assistant support Velora

**Durée** : 1h15
**Modalité** : binôme
**Prérequis** : `pip install -r requirements.txt` (racine du module), environ 3 Go d'espace disque pour les modèles

## Contexte

Le directeur du support Velora vous demande quel modèle d'embedding utiliser pour le futur assistant de support basé sur un RAG. Un collègue propose `all-MiniLM-L6-v2` « parce que c'est le plus téléchargé sur Hugging Face ». Un autre veut `text-embedding-3-large` d'OpenAI « parce que c'est le meilleur sur MTEB ».

Vous allez trancher **avec des chiffres mesurés sur les données du client**, pas avec un classement générique.

Vous disposez de `exercices/_corpus.py` : 50 chunks de la base de connaissances Velora et un golden set de 20 requêtes annotées (`get_golden()`).

## Étape 1 : Short-list depuis MTEB (10 min)

Ouvrez le leaderboard MTEB (`huggingface.co/spaces/mteb/leaderboard`), onglet **Retrieval**, langue **French** (ou MTEB-French).

Retenez **4 candidats** en respectant ces contraintes :

- au moins un modèle **multilingue** de moins de 150 M de paramètres
- au moins un modèle de plus de 300 M de paramètres
- uniquement des modèles **open weights** téléchargeables (hébergement en France exigé par le client)

Pour chaque candidat, notez depuis la model card : dimension, longueur max (tokens), licence, préfixes ou instructions attendus.

## Étape 2 : Enrichir le golden set (15 min)

Le golden set fourni ne contient que 20 requêtes. Ajoutez-en **10** dans votre script, en imitant de vrais tickets :

- 3 requêtes avec des fautes de frappe ou du langage parlé (« jarrive pa a me co »)
- 3 requêtes en anglais
- 2 requêtes qui citent un **code d'erreur** (« erreur 429 »)
- 2 requêtes **sans réponse** dans le corpus (pour observer les scores)

Pour les 8 premières, indiquez l'`id` du chunk attendu. Pour les 2 sans réponse, mettez `None`.

## Étape 3 : Benchmark (30 min)

Complétez `starters/exo1_starter.py` :

1. `encode_corpus(model, prefix)` : encode les 50 chunks, vecteurs **normalisés**
2. `rank_of(...)` : rang du chunk attendu pour une requête
3. `evaluate(...)` : Recall@1, Recall@3, MRR, latence moyenne par requête (ms, après warmup)
4. Afficher un tableau comparatif des 4 modèles, et séparément les scores FR et EN
5. Pour les 2 requêtes sans réponse : afficher le score du top-1. Est-il plus bas que pour les autres ?

## Étape 4 : Décision (20 min)

Remplissez une grille de décision pondérée (sur 5) :

| Critère                                  | Poids | Modèle A | Modèle B | ... |
| ---------------------------------------- | ----- | -------- | -------- | --- |
| Qualité (MRR sur vos données)            | 40 %  |          |          |     |
| Latence requête                          | 15 %  |          |          |     |
| Coût de stockage (dimension x 1 M chunks) | 15 %  |          |          |     |
| Longueur max vs taille de vos chunks     | 10 %  |          |          |     |
| Licence et hébergement                   | 20 %  |          |          |     |

Calcul du stockage : `nb_chunks x dimension x 4 octets` (float32).

## Livrable

- `exo1_solution.py` qui reproduit le benchmark
- La grille remplie et une **recommandation argumentée** (5 à 10 lignes) : quel modèle pour l'assistant support Velora, et dans quel cas vous changeriez d'avis

## Critères de réussite

- Les préfixes de chaque modèle sont respectés (sinon la comparaison est biaisée)
- La latence est mesurée après un warmup
- La recommandation cite des chiffres mesurés, pas seulement le rang MTEB
- L'écart FR / EN est commenté

## Pièges à éviter

- Comparer `e5` sans `query:` / `passage:` à un modèle sans préfixe : vous mesurez votre erreur, pas le modèle
- Conclure sur 30 requêtes avec un écart de 0.02 de MRR : c'est du bruit
- Oublier que changer de modèle plus tard = **réindexer tout le corpus**
- Mélanger des vecteurs de deux modèles dans le même index : les espaces ne sont pas comparables
