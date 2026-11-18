*Projet fil rouge — NSS+ Dev Full Stack assisté par IA · Neosoft*

# NeoFlow

*Livrer une fonctionnalité métier de bout en bout avec un agent de développement encadré, outillé et mesuré*

individuel · 10 jours · une variante métier par stagiaire · OpenCode (J1–J2), puis vos propres outils en Python et Java sur l'API Claude (J3–J10)

✦

## Contexte fictif

Vous êtes consultants Neosoft, développeurs full stack, intégrés au centre de services qui accompagne le **Groupe Velmora**, entreprise fictive de services aux entreprises (facility management, maintenance multitechnique, accueil) : **4 000 salariés**, un siège à Lyon et **14 agences**, dont une à Saint-Denis de La Réunion.

Depuis 2014, toutes les demandes internes de Velmora (congés, notes de frais, matériel, accès aux applications, achats…) passent par un vieil intranet maison, complété au fil des années par des fichiers Excel et des circuits de validation par mail. Environ **25 000 demandes par an** sont traitées ainsi. Les règles de validation ont été codées en 2014, modifiées au gré des incidents, et plus personne ne sait exactement ce qu'elles font.

La DSI de Velmora a lancé **NeoFlow**, une application unique de gestion de demandes. Une première équipe a livré le **socle** : domaine, circuit de validation, API REST, interface minimale, observabilité. Le module de règles de l'ancien intranet a été repris **tel quel** dans le socle : il fonctionne, mais il n'est pas testé.

Neosoft est mandaté pour livrer les **types de demandes métier**, un lot par consultant. Le responsable de mission impose une condition : l'usage de l'IA doit être **outillé, sécurisé et mesuré**. Il attend à la fin non seulement une fonctionnalité qui marche, mais une **méthode transmissible** à l'équipe qui prendra la suite (votre toolbox) et des **preuves chiffrées** de ce que l'IA a réellement apporté.

> Votre mission : livrer la variante métier qui vous est attribuée sur le socle NeoFlow. Vous encadrez d'abord un assistant du marché (OpenCode, J1–J2), puis vous **codez vos propres outils IA** en Python et en Java sur l'API Claude (J3–J10) : vous en bornez les permissions, vous vérifiez chacune de leurs productions et vous mesurez leur coût et leur apport.

## Ce que vous ne faites pas

*Vous ne réécrivez pas le socle et vous ne changez pas de stack. Vous ne mettez pas en place d'authentification d'entreprise (SSO, OIDC) : HTTP Basic suffit. Vous ne déployez rien en production ni dans un cloud : docker-compose sur votre poste suffit. Vous n'utilisez aucune donnée réelle, aucun compte client, aucun code client. Vous ne pratiquez qu'OpenCode en J1–J2, et aucun assistant du commerce ensuite : à partir du J3, les TP se font avec les outils que vous codez. Vous ne corrigez pas tout ce que vous croisez : ce qui sort de votre périmètre fait l'objet d'un ticket ou d'un ADR, pas d'un commit opportuniste. Vous ne cherchez pas l'esthétique de l'interface : un écran clair et testable suffit.*

✦

## Le socle fourni

Chaque stagiaire reçoit le même dépôt, créé depuis le dépôt modèle Neosoft (« Use this template », dépôt **privé** à votre nom). Le socle compile, démarre et ses tests passent.

### Contenu

```
neoflow/
├── README.md  Makefile  docker-compose.yml  .env.example  .gitignore
├── backend/                 Spring Boot 3.5, Java 21, Maven (./mvnw)
│   └── src/main/java/com/neosoft/neoflow/
│       ├── demande/         entité Demande, statuts, service, API REST, journal d'audit
│       ├── regles/          RegleMetierDemande, RegleMetierRegistry, RegleGenerique
│       ├── validation/      CircuitValidationService (adaptateur vers le legacy)
│       ├── legacy/          RegleValidationLegacy, CalculRemboursementLegacy
│       ├── security/        SecurityConfig (HTTP Basic)
│       └── common/          gestion des erreurs (ProblemDetail)
│   └── src/main/resources/  application*.yml, db/migration (Flyway V1, V2)
├── frontend/                React 18, TypeScript, Vite, Vitest
│   └── src/                 api/client.ts, pages/, legacy/utils-legacy.js
├── e2e/                     Playwright : tests/parcours-demande.spec.ts
├── docs/                    architecture/, adr/, specs/ (vide), tickets/ (un ticket par variante)
├── labs/                    spec/ (J3), agent/ (J4), rag/ (J5), mcp/ (J6), tests-ia/ (J7), legacy-ia/ (J8),
│                            workflow/ (J9), evals/ (J10) : outils à compléter ; regressions/ (J7)
├── scripts/                 injecter-regression.sh, retirer-regression.sh
└── .github/workflows/ci.yml build et tests uniquement
```

### Ce que le socle ne contient pas

| Absent | Pourquoi | Construit en |
|---|---|---|
| `AGENTS.md`, `opencode.json` | C'est votre configuration d'agent : vous la construisez | J1, puis J2 et J6 |
| `.opencode/` (agents, commandes, skills, plugins) | Compétences et garde-fous de votre assistant | J1–J2 |
| Fonctions clés des laboratoires `labs/` | Marquées `TODO`, avec des tests qui échouent tant qu'elles ne sont pas écrites : c'est votre code | J3 à J10 |
| `ia-toolbox/` | Politique, règles, prompts, matrices, métriques | J1 à J10 |
| Règles et champs propres aux variantes | C'est votre lot | J3 (spec), J4 (code) |
| Tests du module legacy | Module volontairement non testé, à caractériser | J8 |
| Contrôles de sécurité en CI | Vous les ajoutez vous-même | J2 |

### Démarrage

```bash
git clone <url-de-votre-depot> neoflow && cd neoflow
cp .env.example .env              # valeurs de démonstration ; .env est ignoré par Git, .env.example est versionné
make up                           # stack complète : postgres, jaeger, backend, frontend

# Sans Docker (poste restreint) :
make backend-h2                   # terminal 1 : API sur 8080, base H2 en mémoire
make frontend                     # terminal 2 : interface Vite sur 5173

make test                         # tests backend et frontend
make e2e                          # parcours Playwright (application démarrée)
```

| Service | URL |
|---|---|
| Interface | http://localhost:5173 |
| API | http://localhost:8080/api |
| Swagger UI | http://localhost:8080/swagger-ui.html |
| Jaeger (traces) | http://localhost:16686 |
| Qdrant (profil `ia`, J5) | http://localhost:6333 |
| Ollama (profil `ia`, J5) | http://localhost:11434 |

| Compte | Rôle | Département | Mot de passe |
|---|---|---|---|
| `alice` | DEMANDEUR | COMMERCIAL | `neoflow` |
| `bob` | VALIDEUR | FINANCE | `neoflow` |
| `admin` | ADMIN | DSI | `neoflow` |

Le circuit de base est : `BROUILLON → SOUMISE → VALIDEE | REFUSEE`, puis `VALIDEE → CLOTUREE`. Les règles métier se branchent par un bean `RegleMetierDemande` ; leurs erreurs renvoient une réponse 422. Le détail est dans `docs/architecture/ARCHITECTURE.md` : lisez-le avant de demander quoi que ce soit à l'agent.

### Prérequis poste

| Outil | Version | Quand |
|---|---|---|
| Docker et docker compose | récents (à défaut, profil `dev-h2`) | J1 → J10 |
| Java (et le wrapper Maven `./mvnw`) | 21 | J1 → J10, et les labs Java des J7–J8 |
| Node.js | 20+ | J1 → J10 (frontend, Playwright) |
| **Python et `uv`** | **3.11+**, `uv` récent (`uv --version`) | **obligatoires à partir du J3** (labs Python) |
| OpenCode | **1.19.x** (`opencode --version`) | J1 et J2 |
| Git, `make` | récents | J1 → J10 |

La clé API Anthropic personnelle est fournie par Neosoft et lue dans la variable `ANTHROPIC_API_KEY`. En J1–J2, OpenCode utilise les identifiants `anthropic/claude-sonnet-5-5` (agent `build`), `anthropic/claude-opus-5-5` (planification, revue) et `anthropic/claude-haiku-5-5` (`small_model`), à vérifier avec `opencode models anthropic`. À partir du J3, vos outils appellent l'API directement (SDK Python `anthropic`, SDK Java `com.anthropic:anthropic-java`) avec `claude-sonnet-5-5` par défaut, `claude-haiku-5-5` pour les tâches légères et `claude-opus-5-5` pour la planification et la revue.

Des bases en Python suffisent (lire et écrire un script, `pytest`) : un rappel ciblé est fourni en début de J3.

✦

## Votre variante

Chaque stagiaire reçoit **une variante métier distincte** en J1. Elle correspond à une valeur de `TypeDemande` et à un ticket brut, volontairement ambigu, dans `docs/tickets/<TYPE>.md`. Les règles détaillées, les données d'exemple et l'extension du J10 sont dans `VARIANTES.md`.

| N° | Variante | `TypeDemande` | Thème | Difficulté |
|---|---|---|---|---|
| 1 | Congés | `CONGES` | solde, chevauchement, jours ouvrés | ★★ |
| 2 | Notes de frais | `NOTE_DE_FRAIS` | lignes de frais, plafonds via le legacy, justificatif | ★★★ |
| 3 | Matériel informatique | `MATERIEL_IT` | catalogue, budget d'équipe | ★ |
| 4 | Réservation de salle | `RESERVATION_SALLE` | créneaux, capacité, conflits | ★★ |
| 5 | Formation | `FORMATION` | budget annuel, prérequis, quota | ★★ |
| 6 | Accès applicatif | `ACCES_APPLICATIF` | habilitations, double validation | ★★★ |
| 7 | Déplacement | `DEPLACEMENT` | avance, transport, seuils | ★★ |
| 8 | Achat | `ACHAT` | seuils multi-niveaux, fournisseur référencé | ★ |
| 9 | Incident | `INCIDENT` | priorité, SLA, escalade | ★★★ |
| 10 | Onboarding | `ONBOARDING` | checklist, dépendances de tâches | ★★ |

> En J3, lisez d'abord le ticket **seul**. La comparaison avec `VARIANTES.md` vient après votre propre liste de questions : c'est elle qui est évaluée.

## Règles de la mission

Ces règles s'appliquent comme en mission cliente. Leur non-respect est éliminatoire à la démonstration finale (voir `GRILLE_VALIDATION.md`).

| Règle | Concrètement |
|---|---|
| Données fictives uniquement | Aucun nom, mail, code ou document réel, ni d'un client, ni de Neosoft, ni de vous. Les jeux de données de `VARIANTES.md` suffisent. |
| Clé API personnelle | Fournie par Neosoft, rattachée à un espace de formation. Elle reste dans la variable `ANTHROPIC_API_KEY` (et, en J1–J2, dans `~/.local/share/opencode/auth.json`). Vos outils la lisent dans l'environnement : jamais en dur dans le code, jamais dans un fichier versionné, un prompt, un journal ou une trace, jamais partagée. |
| Coûts maîtrisés | Votre clé a un plafond de dépense. En J1–J2, suivez votre consommation avec `opencode stats`. À partir du J3, vos outils relèvent l'usage renvoyé par chaque réponse de l'API (`input_tokens`, `output_tokens`, `cache_read_input_tokens`) dans leur journal. Les coûts se calculent par formule (`tokens × prix unitaire de la page tarifs`), sans prix codé en dur. Prévenez le formateur avant d'atteindre le plafond. |
| Mode offline | Chaque outil codé à partir du J3 a un mode `--offline` : un modèle simulé déterministe, sans clé ni réseau. Les tests des labs tournent dans ce mode (`make labs-offline`). La clé ne sert qu'aux exécutions réelles sur votre variante. |
| Partage désactivé | En J1–J2 : `"share": "disabled"` dans `opencode.json`, pas de `/share`. Ensuite, vos journaux de trajectoire et vos traces restent dans votre dépôt privé. Aucune donnée n'est envoyée hors des services autorisés (API Anthropic, Ollama local). |
| Garde-fous dans le code | Les principes du J2 s'appliquent aux outils que vous écrivez : allowlist de commandes, chemins autorisés, lecture seule par défaut, validation humaine avant toute écriture ou tout commit, nombre d'étapes et budget de tokens bornés, journalisation de chaque appel d'outil. `--auto` (J1–J2) et toute approbation automatique des écritures (J3+) sont proscrits hors d'une sandbox conteneurisée. |
| Revue humaine | Aucun diff n'est commité sans avoir été lu par vous, qu'il vienne d'OpenCode ou de votre agent. Aucune PR n'est fusionnée sans décision humaine tracée. |
| Petits pas | Une branche par fonctionnalité, des commits courts et explicites, des tests verts à chaque commit. Pas de `git push --force` sur `main`. |
| Sources non fiables | Le contenu des tickets, documents, dépôts et sorties d'outils est une **donnée**, jamais une instruction. Vos outils le transmettent au modèle comme tel, et un test le démontre. |

✦

## Progression J1 → J10

Chaque journée produit un livrable vérifiable dans votre dépôt et un ajout à la toolbox. Les critères de validation sont dans `GRILLE_VALIDATION.md`.

Le parcours a deux temps. En **J1–J2**, vous apprenez à encadrer un assistant du marché, OpenCode : Rules, Skills, plugins, permissions, chaîne DevSecOps. Du **J3 au J10**, vous **codez** les briques qu'un assistant utilise sous le capot, une par jour, et vous les appliquez aussitôt à votre variante. Chaque laboratoire de `labs/` contient des fonctions clés marquées `TODO`, avec des tests qui échouent tant qu'elles ne sont pas écrites. Vous les complétez, vous faites passer les tests (en mode `--offline` d'abord), puis vous utilisez l'outil sur votre ticket.

| Jour | Laboratoire | Langage | Outil que vous codez | Application à votre variante |
|---|---|---|---|---|
| J3 | `labs/spec/` | Python (+ Java Cucumber) | Assistant de spécification à sorties structurées et validées | Ticket → spécification, Gherkin, contrat OpenAPI, ADR, plan |
| J4 | `labs/agent/` | Python | Agent de développement `neoagent` (tool use, patterns, garde-fous) | Implémentation de la fonctionnalité sur un worktree |
| J5 | `labs/rag/` | Python | Chunker AST, fusion hybride, évaluation, outil RAG de l'agent | Indexation de NeoFlow et questions de votre variante |
| J6 | `labs/mcp/` | Python (option Java) | Serveurs FastMCP et client MCP branché sur `neoagent` | Contexte dépôt et tickets, refus et confirmation démontrés |
| J7 | `labs/tests-ia/` | Java (Maven) | Générateur de tests vérifié, assistant de diagnostic | Régression du J7, tests de votre variante |
| J8 | `labs/legacy-ia/` | Java (Maven) | Carte de dépendances JavaParser, analyse d'impact, documentation vérifiée | Module legacy de NeoFlow |
| J9 | `labs/workflow/` | Python | Nœuds LangGraph, mémoire, réindexation | Workflow sur un ticket de votre variante |
| J10 | `labs/evals/` | Python | Évaluations de l'agent et du RAG, mesure des tokens et des coûts | Extension en mode vibe puis structuré, démonstration |

### J1 — Assistants IA, OpenCode et Context Engineering

**Objectif** : se doter d'un environnement IA utilisable en mission et transformer des prompts isolés en conventions versionnées.

1. Créer votre dépôt depuis le modèle, choisir votre variante, vérifier compilation, démarrage et tests initiaux (`make test`).
2. Installer et configurer OpenCode (clé API, modèles), vérifier la configuration résolue avec `opencode debug config`.
3. Mesurer une **baseline** : résoudre une tâche simple fournie par le formateur en mode chat, puis en mode agent ; comparer le diff, le temps, les erreurs, les actions humaines et les tokens.
4. Initialiser `ia-toolbox/` : README d'usage IA, mini-politique d'usage en contexte client, matrice de choix des assistants.
5. Rédiger `AGENTS.md` et les règles par stack, référencées par `instructions` dans `opencode.json`.
6. Rejouer une même tâche avec et sans Rules et noter les écarts.

**Livrables** : dépôt opérationnel, `ia-toolbox/` initialisée, matrice de choix des assistants, baseline, `AGENTS.md`.

**Ajouts à la toolbox** : `AGENTS.md`, `opencode.json`, `ia-toolbox/README.md`, `ia-toolbox/policy/POLITIQUE_USAGE_IA.md`, `ia-toolbox/rules/` (`java-spring.md`, `react-typescript.md`, `tests.md`, `securite.md`), `ia-toolbox/prompts/`, `ia-toolbox/metrics/baseline.md`, `ia-toolbox/matrices/` (choix des assistants).

**Schéma attendu** : contexte IA — développeur, OpenCode, modèles, dépôt Git et frontières de confiance.

### J2 — Skills, Hooks, permissions et DevSecOps

**Objectif** : rendre les compétences réutilisables et encadrer l'agent avant de lui confier du code.

1. Créer deux Skills, `api-spring` et `revue-pr`, et tester leur déclenchement sur des demandes réelles.
2. Créer la commande `review` et l'agent `reviewer` en lecture seule.
3. Écrire le plugin `garde-fous` (fichiers sensibles, commandes destructives) et le plugin `qualite-apres-edition` (lint et tests après édition) ; vérifier les erreurs remontées et les faux positifs.
4. Régler les permissions (`allow`, `ask`, `deny`, accès hors projet, détection de boucles) ; auditer un agent volontairement sur-permissionné, le corriger et tester les refus.
5. Ajouter à la CI Semgrep, Gitleaks et Trivy (avec SBOM) ; lancer la chaîne sur le socle et traiter chaque alerte : correctif, faux positif justifié ou dette acceptée par ADR.
6. Ouvrir une PR, la faire relire par l'agent `reviewer`, puis formaliser votre décision de fusion.

**Livrables** : Skills, commande, plugin et agent reviewer versionnés, matrice de permissions, pipeline CI, PR avec rapport de revue et approbation humaine.

**Ajouts à la toolbox** : `.opencode/agents/reviewer.md`, `.opencode/commands/review.md`, `.opencode/skills/api-spring/`, `.opencode/skills/revue-pr/`, `.opencode/plugins/garde-fous.ts`, `.opencode/plugins/qualite-apres-edition.ts`, `.opencode/package.json`, permissions dans `opencode.json`, `ia-toolbox/policy/` complétée, `ia-toolbox/rules/securite.md`, `ia-toolbox/matrices/` (risques).

**Schémas attendus** : assemblage du contexte (Rules, Skills, fichiers sélectionnés, mémoire, outils) ; chaîne de livraison sécurisée (commit → CI et Quality Gates → revue agent → validation humaine).

### J3 — Spec-Driven Development · `labs/spec/` (Python, Java Cucumber)

**Objectif** : passer d'un ticket ambigu à une spécification vérifiable avant toute génération de code, avec un assistant de spécification que vous codez.

*Coder l'outil*

1. Compléter l'assistant de `labs/spec/` : appel de l'API Claude avec sorties structurées (JSON Schema), chaîne ticket → questions → arbitrage humain → exigences, Gherkin et delta OpenAPI.
2. Brancher les validations automatiques : parseur Gherkin, validateur OpenAPI, contrôle de traçabilité (aucune exigence sans scénario, aucun scénario orphelin).
3. Faire passer les tests du lab, d'abord en `--offline`.

*L'appliquer à votre variante*

4. Lire `docs/tickets/<TYPE>.md` **seul** et noter vos propres questions. Passer ensuite le ticket dans l'assistant et comparer ses ambiguïtés aux vôtres.
5. Trancher vous-même chaque hypothèse et consigner la décision. Le modèle propose, vous arbitrez.
6. Obtenir les exigences fonctionnelles et non fonctionnelles (identifiants stables, par exemple `CONG-EF-01`, `CONG-ENF-01`), les scénarios Gherkin, le contrat OpenAPI, au moins un ADR et le plan de tâches, tous validés par l'outil.
7. Générer les squelettes de step definitions Cucumber-JVM (Java) à partir des scénarios ; ils seront exécutés en J7.
8. Faire relire l'ensemble par un pair et intégrer ses remarques.

**Livrables** : assistant de spécification (tests verts, mode offline), spécification structurée, scénarios d'acceptation, contrat OpenAPI, ADR, plan technique, squelettes de steps.

**Ajouts à la toolbox** : `labs/spec/` complété ; prompts et schémas de sortie versionnés ; `docs/specs/<TYPE>-*` et `docs/adr/ADR-001…` pour votre variante.

**Schéma attendu** : chaîne de traçabilité ticket → exigences → scénarios → contrat → tâches, et flux de l'assistant (ticket → modèle → validateurs → arbitrage humain).

### J4 — Agent de développement et patterns agentiques · `labs/agent/` (Python)

**Objectif** : coder votre agent de développement, `neoagent`, et lui faire implémenter la fonctionnalité spécifiée, de façon traçable et bornée.

*Coder l'outil*

1. Écrire la boucle d'agent (`neoagent/agent.py`) avec le tool use de l'API Claude : observation, décision, action, jusqu'au critère de fin.
2. Compléter les outils de base (`neoagent/tools.py`) : lire, chercher, lister, éditer, exécuter une commande **allowlistée**, voir le diff.
3. Coder les bornes : nombre d'étapes, budget de tokens, timeouts, chemins autorisés, validation humaine avant toute écriture et tout commit, journal de trajectoire JSONL (une ligne par appel au modèle, appel d'outil, approbation, erreur).
4. Coder et comparer les patterns de `neoagent/patterns/` demandés par le TP, dont **Generator–Verifier** avec Maven comme vérificateur.
5. Démontrer chaque garde-fou par un test : commande hors allowlist refusée, écriture hors chemin refusée, budget dépassé interrompu.

*L'appliquer à votre variante*

6. Créer une branche et un worktree dédiés, puis lancer `uv run neoagent --repo <worktree> --tache "…" --pattern generator_verifier --journal traj.jsonl`.
7. Vérifier chaque exigence du J3 par au moins un test. Tenir la traçabilité exigence → commit → test.
8. Relire le diff complet : aucun changement hors périmètre, tests du socle toujours verts. Vous validez chaque écriture.

**Livrables** : agent de développement avec ses garde-fous (tests verts, mode offline), branche de fonctionnalité, journal de trajectoire, traçabilité exigence, test et commit.

**Ajouts à la toolbox** : `labs/agent/` complété (`neoagent`), politique d'outils (allowlist, chemins), journaux de trajectoire de référence.

**Schéma attendu** : diagramme de séquence ticket → plan → `neoagent` → outils → tests Maven → revue humaine.

### J5 — RAG local, Codebase Intelligence et recherche hybride · `labs/rag/` (Python)

**Objectif** : déterminer, mesures à l'appui, si un RAG que vous codez améliore la compréhension du projet par rapport à la recherche native.

*Coder l'outil*

1. Compléter le chunker AST (Tree-sitter), la fusion hybride RRF et les métriques d'évaluation (Recall@k, MRR) du lab ; tests verts.
2. Exposer la recherche comme outil de `neoagent` (fonction `rag_tool` de `labs/rag/agent_tool.py`, chargée par `--outils-externes`).

*L'appliquer à votre variante*

3. Démarrer le profil `ia` (`make up-ia`), vérifier le modèle d'embeddings et indexer NeoFlow.
4. Ajouter à `labs/evals/rag_questions.yaml` trois à cinq questions propres à votre variante (`V01`…), fichiers attendus vérifiés à la main.
5. Comparer recherche native (Git, ripgrep), vectorielle, BM25 et hybride sur les mêmes questions : Recall@k, MRR, latence. Repérer une référence obsolète.
6. Faire répondre `neoagent` à une question de votre variante avec l'outil RAG, en citant ses sources.

**Livrables** : lab RAG complété, jeu de questions de référence, tableau comparatif mesuré, outil RAG de l'agent.

**Ajouts à la toolbox** : `labs/rag/` complété, `ia-toolbox/rag/` (configuration d'indexation), `ia-toolbox/evals/` (résultats).

**Schéma attendu** : pipeline d'ingestion et de retrieval — fichiers → AST et chunks → embeddings et index → recherche → sources → agent.

### J6 — MCP : écrire et sécuriser des serveurs d'outils · `labs/mcp/` (Python, option Java)

**Objectif** : exposer le dépôt, la base, les tickets et le retriever par MCP, sous contrôle, et les consommer depuis votre agent.

*Coder l'outil*

1. Compléter deux serveurs FastMCP du lab (retriever du J5, tickets, base SQL en lecture seule) : schémas d'entrée validés, lecture seule par défaut, journal d'audit.
2. Compléter le client MCP (`labs/mcp/client/`, fonction `outils_mcp`) qui transforme les outils des serveurs en outils de `neoagent`.
3. Coder la confirmation explicite des écritures (par exemple `comment_ticket`) et le refus des lectures hors périmètre ; tests verts.

*L'appliquer à votre variante*

4. Brancher les serveurs sur `neoagent` et enchaîner inspection du dépôt et récupération de contexte métier sur votre ticket.
5. Prouver qu'une lecture interdite est refusée et qu'une écriture exige votre confirmation ; conserver les journaux d'accès.
6. Montrer qu'une instruction cachée dans un ticket ou une sortie d'outil reste une donnée.

**Livrables** : serveurs MCP, client branché sur l'agent, matrice de permissions, journaux d'accès.

**Ajouts à la toolbox** : `labs/mcp/` complété, `ia-toolbox/mcp/` (matrice de permissions MCP).

**Schéma attendu** : diagramme de séquence `neoagent` → client MCP → serveurs dépôt, RAG, base, tickets → contrôle des permissions.

### J7 — Tests, TDD, E2E et debugging assistés par IA · `labs/tests-ia/` (Java, Maven)

**Objectif** : faire produire des tests et des correctifs en conservant des preuves indépendantes de leur bon fonctionnement, avec des outils que vous écrivez en Java.

*Coder l'outil*

1. Compléter le générateur de tests (SDK Java Anthropic) : il propose des tests JUnit 5 à partir de la spécification et du code, puis les **vérifie** par compilation, exécution et score de mutation (PIT). Les tests qui ne compilent pas, échouent sans raison ou ne tuent aucun mutant (tests tautologiques) sont rejetés.
2. Compléter l'assistant de diagnostic : lecture des logs ECS et des traces exportées, hypothèses de cause racine en sortie structurée.

*L'appliquer à votre variante*

3. Injecter la régression fournie (`make regression-on`), reproduire le symptôme.
4. Faire produire des hypothèses par l'assistant, puis les vérifier vous-même : log, `traceId`, trace dans Jaeger. Une hypothèse ne vaut rien sans preuve.
5. Écrire les tests unitaires, API et le scénario E2E Playwright **avant** la correction, et les voir échouer.
6. Corriger, rejouer les tests, comparer les traces, relire le diff. Le correctif se fait dans le code : `make regression-off` sert seulement à revenir à l'état initial.
7. Automatiser les scénarios Gherkin de votre variante avec les steps Cucumber-JVM du J3. Générer des tests pour votre variante et ne garder que ceux qui survivent à la vérification.

**Livrables** : outil de génération de tests (tests verts, mode offline), suite de tests, scénario E2E, rapport de diagnostic, correctif.

**Ajouts à la toolbox** : `labs/tests-ia/` complété, rapports de mutation de référence.

**Schéma attendu** : flux de diagnostic navigateur → API → base, logs et traces corrélées → assistant → hypothèse → test qui reproduit.

### J8 — Refactoring, code legacy et documentation technique · `labs/legacy-ia/` (Java, Maven)

**Objectif** : moderniser et documenter le module legacy sans modifier involontairement son comportement, avec un outillage Java que vous codez.

*Coder l'outil*

1. Compléter la carte de dépendances calculée avec JavaParser, de façon **déterministe** : classes, méthodes, appels, dépendances statiques.
2. Compléter l'explication et l'analyse d'impact par Claude, à partir de cette carte. Chaque affirmation du modèle est vérifiée par un test ou rejetée.
3. Compléter la génération de documentation (JavaDoc, README, Mermaid), vérifiée contre le code.

*L'appliquer à votre variante*

4. Explorer `backend/.../legacy/` et `frontend/src/legacy/` avec votre outil ; expliquer trois risques de modification.
5. Écrire les tests de caractérisation (golden master, horloge injectée), y compris sur les cas qui vous semblent faux.
6. Refactorer par petits commits, en rejouant les tests à chaque étape. Traduire `utils-legacy.js` en TypeScript avec des tests de parité. Tout changement de comportement voulu fait l'objet d'un commit séparé et d'un ADR.
7. Documenter avant et après : JavaDoc, TSDoc, README technique, diagrammes.

**Livrables** : outil d'analyse legacy, module refactoré, tests de non-régression, documentation, ADR, diagrammes avant et après.

**Ajouts à la toolbox** : `labs/legacy-ia/` complété.

**Schéma attendu** : diagramme C4 composants ou Mermaid des dépendances avant et après refactoring, produit à partir de la carte JavaParser.

### J9 — Mémoire des agents et pipelines intelligents · `labs/workflow/` (Python)

**Objectif** : articuler mémoire, connaissances et orchestration résiliente sans confondre un agent avec un ordonnanceur.

*Coder l'outil*

1. Compléter les nœuds du workflow LangGraph : routage de source, récupération RAG, proposition, approbation humaine, action idempotente.
2. Compléter la mémoire (sémantique, épisodique, procédurale) avec provenance, portée, expiration et invalidation.
3. Compléter la réindexation incrémentale déclenchée par commit ; tests verts en `--offline`.

*L'appliquer à votre variante*

4. Exécuter le workflow sur un ticket de votre variante, jusqu'à l'approbation.
5. Provoquer une interruption, reprendre depuis le checkpoint et vérifier l'absence de double exécution.
6. Enregistrer un souvenir, modifier le dépôt, vérifier que le souvenir obsolète est écarté, puis réindexer.

**Livrables** : workflow avec état sauvegardé, mémoire, journal de reprise, scénario de réindexation.

**Ajouts à la toolbox** : `labs/workflow/` complété ; choix de mémoire et de workflow documentés dans `ia-toolbox/README.md`.

**Schéma attendu** : diagramme d'états LangGraph et pipeline Git → extraction → embeddings et index → validation.

### J10 — Vibe coding encadré, mesure d'impact et démos individuelles · `labs/evals/` (Python)

**Objectif** : prouver les gains et les limites des outils que vous avez construits, et remettre une toolbox transmissible.

*Coder l'outil*

1. Compléter les évaluations : critères d'acceptation, trajectoires et appels d'outils de `neoagent` (lus dans le journal JSONL), jeu de référence RAG du J5, régression des prompts.
2. Compléter la mesure des tokens et des coûts à partir de l'usage renvoyé par l'API, et la comparaison des modes vibe et structuré.

*L'appliquer à votre variante*

3. Faire produire l'extension proposée pour votre variante (`VARIANTES.md`) par `neoagent --mode vibe` : sans spécification ni vérificateur, en temps limité. Noter les oublis, la dette et les fragilités.
4. La reprendre en `--mode structure` : spécification du J3, Generator–Verifier, tests E2E, contrôles de sécurité.
5. Rejouer les évaluations et mesurer avant et après : délai complet, reprises humaines, défauts, couverture, tokens et coûts. Les traces des labs vont dans Langfuse si le profil `obs` est démarré.
6. Nettoyer, versionner et documenter la toolbox ; présenter la démonstration individuelle.

**Livrables** : démonstration individuelle, toolbox documentée, rapport qualité et coût, dossier de preuves.

**Ajouts à la toolbox** : `labs/evals/` complété, `ia-toolbox/metrics/` (rapport avant et après), `ia-toolbox/evals/` (résultats), `ia-toolbox/install.sh`.

**Schéma attendu** : vue d'ensemble de la toolbox et séquence de livraison de bout en bout.

✦

## La toolbox à remettre

Votre toolbox vit dans votre dépôt NeoFlow. Elle réunit la configuration d'assistant des J1–J2 et les outils que vous avez codés du J3 au J10. `ia-toolbox/install.sh` doit pouvoir l'installer dans un autre dépôt.

```
neoflow/
├── AGENTS.md                      règles projet (J1)
├── opencode.json                  modèles, permissions, instructions (J1, J2)
├── .opencode/                     assistant encadré (J2)
│   ├── agents/    reviewer.md
│   ├── commands/  review.md
│   ├── skills/    api-spring/, revue-pr/
│   ├── plugins/   garde-fous.ts, qualite-apres-edition.ts
│   └── package.json
├── ia-toolbox/
│   ├── README.md                  usage IA du projet (J1), choix de mémoire et de workflow (J9)
│   ├── policy/POLITIQUE_USAGE_IA.md (J1, complétée J2)
│   ├── rules/                     java-spring.md, react-typescript.md, tests.md, securite.md (J1, J2)
│   ├── prompts/                   bibliothèque de prompts (J1+)
│   ├── matrices/                  choix des assistants (J1), risques (J2)
│   ├── rag/                       configuration d'indexation (J5)
│   ├── mcp/                       matrice de permissions MCP (J6)
│   ├── evals/                     résultats d'évaluation (J5, J10)
│   ├── metrics/                   baseline.md (J1), rapport avant et après (J10)
│   └── install.sh                 installe la toolbox dans un autre dépôt (J10)
├── labs/                          outils codés, tests verts, mode --offline
│   ├── spec/        assistant de spécification (J3, Python + steps Cucumber Java)
│   ├── agent/       neoagent : boucle, outils, patterns, garde-fous (J4, Python)
│   ├── rag/         chunker AST, recherche hybride, évaluation, outil de l'agent (J5, Python)
│   ├── mcp/         serveurs FastMCP et client branché sur neoagent (J6, Python)
│   ├── tests-ia/    générateur de tests vérifié, assistant de diagnostic (J7, Java)
│   ├── legacy-ia/   carte JavaParser, analyse d'impact, documentation vérifiée (J8, Java)
│   ├── workflow/    workflow LangGraph, mémoire, réindexation (J9, Python)
│   └── evals/       évaluations, mesure des tokens et des coûts (J10, Python)
└── .github/workflows/             CI : build, tests, sécurité (J2), tests des labs en offline
```

## Livrables finaux

| Livrable | Emplacement attendu |
|---|---|
| Spécification et ADR de la variante | `docs/specs/`, `docs/adr/`, produits et validés par `labs/spec/` |
| Scénarios ATDD/BDD automatisés | fichiers `.feature` et steps Cucumber-JVM exécutés |
| Fonctionnalité testée (back, front, E2E) | branche implémentée avec `neoagent` et fusionnée par PR ; `make test` et `make e2e` verts |
| Outils IA codés | `labs/<lab>/` complétés ; `make labs-test` et `make labs-offline` verts |
| Agent de développement borné | `labs/agent/`, garde-fous démontrés par des tests, journaux de trajectoire |
| Module legacy documenté et sécurisé | tests de caractérisation, ADR, diagrammes avant et après issus de `labs/legacy-ia/` |
| RAG local évalué | collection `neoflow`, `ia-toolbox/rag/`, résultats dans `ia-toolbox/evals/` |
| MCP à privilèges limités | serveurs et client de `labs/mcp/`, `ia-toolbox/mcp/`, journaux d'accès |
| Workflow résilient | `labs/workflow/` avec checkpoint, journal de reprise |
| PR sécurisée | CI verte (tests, Semgrep, Gitleaks, Trivy), rapport de revue, décision humaine |
| Toolbox Git transmissible | `AGENTS.md`, `opencode.json`, `.opencode/`, `ia-toolbox/` avec `install.sh`, `labs/` |

## Dossier de preuves

Le dossier de preuves répond à une question simple : **qu'est-ce que vos outils IA ont réellement apporté, à quel coût, avec quelles limites ?** Rassemblez-le dans `ia-toolbox/metrics/` et `ia-toolbox/evals/`, avec un index qui pointe vers chaque preuve.

| Famille | Exemples de preuves |
|---|---|
| Évaluations | Recall@k et MRR du J5 avant et après, critères d'acceptation réussis par `neoagent`, trajectoires et appels d'outils, régression des prompts |
| Qualité | Tests verts (socle, variante, labs), score de mutation commenté, couverture commentée (et pas seulement affichée), défauts trouvés en revue, alertes de sécurité traitées |
| Garde-fous | Tests qui prouvent les refus (commande, chemin, lecture MCP interdite), confirmations d'écriture tracées dans les journaux |
| Coûts | Tokens par tâche relevés dans l'usage de l'API (journaux des labs), calculés par formule, comparés à la baseline OpenCode du J1 |
| Efficacité | Délai bout en bout, nombre de reprises humaines, temps de revue, nombre d'étapes de l'agent ; vibe contre structuré |
| Limites | Ce que vos outils ont mal fait, ce que vous avez dû refaire, les biais de vos mesures, ce que vous ne recommanderiez pas en mission |

## Schémas attendus

| Quand | Schéma |
|---|---|
| J1 | Contexte IA et frontières de confiance |
| J2 | Assemblage du contexte ; chaîne de livraison sécurisée |
| J3 | Chaîne de traçabilité ticket → exigences → scénarios → contrat → tâches ; flux de l'assistant de spécification |
| J4 | Séquence ticket → plan → `neoagent` → outils → tests → revue humaine |
| J5 | Pipeline d'ingestion et de retrieval jusqu'à l'outil de l'agent |
| J6 | Séquence `neoagent` → client MCP → serveurs → contrôle des permissions |
| J7 | Flux de diagnostic navigateur → API → base, logs et traces → hypothèse → test |
| J8 | Dépendances du module legacy avant et après |
| J9 | États du workflow LangGraph ; pipeline de réindexation |
| J10 | Vue d'ensemble de la toolbox ; séquence de livraison de bout en bout |
| Final | **Architecture de la toolbox, chaîne RAG/MCP, séquence agentique, mémoire** |

Format libre (Mermaid dans le dépôt de préférence, SVG ou PNG accepté), à condition que le schéma soit **exact** par rapport à ce que vous avez construit.

✦

## Démonstration individuelle (J10)

Pas de soutenance formelle : une démonstration de votre travail, sur votre poste, devant le formateur et le groupe, en **10 minutes, suivies de 5 minutes de questions**. Chaque démonstration est **distincte** puisque chaque variante l'est.

| Temps | Séquence | Ce que vous montrez |
|---|---|---|
| 1 min 30 | Ticket et spécification | Le ticket brut, les ambiguïtés trouvées et tranchées, la sortie validée de votre assistant de spécification |
| 3 min | Agent | `neoagent` sur votre variante (en direct ou trajectoire rejouée), un garde-fou qui se déclenche, le diff que vous avez validé |
| 2 min | Tests | Tests générés et vérifiés, régression du J7 et preuve de sa correction, E2E vert |
| 1 min 30 | RAG et MCP | Une réponse sourcée obtenue par l'outil RAG ou MCP de l'agent, un refus d'accès démontré |
| 1 min | PR | La CI de sécurité, le rapport de revue, votre décision de fusion |
| 1 min | Mesure | Vibe contre structuré, tokens et coûts, reprises humaines, limites |
| 5 min | Questions | Questions du formateur et du groupe |

> Une démonstration réussie se rejoue : un autre développeur doit pouvoir cloner votre dépôt, lancer `make labs-offline`, installer votre toolbox et obtenir le même résultat. Si le réseau tombe, vos outils tournent en `--offline` et vos journaux de trajectoire servent de preuve.

## Validation

La validation est **continue** : chaque journée est validée sur ses livrables et ses preuves, puis la démonstration du J10, la toolbox remise et le dossier de preuves complètent l'évaluation. Les critères, le barème et les points éliminatoires sont dans `GRILLE_VALIDATION.md`.
