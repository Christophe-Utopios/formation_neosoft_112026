# Formation Neosoft : lancer les démos NeoFlow

Les démos des modules M03 à M08 utilisent NeoFlow, le fil rouge du dossier `fil-rouge/neoflow`, comme exemple : sa documentation (notes de frais, barèmes, tickets) pour le RAG, et ses collaborateurs et ses demandes pour les agents et MCP.

Les démos n'ont pas besoin que l'application NeoFlow tourne. Elles embarquent leurs propres données NeoFlow : `_corpus.py`, `_docs.py` et `_neoflow.py`, une API simulée.

Les commandes ci-dessous sont pour PowerShell sous Windows, depuis le dossier `formation_neosoft`.

## 1. Prérequis

| Outil                   | Pour                                       | Vérifier           |
| ----------------------- | ------------------------------------------ | ------------------ |
| Python 3.11             | toutes les démos                           | `python --version` |
| Docker Desktop, démarré | Qdrant (M04, M05) et pgvector (M04 demo 2) | `docker ps`        |
| Clé API Anthropic       | M05 à M08                                  | voir l'étape 2     |

Les démos M03 et la plupart des démos M04 tournent sans clé API. Au premier lancement, les modèles d'embeddings et le reranker sont téléchargés depuis Hugging Face (environ 3 Go en tout pour M03 à M05).

## 2. Clé API

Créer un fichier `.env` à la racine de `formation_neosoft`, à côté de ce README :

```
ANTHROPIC_API_KEY=sk-ant-...
```

Toutes les démos le trouvent (`load_dotenv()` remonte les dossiers parents). Le fichier est ignoré par git.

## 3. Environnements Python

Deux environnements suffisent : un pour le RAG (M03 à M05), un pour les agents (M06 à M08). Ils sont créés dans `.venv/`, ignoré par git.

```powershell
python -m venv .venv\rag
.venv\rag\Scripts\python -m pip install -r M03_embeddings\requirements.txt -r M04_vector_search\demos\requirements.txt -r M05_rag_avance\requirements.txt
```

```powershell
python -m venv .venv\agents
.venv\agents\Scripts\python -m pip install -r M06_agents_partie1\demos\requirements.txt -r M07_agents_partie2\demos\requirements.txt -r M08_mcp_si\demos\requirements.txt
```

Facultatif, pour essayer le découpage de code avec Tree-sitter (slide « Stratégie 3 bis » du M03) :

```powershell
.venv\rag\Scripts\python -m pip install tree-sitter tree-sitter-language-pack
```

## 4. Services Docker

Qdrant (M04 et M05), sur le port 6333. Le plus simple est d'utiliser celui de NeoFlow :

```powershell
cd fil-rouge\neoflow
docker compose --profile ia up -d qdrant
cd ..\..
```

Ou, sans passer par NeoFlow :

```powershell
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.20.0
```

PostgreSQL avec pgvector (M04 demo 2 seulement), sur le port 5432. Il entre en conflit avec le PostgreSQL de NeoFlow : ne pas lancer les deux en même temps.

```powershell
docker run -d --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg17
```

## 5. Lancer les démos

Activer l'environnement, se placer dans le dossier des démos, puis lancer un fichier. Exemple pour le M03 :

```powershell
.venv\rag\Scripts\Activate.ps1
cd M03_embeddings\demos
python demo_01_tokenisation.py
```

| Module                     | Dossier                                        | Environnement | Services                         | Clé API                    |
| -------------------------- | ---------------------------------------------- | ------------- | -------------------------------- | -------------------------- |
| M03 Embeddings et chunking | `M03_embeddings\demos`                         | rag           | aucun                            | non                        |
| M04 Recherche vectorielle  | `M04_vector_search\demos`                      | rag           | Qdrant ; pgvector pour la demo 2 | non                        |
| M05 RAG avancé             | `M05_rag_avance` (pas de sous-dossier `demos`) | rag           | Qdrant                           | oui, sauf la demo 3        |
| M06 Agents, partie 1       | `M06_agents_partie1\demos`                     | agents        | aucun                            | oui                        |
| M07 Agents, partie 2       | `M07_agents_partie2\demos`                     | agents        | aucun                            | oui, sauf les demos 3 et 4 |
| M08 MCP et SI              | `M08_mcp_si\demos`                             | agents        | aucun                            | oui pour la demo 4         |

À savoir :

- M05 : la première démo lancée indexe le corpus NeoFlow dans Qdrant (collection `m5_rag_demos_neoflow`), les suivantes réutilisent cet index. La demo 3 (reranker) prend quelques secondes sur CPU.
- M07 : les demos 1 à 3 écrivent leurs checkpoints dans des fichiers `.db` du dossier courant ; les supprimer pour repartir de zéro. La demo 6 (CrewAI) n'a pas été testée dans cet environnement.
- M08 : la demo 2 lance elle-même le serveur MCP de la demo 1 ; pas besoin de le démarrer à part.

Changer d'environnement entre M05 et M06 :

```powershell
deactivate
.venv\agents\Scripts\Activate.ps1
```

## 6. Facultatif : lancer l'application NeoFlow

Il faut Java 21 (`java -version`) et Node.js 20 ou plus. Les cibles `make` du README de NeoFlow ne marchent pas sous Windows sans `make` ; voici leurs équivalents.

Avec Docker (base PostgreSQL, Jaeger, API et frontend) :

```powershell
cd fil-rouge\neoflow
docker compose up -d --build
```

Sans Docker (base H2 en mémoire), dans deux terminaux :

```powershell
cd fil-rouge\neoflow\backend
.\mvnw.cmd spring-boot:run "-Dspring-boot.run.profiles=dev-h2"
```

```powershell
cd fil-rouge\neoflow\frontend
npm ci
npm run dev
```

| Service     | URL                                   |
| ----------- | ------------------------------------- |
| Application | http://localhost:5173                 |
| API         | http://localhost:8080/api             |
| Swagger UI  | http://localhost:8080/swagger-ui.html |

Comptes de démonstration, mot de passe `neoflow` : `alice` (demandeuse), `bob` (valideur), `admin`. Plus de détails dans [fil-rouge/neoflow/README.md](fil-rouge/neoflow/README.md).

Pour tout arrêter : `docker compose --profile ia down` dans `fil-rouge\neoflow`, puis `docker rm -f qdrant pgvector` pour les conteneurs lancés à la main.
