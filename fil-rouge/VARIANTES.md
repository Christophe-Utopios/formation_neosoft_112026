*Projet fil rouge — NSS+ Dev Full Stack assisté par IA · Neosoft*

# NeoFlow — Variantes métier

*Dix types de demandes, une variante par stagiaire, pour dix démonstrations distinctes*

✦

## Mode d'emploi

Chaque variante correspond à une valeur de `TypeDemande` du socle et à un **ticket brut** dans `docs/tickets/<TYPE>.md`. Le ticket est la demande telle que le métier l'a écrite : incomplète, parfois contradictoire, jamais chiffrée là où il le faudrait. Ce document est la **référence métier consolidée** après plusieurs ateliers avec le client fictif.

1. **En J3, lisez d'abord le ticket seul** et notez vos propres questions. Passez ensuite le ticket dans l'assistant de spécification que vous codez (`labs/spec/`), comparez ses ambiguïtés aux vôtres, puis tranchez vous-même.
2. **Ensuite seulement**, comparez votre liste avec la section de votre variante ci-dessous. Notez ce que vous aviez vu, ce que vous aviez manqué, ce que vous aviez tranché autrement.
3. Les **règles R1…Rn** sont validées par le métier : elles deviennent des exigences identifiées dans votre spécification.
4. Les **points à trancher** sont volontairement ouverts. Vous les tranchez, et chaque décision structurante fait l'objet d'un **ADR** dans `docs/adr/`. Il n'y a pas de bonne réponse unique : il y a des décisions argumentées, cohérentes et testées.
5. Les **données d'exemple** sont fictives. Elles servent de jeux de test et de données de démonstration (migration Flyway dédiée). Date de référence des exemples : **lundi 16 novembre 2026** ; en test, fixez l'horloge plutôt que de dépendre de la date du jour.
6. **Du J3 au J10, vous travaillez avec les outils que vous codez**, pas avec un assistant du marché : assistant de spécification (J3), agent `neoagent` (J4) avec ses outils RAG (J5) et MCP (J6), générateur de tests et assistant de diagnostic (J7), outil d'analyse legacy (J8), workflow (J9), évaluations (J10). OpenCode reste réservé aux J1–J2.
7. **L'extension proposée pour le vibe coding du J10** est produite par votre agent `neoagent` : d'abord en `--mode vibe` (sans spécification ni vérificateur, en temps limité), puis reprise en `--mode structure` (spécification du J3, pattern Generator–Verifier, tests E2E, contrôles de sécurité). Les deux versions sont mesurées par `labs/evals/`.

> Une règle qui n'est pas testée n'existe pas. Une ambiguïté qui n'est pas tracée reviendra en recette.

### Brancher une variante sur le socle

| Besoin | Mécanisme du socle | Votre travail |
|---|---|---|
| Données propres à la variante | Flyway (`db/migration`, V1 et V2 fournies) | `V3__<variante>.sql` puis suivantes, SQL compatible PostgreSQL et H2 en mode PostgreSQL |
| Règles bloquantes | Bean `RegleMetierDemande { TypeDemande type(); List<String> verifier(Demande d); }` | Une ou plusieurs classes dont `type()` renvoie votre type ; chaque message renvoyé produit une erreur 422 (propriété `erreurs`) |
| Moment des contrôles | `RegleMetierRegistry`, appelé à la création, à la modification et à la soumission | À la soumission, la demande est déjà au statut `SOUMISE` avec son `niveauValidation` calculé, non encore enregistrée : une règle peut distinguer brouillon et soumission |
| Niveau de validation | `CircuitValidationService` → `RegleValidationLegacy` | Ne pas recalculer le niveau ailleurs ; décider ce que vous transmettez au circuit (montant, département) |
| API | Routes `/api/demandes` du socle | Extension des DTO ou sous-ressource (`/api/demandes/{id}/...`) : à décider en ADR, sans casser l'existant |
| Interface | Pages liste, formulaire, détail | Champs, contrôles et affichages de votre variante |
| Circuit | Un seul valideur (`bob`) quel que soit le niveau | Toute évolution du circuit (étapes, statuts) est une décision d'architecture : ADR obligatoire |

Contraintes communes : pas de modification du module legacy avant le J8 ; les tests du socle restent verts ; toute modification de `StatutDemande` ou des transitions est justifiée par un ADR, car elle touche toutes les variantes.

### Utilisateurs et collaborateurs disponibles

| Login | Rôle applicatif | Département | Date d'entrée |
|---|---|---|---|
| `alice` | DEMANDEUR | COMMERCIAL | 2021-03-15 |
| `bob` | VALIDEUR | FINANCE | 2018-09-01 |
| `admin` | ADMIN | DSI | 2016-01-04 |
| `chloe` | (collaborateur seulement) | DSI | 2025-06-02 |
| `karim` | (collaborateur seulement) | RH | 2023-11-20 |
| `claire` | (collaborateur seulement) | DSI | 2026-07-01 |
| `david` | (collaborateur seulement) | RH | 2019-02-18 |
| `emma` | (collaborateur seulement) | MARKETING | 2026-10-05 |
| `farid` | (collaborateur seulement) | ACHATS | 2023-05-15 |

Seule `alice` peut créer des demandes. Si votre variante a besoin d'un autre demandeur ou d'un nouveau rôle (second valideur, service exécutant), ajoutez-le dans la configuration de sécurité et documentez-le.

## Tableau récapitulatif

| N° | Variante | `TypeDemande` | Ticket | Difficulté | Tables à ajouter | Règles | Legacy mobilisé | Extension J10 |
|---|---|---|---|---|---|---|---|---|
| 1 | Congés | `CONGES` | NF-401 | ★★ | 3 | 10 | `determinerNiveau`, `joursOuvres` | Calendrier d'équipe |
| 2 | Notes de frais | `NOTE_DE_FRAIS` | NF-402 | ★★★ | 2 + fichiers | 9 | `calculer`, `determinerNiveau`, `formatMontant` | Export comptable |
| 3 | Matériel informatique | `MATERIEL_IT` | NF-403 | ★ | 3 | 7 | `determinerNiveau`, `formatMontant` | Tableau de bord budgétaire |
| 4 | Réservation de salle | `RESERVATION_SALLE` | NF-404 | ★★ | 2 | 8 | `determinerNiveau`, `formatDate` | Planning du site |
| 5 | Formation | `FORMATION` | NF-405 | ★★ | 2 | 9 | `determinerNiveau` | Plan de formation |
| 6 | Accès applicatif | `ACCES_APPLICATIF` | NF-406 | ★★★ | 3 | 10 | `determinerNiveau` | Revue des habilitations |
| 7 | Déplacement | `DEPLACEMENT` | NF-407 | ★★ | 2 | 8 | `calculer`, `determinerNiveau` | Note de frais pré-remplie |
| 8 | Achat | `ACHAT` | NF-408 | ★ | 2 | 7 | `determinerNiveau` | Tableau de bord fournisseurs |
| 9 | Incident | `INCIDENT` | NF-409 | ★★★ | 2 | 9 | `determinerNiveau`, `formatDate` | Tableau de bord SLA |
| 10 | Onboarding | `ONBOARDING` | NF-410 | ★★ | 3 | 9 | `determinerNiveau`, `joursOuvres` | Kanban des tâches |

| Difficulté | Charge estimée | Profil conseillé |
|---|---|---|
| ★ | Implémentation confortable en J4 avec `neoagent`, temps disponible pour approfondir les patterns et les garde-fous de l'agent | Première expérience de développement d'un agent, ou envie d'approfondir les garde-fous |
| ★★ | J4 complète, quelques finitions en J7 | Développeur à l'aise sur Spring et React |
| ★★★ | J4 complète et reprise en J7 ; au moins une décision d'architecture lourde | Développeur expérimenté, à l'aise avec la modélisation |

✦

## 1. Congés — `CONGES`

| | |
|---|---|
| **Difficulté** | ★★ |
| **Charge estimée** | 3 tables, 10 règles, formulaire enrichi (sous-type, demi-journées, décompte affiché) |
| **Ticket** | `docs/tickets/CONGES.md` (NF-401) |

**Pitch** — Permettre à chaque collaborateur de poser ses congés payés, RTT et congés sans solde dans NeoFlow, avec contrôle du solde, des chevauchements et du préavis, à la place du couple mail et tableur actuel.

**Acteurs** — Le collaborateur (`alice`) dépose la demande ; le manager (`bob`) valide ou refuse ; l'administration du personnel (`admin`) clôture la demande quand les congés sont intégrés en paie.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Le sous-type est obligatoire : `CP`, `RTT` ou `SANS_SOLDE`. |
| R2 | `dateDebut` et `dateFin` sont obligatoires, avec `dateFin ≥ dateDebut`. |
| R3 | Demi-journées : le premier jour peut commencer l'après-midi, le dernier jour peut finir à midi. Le décompte se fait par pas de 0,5 jour. |
| R4 | Le décompte se fait en jours ouvrés : samedis, dimanches et jours fériés (table de référence) ne sont pas décomptés. Une demande sans aucun jour ouvré est rejetée. |
| R5 | Une demande ne peut pas dépasser 20 jours ouvrés. |
| R6 | Solde : pour `CP` et `RTT`, jours demandés ≤ solde disponible = acquis − pris − en cours (demandes `SOUMISE` et `VALIDEE` non clôturées du même sous-type). Période de référence : du 1er juin au 31 mai pour les CP, année civile pour les RTT. |
| R7 | Chevauchement : rejet si une autre demande `CONGES` du même demandeur, au statut `SOUMISE`, `VALIDEE` ou `CLOTUREE`, partage au moins une demi-journée avec la demande. |
| R8 | Préavis : au-delà de 5 jours ouvrés, `dateDebut ≥ date du jour + 14 jours calendaires` ; sinon `dateDebut ≥ date du jour + 2 jours ouvrés`. Une demande `urgent` déroge au préavis, pas au solde. |
| R9 | `SANS_SOLDE` : aucun contrôle de solde, mais un motif (description) d'au moins 20 caractères est obligatoire. |
| R10 | Refus d'une demande : les jours « en cours » sont libérés immédiatement. |

### Points à trancher

- Moment où le solde est débité : à la validation par le manager, ou à la clôture après intégration en paie ?
- Les brouillons comptent-ils dans le contrôle de chevauchement ?
- Jours fériés : liste nationale unique ou par site (l'agence de La Réunion a un jour férié local le 20 décembre) ?
- Nouveaux arrivants : acquisition des CP au prorata des mois travaillés ? Quel solde pour `emma` ?
- Origine des soldes : migration initiale, import depuis la paie (hors périmètre), écran d'administration ?
- Décompte côté front et côté back : comment garantir qu'ils donnent le même résultat ?
- Exigence « simple et rapide » : à traduire en critères mesurables (nombre d'étapes, temps de réponse du calcul de décompte).

### Données d'exemple

Soldes (période en cours) :

| Login | Sous-type | Période | Acquis | Pris |
|---|---|---|---|---|
| `alice` | CP | 2026-06-01 → 2027-05-31 | 25 | 7 |
| `alice` | RTT | 2026 | 10 | 4 |

Demande existante : `alice`, CP du 2026-12-28 au 2026-12-30, statut `SOUMISE` (3 jours en cours). Solde CP disponible : 25 − 7 − 3 = 15. Solde RTT disponible : 6.

Jours fériés à charger : 2026-11-11, 2026-12-25, 2027-01-01, 2027-03-29, 2027-05-01, 2027-05-08 ; pour La Réunion, 2026-12-20.

| Cas | Demande d'`alice` (créée le 2026-11-16) | Résultat attendu |
|---|---|---|
| C1 | CP du 2026-12-21 au 2026-12-24 | Acceptée : 4 jours ouvrés |
| C2 | CP du 2026-12-21 au 2026-12-31 | 422 : chevauchement avec la demande du 28 au 30 décembre |
| C3 | RTT du 2026-12-07 au 2026-12-16 | 422 : 8 jours demandés pour un solde disponible de 6 |
| C4 | CP du 2026-11-23 au 2026-12-04 | 422 : 10 jours ouvrés, préavis de 14 jours non respecté |
| C5 | Même demande que C4 avec `urgent = true` | Acceptée : 10 jours ≤ 15 disponibles |
| C6 | CP du 2026-12-17 (après-midi) au 2026-12-18 | Acceptée : 1,5 jour |
| C7 | CP du 2026-12-19 au 2026-12-20 | 422 : aucun jour ouvré |
| C8 | SANS_SOLDE du 2027-02-01 au 2027-02-05, sans description | 422 : motif obligatoire |
| C9 | CP du 2027-01-04 au 2027-02-01 | 422 : 21 jours ouvrés, maximum 20 |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `conges_detail` | `demande_id` (PK, FK `demande`), `sous_type`, `demi_journee_debut`, `demi_journee_fin`, `nb_jours_ouvres` NUMERIC(4,1) |
| `solde_conges` | `login`, `sous_type`, `periode_debut`, `periode_fin`, `acquis` NUMERIC(4,1), `pris` NUMERIC(4,1) |
| `jour_ferie` | `date_ferie`, `zone` (FR, REUNION…), `libelle` |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : pour `CONGES`, le niveau dépend de l'ancienneté du demandeur et de l'urgence. L'ancienneté provient de `collaborateur.date_entree`. Le circuit reste la seule source du niveau : ne le recalculez pas dans vos règles.
- `NeoUtils.joursOuvres` (front) : candidat naturel pour afficher le décompte pendant la saisie. Comportement à caractériser avant de s'y fier, puis à confronter à R3 et R4.
- `NeoUtils.formatDate` : affichage des périodes.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Calendrier d'équipe : vue mensuelle des absences du département, avec mise en évidence des jours où plus de deux personnes sont absentes.

✦

## 2. Notes de frais — `NOTE_DE_FRAIS`

| | |
|---|---|
| **Difficulté** | ★★★ |
| **Charge estimée** | 2 tables et un stockage de fichiers, 9 règles, saisie de lignes multiples, dépôt de justificatifs |
| **Ticket** | `docs/tickets/NOTE_DE_FRAIS.md` (NF-402) |

**Pitch** — Dématérialiser les notes de frais : une note regroupe plusieurs dépenses, chacune plafonnée selon le barème historique de l'entreprise, avec justificatifs.

**Acteurs** — Le collaborateur (`alice`) saisit la note ; le valideur (`bob`) contrôle ; la comptabilité (`admin`) clôture la note à la mise en paiement.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Une note contient de 1 à 30 lignes. Chaque ligne : date de dépense, catégorie (`REPAS`, `HOTEL`, `TRANSPORT`, `KILOMETRIQUE`, `AUTRE`), montant TTC déclaré en euros, indicateur « étranger », nombre de nuits (`HOTEL`, au moins 1), nombre de kilomètres (`KILOMETRIQUE`, à la place du montant), commentaire. |
| R2 | Le montant remboursable de chaque ligne est calculé par `CalculRemboursementLegacy.calculer(categorie, montant, nbNuits, etranger)`. Pour `KILOMETRIQUE`, la valeur transmise est le nombre de kilomètres. |
| R3 | Le `montant` de la demande est le total remboursable des lignes ; le total déclaré est conservé et affiché à côté. |
| R4 | Justificatif obligatoire pour toute ligne dont le montant déclaré dépasse 15,00 € (hors `KILOMETRIQUE`) : PDF, JPEG ou PNG, 5 Mo au plus, un fichier par ligne. |
| R5 | La date de dépense est antérieure ou égale à la date de soumission et postérieure ou égale à cette date moins 90 jours calendaires. |
| R6 | Doublon : une même dépense (même date, même catégorie, même montant déclaré) ne peut figurer sur deux notes non refusées du même demandeur. |
| R7 | Soumission impossible si la note n'a aucune ligne ou si son total remboursable est nul. |
| R8 | `dateDebut` et `dateFin` de la demande sont calculées : date de la première et de la dernière dépense. |
| R9 | Une note refusée reste consultable ; ses lignes ne sont pas modifiables. |

### Points à trancher

- Petites dépenses sans justificatif : seuil unique ou liste de catégories (parking, péage) ?
- Exactitude au centime demandée par la comptabilité, alors que le barème existant « ne doit pas être touché » : que faire si le calcul existant ne donne pas le montant attendu par le barème ? (caractériser d'abord ; toute correction dans un commit séparé, avec ADR et accord du métier)
- Dépenses en devise (CHF, GBP) : conversion, source et date du taux ?
- Montant transmis au circuit de validation : total déclaré ou total remboursable ?
- Justificatifs : stockage (base, disque, stockage objet), durée de conservation, droits de consultation.
- Duplication d'une note refusée en nouveau brouillon : utile ou source de doublons ?
- Exigence « ergonomique, utilisable sur mobile » : à traduire en critères mesurables.

### Données d'exemple

Barème communiqué par le contrôle de gestion (millésime 2023) :

| Catégorie | Plafond | Particularité |
|---|---|---|
| `REPAS` | 25,50 € par repas | +10 % à l'étranger |
| `HOTEL` | 110,00 € par nuit | plafond ×1,3 à l'étranger |
| `TRANSPORT` | aucun | +10 % à l'étranger |
| `KILOMETRIQUE` | 0,636 € par km (barème 5 CV) | |
| `AUTRE` | 50,00 € | +10 % à l'étranger |

Note d'`alice` (mission Paris puis Genève), soumise le 2026-11-16 :

| Ligne | Date | Catégorie | Déclaré | Détail | Attendu métier (barème) |
|---|---|---|---|---|---|
| L1 | 2026-10-12 | REPAS | 32,80 € | déjeuner client, Lyon | 25,50 € |
| L2 | 2026-10-12 | TRANSPORT | 89,00 € | train Lyon–Paris | 89,00 € |
| L3 | 2026-10-13 | HOTEL | 260,00 € | 2 nuits, Paris | 220,00 € |
| L4 | 2026-10-20 | HOTEL | 150,00 € | 1 nuit, Genève (étranger) | 143,00 € |
| L5 | 2026-10-21 | REPAS | 20,00 € | Genève (étranger) | 22,00 € |
| L6 | 2026-10-27 | KILOMETRIQUE | 120 km | visite de l'agence de Villefranche | 76,32 € |
| L7 | 2026-10-28 | AUTRE | 12,00 € | parking, sans justificatif | 12,00 € |
| | | | | **Total attendu** | **587,82 €** |

> La colonne « Attendu métier » est le barème tel que la comptabilité le comprend. Confrontez-la au calcul réel du code existant par des tests de caractérisation avant d'écrire la moindre assertion.

| Cas | Situation | Résultat attendu |
|---|---|---|
| E1 | Ligne REPAS du 2026-07-10 dans une note soumise le 2026-11-16 | 422 : dépense de plus de 90 jours |
| E2 | Ligne L2 sans justificatif | 422 : justificatif obligatoire au-delà de 15 € |
| E3 | Ligne L1 saisie à nouveau sur une autre note `SOUMISE` | 422 : doublon |
| E4 | Note soumise sans aucune ligne | 422 |
| E5 | Justificatif de 8 Mo | 422 : taille maximale 5 Mo |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `ligne_frais` | `id`, `demande_id` (FK), `date_depense`, `categorie`, `montant_declare` NUMERIC(10,2), `nb_nuits`, `nb_km`, `etranger`, `montant_rembourse` NUMERIC(10,2), `justificatif_id` |
| `justificatif` | `id`, `nom_fichier`, `type_mime`, `taille_octets`, `empreinte_sha256`, emplacement ou contenu (à trancher), `depose_par`, `depose_le` |

### Interactions avec le legacy

- `CalculRemboursementLegacy.calculer` : cœur de la variante. Barème à préserver tel quel ; comportement à caractériser avant tout usage dans vos assertions et avant tout refactoring. Une correction éventuelle se fait dans un commit séparé, justifiée par un ADR.
- `RegleValidationLegacy.determinerNiveau` : pour `NOTE_DE_FRAIS`, le niveau dépend du montant transmis et de l'ancienneté du demandeur.
- `NeoUtils.formatMontant` : affichage des montants.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Export CSV comptable des notes clôturées (une ligne par dépense : catégorie, montant déclaré, montant remboursé, code collaborateur) et synthèse mensuelle par catégorie.

✦

## 3. Matériel informatique — `MATERIEL_IT`

| | |
|---|---|
| **Difficulté** | ★ |
| **Charge estimée** | 3 tables, 7 règles, sélection d'articles dans le formulaire |
| **Ticket** | `docs/tickets/MATERIEL_IT.md` (NF-403) |

**Pitch** — Commander du matériel depuis un catalogue tenu par la DSI, dans la limite du budget annuel de chaque département.

**Acteurs** — Le collaborateur (`alice`) commande ; le valideur (`bob`) arbitre ; la DSI (`admin`) clôture à la livraison.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Une demande contient de 1 à 5 lignes : référence du catalogue et quantité (au moins 1). |
| R2 | Quantité maximale : 2 par référence, sauf pour le département DSI. |
| R3 | Seuls les articles actifs du catalogue sont commandables. |
| R4 | Le `montant` est calculé par le serveur : somme des prix unitaires HT × quantités. Le prix unitaire est figé dans la ligne. |
| R5 | Budget : le cumul des demandes `MATERIEL_IT` du département sur l'année civile, augmenté de la nouvelle demande, ne dépasse pas le budget annuel du département. |
| R6 | Un seul ordinateur portable (catégorie `PORTABLE`) par collaborateur : rejet si une demande contenant un portable est `SOUMISE` ou `VALIDEE`, ou si le dernier portable livré (`CLOTUREE`) date de moins de 36 mois. |
| R7 | Le délai de livraison estimé affiché est le plus long délai des articles demandés. |

### Points à trancher

- Le budget est-il consommé à la soumission ou à la validation ? Les interlocuteurs du ticket ne disent pas la même chose.
- « Équipe » : le département du socle, ou une notion plus fine ?
- Département DSI : hors budget, ou budget propre ?
- Variation trimestrielle des prix : prix figé à la création, à la soumission ou à la validation ?
- Qui peut imputer une demande sur le budget d'un autre département (champ `departement` de la requête) ?
- Exigence « catalogue rapide » : volume visé, temps de réponse cible.

### Données d'exemple

Catalogue :

| Référence | Libellé | Catégorie | Prix HT | Délai | Actif |
|---|---|---|---|---|---|
| `PC-STD-14` | Portable standard 14 pouces | PORTABLE | 1 150,00 € | 10 j | oui |
| `PC-DEV-16` | Portable développeur 16 pouces, 32 Go | PORTABLE | 1 890,00 € | 15 j | oui |
| `ECR-27` | Écran 27 pouces QHD | ECRAN | 329,00 € | 5 j | oui |
| `DOCK-USBC` | Station d'accueil USB-C | ACCESSOIRE | 189,00 € | 5 j | oui |
| `CASQ-BT` | Casque Bluetooth à réduction de bruit | ACCESSOIRE | 149,00 € | 3 j | oui |
| `TEL-PRO` | Smartphone professionnel | TELEPHONE | 549,00 € | 7 j | non |

Budgets 2026 :

| Département | Budget annuel | Déjà consommé |
|---|---|---|
| COMMERCIAL | 12 000 € | 11 300 € |
| MARKETING | 8 000 € | 2 150 € |
| FINANCE | 6 000 € | 1 890 € |
| RH | 5 000 € | 0 € |
| ACHATS | 5 000 € | 1 150 € |
| DSI | 40 000 € | 18 400 € |

| Cas | Demande d'`alice` (COMMERCIAL) | Résultat attendu |
|---|---|---|
| M1 | 1 × `ECR-27` + 1 × `DOCK-USBC` | Acceptée : 518 €, cumul 11 818 € |
| M2 | 2 × `ECR-27` + 1 × `DOCK-USBC` | 422 : 847 €, cumul 12 147 € > 12 000 € |
| M3 | 3 × `CASQ-BT` | 422 : quantité maximale 2 |
| M4 | 1 × `TEL-PRO` | 422 : article inactif |
| M5 | 1 × `PC-DEV-16` alors qu'une demande avec `PC-STD-14` est `SOUMISE` | 422 : un seul portable |
| M6 | 1 × `PC-DEV-16` + 1 × `ECR-27` avec `departement = "DSI"` dans la requête | À trancher (imputation sur un autre département) |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `article_catalogue` | `reference` (PK), `libelle`, `categorie`, `prix_ht` NUMERIC(10,2), `delai_jours`, `actif` |
| `ligne_materiel` | `id`, `demande_id` (FK), `reference` (FK), `quantite`, `prix_unitaire_fige` NUMERIC(10,2) |
| `budget_departement` | `departement`, `annee`, `montant` NUMERIC(12,2) |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : pour `MATERIEL_IT`, le niveau dépend du département et du montant. Caractériser le niveau obtenu pour un demandeur DSI et non DSI avant tout refactoring.
- `NeoUtils.formatMontant` : affichage des prix et du budget restant.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Tableau de bord budgétaire par département : consommé, engagé, restant, projection de fin d'année.

✦

## 4. Réservation de salle — `RESERVATION_SALLE`

| | |
|---|---|
| **Difficulté** | ★★ |
| **Charge estimée** | 2 tables, 8 règles, sélection de créneau, gestion des intervalles |
| **Ticket** | `docs/tickets/RESERVATION_SALLE.md` (NF-404) |

**Pitch** — Remplacer le fichier partagé de réservation des salles de réunion par une réservation contrôlée : créneau, capacité, équipements, conflits.

**Acteurs** — L'organisateur (`alice`) réserve ; les services généraux (`bob`) valident ; `admin` clôture après la réunion.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Une réservation porte sur une salle, une date (`dateDebut = dateFin`), une heure de début et une heure de fin, par pas de 30 minutes, entre 08:00 et 20:00, heure locale du site. |
| R2 | Durée comprise entre 30 minutes et 4 heures. |
| R3 | Nombre de participants compris entre 2 et la capacité de la salle. |
| R4 | Conflit : rejet si une réservation `SOUMISE` ou `VALIDEE` de la même salle chevauche le créneau. Les intervalles sont semi-ouverts : 09:00–10:00 et 10:00–11:00 ne se chevauchent pas. |
| R5 | Pas de réservation dans le passé, ni à plus de 60 jours. |
| R6 | Les équipements demandés (écran, visio, micro) doivent être présents dans la salle. |
| R7 | Les salles de catégorie `PRESTIGE` sont toujours validées par les services généraux. |
| R8 | Récurrence hebdomadaire possible, 8 occurrences au plus. |

### Points à trancher

- Validation systématique, ou confirmation immédiate pour les petites salles ? Le ticket affirme les deux.
- Fuseau horaire : sites de métropole et agence de La Réunion. Heure stockée en local ou en UTC ? Affichage pour un collaborateur d'un autre site ?
- Un brouillon bloque-t-il un créneau ?
- Annulation d'une réservation validée : le circuit du socle ne prévoit pas d'annulation. Nouvelle transition (impact sur tout le socle) ou autre mécanisme ?
- Récurrence : une demande par occurrence ou une demande parent ? Une occurrence en conflit bloque-t-elle la série ?
- Exigence « clair et instantané » : à traduire en critères mesurables.

### Données d'exemple

| Code | Nom | Site | Capacité | Équipements | Catégorie |
|---|---|---|---|---|---|
| `LYO-A` | Fourvière | Lyon (siège) | 8 | écran, visio | STANDARD |
| `LYO-B` | Croix-Rousse | Lyon (siège) | 4 | écran | STANDARD |
| `LYO-C` | Confluence | Lyon (siège) | 20 | écran, visio, micro | PRESTIGE |
| `PAR-A` | Montmartre | Paris | 12 | visio | STANDARD |
| `RUN-A` | Le Barachois | Saint-Denis (La Réunion) | 6 | écran, visio | STANDARD |

Réservation existante : `LYO-A`, mardi 2026-11-24 de 09:00 à 10:00, organisateur `david`, statut `VALIDEE`.

| Cas | Demande d'`alice` (créée le 2026-11-16) | Résultat attendu |
|---|---|---|
| S1 | `LYO-A`, 2026-11-24, 10:00–11:30, 6 participants, visio | Acceptée |
| S2 | `LYO-A`, 2026-11-24, 09:30–10:30 | 422 : conflit |
| S3 | `LYO-B`, 2026-11-25, 14:00–15:00, 6 participants | 422 : capacité 4 |
| S4 | `LYO-B`, 2026-11-25, 07:30–08:30 | 422 : hors plage horaire |
| S5 | `PAR-A`, 2027-02-01, 10:00–11:00 | 422 : au-delà de 60 jours |
| S6 | `LYO-C`, 2026-11-26, 14:00–18:30 | 422 : plus de 4 heures |
| S7 | `LYO-B`, 2026-11-27, 11:15–12:00 | 422 : pas de 30 minutes non respecté |
| S8 | `LYO-B`, 2026-11-25, 10:00–11:00, 3 participants, visio | 422 : équipement absent |
| S9 | `RUN-A`, 2026-11-24, 09:00–10:00 heure de La Réunion | Acceptée ; affichage pour Lyon à trancher |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `salle` | `code` (PK), `nom`, `site`, `fuseau`, `capacite`, `equipements`, `categorie`, `active` |
| `reservation_salle` | `demande_id` (PK, FK), `salle_code` (FK), `heure_debut`, `heure_fin`, `nb_participants`, `equipements_requis`, `serie_id` (nullable) |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : aucun traitement dédié à ce type ; le niveau par défaut est modulé par l'urgence, et la demande n'a pas de montant. Caractériser le niveau obtenu avant de décider si une confirmation automatique peut s'appuyer dessus.
- `NeoUtils.formatDate` : affichage des dates (les heures sont à votre charge).

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Planning journalier d'un site : grille horaire des salles, avec proposition du créneau libre le plus proche pour une capacité donnée.

✦

## 5. Formation — `FORMATION`

| | |
|---|---|
| **Difficulté** | ★★ |
| **Charge estimée** | 2 tables, 9 règles, choix d'une session ou saisie hors catalogue |
| **Ticket** | `docs/tickets/FORMATION.md` (NF-405) |

**Pitch** — Gérer les demandes d'inscription aux formations externes, dans la limite d'un budget individuel annuel, avec quotas, places limitées et prérequis.

**Acteurs** — Le collaborateur (`alice`) demande ; le manager (`bob`) valide ; le service formation (`admin`) clôture après la présence effective.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Une demande porte soit sur une session du catalogue (code), soit sur une formation hors catalogue (organisme, intitulé, dates, coût HT, référence de devis obligatoire). |
| R2 | Le `montant` est le coût HT ; le TTC (TVA 20 %) est affiché à titre indicatif. |
| R3 | Budget individuel : le cumul HT des demandes `FORMATION` `SOUMISE`, `VALIDEE` et `CLOTUREE` de l'année, augmenté de la nouvelle demande, ne dépasse pas 2 500 € HT. |
| R4 | Quota : au plus 3 formations par collaborateur et par an (mêmes statuts). |
| R5 | Places : rejet si le nombre de demandes `VALIDEE` sur la session atteint son nombre de places. |
| R6 | Prérequis : rejet si la session exige une formation préalable que le demandeur n'a pas suivie (demande `CLOTUREE` sur la session prérequise). |
| R7 | Délai : inscription au moins 21 jours calendaires avant le début de la session. |
| R8 | Hors catalogue au-delà de 1 500 € HT : ancienneté minimale de 6 mois. |
| R9 | Pour une session du catalogue, `dateDebut` et `dateFin` sont copiées depuis la session. |

### Points à trancher

- Délai de 21 jours contre inscription possible jusqu'à la veille pour les sessions catalogue : le ticket dit les deux.
- « Par an » : année civile de la demande, de la session, ou exercice budgétaire ?
- HT ou TTC : les échanges avec les organismes se font en TTC, le budget est exprimé en HT.
- Tolérance de dépassement du budget (par exemple 5 %) ?
- Places réservées dès la soumission ou seulement à la validation ?
- Formation interne gratuite : compte-t-elle dans le quota ?
- Exigence « parcours fluide » : à traduire en critères mesurables.

### Données d'exemple

| Code | Intitulé | Organisme | Dates | Coût HT | Places | Prérequis |
|---|---|---|---|---|---|---|
| `K8S-F` | Kubernetes fondamentaux | Orsalys Formation | 2027-01-11 → 2027-01-13 | 1 650,00 € | 8 | — |
| `K8S-A` | Kubernetes avancé | Orsalys Formation | 2027-03-08 → 2027-03-10 | 1 950,00 € | 6 | `K8S-F` |
| `PO-CERT` | Product Owner certifiant | Talvane | 2027-02-01 → 2027-02-02 | 1 200,00 € | 12 | — |
| `ANG-B2` | Anglais professionnel B2 (20 h) | Linguarium | 2027-01-05 → 2027-03-30 | 890,00 € | 10 | — |
| `SEC-WEB` | Sécurité des applications web | Orsalys Formation | 2026-11-30 → 2026-12-02 | 1 400,00 € | 8 | — |

| Cas | Demande (créée le 2026-11-16) | Résultat attendu |
|---|---|---|
| FO1 | `alice`, `K8S-F` | Acceptée : 1 650 € |
| FO2 | `alice`, `K8S-A` sans avoir suivi `K8S-F` | 422 : prérequis |
| FO3 | `alice`, `ANG-B2` après FO1 | 422 : 2 540 € > 2 500 € (tolérance à trancher) |
| FO4 | `alice`, `SEC-WEB` | 422 : la session commence dans 14 jours |
| FO5 | `alice`, `PO-CERT` alors que 12 demandes sont `VALIDEE` | 422 : session complète |
| FO6 | `alice`, hors catalogue « Architecture cloud », 2 100 € HT, devis `DV-2026-118` | Acceptée (ancienneté suffisante) |
| FO7 | `emma` (entrée 2026-10-05, si vous l'ajoutez comme demandeur), hors catalogue, 1 800 € HT | 422 : ancienneté inférieure à 6 mois |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `session_formation` | `code` (PK), `intitule`, `organisme`, `date_debut`, `date_fin`, `cout_ht` NUMERIC(10,2), `nb_places`, `prerequis_code` (FK, nullable) |
| `inscription_formation` | `demande_id` (PK, FK), `session_code` (nullable), `hors_catalogue`, `organisme`, `intitule`, `reference_devis` |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : pour `FORMATION`, le niveau dépend du montant transmis, auquel le code existant applique lui-même une TVA. Décider si vous transmettez le HT ou le TTC, et caractériser le comportement autour du seuil avant tout refactoring.
- `NeoUtils.formatMontant` : affichage HT et TTC.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Plan de formation annuel du département (export CSV) et suggestion de la prochaine formation d'un collaborateur selon les prérequis.

✦

## 6. Accès applicatif — `ACCES_APPLICATIF`

| | |
|---|---|
| **Difficulté** | ★★★ |
| **Charge estimée** | 3 tables, 10 règles, évolution du circuit de validation (deux étapes), nouveau rôle |
| **Ticket** | `docs/tickets/ACCES_APPLICATIF.md` (NF-406) |

**Pitch** — Faire passer toutes les demandes d'habilitation aux applications internes par NeoFlow, avec une double validation pour les droits d'administration et une traçabilité exploitable en audit.

**Acteurs** — Le demandeur (`alice`), pour lui-même ou pour un collègue ; le manager (`bob`) ; un second valideur (rôle `SECURITE` à créer, avec un utilisateur de démonstration) ; `admin` clôture quand les droits sont effectivement ouverts.

### Règles métier

| Id | Règle |
|---|---|
| R1 | La demande cible une application du référentiel et un profil : `LECTURE`, `CONTRIBUTEUR` ou `ADMIN`. |
| R2 | Le bénéficiaire est le demandeur ou un autre collaborateur existant (`collaborateur.login`). |
| R3 | Profil `ADMIN` : deux validations successives, le manager puis le second valideur. La demande ne passe `VALIDEE` qu'après la seconde. |
| R4 | Les deux valideurs sont distincts ; aucun valideur ne peut être le demandeur ni le bénéficiaire. |
| R5 | Profil `ADMIN` : `dateFin` obligatoire, au plus 90 jours après `dateDebut`. |
| R6 | Profils `LECTURE` et `CONTRIBUTEUR` : `dateFin` facultative. |
| R7 | Séparation des tâches : un même bénéficiaire ne peut pas détenir `CONTRIBUTEUR` ou `ADMIN` à la fois sur `COMPTA` et sur `PAIE` (accès `VALIDEE` ou `CLOTUREE` non expirés, ou demande `SOUMISE`). |
| R8 | Pas de doublon : rejet si un accès identique (application, profil, bénéficiaire) est `SOUMISE`, ou `VALIDEE`/`CLOTUREE` et non expiré. |
| R9 | Justification (description) d'au moins 30 caractères pour un profil `ADMIN` ou une application de sensibilité élevée. |
| R10 | Chaque validation intermédiaire produit un événement d'audit (auteur, horodatage, étape). |

### Points à trancher

- Tous les accès limités dans le temps, ou accès en lecture permanents ? Le ticket affirme les deux.
- Qui est le second valideur : le propriétaire de l'application (département propriétaire) ou la sécurité ?
- Modélisation de la double validation : nouveau statut (impact sur `StatutDemande`, les transitions et les tests du socle) ou étapes dans une table dédiée, la demande restant `SOUMISE` jusqu'à la seconde validation ?
- Le niveau calculé par le circuit existant et la règle de double validation peuvent diverger : lequel fait foi ? Le département pris en compte est-il celui du demandeur ou du bénéficiaire ?
- Expiration : qui retire les droits, et comment NeoFlow en est-il informé ?
- Exigence « sécurisé et conforme » : à traduire en exigences vérifiables (journalisation, conservation, consultation de l'historique).

### Données d'exemple

Référentiel des applications :

| Code | Application | Département propriétaire | Sensibilité |
|---|---|---|---|
| `CRM` | Velmora CRM | COMMERCIAL | normale |
| `GED` | Gestion documentaire | DSI | normale |
| `BI` | Décisionnel | DSI | normale |
| `COMPTA` | Comptabilité générale | FINANCE | élevée |
| `PAIE` | Paie et temps | RH | élevée |

Accès existants :

| Bénéficiaire | Application | Profil | Statut | Fin |
|---|---|---|---|---|
| `farid` | PAIE | CONTRIBUTEUR | CLOTUREE | — |
| `david` | GED | ADMIN | CLOTUREE | 2026-12-31 |

| Cas | Situation | Résultat attendu |
|---|---|---|
| A1 | `alice` pour elle-même, `CRM` `CONTRIBUTEUR` | Une seule validation (`bob`) |
| A2 | `alice` pour `david`, `COMPTA` `ADMIN` du 2026-12-01 au 2027-01-15, justification de 45 caractères | Validation par `bob` puis par le second valideur |
| A3 | Comme A2, fin au 2027-04-01 | 422 : plus de 90 jours |
| A4 | `alice` pour `farid`, `COMPTA` `CONTRIBUTEUR` | 422 : séparation des tâches avec `PAIE` |
| A5 | `bob` tente la seconde validation de A2 après avoir fait la première | Refus (403 ou 409, à trancher) |
| A6 | `alice` pour `david`, `GED` `ADMIN` | 422 : accès identique en cours jusqu'au 2026-12-31 |
| A7 | `alice` pour le login `zoe` | 422 : bénéficiaire inconnu |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `application` | `code` (PK), `libelle`, `departement_proprietaire`, `sensibilite` |
| `habilitation_demande` | `demande_id` (PK, FK), `application_code` (FK), `profil`, `beneficiaire_login` |
| `etape_validation` | `id`, `demande_id` (FK), `rang` (1 ou 2), `valideur`, `decision`, `horodatage`, `commentaire` |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : pour `ACCES_APPLICATIF`, le niveau dépend du département, avec un cas particulier pour l'un d'eux. Caractériser avant tout refactoring, et décider dans un ADR comment ce niveau s'articule avec la double validation.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Campagne de revue des habilitations : liste des accès expirant dans les 15 jours, relance du bénéficiaire et du propriétaire, export pour l'audit.

✦

## 7. Déplacement — `DEPLACEMENT`

| | |
|---|---|
| **Difficulté** | ★★ |
| **Charge estimée** | 2 tables, 8 règles, estimation de coût affichée pendant la saisie |
| **Ticket** | `docs/tickets/DEPLACEMENT.md` (NF-407) |

**Pitch** — Dématérialiser l'ordre de mission : destination, transport, estimation du coût et demande d'avance avant le départ.

**Acteurs** — Le missionné (`alice`) ; le manager (`bob`) ; les services généraux (`admin`) clôturent après réservation et versement de l'avance.

### Règles métier

| Id | Règle |
|---|---|
| R1 | `dateDebut` (départ) et `dateFin` (retour) obligatoires ; ville et pays de destination obligatoires ; « étranger » si le pays n'est pas la France. |
| R2 | Transport : `TRAIN` par défaut ; `AVION` autorisé si le trajet en train dépasse 4 heures ou si la destination est étrangère et non frontalière ; `VOITURE_PERSONNELLE` avec kilométrage aller-retour estimé. |
| R3 | Nombre de nuits = nombre de jours − 1 (aller-retour dans la journée : 0 nuit). |
| R4 | Coût estimé = transport (saisi, ou kilométrage au barème) + hôtel + repas (2 par jour), hôtel et repas évalués avec le barème de remboursement existant. |
| R5 | Le `montant` de la demande est le coût estimé. |
| R6 | Avance possible si le coût estimé atteint 300 € ; avance au plus égale à 75 % du coût estimé. |
| R7 | Délai : soumission au moins 7 jours calendaires avant le départ (15 jours à l'étranger), sauf demande `urgent`. |
| R8 | Destinations classées « rouge » interdites ; « orange » : justification d'au moins 50 caractères. |

### Points à trancher

- Délai d'une semaine contre départs du lendemain des commerciaux : le ticket dit les deux.
- « Long trajet » : 4 heures de train, porte à porte, ou autre critère ?
- Arrondi de l'avance : au centime, à l'euro inférieur ?
- Annulation après versement de l'avance : remboursement, compensation sur la note de frais ?
- Montant transmis au circuit de validation : coût estimé ou avance demandée ?
- Lien avec la note de frais après le retour.
- Exigence « calcul fiable » : quelle tolérance, quelles sources de prix ?

### Données d'exemple

Classement des destinations (pays fictifs pour les cas à risque) :

| Pays | Classement |
|---|---|
| Suisse, Belgique, Italie, Espagne, Allemagne, Luxembourg | vert, frontalier |
| Royaume-Uni | vert |
| Kaldonie (fictif) | orange |
| Ostrovie (fictif) | rouge |

| Cas | Demande d'`alice` (créée le 2026-11-16) | Résultat attendu (barème métier) |
|---|---|---|
| D1 | Lyon → Nantes, 2026-12-02 → 2026-12-04, train 120 € | 2 nuits (220 €), 6 repas (153 €), coût 493,00 € ; avance maximale 369,75 € |
| D2 | Lyon → Milan, 2026-12-09 → 2026-12-10, train déclaré 6 h 30, avion 280 € | Avion autorisé ; 1 nuit à l'étranger (143 €), 4 repas (112,20 €), coût 535,20 € |
| D3 | Lyon → Paris, 2026-11-19, aller-retour dans la journée, train 130 € | 422 : moins de 7 jours avant le départ |
| D4 | Comme D3 avec `urgent = true` | Acceptée |
| D5 | Lyon → Marseille en voiture, 630 km aller-retour, 2026-12-14 → 2026-12-15 | Transport au barème kilométrique : 400,68 € |
| D6 | D1 avec une avance de 400 € | 422 : avance supérieure à 75 % |
| D7 | Destination Ostrovie | 422 : destination interdite |

> Les montants attendus sont calculés avec le barème tel que le métier le décrit (voir la variante 2). Confrontez-les au calcul réel du code existant avant d'écrire vos assertions.

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `ordre_mission` | `demande_id` (PK, FK), `ville`, `pays`, `etranger`, `transport`, `duree_train_minutes`, `km_aller_retour`, `nb_nuits`, `cout_estime` NUMERIC(10,2), `avance_demandee` NUMERIC(10,2) |
| `pays_risque` | `code_pays` (PK), `libelle`, `niveau` (VERT, ORANGE, ROUGE), `frontalier` |

### Interactions avec le legacy

- `CalculRemboursementLegacy.calculer` : estimation de l'hôtel (`HOTEL`, nombre de nuits, étranger), des repas (`REPAS`) et du kilométrique (`KILOMETRIQUE`). Comportement à caractériser avant de l'utiliser dans vos assertions et avant tout refactoring.
- `RegleValidationLegacy.determinerNiveau` : pour `DEPLACEMENT`, le niveau dépend du montant transmis et de l'ancienneté.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Création d'une note de frais pré-remplie à partir d'un déplacement clôturé (lignes hôtel, repas, transport), ou ordre de mission imprimable.

✦

## 8. Achat — `ACHAT`

| | |
|---|---|
| **Difficulté** | ★ |
| **Charge estimée** | 2 tables, 7 règles, formulaire simple |
| **Ticket** | `docs/tickets/ACHAT.md` (NF-408) |

**Pitch** — Faire passer les achats hors catalogue par NeoFlow : fournisseur référencé, nombre de devis selon le montant, lutte contre le fractionnement.

**Acteurs** — Le demandeur (`alice`) ; le valideur (`bob`) ; la direction des achats (`admin`) clôture à l'émission du bon de commande.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Fournisseur obligatoire, identifié par son SIRET (14 chiffres), présent au référentiel avec le statut `REFERENCE`. |
| R2 | Montant HT obligatoire et strictement positif. |
| R3 | Nombre de devis requis selon le montant : 1 devis en dessous de 1 000 € ; 2 devis de 1 000 € à 5 000 € ; 3 devis au-delà de 5 000 €. |
| R4 | Code analytique obligatoire, au format `CC-` suivi de 4 chiffres (exemple : `CC-4120`). |
| R5 | Fractionnement : rejet si le cumul des demandes `ACHAT` du même demandeur auprès du même fournisseur sur 30 jours glissants (`SOUMISE`, `VALIDEE`, `CLOTUREE`), augmenté de la nouvelle demande, franchit un seuil de R3 que chaque demande prise isolément ne franchit pas. |
| R6 | Fournisseur dont la note qualité est inférieure à 2 sur 5 : avertissement affiché, non bloquant. |
| R7 | `dateDebut` est la date de besoin souhaitée. |

### Points à trancher

- Seuils en HT ou en TTC : le ticket dit les deux.
- Montants exactement égaux à 1 000 € et 5 000 € : quel nombre de devis ?
- Fournisseur non référencé : rejet, ou déclenchement d'une demande de référencement ?
- Avertissement non bloquant : le registre de règles ne renvoie que des erreurs bloquantes ; comment représenter un avertissement dans l'API ?
- Fenêtre de fractionnement : 30 jours glissants, mois civil, année ?
- Exigence « contrôle robuste » : à traduire en critères vérifiables.

### Données d'exemple

| SIRET | Raison sociale | Statut | Note qualité |
|---|---|---|---|
| 41234567800019 | Bureautix SARL | REFERENCE | 4 |
| 52345678900027 | Mobilio Pro | REFERENCE | 3 |
| 63456789000035 | Imprimerie des Brotteaux | REFERENCE | 1 |
| 74567890100043 | Neotech Distribution | EN_COURS | — |

| Cas | Demande d'`alice` | Résultat attendu |
|---|---|---|
| H1 | Bureautix, 850 € HT, 1 devis, `CC-4120` | Acceptée |
| H2 | Mobilio Pro, 1 000,00 € HT, 1 devis | À trancher (borne) |
| H3 | Mobilio Pro, 3 200 € HT, 1 devis | 422 : 2 devis requis |
| H4 | Bureautix, 1 800 € HT les 2, 9 et 16 novembre 2026, 2 devis chacune | Troisième demande en 422 : cumul de 5 400 € sur 30 jours |
| H5 | Neotech Distribution, 600 € HT | 422 : fournisseur non référencé |
| H6 | Imprimerie des Brotteaux, 400 € HT, 1 devis | Acceptée avec avertissement |
| H7 | Bureautix, 300 € HT, code analytique `4120` | 422 : format du code analytique |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `fournisseur` | `siret` (PK), `raison_sociale`, `statut`, `note_qualite` |
| `achat_detail` | `demande_id` (PK, FK), `siret` (FK), `nb_devis`, `code_analytique` |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : pour `ACHAT`, le niveau dépend de seuils de montant proches de ceux de la politique achats. Comparer les deux et caractériser le comportement existant avant toute décision ou tout refactoring.
- `NeoUtils.formatMontant` : affichage des montants.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Tableau de bord des achats par fournisseur et par code analytique, avec détection a posteriori des fractionnements.

✦

## 9. Incident — `INCIDENT`

| | |
|---|---|
| **Difficulté** | ★★★ |
| **Charge estimée** | 2 tables, 9 règles, calcul d'échéances en heures ouvrées, tâche planifiée d'escalade |
| **Ticket** | `docs/tickets/INCIDENT.md` (NF-409) |

**Pitch** — Déclarer les incidents internes (poste, application, réseau, locaux) avec une priorité calculée, des engagements de délai (SLA) et une escalade automatique.

**Acteurs** — Le déclarant (`alice`) ; le support (`bob`), qui prend en charge ; `admin`, qui clôture à la résolution.

### Règles métier

| Id | Règle |
|---|---|
| R1 | Catégorie (`POSTE`, `APPLICATION`, `RESEAU`, `LOCAUX`), impact (`INDIVIDUEL`, `EQUIPE`, `SITE`) et urgence (`BASSE`, `NORMALE`, `HAUTE`) obligatoires. |
| R2 | La priorité est calculée par la matrice ci-dessous ; elle n'est pas saisissable. |
| R3 | Chaque priorité fixe un délai de prise en charge et un délai de résolution (tableau ci-dessous). |
| R4 | Les délais se décomptent en heures ouvrées : 08:00–18:00, hors samedis, dimanches et jours fériés. |
| R5 | Escalade : prise en charge non faite à 100 % du délai → escalade de niveau 1 (événement d'audit et notification de l'administrateur) ; à 200 % → niveau 2. |
| R6 | Un incident P1 exige un numéro de rappel au format téléphonique français. |
| R7 | Un doublon est refusé avec le motif « doublon de #id ». |
| R8 | La mise en attente d'une réponse du déclarant suspend le décompte. |
| R9 | `dateDebut` est la date de constat, au plus tard aujourd'hui. |

Matrice de priorité :

| Impact \ Urgence | BASSE | NORMALE | HAUTE |
|---|---|---|---|
| INDIVIDUEL | P4 | P3 | P3 |
| EQUIPE | P3 | P2 | P2 |
| SITE | P2 | P1 | P1 |

Délais :

| Priorité | Prise en charge | Résolution |
|---|---|---|
| P1 | 30 minutes | 4 heures |
| P2 | 2 heures | 1 jour ouvré |
| P3 | 1 jour ouvré | 3 jours ouvrés |
| P4 | 2 jours ouvrés | 10 jours ouvrés |

### Points à trancher

- Décompte 24 h sur 24 ou en heures ouvrées : le ticket dit les deux (au moins pour les P1).
- Correspondance avec le circuit du socle : `SOUMISE` = ouvert, `VALIDEE` = pris en charge, `CLOTUREE` = résolu ? Que signifie « refuser » un incident ? Faut-il de nouveaux statuts (ADR, impact sur tout le socle) ?
- Le champ `urgent` du socle fait-il double emploi avec l'urgence de l'incident ?
- Qui est notifié lors d'une escalade, et par quel canal ?
- Heures ouvrées de l'agence de La Réunion : heure locale ou heure du siège ?
- Mise en attente : quel statut, qui la déclenche ?
- Exigences « temps de réponse excellent » et « alerter rapidement » : à chiffrer.

### Données d'exemple

| Cas | Déclaration d'`alice` | Résultat attendu |
|---|---|---|
| I1 | VPN inaccessible pour tout le site de Lyon, `RESEAU`, `SITE` × `HAUTE`, lundi 2026-11-16 à 09:10, rappel 04 72 00 00 00 | P1 ; prise en charge avant 09:40 |
| I2 | Écran qui scintille, `POSTE`, `INDIVIDUEL` × `BASSE`, lundi 2026-11-16 à 17:30 | P4 ; prise en charge avant le mercredi 2026-11-18 à 17:30 |
| I3 | CRM très lent pour l'équipe, `APPLICATION`, `EQUIPE` × `NORMALE`, samedi 2026-11-21 à 10:00 | P2 ; décompte à partir du lundi 2026-11-23 à 08:00, prise en charge avant 10:00 |
| I4 | I3 toujours non pris en charge le lundi 2026-11-23 à 12:00 | Escalade de niveau 2 |
| I5 | Incident P1 sans numéro de rappel | 422 |
| I6 | Climatisation en panne, `LOCAUX`, `EQUIPE` × `HAUTE`, constatée le mercredi 2026-11-11 (férié) | P2 ; décompte à partir du jeudi 2026-11-12 à 08:00 |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `incident_detail` | `demande_id` (PK, FK), `categorie`, `impact`, `urgence`, `priorite`, `telephone_rappel`, `echeance_prise_en_charge`, `echeance_resolution`, `niveau_escalade`, `pris_en_charge_le` |
| `jour_ferie` | `date_ferie`, `zone`, `libelle` |

L'escalade suppose une tâche planifiée : rendez l'horloge injectable pour que les tests restent déterministes.

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : aucun traitement dédié à ce type ; niveau par défaut modulé par l'urgence. Décider dans un ADR si le niveau a encore un sens pour un incident, et caractériser le niveau obtenu avant d'en dépendre.
- `NeoUtils.formatDate` : affichage des dates d'échéance ; l'affichage de l'heure est à votre charge.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Tableau de bord SLA (incidents en retard, taux de respect par priorité) et suggestion d'incidents similaires à l'aide du retriever construit en J5 et J6.

✦

## 10. Onboarding — `ONBOARDING`

| | |
|---|---|
| **Difficulté** | ★★ |
| **Charge estimée** | 3 tables, 9 règles, sous-ressource « tâches » (API et écran), graphe de dépendances |
| **Ticket** | `docs/tickets/ONBOARDING.md` (NF-410) |

**Pitch** — Préparer l'arrivée d'un nouveau collaborateur : une checklist de tâches réparties entre services, avec échéances et dépendances, pour que tout soit prêt le premier jour.

**Acteurs** — Le manager qui recrute (`alice`) ; le valideur (`bob`) lance la checklist ; les services (DSI, services généraux, RH, manager) réalisent les tâches ; `admin` clôture.

### Règles métier

| Id | Règle |
|---|---|
| R1 | La demande décrit l'arrivée : prénom, nom, poste, département d'affectation, date d'arrivée (`dateDebut`). |
| R2 | La date d'arrivée est au moins 10 jours ouvrés après la date de création. |
| R3 | À la validation, la checklist est générée à partir du modèle du département d'affectation. |
| R4 | Chaque tâche a un service responsable, une échéance exprimée en jours ouvrés par rapport à l'arrivée (J-10, J-5, J-2, J-1, J+5), un caractère obligatoire ou facultatif et des prérequis. |
| R5 | Une tâche ne peut être marquée « faite » que si tous ses prérequis le sont. |
| R6 | Un modèle de checklist ne contient pas de cycle de dépendances ; le contrôle a lieu à l'enregistrement du modèle. |
| R7 | Report de la date d'arrivée : les échéances des tâches non faites sont recalculées. |
| R8 | La clôture n'est possible que lorsque toutes les tâches obligatoires sont faites. |
| R9 | Données personnelles minimales : ni numéro de sécurité sociale, ni adresse, ni date de naissance. |

### Points à trancher

- Clôture quand toutes les tâches sont faites, ou le jour de l'arrivée pour les statistiques RH ? Le ticket dit les deux.
- Le futur collaborateur n'existe pas encore dans `collaborateur` : quand et par qui est-il créé ?
- Désistement du candidat : refus, annulation, purge des données personnelles ?
- Qui marque une tâche « faite » : faut-il un rôle par service ?
- Prérequis non satisfait : 409 (état) ou 422 (règle) ?
- Arrivées très rapprochées (intérim) : dérogation au délai de 10 jours ouvrés ?
- Exigence « suivi en temps réel » : rafraîchissement, notifications, ou simple consultation ?

### Données d'exemple

Modèle de checklist du département COMMERCIAL :

| Code | Tâche | Service | Échéance | Prérequis | Obligatoire |
|---|---|---|---|---|---|
| T1 | Créer le compte annuaire | DSI | J-5 | — | oui |
| T2 | Préparer le poste de travail | DSI | J-2 | T1 | oui |
| T3 | Commander le badge d'accès | Services généraux | J-5 | — | oui |
| T4 | Ouvrir l'accès CRM | DSI | J-1 | T1 | oui |
| T5 | Désigner un parrain | Manager | J-10 | — | non |
| T6 | Planifier la formation sécurité | RH | J+5 | T1 | oui |

| Cas | Situation (demande créée le 2026-11-16) | Résultat attendu |
|---|---|---|
| O1 | `alice` annonce l'arrivée de Léa Fontaine, commerciale, COMMERCIAL, le lundi 2026-12-07 | Acceptée ; échéances : T5 2026-11-23, T1 et T3 2026-11-30, T2 2026-12-03, T4 2026-12-04, T6 2026-12-14 |
| O2 | Arrivée annoncée pour le 2026-11-25 | 422 : moins de 10 jours ouvrés |
| O3 | T4 marquée faite alors que T1 ne l'est pas | Rejet : prérequis non satisfait |
| O4 | Report de l'arrivée de O1 au 2026-12-14 | Échéances recalculées (T1 au 2026-12-07) |
| O5 | Clôture demandée alors que T6 n'est pas faite | Rejet |
| O6 | Modèle où T2 dépend de T4 et T4 de T2 | Modèle rejeté : cycle |

### Modèle de données suggéré

| Table | Champs |
|---|---|
| `arrivee` | `demande_id` (PK, FK), `prenom`, `nom`, `poste`, `departement_affectation` |
| `modele_tache` | `code`, `departement`, `libelle`, `service`, `echeance_relative`, `obligatoire`, prérequis (colonne ou table d'association) |
| `tache_onboarding` | `id`, `demande_id` (FK), `code`, `libelle`, `service`, `echeance`, `obligatoire`, `statut`, `faite_par`, `faite_le` |

### Interactions avec le legacy

- `RegleValidationLegacy.determinerNiveau` : aucun traitement dédié à ce type ; niveau par défaut modulé par l'urgence.
- `NeoUtils.joursOuvres` (front) : candidat pour afficher les échéances ; comportement à caractériser avant réutilisation. Le calcul de référence des échéances reste côté serveur.
- `NeoUtils.formatDate` : affichage des échéances.

### Extension proposée pour le vibe coding (J10, avec `neoagent`)

Vue Kanban des tâches par service, avec mise en évidence des tâches en retard et des tâches bloquées par un prérequis.
