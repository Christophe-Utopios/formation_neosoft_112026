# Notes formateur — Fil rouge NeoFlow

*Document réservé au formateur. Ne pas le copier dans le dépôt des stagiaires, ne pas le projeter.*

Ce document décrit ce que le dépôt stagiaire ne dit pas : les failles volontaires du socle (cibles du J2), les pièges du module legacy (J8), le détail de la régression injectable (J7), la préparation de la session (dont les laboratoires Python et Java des J3–J10), le plan B en mode offline et les problèmes fréquents. Rappel du parcours : OpenCode en J1–J2 uniquement ; à partir du J3, les stagiaires codent leurs outils IA en Python et en Java sur l'API Claude, dans `labs/`. Toutes les sorties citées ont été obtenues sur le socle livré (Spring Boot 3.5.16, Java 21, Node 20.17, Semgrep 1.90.0, Trivy 0.54.1) le 2026-11-04.

---

## 1. Versions du socle

| Composant | Version | Remarque |
|---|---|---|
| Spring Boot | 3.5.16 | Surcharges `tomcat.version` 10.1.61, `jackson-bom.version` 2.21.8, `postgresql.version` 42.7.12 ; exceptions justifiées dans `.trivyignore` (voir F3) |
| Java | 21 (Temurin ou équivalent) | Le wrapper `./mvnw` (Maven 3.9.8) utilise `JAVA_HOME` |
| springdoc-openapi | 2.8.17 | Ligne compatible Boot 3.5 |
| Flyway / H2 / PostgreSQL JDBC | 10.20.1 / 2.3.232 / 42.7.8 | Gérés par Boot ; Flyway signale « H2 newer than this version » (sans effet) |
| Micrometer Tracing / OpenTelemetry | 1.4.13 / 1.43.0 | Bridge OTel et exporteur OTLP HTTP |
| commons-text | **1.9** | Faille F3 volontaire |
| React / React Router / TypeScript | 18.3.1 / 6.30.6 / 5.9.3 | Drapeaux `v7_*` activés |
| Vite / Vitest / ESLint | 6.4.5 / 3.2.7 / 9.39.5 | Vite 6 retenu car Vite 7+ exige Node 20.19+ |
| Playwright | 1.63.0 | Chromium révision 1243 |
| Python / uv | 3.11+ / récent (0.9 sur le poste auteur) | Obligatoires à partir du J3 ; chaque lab Python a son `pyproject.toml` et, de préférence, son `uv.lock` |
| SDK Anthropic Python | `anthropic` (ligne 2.x au 2026-11-04) | Version épinglée par chaque lab (`uv.lock`) |
| SDK Anthropic Java | `com.anthropic:anthropic-java` (ligne 3.x au 2026-11-04) | Labs Java `tests-ia` (J7) et `legacy-ia` (J8), version épinglée dans leur `pom.xml` |
| Images docker | `postgres:16-alpine`, `jaegertracing/jaeger:2.20.0`, `qdrant/qdrant:v1.20.0`, `ollama/ollama:0.40.14`, `eclipse-temurin:21-jdk` / `21-jre`, `node:20-alpine`, `nginx:1.30-alpine` | Jaeger v2 : l'image `jaegertracing/jaeger` remplace `all-in-one` (v1 en fin de vie) |

---

## 2. Failles volontaires F1 à F5 (J2)

Elles ne sont signalées nulle part dans le dépôt stagiaire ; le code est écrit pour paraître plausible. Les stagiaires les découvrent par les scans et la revue du J2, puis les corrigent dans des PR séparées, chacune passant par la CI de sécurité et la revue par l'agent `reviewer`.

| Id | Faille | Emplacement | Détection vérifiée | Sévérité outil |
|---|---|---|---|---|
| F1 | Injection SQL | `backend/.../demande/DemandeRechercheController.java:38` | Semgrep `p/java` : 3 résultats | CRITICAL (`jpa-sqli`) |
| F2 | XSS stockée | `frontend/src/pages/DemandeDetail.tsx:20` (composant `DescriptionRiche`) | Semgrep `p/react` : 1 résultat | WARNING |
| F3 | Dépendance vulnérable | `backend/pom.xml:24` (`commons-text.version` 1.9), utilisée dans `DemandeMapper.java:54` | Trivy `fs backend` | CRITICAL |
| F4 | Secret en clair | `backend/src/main/resources/application.yml:35` (`neoflow.notification.api-key`) | Gitleaks `generic-api-key` (voir encadré) | — |
| F5 | Actuator exposé sans authentification | `application.yml:42` (`include: "*"`), `:47` et `:49` (`show-values: always`), `SecurityConfig.java:37` (`permitAll`) | Semgrep `r/java.spring.security` ; revue ; ZAP | — |

### F1 — Injection SQL (`GET /api/demandes/recherche?q=`)

```java
entityManager.createNativeQuery("SELECT * FROM demande WHERE titre LIKE '%" + q + "%'", Demande.class)
```

- **Démonstration** : `curl -s -u alice:neoflow "http://localhost:8080/api/demandes/recherche?q=%27%20OR%20%271%27%3D%271"` renvoie toutes les demandes (13 lignes sur la base de démo après une création), au lieu de celles dont le titre contient le texte. Le champ « Rechercher par titre » de la liste est le chemin d'interface.
- **Détection** (`semgrep scan --config p/java --config p/react --config p/secrets backend frontend/src`) :
  - `java.lang.security.audit.formatted-sql-string.formatted-sql-string` (ERROR, ligne 37) ;
  - `java.spring.security.injection.tainted-sql-string.tainted-sql-string` (ERROR, ligne 38) ;
  - `java.spring.security.jpa-sqli.jpa-sqli` (CRITICAL, ligne 38).
- **Correctif** : requête paramétrée, ou méthode dérivée du repository.
  ```java
  return entityManager.createQuery("select d from Demande d where d.titre like :q", Demande.class)
          .setParameter("q", "%" + q + "%").setMaxResults(MAX_RESULTATS).getResultList()
          .stream().map(mapper::versResponse).toList();
  ```
  Attendu en plus : un test d'intégration qui envoie `' OR '1'='1` et vérifie qu'aucune demande n'est renvoyée.

### F2 — XSS stockée (description rendue en HTML)

```tsx
function DescriptionRiche({ html }: DescriptionRicheProps) {
  return <div className="description" dangerouslySetInnerHTML={{ __html: html }} />;
}
```

- **Contexte plausible** : les données de démonstration contiennent de la mise en forme reprise de l'ancien intranet (`<ul>`, `<b>`, entités HTML), et `DemandeMapper` décode les entités (`StringEscapeUtils.unescapeHtml4`). Une charge encodée en entités (`&lt;img ...&gt;`) est donc décodée par l'API puis exécutée par le navigateur.
- **Démonstration** : alice crée une demande dont la description vaut `<img src=x onerror="alert(atob(sessionStorage.getItem('neoflow.auth')))">`, puis la soumet ; bob ouvre le détail, et ses identifiants Basic (`bob:neoflow`) s'affichent. C'est une vraie exfiltration d'identifiants du valideur, car le frontend garde les identifiants en `sessionStorage`.
- **Détection** : `typescript.react.security.audit.react-dangerouslysetinnerhtml.react-dangerouslysetinnerhtml` (WARNING, ligne 20).
  > Point à souligner : cette règle Semgrep est en mode *taint*, avec pour source un paramètre de fonction (les props). Écrite directement dans la page à partir d'un état React, ou avec un type de props littéral en ligne (`({ html }: { html: string })`), la même faille n'est **pas** détectée (vérifié). Le code a été structuré pour être détecté ; c'est une bonne illustration des limites du SAST et de la nécessité de la revue humaine.
- **Correctif** : afficher le texte (`<p className="description">{demande.description}</p>` avec `white-space: pre-wrap`), ou assainir avec DOMPurify (`DOMPurify.sanitize(html)`). En complément : en-tête `Content-Security-Policy` dans `nginx.conf`, et question à poser au métier sur la nécessité réelle du HTML.

### F3 — Dépendance vulnérable `commons-text 1.9` (CVE-2022-42889, « Text4Shell »)

- **Détection** : `trivy fs backend` → `org.apache.commons:commons-text 1.9 CVE-2022-42889 CRITICAL, fixed 1.10.0`.
- **Accessibilité du code vulnérable** : le socle n'utilise que `StringEscapeUtils.unescapeHtml4`, et non `StringSubstitutor.createInterpolator()`, qui porte la vulnérabilité. La CVE n'est donc pas exploitable en l'état. Ce point se prête à la discussion sur l'atteignabilité (reachability) : faut-il corriger quand même ? Oui, le coût est faible et le prochain usage pourrait l'atteindre.
- **Correctif** : `<commons-text.version>1.15.0</commons-text.version>` (ou toute 1.10.0+), relancer `./mvnw verify` et Trivy.

> **État Trivy du socle (vérifié le 2026-11-04).** Le socle est en Spring Boot 3.5.16 avec des surcharges de version pour Tomcat (10.1.61), Jackson (2.21.8) et le pilote PostgreSQL (42.7.12). Deux CVE CRITICAL de `spring-webmvc` 6.2.x (CVE-2026-47884 sur XsltView, CVE-2026-47890 sur SSE avec fragments de vue) ne sont corrigées qu'en Spring Framework 7, donc en Spring Boot 4. Elles ne concernent pas NeoFlow, qui n'utilise ni XsltView ni SSE. Elles sont donc acceptées dans `.trivyignore` à la racine du dépôt, avec justification et expiration au 2027-03-31. Résultat : `trivy fs --severity CRITICAL,HIGH backend/pom.xml` lancé depuis la racine ne remonte **que F3**. Conséquences pédagogiques :
> - la Quality Gate `--severity CRITICAL --exit-code 1` bloque tant que F3 n'est pas corrigée, puis passe : le blocage est démontrable ;
> - le `.trivyignore` sert de support à la discussion sur la gestion des exceptions (justification, responsable, date d'expiration, ADR « migration Spring Boot 4 ») ;
> - Trivy lit `.trivyignore` dans le répertoire courant : lancer les scans depuis la racine du dépôt, ou passer `--ignorefile .trivyignore`.
> La base de vulnérabilités évolue : refaire ce comptage la veille de la session (`trivy fs --format table backend`).

### F4 — Secret en clair (`neoflow.notification.api-key`)

```yaml
neoflow:
  notification:
    actif: false
    api-key: nfk_7Qm2xV9pL4tR8sW1zB6nK3yH5jD0cF2aG8eU
```

- La clé est fausse mais à forte entropie (5,17 bits par caractère). Elle est réellement lue par `NotificationProperties` et envoyée en en-tête `X-Api-Key` par `NotificationService` (inactif par défaut). Le stagiaire ne peut donc pas se contenter de la supprimer.
- **Détection attendue** : Gitleaks, règle `generic-api-key` (`gitleaks git .` sur l'historique, `gitleaks dir .` sur l'arbre de travail, ou l'action GitHub `gitleaks/gitleaks-action`).
  > **Vérification faite** : Gitleaks n'était pas installé sur le poste auteur, et le téléchargement du binaire y a été refusé. La règle `generic-api-key` (expression régulière et seuil d'entropie 3,5) a été reproduite et valide uniquement la ligne 35 : les mots de passe `{noop}neoflow` et les `${DB_PASSWORD:...}` ne sont pas concernés. **Faire tourner `gitleaks dir backend` une fois avant la session.** Ni Trivy (scanner `secret`) ni Semgrep `p/secrets` ne détectent cette clé (vérifié) : c'est justement l'intérêt d'outiller les trois.
- **Chaînage avec F5** : `curl -s http://localhost:8080/actuator/env | grep -o 'nfk_[A-Za-z0-9]*'` affiche la clé **sans authentification** (vérifié), car `show-values: always`.
- **Correctif** : `api-key: ${NEOFLOW_NOTIFICATION_API_KEY:}`, valeur injectée par l'environnement ou un gestionnaire de secrets, rotation de la clé (révocation de l'ancienne). Expliquer que supprimer la ligne ne suffit pas : la clé reste dans l'historique Git (`git log -p`), d'où purge (`git filter-repo`) ou, mieux, révocation. Ajouter Gitleaks en pré-commit et en CI.
- **Publication du modèle** : la protection contre l'envoi de secrets de GitHub (« push protection ») ne bloque pas ce motif générique. Si un jour elle le faisait, autoriser ce faux secret explicitement.

### F5 — Actuator entièrement exposé sans authentification

```yaml
management.endpoints.web.exposure.include: "*"      # application.yml:42
management.endpoint.env.show-values: always         # :47 (configprops : :49)
```
```java
.requestMatchers("/actuator/**").permitAll()          // SecurityConfig.java:37
```

- **Démonstration** : `curl -s http://localhost:8080/actuator` liste tous les endpoints. Ensuite, `/actuator/env` (secrets en clair, voir F4), `/actuator/heapdump` (vidage mémoire contenant les identifiants), `/actuator/loggers` en POST (modification des niveaux de log sans authentification), `/actuator/threaddump` et `/actuator/mappings`.
- **Détection** : `semgrep scan --config r/java.spring.security backend/src` remonte `java.spring.security.audit.spring-actuator-fully-enabled-yaml.spring-actuator-fully-enabled-yaml` (application.yml:42). Cette règle **n'est pas** dans `p/java` (vérifié) : il faut l'ajouter explicitement à la configuration Semgrep de la CI. Une revue de `SecurityConfig` ou un scan ZAP en mode baseline la trouvent aussi.
- **Correctif** : `include: health,info` (et `prometheus` si nécessaire), suppression des `show-values`, `requestMatchers("/actuator/health/**", "/actuator/info").permitAll()` puis `requestMatchers("/actuator/**").hasRole("ADMIN")`. Un port de management séparé (`management.server.port`) est à discuter.

### Autres résultats à anticiper

| Constat | Outil | Position à tenir |
|---|---|---|
| `csrf.disable()` (`SecurityConfig.java:32`) | revue, éventuellement Semgrep selon les règles chargées (non remonté par `p/java` ici) | Défendable : API sans état, identifiants envoyés par en-tête, pas de cookie. À documenter, pas à « corriger » aveuglément |
| Mots de passe `{noop}neoflow` dans `application.yml` | revue | Comptes de démonstration assumés ; en mission : fournisseur d'identité |
| Identifiants Basic en `sessionStorage` | revue | Aggrave F2 ; alternative : jeton à durée courte, cookie `HttpOnly` |
| Swagger UI exposé | avertissement springdoc au démarrage | Acceptable en développement ; à désactiver par profil en production |
| Semgrep 1.90 : une règle de `p/secrets` exige 1.91 (`IncompatibleRule`) | Semgrep | Mettre Semgrep à jour sur les postes |

---

## 3. Pièges du module legacy (J8)

Fichiers à ne pas modifier avant le J8 : `backend/src/main/java/com/neosoft/neoflow/legacy/RegleValidationLegacy.java`, `CalculRemboursementLegacy.java`, `frontend/src/legacy/utils-legacy.js`. Aucun test ne les couvre dans le socle.

| Piège | Où | Effet | Valeur observée (caractérisation) |
|---|---|---|---|
| Dépendance cachée à l'horloge | `determinerNiveau`, fin de méthode (`Calendar.getInstance()`, NF-301) | Le vendredi à partir de 14 h, une demande chiffrée (`m > 0`) de niveau 1 passe au niveau 2. Tests non déterministes | À neutraliser par une `Clock` injectée au refactoring (le socle injecte déjà une `Clock` dans `CircuitValidationService`, que le legacy ignore) |
| Comparaison de références | `departement == DSI` (branche `MATERIEL_IT`) | Vraie avec le littéral `"DSI"`, fausse avec une valeur venue de la base ou du JSON | `MATERIEL_IT`, 2000 €, `"DSI"` littéral → **1** ; `new String("DSI")` → **2**. Dans l'application, toujours 2 au-delà de 1500 € |
| Bornes incohérentes | frais et déplacement `> 1000` / `>= 5000`, achat `>= 1000` / `> 5000` | Cas limites différents selon le type | `NOTE_DE_FRAIS` 1000 → 1, `ACHAT` 1000 → 2 ; `NOTE_DE_FRAIS` 5000 → 3, `ACHAT` 5000 → 2 |
| `NIVEAU_MAX` public, statique, modifiable | `RegleValidationLegacy.NIVEAU_MAX` | État global : un test qui le modifie pollue les autres | — |
| NPE sur montant nul | `montant.doubleValue()` en tête de `determinerNiveau` | L'adaptateur passe `0.0` ; c'est ce garde-fou que casse la régression du J7 | `determinerNiveau("GENERIQUE", null, ...)` → `NullPointerException` |
| Division entière | `Math.round(rembourse * 100) / 100` (`long / int`) | Arrondi à l'euro inférieur au lieu du centime | `REPAS` 30 € → **25.0** (plafond 25,50 attendu) ; `REPAS` 20,75 → 20.0 ; `KILOMETRIQUE` 100 km → 63.0 au lieu de 63,60 |
| TVA en `double` | branche `FORMATION` (`m + m * 0.2 > 2400`) | Fragilité plutôt que bug : sur des montants au centime, le calcul reste exact (vérifié par le corrigé du J8), mais le seuil TTC strict et le taux en dur sont implicites. Bon cas pour montrer qu'un soupçon de l'agent doit être vérifié par un test | 2000 → 1 ; 2000,01 → 2 |
| Majoration étranger | `etranger && !HOTEL` → ×1,1 ; hôtel ×1,3 sur le plafond | Règles implicites | `HOTEL` 300 €, 2 nuits, étranger → 286.0 ; catégorie inconnue `TAXI` 80 €, étranger → 55.0 (plafond 50 × 1,1) |
| Fuseau horaire | `formatDate(new Date('2026-03-01'))` | Une date ISO est interprétée en UTC : la veille s'affiche dans un fuseau négatif | En Europe/Paris l'affichage est correct : faire tester avec `TZ=America/New_York npm test` |
| Jours fériés ignorés, `!=` faibles | `joursOuvres` | Écart métier (1er mai, 25 décembre…) ; utilisé par l'écran de détail | Congés du 21/12/2026 au 01/01/2027 : 10 jours ouvrés affichés, fériés compris |

Valeurs obtenues un mercredi (hors règle du vendredi), en appelant directement les classes legacy. Points pédagogiques : faire écrire les tests de caractérisation **avant** tout changement, figer l'horloge, distinguer le nettoyage (même comportement) de la correction métier (division entière : commit séparé, ADR, validation du métier).

---

## 4. Régression du J07

### Contenu du patch (`labs/regressions/j07-regression.patch`)

| Fichier | Avant | Après | Effet |
|---|---|---|---|
| `validation/CircuitValidationService.java` | `Double montant = d.getMontant() != null ? d.getMontant().doubleValue() : 0.0;` | `Double montant = d.getMontant().doubleValue();` | **Erreur 500 visible** à la soumission d'une demande sans montant |
| `demande/DemandeService.java` (`lister`) | `PageRequest.of(page, size, TRI)` | `int index = page > 0 ? page - 1 : 0;` puis `PageRequest.of(index, size, TRI)`, et la JavaDoc annonce « 1 pour la première page » | **Défaut silencieux** : `page=1` renvoie la page 0 |

### Mode opératoire conseillé

1. La veille ou en début de J7, chaque stagiaire lance `make regression-on` dans son dépôt. Pour rendre l'enquête Git réaliste (`git log -p`, `git bisect`), faire commiter l'injection avec un message anodin : `git commit -am "refactor: simplification du calcul de niveau et de la pagination"`.
2. Redémarrer le backend (`make backend`, `make backend-h2`, ou `docker compose up -d --build backend`).
3. Ne pas montrer le patch. L'en-tête du fichier demande aux stagiaires de ne pas le lire.

Les scripts sont idempotents : ils détectent un patch déjà appliqué ou déjà retiré. Ils fonctionnent dans un dépôt Git (y compris imbriqué dans un dépôt parent, grâce à `GIT_CEILING_DIRECTORIES`) comme dans une copie sans Git, avec `patch -p1` en repli. `retirer-regression.sh` refuse de retirer le patch si les fichiers ont été modifiés depuis. Dans ce cas : `git checkout -- <fichier>` ou correction manuelle.

### Symptômes (vérifiés)

- **Interface** : alice crée une demande GENERIQUE (ou CONGES, INCIDENT, RESERVATION_SALLE, ACCES_APPLICATIF, ONBOARDING) sans montant puis clique sur « Soumettre ». Un message « Une erreur inattendue est survenue. Communiquez le traceId au support. » s'affiche et le statut reste « Brouillon ». Les demandes chiffrées se soumettent normalement, ce qui brouille les premières hypothèses.
- **API** : `500` en ProblemDetail, avec `{"title":"Erreur interne","status":500,"traceId":"b5b7…"}`.
- **Logs ECS** (une ligne JSON) : `"log.level":"ERROR"`, `"message":"Erreur inattendue sur POST /api/demandes/100/soumettre"`, `"traceId":"…"`, `"error.type":"java.lang.NullPointerException"`, `"error.message":"Cannot invoke \"java.math.BigDecimal.doubleValue()\" because the return value of \"com.neosoft.neoflow.demande.Demande.getMontant()\" is null"`, et une pile qui commence par `at com.neosoft.neoflow.validation.CircuitValidationService.calculerNiveau(CircuitValidationService.java:31)`.
- **Jaeger** (profil `dev`) : rechercher le service `neoflow-backend` et le `traceId` des logs ; le span HTTP `POST /api/demandes/{id}/soumettre` est en erreur (statut 500, exception enregistrée par `GlobalExceptionHandler`).
- **E2E** : `make e2e` échoue à l'étape « alice soumet la demande » (`data-statut` attendu `SOUMISE`, obtenu `BROUILLON`).
- **Défaut silencieux** : `GET /api/demandes?page=1&size=5` renvoie les mêmes identifiants que `page=0`, avec `"page":{"number":0,…}`. Dans l'interface, avec 10 demandes par page, le bouton « Suivant » réaffiche la première page, et le compteur reste sur « Page 1 / 2 ».
- **Tests du socle** : tous verts avec la régression (15 tests unitaires et 17 tests d'intégration, vérifié). Les tests n'exercent ni la soumission sans montant, ni une page au-delà de 0. C'est le « faux sentiment de couverture » à faire constater, rapport JaCoCo à l'appui : `CircuitValidationService` y est couvert.

### Attendus du TP

- Hypothèse formulée à partir du log et de la trace, avant de lire le code.
- Tests écrits **avant** la correction et rouges sur le code régressé : test unitaire de `CircuitValidationService.calculerNiveau` avec montant nul ; test d'intégration de soumission sans montant (200, statut `SOUMISE`) ; test d'intégration de pagination (`page=1` renvoie d'autres identifiants que `page=0` et `page.number == 1`) ; le scénario E2E existant.
- Correctif minimal (les deux lignes), tests verts, même scénario rejoué, comparaison des traces avant et après.
- Règle à faire respecter : ne jamais affirmer une valeur de `niveauValidation` dans un test sans figer l'horloge (règle du vendredi).

Pour revenir au socle : `make regression-off` (le code redevient identique à l'original, vérifié avec `diff -r`).

---

## 5. Checklist de préparation

### J-15

- [ ] **Clés API Anthropic** : une par stagiaire (plus une de secours), dans un workspace de formation dédié, avec un plafond de dépense par workspace ou par clé dans la console Anthropic. Noter la date de révocation (fin de session + 1 jour). Ne jamais réutiliser une clé d'une session précédente.
- [ ] Estimer le budget par formule : `stagiaires × jours × tokens moyens par jour × prix unitaire` (page tarifs Anthropic du moment, sans prix codés en dur dans les supports). Prévoir une marge pour les J4 (boucles de `neoagent`, orchestrator-workers) et J10 (évaluations rejouées, modes vibe et structuré). À partir du J3, ce sont les outils des stagiaires qui appellent l'API : vérifier que `neoagent` a un `budget_tokens` par défaut raisonnable et que les tests des labs tournent en `--offline`, sans consommer la clé.
- [ ] **Dépôt modèle** : copie propre du dossier `neoflow/`, régression retirée, aucun `node_modules`, `target`, `dist`, `.env`. Puis `./scripts/init-depot.sh <organisation>/neoflow` (vérifications automatiques, commit initial sur `main`) et publication en dépôt modèle (`gh repo create … --private --source . --push`, puis `gh repo edit … --template`). Vérifier que la CI passe sur `main`.
- [ ] Attribuer les variantes (une par stagiaire, mélange de difficultés ★ à ★★★) et préparer la liste.
- [ ] Ne pas publier `fil-rouge/NOTES_FORMATEUR.md` ni les dossiers `solutions/` dans le dépôt modèle.

### J-3 : poste de référence et postes stagiaires

- [ ] **OpenCode 1.19.x** : `npm i -g opencode-ai@1.19` (ou `curl -fsSL https://opencode.ai/install | bash`), puis `opencode --version`. Désactiver la mise à jour automatique (`"autoupdate": false`) pour garder la même version toute la session.
- [ ] `opencode auth login` avec une clé de test, `opencode models anthropic` (vérifier les identifiants `anthropic/claude-sonnet-5-5`, `anthropic/claude-opus-5-5`, `anthropic/claude-haiku-5-5`), puis `opencode run "Réponds OK"` et `opencode stats`.
- [ ] `opencode debug config` dans un dépôt contenant le corrigé `opencode.json` du J1 : vérifier la configuration résolue (permissions, `share: disabled`, `instructions`). Le format historique est signalé déprécié par la 1.19 mais reste accepté.
- [ ] **Java 21** (`java -version`), **Node 20+** (`node -v`), **Python 3.11+ et uv** (`uv --version`), Git, make.
- [ ] **Docker** : `docker compose version`. Pré-télécharger les images :
  ```bash
  docker compose pull && docker compose --profile ia pull
  docker compose build                     # remplit les caches Maven et npm des images
  docker pull eclipse-temurin:21-jdk eclipse-temurin:21-jre node:20-alpine nginx:1.30-alpine
  ```
  Ajouter les images du fichier `labs/evals/docker-compose.langfuse.yml` (profil `obs`).
- [ ] **Modèles Ollama** : `make up-ia` lance le service `ollama-modeles`, qui télécharge `nomic-embed-text` (environ 275 Mo) dans le volume `ollama-data`. Vérifier avec `docker compose exec ollama ollama list`. Pour d'autres modèles cités par les laboratoires : `docker compose exec ollama ollama pull <modèle>`.
- [ ] **Caches applicatifs** : `cd backend && ./mvnw -B verify` ; `cd frontend && npm ci` ; `cd e2e && npm ci && npx playwright install chromium` (environ 150 Mo par poste) ; `uv sync` dans chaque laboratoire.
- [ ] **Laboratoires J3–J10 (Python, uv, Java)** : sur le poste de référence, puis sur chaque poste (ou via un cache partagé).
  ```bash
  uv --version && uv python install 3.11          # interpréteur géré par uv si le poste n'en a pas
  for lab in labs/*/; do                          # labs Python : dépendances verrouillées dans le cache uv
    [ -f "$lab/pyproject.toml" ] && (cd "$lab" && uv sync --all-extras --frozen || uv sync --all-extras)
  done
  for lab in labs/*/; do                          # labs Java : dépendances Maven (SDK Anthropic, JavaParser, PIT, Cucumber)
    [ -f "$lab/pom.xml" ] && backend/mvnw -B -q -f "$lab/pom.xml" dependency:go-offline test-compile
  done
  (cd labs/rag && uv run python indexer.py --prefetch)   # grammaires Tree-sitter et modèle (si le lab le propose)
  make labs-offline                               # tous les labs en mode simulé, sans clé
  ```
  Attendu : `make labs-offline` passe sur les **corrigés** (`JXX_.../solutions/labs/<lab>/` copiés dans un dépôt de test). Sur le socle livré aux stagiaires, les tests des labs à compléter échouent tant que les `TODO` ne sont pas écrits : c'est normal, et `make labs-test` sert justement à suivre leur avancement.
- [ ] **SDK Java Anthropic** : vérifier que `com.anthropic:anthropic-java` se résout depuis le poste (proxy Maven, miroir d'entreprise) avec `backend/mvnw -f labs/tests-ia/pom.xml dependency:resolve`. Le SDK lit `ANTHROPIC_API_KEY` dans l'environnement, comme le SDK Python.
- [ ] **Appel réel de contrôle**, une seule fois et avec la clé de test : la commande de fumée d'un lab sans `--offline` (par exemple `uv run neoagent --repo . --tache "Liste les fichiers de docs/" --journal /tmp/fumee.jsonl` dans `labs/agent/`), puis lire l'usage (`input_tokens`, `output_tokens`) dans le journal.
- [ ] **Cache transportable** (plan B réseau) : `~/.cache/uv`, `~/.m2/repository`, `~/Library/Caches/ms-playwright` (ou `~/.cache/ms-playwright`) et `docker save` des images, sur un disque partagé ou une clé USB.
- [ ] **Outils de sécurité du J2** : Semgrep (version 1.91 ou plus), Gitleaks, Trivy installés (ou leurs images Docker), et base Trivy à jour (`trivy fs --download-db-only` ou un premier `trivy fs backend`). Recompter les vulnérabilités Trivy (voir F3).
- [ ] Parcours complet sur le poste de référence : `make up`, connexion alice, création, soumission, validation bob, clôture admin, trace visible dans Jaeger ; `make e2e` vert ; `make regression-on`, `make e2e` rouge, `make regression-off`.

### Jour J1

- [ ] Rappeler les règles : clé personnelle, jamais dans un fichier versionné ni dans un prompt ; `"share": "disabled"` ; `--auto` proscrit hors sandbox ; données fictives uniquement.
- [ ] Faire relever `opencode stats` en fin de journée (baseline des coûts).

### Jour J3

- [ ] Vérifier sur chaque poste `uv --version`, `python3 --version` (ou `uv python list`) et `make labs-test` : les labs du jour sont rouges tant que les `TODO` ne sont pas écrits, mais aucun ne doit échouer pour une raison d'environnement (dépendance absente, interpréteur introuvable).
- [ ] Rappeler qu'OpenCode n'est plus la matière des TP : les stagiaires codent leurs outils. Les sorties du modèle restent des données, et chaque écriture de `neoagent` passe par une approbation humaine.
- [ ] Faire travailler en `--offline` d'abord (tests verts), puis passer aux appels réels sur la variante.

### Plan B : mode offline

Chaque outil codé à partir du J3 a un mode `--offline` : un modèle simulé, déterministe, qui renvoie des réponses préparées (sorties structurées, appels d'outils scénarisés). Il sert aux tests, à la préparation et de plan B quand l'API n'est pas utilisable.

| Situation | Ce qu'on fait |
|---|---|
| Panne réseau, proxy bloquant `api.anthropic.com`, incident de l'API | Les TP continuent en `--offline` : les `TODO` se codent et se testent sans modèle réel (`make labs-offline`). Les démonstrations formateur se rejouent en `--offline` |
| Plafond de dépense atteint sur une clé | Le stagiaire passe en `--offline` ; le formateur relève le plafond ou fournit la clé de secours |
| Démonstration J10 sans réseau | La démonstration se fait en `--offline`, avec les journaux de trajectoire enregistrés lors des exécutions réelles : la grille prévoit ce cas sans pénalité |
| J5 (RAG) sans réseau | Ollama et Qdrant sont locaux : l'indexation et la recherche fonctionnent si le modèle d'embeddings est déjà téléchargé ; seule la génération par Claude passe en `--offline` |
| J6 (MCP) sans réseau | Les serveurs MCP tournent en local (stdio) ; seul l'agent client passe en `--offline` |
| J7–J8 (Java) sans réseau | `--offline` dans les outils Java ; Maven en mode hors ligne (`-o`) grâce au cache `~/.m2` préparé |

Limites à dire aux stagiaires : le mode offline prouve que le code tient (boucle, garde-fous, validations, journal), pas la qualité des réponses du modèle ni les coûts réels. Pour les mesures du J10, utiliser les journaux des exécutions réelles, ou les journaux de référence des corrigés s'il n'y en a pas.

Pour garantir qu'aucun test ne consomme la clé : `env -u ANTHROPIC_API_KEY make labs-offline`. C'est ce que fait déjà la cible `labs-offline`.

---

## 6. Problèmes fréquents

| Symptôme | Cause probable | Solution |
|---|---|---|
| `make up` : le port 5432 est déjà utilisé | PostgreSQL local | `POSTGRES_PORT=5433` dans `.env` ; pour `make backend` : `DB_URL=jdbc:postgresql://localhost:5433/neoflow make backend` |
| Le port 8080 est déjà pris (par exemple par `gvproxy` de Podman ou un autre Tomcat) | autre service local | `cd backend && ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev-h2 -Dspring-boot.run.arguments=--server.port=18080`, puis `VITE_API_PROXY=http://localhost:18080 npm run dev` dans `frontend/` |
| Pas de Docker sur le poste | politique du poste | `make backend-h2` + `make frontend` ; les traces ne sont pas exportées, mais le `traceId` reste dans les logs |
| `./mvnw` : erreur de version de classe ou de release 21 | `JAVA_HOME` pointe vers un autre JDK | `export JAVA_HOME=$(/usr/libexec/java_home -v 21)` (macOS) ou chemin du JDK 21 |
| `npm ci` : `EACCES` sur `~/.npm` | cache npm créé par root | `sudo chown -R $(id -u):$(id -g) ~/.npm`, ou `npm_config_cache=/tmp/npm-cache npm ci` |
| `npx playwright install` bloqué par le proxy | réseau d'entreprise | Pré-installer, ou `HTTPS_PROXY=…` ; `PLAYWRIGHT_DOWNLOAD_HOST` pour un miroir interne |
| Fenêtre d'authentification native du navigateur | appel fait sans l'en-tête `X-Requested-With` | Passer par `api/client.ts` (qui l'ajoute) |
| Aucune trace dans Jaeger | profil `dev-h2` (export désactivé), ou Jaeger arrêté | `make infra`, puis lancer le backend avec `--management.otlp.tracing.endpoint=http://localhost:4318/v1/traces` |
| Avertissements périodiques « Failed to export spans » | profil `dev` sans Jaeger démarré | `make infra` ; sans effet sur l'application |
| Démarrage refusé : `Validate failed: Migrations have failed validation` (checksum) | V1 ou V2 modifiées après un premier démarrage PostgreSQL | Ne jamais modifier une migration appliquée : ajouter `V3__…`. En développement, repartir d'une base vide : `docker compose down -v` (supprime les volumes) |
| `Schema-validation: missing column` | entité modifiée sans migration | Ajouter la migration `V3__…` correspondante |
| Test qui échoue « au hasard » le vendredi après-midi | assertion sur `niveauValidation` sans horloge figée | Voir §3 : ne pas affirmer le niveau sans maîtriser l'horloge |
| `retirer-regression.sh` refuse de retirer le patch | fichiers modifiés depuis l'injection (correctif déjà fait) | Normal en fin de TP : le correctif du stagiaire remplace le retrait |
| OpenCode : erreurs 429 ou « credit balance » | limite de débit, ou plafond du workspace atteint | Espacer les exécutions parallèles (J4), relever le plafond du workspace ; `opencode stats` pour identifier les sessions coûteuses |
| OpenCode ne lit pas les Rules ou la config | mauvais dossier de lancement, ou erreur de syntaxe JSON | `opencode debug config` dans la racine du dépôt |
| `uv: command not found` ou `requires-python >=3.11` | uv absent, ou interpréteur trop ancien | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (ou `pipx install uv`), puis `uv python install 3.11` |
| `uv sync` échoue derrière le proxy | index PyPI inaccessible | `HTTPS_PROXY=…`, ou `UV_INDEX_URL` vers le miroir d'entreprise ; à défaut, cache `~/.cache/uv` pré-rempli et `uv sync --offline` |
| Lab Java : `Could not resolve com.anthropic:anthropic-java` | dépôt Maven inaccessible | Miroir dans `~/.m2/settings.xml`, ou cache `~/.m2` pré-rempli et `-o` |
| `AuthenticationError` ou 401 dans un lab | `ANTHROPIC_API_KEY` absente, mal exportée ou révoquée | `echo ${ANTHROPIC_API_KEY:+définie}` ; ré-exporter la clé dans le terminal du lab ; en attendant, `--offline` |
| 429 ou dépassement de plafond dans les labs | boucles d'agent trop longues, exécutions parallèles | Baisser `max_etapes` et `budget_tokens` de `neoagent`, utiliser `claude-haiku-5-5` pour les tâches légères, activer le cache de prompt ; plafond relevé par le formateur |
| Un test de lab appelle l'API réelle | mode offline non propagé jusqu'au client du modèle | Corriger le code du stagiaire (c'est un défaut) ; `env -u ANTHROPIC_API_KEY` le révèle immédiatement |
| `make labs-test` signale « aucun test » pour un lab | lab sans dossier `tests/` (lab d'infrastructure, ou pas encore livré) | Normal : la cible ignore les labs absents ou sans tests |
| Windows : `bad interpreter` sur `mvnw` ou les scripts | fins de ligne CRLF | `.gitattributes` force LF ; recloner après `git config core.autocrlf input` ; travailler sous WSL2 |
| Images lentes à construire en salle | caches Maven et npm vides | Pré-construire (`docker compose build`) la veille sur chaque poste |
