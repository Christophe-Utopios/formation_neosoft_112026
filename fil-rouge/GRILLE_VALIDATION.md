*Projet fil rouge — NSS+ Dev Full Stack assisté par IA · Neosoft*

# NeoFlow — Grille de validation

*Validation continue par journée et démonstration individuelle en J10, sans soutenance formelle*

✦

## Principe

La validation repose sur trois éléments : les **livrables de chaque journée**, vérifiés dans le dépôt du stagiaire ; la **démonstration individuelle du J10** ; la **toolbox remise** et le **dossier de preuves** (évaluations, qualité, coûts, limites).

| Statut | Signification |
|---|---|
| **Acquis** | Tous les critères de la journée sont satisfaits et prouvés dans le dépôt |
| **En cours** | Livrables présents mais au moins un critère non prouvé ; reprise possible jusqu'au J10 |
| **Non acquis** | Livrable principal absent, ou critère bloquant non satisfait à la fin du J10 |

Mode opératoire : le stagiaire indique, pour chaque critère, le chemin ou la commande qui le prouve ; le formateur vérifie en fin de journée ou le lendemain matin. Une preuve est un fichier versionné, une commande rejouable ou une capture datée : une affirmation orale n'est pas une preuve.

Les critères de chaque journée reprennent la ligne « Validation » du programme détaillé, complétée de critères vérifiables propres au fil rouge.

✦

## J1 — Assistants IA, OpenCode et Context Engineering

> Programme : choix argumenté ; environnement reproductible ; aucune donnée sensible utilisée ; changements Git relus.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Dépôt opérationnel | ☐ Le socle compile, démarre et ses tests passent sur le poste du stagiaire | `make test` vert ; capture de l'interface connectée en `alice` | |
| Environnement reproductible | ☐ OpenCode 1.19.x configuré, configuration résolue vérifiée ; Python 3.11+ et `uv` installés pour les labs du J3 au J10 | `opencode --version`, `opencode debug config` sans erreur ; `uv --version` | |
| Matrice de choix des assistants | ☐ Choix argumenté selon données, confidentialité, coût, licences, politique client | `ia-toolbox/matrices/` | |
| Baseline | ☐ Même tâche en chat et en agent, mesurée : temps, diff, erreurs, actions humaines, tokens | `ia-toolbox/metrics/baseline.md` | |
| `ia-toolbox/` initialisée | ☐ README d'usage IA et mini-politique d'usage en contexte client | `ia-toolbox/README.md`, `ia-toolbox/policy/POLITIQUE_USAGE_IA.md` | |
| `AGENTS.md` et Rules | ☐ Règles projet et règles par stack, périmètre explicite, référencées par `instructions` | `AGENTS.md`, `ia-toolbox/rules/*.md`, `opencode.json` | |
| Comparaison avec et sans Rules | ☐ Écart observé et documenté sur une même tâche | note dans `ia-toolbox/metrics/` ou `ia-toolbox/prompts/` | |
| Gouvernance | ☐ Partage désactivé, aucune donnée réelle, aucune clé dans le dépôt | `"share": "disabled"` ; `git log -p` sans secret | |
| Revue Git | ☐ Chaque commit de la journée relu et explicite | `git log --oneline` | |
| Schéma | ☐ Contexte IA et frontières de confiance | fichier Mermaid, SVG ou PNG versionné | |

## J2 — Skills, Hooks, permissions et DevSecOps

> Programme : instructions compréhensibles, périmètre explicite, déclenchement pertinent, Hook reproductible. Blocage démontré en cas de défaut critique, secrets protégés et trace d'approbation humaine.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Skills `api-spring` et `revue-pr` | ☐ `name` identique au dossier ; description qui dit quoi et quand ; déclenchement constaté sur une demande pertinente, et non déclenchement sur une demande hors sujet | `.opencode/skills/*/SKILL.md` ; extrait de session | |
| Commande `review` | ☐ Rejouable, contexte injecté explicitement | `.opencode/commands/review.md` | |
| Agent `reviewer` | ☐ Lecture seule effective : écriture et édition refusées, shell limité | `.opencode/agents/reviewer.md` ; refus constaté | |
| Plugins | ☐ `garde-fous` bloque la lecture d'un `.env` et une commande destructive ; `qualite-apres-edition` remonte une erreur de lint ou de test ; faux positifs identifiés | `.opencode/plugins/*.ts` ; journal du blocage | |
| Permissions | ☐ Agent sur-permissionné audité, corrigé, refus testés | matrice de permissions ; `opencode.json` ; `opencode debug config` | |
| Matrice de risques | ☐ Risques du code généré et des agents, avec parade | `ia-toolbox/matrices/` | |
| Pipeline CI | ☐ Semgrep, Gitleaks, Trivy et SBOM exécutés sur chaque PR ; un défaut critique fait échouer la CI | `.github/workflows/` ; exécution rouge puis verte | |
| Traitement des alertes | ☐ Chaque alerte du socle classée : corrigée, faux positif justifié ou dette acceptée par ADR | rapport de scan annoté, commits ou ADR | |
| PR relue | ☐ Rapport de l'agent `reviewer` sur la PR et décision de fusion humaine tracée | lien de PR, commentaire de revue, approbation | |
| Secrets | ☐ Aucun secret dans le dépôt ni dans l'historique ; `.env` ignoré | Gitleaks vert ; `.gitignore` | |
| Schémas | ☐ Assemblage du contexte ; chaîne de livraison sécurisée | fichiers versionnés | |

## Critères communs aux outils codés (J3 à J10)

À partir du J3, chaque journée livre un **outil codé** dans `labs/<lab>/`, puis son application à la variante. Les critères ci-dessous s'ajoutent à ceux de chaque journée ; un outil qui ne les remplit pas laisse la journée au statut En cours.

| Critère commun | Critère vérifiable | Preuve attendue |
|---|---|---|
| Tests verts | ☐ Tous les `TODO` du lab sont écrits ; les tests du lab passent | `uv run pytest` (Python) ou `./mvnw test` (Java) dans le lab ; `make labs-test` |
| Mode offline | ☐ L'outil fonctionne avec `--offline` (modèle simulé déterministe), sans clé ni réseau API | `make labs-offline` vert, clé absente de l'environnement |
| Garde-fous démontrés | ☐ Au moins un refus prouvé par un test : commande hors allowlist, chemin non autorisé, écriture sans confirmation, budget dépassé | test nommé, sortie du test |
| Clé et secrets | ☐ Clé lue dans `ANTHROPIC_API_KEY` uniquement ; aucune clé ni valeur sensible dans le code, les journaux ou les traces versionnés | `git grep`, Gitleaks vert |
| Données non fiables | ☐ Les contenus de tickets, de documents et de sorties d'outils sont transmis au modèle comme des données | test ou extrait de prompt |
| Usage et coût | ☐ Usage renvoyé par l'API (`input_tokens`, `output_tokens`, `cache_read_input_tokens`) journalisé pour chaque appel réel | journal JSONL ou sortie de l'outil |
| Application à la variante | ☐ L'outil a été exécuté pour de vrai sur le ticket ou le code de la variante, et sa sortie relue | journal d'exécution, fichiers produits, commit |

## J3 — Spec-Driven Development · `labs/spec/`

> Programme : traduire une demande en spécification, critères d'acceptation et conception vérifiables avant la génération du code ; validation humaine des hypothèses.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Assistant de spécification | ☐ Sorties structurées par JSON Schema ; chaîne ticket → questions → arbitrage → exigences, Gherkin, OpenAPI ; tests verts, offline compris | `labs/spec/` ; tests du lab | |
| Validations automatiques | ☐ Un Gherkin invalide, un contrat OpenAPI invalide et une exigence sans scénario sont rejetés par l'outil | tests du lab qui le prouvent | |
| Ambiguïtés | ☐ Liste personnelle produite à partir du ticket seul, avant l'outil et avant `VARIANTES.md` ; comparée à celle de l'assistant ; décisions humaines tracées | journal des questions et décisions dans `docs/specs/` | |
| Spécification structurée | ☐ Exigences fonctionnelles et non fonctionnelles identifiées ; exigences non fonctionnelles chiffrées | `docs/specs/` | |
| Scénarios d'acceptation | ☐ Chaque exigence fonctionnelle est couverte par au moins un scénario Gherkin, référencé par son identifiant | fichiers `.feature`, contrôle de traçabilité vert | |
| Contrat OpenAPI | ☐ Contrat valide, cohérent avec l'API existante, sans rupture de compatibilité | validation par l'outil | |
| Squelettes Cucumber-JVM | ☐ Step definitions générées à partir des scénarios, compilables | classes Java générées, `./mvnw test-compile` | |
| ADR et plan | ☐ Au moins un ADR sur un point à trancher ; tâches ordonnées avec dépendances, reliées aux exigences | `docs/adr/`, `docs/specs/` | |
| Relecture par un pair | ☐ Remarques du pair consignées et traitées | commentaires de PR ou note de relecture | |
| Schéma | ☐ Chaîne de traçabilité ticket → exigences → scénarios → contrat → tâches ; flux de l'assistant | fichier versionné | |

## J4 — Agent de développement et patterns agentiques · `labs/agent/`

> Programme : chaque exigence a une preuve de test ; aucun changement hors périmètre ; validation explicite du diff.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| `neoagent` | ☐ Boucle tool use et outils de base complétés ; CLI `uv run neoagent --repo … --tache … [--offline]` opérationnelle ; tests verts | `labs/agent/` ; tests du lab | |
| Bornes d'autonomie | ☐ Nombre d'étapes, budget de tokens et timeouts appliqués ; arrêt propre démontré quand une borne est atteinte | test du lab ; journal avec événement `fin` | |
| Garde-fous | ☐ Commande hors allowlist refusée ; écriture hors des chemins autorisés refusée ; écriture et commit soumis à approbation humaine | tests du lab ; événements `approbation` du journal | |
| Patterns | ☐ Generator–Verifier avec Maven comme vérificateur ; au moins un autre pattern codé et comparé sur une même tâche | `neoagent/patterns/` ; note de comparaison | |
| Journal de trajectoire | ☐ JSONL conforme au contrat (une ligne par événement, usage par appel au modèle) | `traj.jsonl` de la variante | |
| Branche de fonctionnalité | ☐ Fonctionnalité de la variante implémentée par `neoagent` dans un worktree dédié | `git worktree list`, `git branch` | |
| Preuve par exigence | ☐ Chaque exigence de la spécification est reliée à au moins un test vert | traçabilité exigence → commit → test | |
| Périmètre et diff | ☐ Aucun changement hors périmètre ; tests du socle verts ; décision humaine explicite sur le diff | `git diff main...` relu ; `make test` vert ; note de revue | |
| Schéma | ☐ Séquence ticket → plan → `neoagent` → outils → tests → revue humaine | fichier versionné | |

## J5 — RAG local, Codebase Intelligence et recherche hybride · `labs/rag/`

> Programme : réponses sourcées ; dépôt et commit identifiables ; métriques calculables et limites explicites.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Code du lab | ☐ Chunker AST, fusion RRF et métriques (Recall@k, MRR) complétés ; tests verts | `labs/rag/` ; tests du lab | |
| Collection RAG | ☐ Documentation et code indexés, métadonnées chemin, symbole, lignes, commit, branche | collection `neoflow` ; sortie de l'indexeur | |
| Configuration d'indexation | ☐ Versionnée, rejouable par un tiers | `ia-toolbox/rag/` | |
| Jeu de questions de référence | ☐ Questions propres à la variante ajoutées, fichiers attendus vérifiés à la main | `labs/evals/rag_questions.yaml` | |
| Tableau comparatif | ☐ Recherche native, vectorielle, BM25 et hybride comparées sur les mêmes questions : Recall@k, MRR, latence | `ia-toolbox/evals/` | |
| Outil RAG de l'agent | ☐ `neoagent` répond à une question de la variante avec l'outil RAG, en citant chemin, lignes et commit | journal de trajectoire | |
| Référence obsolète et limites | ☐ Une source obsolète repérée et traitée ; cas où la recherche native suffit explicités | note dans `ia-toolbox/evals/` | |
| Schéma | ☐ Pipeline fichiers → chunks → embeddings et index → recherche → sources → agent | fichier versionné | |

## J6 — MCP : écrire et sécuriser des serveurs d'outils · `labs/mcp/`

> Programme : outils découverts, réponses exploitées avec provenance, accès interdits refusés et secrets absents du dépôt.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Serveurs MCP | ☐ Deux serveurs FastMCP complétés, schémas d'entrée validés, lecture seule par défaut ; tests verts | `labs/mcp/` ; tests du lab | |
| Client MCP | ☐ Outils des serveurs découverts et fournis à `neoagent` sous forme de `Tool` | `labs/mcp/client/` ; journal de trajectoire | |
| Scénario combiné | ☐ Inspection du dépôt et récupération de contexte métier enchaînées sur la variante | journal de trajectoire | |
| Refus démontré | ☐ Une lecture interdite est refusée ; une écriture exige une confirmation explicite, tracée | tests ; journaux d'accès | |
| Injection d'instructions | ☐ Une instruction cachée dans un ticket ou une sortie d'outil reste une donnée | test ou extrait de trajectoire | |
| Matrice de permissions | ☐ Outil par outil : lecture, écriture, confirmation, identité technique | `ia-toolbox/mcp/` | |
| Secrets | ☐ Aucun identifiant de base ni jeton dans le dépôt | Gitleaks vert ; variables d'environnement | |
| Schéma | ☐ Séquence `neoagent` → client MCP → serveurs → contrôle des permissions | fichier versionné | |

## J7 — Tests, TDD, E2E et debugging assistés par IA · `labs/tests-ia/`

> Programme : bug reproduit avant correction, tests indépendants et verts après correction, cause racine expliquée.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Générateur de tests | ☐ Tests JUnit 5 proposés puis vérifiés par compilation, exécution et mutation (PIT) ; tests tautologiques rejetés ; tests du lab verts | `labs/tests-ia/` ; `./mvnw test` dans le lab | |
| Assistant de diagnostic | ☐ Hypothèses de cause racine en sortie structurée, à partir des logs ECS et des traces | rapport produit par l'outil | |
| Reproduction | ☐ Régression injectée et symptôme reproduit (interface, API ou E2E) | `make regression-on` ; sortie de test | |
| Diagnostic vérifié | ☐ Hypothèse confirmée par un humain : log, `traceId` cité, trace Jaeger | rapport de diagnostic, capture Jaeger | |
| Tests avant correction | ☐ Tests unitaires, API et E2E rouges avant le correctif | commit des tests précédant le commit du correctif | |
| Correctif | ☐ Tests verts après correction, sur le même scénario ; diff relu ; cause racine expliquée, avec la raison pour laquelle les tests existants ne la détectaient pas | `make test`, `make e2e`, rapport | |
| Tests de la variante | ☐ Scénarios Gherkin du J3 exécutés par Cucumber-JVM ; tests générés conservés seulement s'ils tuent des mutants | rapport PIT ; tests associés aux `.feature` | |
| Schéma | ☐ Flux navigateur → API → base, logs et traces → hypothèse → test | fichier versionné | |

## J8 — Refactoring, code legacy et documentation technique · `labs/legacy-ia/`

> Programme : comportement conservé ; diff justifié ; documentation exacte et maintenable.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Outil d'analyse legacy | ☐ Carte de dépendances JavaParser déterministe ; explications et analyse d'impact par Claude vérifiées ; documentation générée contrôlée ; tests verts | `labs/legacy-ia/` ; `./mvnw test` dans le lab | |
| Exploration | ☐ Points d'entrée, dépendances et trois risques de modification expliqués à partir de la carte | note d'exploration | |
| Tests de caractérisation | ☐ Comportements observés figés (golden master, horloge injectée), y compris les comportements surprenants | tests verts avant le premier commit de refactoring | |
| Refactoring incrémental | ☐ Petits commits, tests rejoués à chaque étape ; tout changement voulu isolé dans un commit séparé avec ADR | `git log` ; ADR | |
| Traduction | ☐ `utils-legacy.js` traduit en TypeScript avec tests de parité | fichiers `.ts` et tests Vitest | |
| Documentation | ☐ JavaDoc, TSDoc et README technique exacts par rapport au code | fichiers versionnés | |
| Schéma | ☐ Dépendances avant et après refactoring, issues de la carte (C4 composants ou Mermaid) | fichiers versionnés | |

## J9 — Mémoire des agents et pipelines intelligents · `labs/workflow/`

> Programme : reprise effective, aucune action sensible sans approbation, connaissance obsolète écartée.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Code du lab | ☐ Nœuds du workflow, mémoire et réindexation complétés ; tests verts en `--offline` | `labs/workflow/` ; tests du lab | |
| Workflow avec état | ☐ Exécution complète sur un ticket de la variante, checkpoints persistés | base de checkpoints ; sortie d'exécution | |
| Reprise | ☐ Interruption provoquée puis reprise depuis le checkpoint, sans double exécution de l'action | journal de reprise | |
| Approbation | ☐ L'action sensible attend une approbation humaine explicite | trace de l'interruption et de la décision | |
| Mémoire | ☐ Souvenirs avec provenance et portée ; souvenir obsolète invalidé après modification du dépôt | journal de la mémoire | |
| Réindexation | ☐ Réindexation ciblée déclenchée par un commit, limitée aux fichiers modifiés | sortie du pipeline | |
| Schéma | ☐ États du workflow LangGraph ; pipeline Git → extraction → embeddings et index → validation | fichiers versionnés | |

## J10 — Vibe coding encadré, mesure d'impact et démos individuelles · `labs/evals/`

> Programme : résultat reproductible, démonstration distincte par participant et limites clairement expliquées.

| Livrable | Critère vérifiable | Preuve attendue | Statut |
|---|---|---|---|
| Code du lab | ☐ Évaluations de l'agent (critères d'acceptation, trajectoires, appels d'outils) et du RAG, mesure des tokens et des coûts depuis l'usage API ; tests verts en `--offline` | `labs/evals/` ; tests du lab | |
| Vibe puis structuré | ☐ Extension de la variante produite par `neoagent --mode vibe`, oublis et dette relevés, puis reprise en `--mode structure` (spécification, Generator–Verifier, tests E2E, contrôles de sécurité) | deux branches comparables ; liste des défauts relevés ; journaux | |
| Évaluations rejouées | ☐ Jeu de référence du J5 et régression des prompts rejoués ; écarts analysés | `ia-toolbox/evals/` | |
| Rapport qualité et coût | ☐ Avant et après : délai, reprises humaines, défauts, couverture, tokens et coûts calculés par formule ; biais de mesure commentés | `ia-toolbox/metrics/` | |
| Toolbox documentée | ☐ Installable dans un autre dépôt par `install.sh` ; `make labs-test` et `make labs-offline` verts ; README à jour | `ia-toolbox/install.sh`, `ia-toolbox/README.md` | |
| Dossier de preuves | ☐ Index des preuves de J1 à J10 | `ia-toolbox/metrics/` ou `ia-toolbox/evals/` | |
| Démonstration | ☐ Réalisée selon la grille ci-dessous | grille renseignée | |
| Schéma | ☐ Vue d'ensemble de la toolbox et séquence de livraison de bout en bout | fichiers versionnés | |

✦

## Grille de la démonstration individuelle (J10)

Durée : **10 minutes de démonstration** sur le poste du stagiaire, puis **5 minutes de questions**. Pas de support de soutenance exigé : on montre le dépôt, les outils codés en action, leurs journaux, les tests et la PR. Si le réseau ou la clé font défaut, la démonstration se fait en `--offline` avec les journaux de trajectoire enregistrés, sans pénalité.

| N° | Critère | Points | Attendu pour la note maximale | Preuves attendues |
|---|---|---|---|---|
| 1 | Parcours de bout en bout | 15 | Ticket → spécification (assistant) → `neoagent` → tests → RAG/MCP → PR enchaînés sans rupture, sur la variante du stagiaire | dépôt, journaux de trajectoire, PR |
| 2 | Outils codés | 20 | Labs du J3 au J10 complétés et lisibles ; `make labs-test` et `make labs-offline` verts ; contrat de `neoagent` respecté | `labs/`, sortie des cibles make |
| 3 | Garde-fous et sécurité | 15 | Un refus déclenché en direct (commande, chemin ou lecture MCP) ; une écriture confirmée par un humain ; CI de sécurité verte, alertes traitées ; décision de fusion humaine tracée | journaux, workflow CI, rapport de revue |
| 4 | Spécification et traçabilité | 10 | Ambiguïtés tranchées et tracées ; chaque exigence reliée à un scénario, un commit et un test, contrôle de traçabilité vert | `docs/specs/`, `docs/adr/`, sortie de `labs/spec/` |
| 5 | Qualité et preuves de test | 10 | Tests unitaires, API et E2E verts ; tests générés vérifiés par mutation ; régression du J7 couverte ; aucun test tautologique | `make test`, `make e2e`, rapport PIT |
| 6 | RAG et MCP | 10 | Une réponse sourcée obtenue par l'outil de l'agent ; métriques du J5 connues | `ia-toolbox/evals/`, `ia-toolbox/mcp/`, journaux |
| 7 | Mesure avant et après | 10 | Vibe contre structuré et baseline du J1 chiffrés (tokens depuis l'usage API, coûts par formule, reprises humaines) ; biais expliqués | `ia-toolbox/metrics/` |
| 8 | Toolbox transmissible | 5 | Installation dans un dépôt vierge démontrée ou rejouable ; README suffisant pour un tiers | `ia-toolbox/install.sh`, README |
| 9 | Lucidité sur les limites | 5 | Ce que les outils ont mal fait, ce qui a été refait, ce qui ne serait pas recommandé en mission | fiche de limites |
| | **Total** | **100** | | |

Barème par critère : note maximale si l'attendu est démontré et prouvé ; moitié des points si l'attendu est partiellement démontré ou si la preuve manque ; zéro si le critère n'est pas abordé. Le temps est tenu : ce qui n'est pas montré dans les 10 minutes peut être prouvé pendant les questions par un fichier ou une commande, pas par une affirmation orale.

### Seuil de validation

- Démonstration : **60 points sur 100** au minimum, et aucun zéro sur les critères 1, 2 et 3.
- Journées : au moins **8 journées sur 10 au statut Acquis**, et aucune au statut Non acquis à la fin du J10.
- Toolbox remise et dossier de preuves présent.

### Points éliminatoires

Chacun de ces points entraîne la non-validation, quelle que soit la note :

| Point éliminatoire | Vérification |
|---|---|
| Secret committé : clé API, mot de passe réel ou jeton, dans un fichier ou dans l'historique Git | Gitleaks sur tout l'historique |
| Clé API écrite en dur dans le code d'un outil, ou présente dans un journal de trajectoire ou une trace versionnés | `git grep`, Gitleaks |
| Donnée réelle utilisée : donnée client, donnée personnelle, code ou document d'un client | revue du dépôt et des sessions exportées |
| Diff fusionné sans relecture humaine tracée | historique de la PR |
| Contournement délibéré des garde-fous pour faire passer un livrable (hooks désactivés, CI de sécurité neutralisée, `--auto` ou approbation automatique des écritures de `neoagent` hors sandbox) | historique Git, configuration et code des outils |

## Fiche de synthèse du stagiaire

| Stagiaire | Variante | J1 | J2 | J3 | J4 | J5 | J6 | J7 | J8 | J9 | J10 | Démo /100 | Validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | |
