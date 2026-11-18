from __future__ import annotations

# Documents longs du projet NeoFlow (copie de fil-rouge/neoflow/docs : les dix tickets
# et deux extraits d'ARCHITECTURE.md), utilisés pour comparer les stratégies de chunking.

DOCS: list[dict] = [
    {
        "doc_id": "NF-401",
        "title": 'NF-401 — Poser ses congés dans NeoFlow',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-401 — Poser ses congés dans NeoFlow

| Champ | Valeur |
|---|---|
| Identifiant | NF-401 |
| Type de demande | `CONGES` |
| Nature | Évolution |
| Rapporteur | Sophie Garnier, responsable de l'administration du personnel (DRH) |
| Priorité | Haute |
| Créé le | 2026-10-14 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux poser mes congés dans NeoFlow afin de ne plus passer par un mail à mon manager doublé d'une ligne dans le tableur de la DRH.

## Description (telle que reçue)

Bonjour,

Aujourd'hui les congés se demandent par mail au manager, qui transfère à la DRH, qui ressaisit dans le tableur de suivi puis dans la paie. On perd des demandes et on a régulièrement des erreurs de solde.

On voudrait que les collaborateurs posent leurs congés directement dans NeoFlow :

- congés payés et RTT, et aussi les congés sans solde de temps en temps ;
- il faut vérifier que la personne a assez de jours avant d'envoyer la demande ;
- les jours sont comptés en jours ouvrés, comme d'habitude, et on doit pouvoir poser des demi-journées comme dans l'ancien intranet ;
- on ne doit pas pouvoir poser deux fois les mêmes jours ;
- le manager valide ou refuse, et quand c'est validé le solde du collaborateur doit être mis à jour tout de suite pour qu'il voie ce qui lui reste ;
- il faut respecter un délai de prévenance raisonnable, sauf cas exceptionnels.

Les soldes de chacun sont dans le logiciel de paie, c'est la référence.

Il faut que ce soit simple et rapide pour les collaborateurs : ils ne doivent pas y passer plus de temps qu'à écrire un mail.

C'est valable pour toutes les agences.

Merci,
Sophie

## Pièces jointes

- Capture d'écran de l'ancien formulaire de congés (non jointe, « je la retrouve et je vous l'envoie »).

## Commentaires

**Bertrand Collin, gestionnaire paie — 2026-10-15**

> Point important pour nous : le solde ne doit être débité qu'une fois les congés intégrés dans la paie, à la clôture de fin de mois. Sinon on a des écarts entre NeoFlow et les bulletins à chaque fois qu'un congé est modifié après validation.

**Sophie Garnier — 2026-10-15**

> OK pour moi, on voit ça avec l'équipe projet.
""",
    },
    {
        "doc_id": "NF-402",
        "title": 'NF-402 — Dématérialiser les notes de frais',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-402 — Dématérialiser les notes de frais

| Champ | Valeur |
|---|---|
| Identifiant | NF-402 |
| Type de demande | `NOTE_DE_FRAIS` |
| Nature | Évolution |
| Rapporteur | Julien Roche, contrôleur de gestion |
| Priorité | Haute |
| Créé le | 2026-10-09 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux déclarer mes frais professionnels dans NeoFlow afin d'être remboursé sans remplir de formulaire papier.

## Description (telle que reçue)

Bonjour,

Nous recevons encore environ 600 notes de frais papier par mois, avec les tickets agrafés. La saisie en comptabilité prend deux jours par mois et les erreurs sont fréquentes.

Ce que nous voulons :

1. Une note de frais regroupe plusieurs dépenses (repas, hôtel, transport, kilomètres, divers).
2. Chaque dépense est remboursée selon notre barème. Le barème est déjà dans l'application (le calcul de l'ancien intranet a été repris) : ne surtout pas y toucher, il a été validé par la direction financière.
3. Le justificatif est obligatoire pour toutes les dépenses, sans exception : c'est une exigence de nos commissaires aux comptes.
4. Les dépenses trop anciennes ne sont pas remboursées (plus de trois mois).
5. Le remboursement doit être exact au centime près : les collaborateurs vérifient et nous avons des réclamations dès qu'il manque quelques centimes.
6. Une même dépense ne doit pas pouvoir être remboursée deux fois.

L'écran doit être ergonomique, et utilisable sur mobile si possible, car les commerciaux saisissent souvent leurs frais entre deux rendez-vous.

Nos commerciaux vont régulièrement à Genève et à Londres pour les clients grands comptes.

Cordialement,
Julien Roche

## Pièces jointes

- `bareme_frais_2023.pdf` (non joint au ticket, disponible auprès du contrôle de gestion).

## Commentaires

**Nadia Ferhat, comptable fournisseurs — 2026-10-12**

> Pour les petites dépenses comme le parking ou les péages, on ne demande jamais le justificatif, ce serait ingérable pour tout le monde. Il faudrait garder cette souplesse.

**Julien Roche — 2026-10-12**

> Noté.
""",
    },
    {
        "doc_id": "NF-403",
        "title": 'NF-403 — Commande de matériel informatique sur catalogue',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-403 — Commande de matériel informatique sur catalogue

| Champ | Valeur |
|---|---|
| Identifiant | NF-403 |
| Type de demande | `MATERIEL_IT` |
| Nature | Évolution |
| Rapporteur | Karim Haddad, responsable du parc informatique (DSI) |
| Priorité | Moyenne |
| Créé le | 2026-10-06 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux commander mon matériel informatique depuis un catalogue afin de ne plus avoir à décrire mon besoin par mail au support.

## Description (telle que reçue)

Salut l'équipe,

Aujourd'hui les demandes de matériel arrivent en vrac au support (« il me faudrait un écran », « mon PC est lent »), on doit relancer pour savoir quoi commander et on dépasse les budgets sans s'en rendre compte.

Le besoin :

- un catalogue de matériel référencé par la DSI (portables, écrans, stations d'accueil, casques…) ;
- le collaborateur choisit dans le catalogue, il ne saisit pas de prix ;
- chaque équipe a un budget matériel annuel qu'on ne doit pas dépasser ;
- le budget d'une équipe est consommé dès que la demande est envoyée, pour qu'on ne se retrouve pas avec dix demandes simultanées qui passent toutes ;
- un seul PC portable par personne, sauf renouvellement ;
- on ne commande pas des articles qui ne sont plus au catalogue.

La DSI gère son propre matériel, on verra pour elle.

Les prix du catalogue changent tous les trimestres en fonction de notre contrat avec le distributeur.

L'écran catalogue doit être rapide, même avec beaucoup d'articles.

Karim

## Pièces jointes

- `catalogue_T4_2026.xlsx` (extrait, non joint).

## Commentaires

**Hélène Dubreuil, direction des achats — 2026-10-08**

> Attention : on ne doit compter dans le budget que ce qui est validé. Sinon une équipe se retrouve bloquée par des demandes qui seront refusées ensuite, et ça arrive souvent.

**Karim Haddad — 2026-10-08**

> À voir en atelier.
""",
    },
    {
        "doc_id": "NF-404",
        "title": 'NF-404 — Réservation des salles de réunion',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-404 — Réservation des salles de réunion

| Champ | Valeur |
|---|---|
| Identifiant | NF-404 |
| Type de demande | `RESERVATION_SALLE` |
| Nature | Évolution |
| Rapporteur | Nathalie Brun, responsable des services généraux |
| Priorité | Moyenne |
| Créé le | 2026-10-20 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux réserver une salle de réunion dans NeoFlow afin de ne plus dépendre du fichier partagé où tout le monde écrase les réservations des autres.

## Description (telle que reçue)

Bonjour,

Les salles de réunion sont réservées dans un fichier partagé. Chaque semaine, deux réunions se retrouvent dans la même salle et les visiteurs attendent à l'accueil.

Ce que nous voulons :

- réserver une salle pour un créneau donné, par demi-heure ;
- impossible de réserver une salle déjà prise ;
- vérifier que le nombre de participants tient dans la salle ;
- indiquer si on a besoin de la visio ou d'un écran ;
- toutes les réservations sont validées par les services généraux, sans exception, pour que nous gardions la maîtrise des salles ;
- pour les petites salles de moins de 6 places, la réservation doit être confirmée immédiatement, sans attendre personne : les équipes se plaignent assez des délais ;
- pouvoir réserver une salle toutes les semaines pour les réunions récurrentes (comité du lundi, points d'équipe).

C'est valable pour tous nos sites, y compris l'agence de Saint-Denis de La Réunion qui a deux salles.

L'affichage des disponibilités doit être clair et instantané.

Nathalie Brun

## Pièces jointes

- Plan des salles du siège (non joint).
- Liste des salles par site avec capacités (en cours de mise à jour).

## Commentaires

**Olivier Masson, assistant de direction — 2026-10-21**

> La salle Confluence est réservée en priorité pour le comité de direction. Merci de le prévoir.
""",
    },
    {
        "doc_id": "NF-405",
        "title": 'NF-405 — Demandes de formation',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-405 — Demandes de formation

| Champ | Valeur |
|---|---|
| Identifiant | NF-405 |
| Type de demande | `FORMATION` |
| Nature | Évolution |
| Rapporteur | Élodie Marchand, responsable formation (DRH) |
| Priorité | Moyenne |
| Créé le | 2026-10-02 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux demander une formation dans NeoFlow afin de savoir rapidement si elle est acceptée et financée.

## Description (telle que reçue)

Bonjour,

Le plan de formation est piloté dans un tableur et les demandes arrivent par mail, souvent trop tard. Nous refusons des demandes faute de visibilité sur le budget restant.

Les règles :

- chaque collaborateur dispose d'un budget formation de 2 500 € par an ;
- les formations de notre catalogue (sessions négociées avec nos organismes partenaires) sont prioritaires ; les formations hors catalogue sont possibles sur devis ;
- certaines formations nécessitent d'en avoir suivi une autre avant ;
- pas plus de 3 formations par an et par personne ;
- les sessions ont un nombre de places limité ;
- une demande doit être faite au moins trois semaines avant le début de la formation, pour que nous ayons le temps de traiter l'inscription avec l'organisme.

Les montants des formations sont toujours exprimés TTC dans nos échanges avec les organismes.

Le manager valide la demande, puis nous clôturons quand le collaborateur a effectivement suivi la formation.

Le parcours doit être fluide pour le collaborateur.

Élodie Marchand

## Pièces jointes

- `catalogue_formation_2027.pdf` (non joint).

## Commentaires

**Romain Giraud, manager d'équipe commerciale — 2026-10-05**

> Pour les sessions du catalogue, il faut pouvoir s'inscrire jusqu'à la veille s'il reste des places : on a souvent des désistements de dernière minute et c'est dommage de perdre la place.

**Élodie Marchand — 2026-10-06**

> Bonne remarque, on garde.
""",
    },
    {
        "doc_id": "NF-406",
        "title": "NF-406 — Demandes d'accès aux applications internes",
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-406 — Demandes d'accès aux applications internes

| Champ | Valeur |
|---|---|
| Identifiant | NF-406 |
| Type de demande | `ACCES_APPLICATIF` |
| Nature | Évolution réglementaire |
| Rapporteur | Thomas Lefèvre, RSSI |
| Priorité | Haute |
| Créé le | 2026-09-29 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que responsable de la sécurité, je veux que toute demande d'accès à une application interne passe par NeoFlow afin de pouvoir justifier chaque habilitation lors des audits.

## Description (telle que reçue)

Bonjour,

L'audit ISO 27001 de septembre a relevé une non-conformité majeure : nous sommes incapables de dire qui a autorisé la plupart des accès à la comptabilité et à la paie. Les demandes passent par mail, par téléphone, parfois par un simple message au support.

À partir de la version 1.1, toutes les demandes d'accès passent par NeoFlow :

- la demande précise l'application et le niveau de droits souhaité (lecture, contribution, administration) ;
- le manager valide ;
- pour les droits d'administration, il faut une double validation ;
- personne ne doit pouvoir valider sa propre demande ;
- tous les accès doivent être limités dans le temps, c'est un point clé de la remarque d'audit ;
- un collaborateur ne doit pas cumuler des droits incompatibles (par exemple saisir en comptabilité et en paie) ;
- tout doit être tracé : qui a demandé, qui a validé, quand.

Les managers doivent aussi pouvoir faire la demande pour un membre de leur équipe, notamment pour les nouveaux arrivants.

Le système doit être sécurisé et conforme.

Thomas Lefèvre
RSSI

## Pièces jointes

- Extrait du rapport d'audit (diffusion restreinte, non joint).

## Commentaires

**Karim Haddad, DSI — 2026-09-30**

> Pour les accès en lecture, il ne faut pas imposer de date de fin : les accès en consultation sont permanents, on ne va pas embêter tout le monde avec des renouvellements tous les trois mois.

**Thomas Lefèvre — 2026-10-01**

> On en reparle, mais l'idée est là.
""",
    },
    {
        "doc_id": "NF-407",
        "title": 'NF-407 — Ordres de mission et avances',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-407 — Ordres de mission et avances

| Champ | Valeur |
|---|---|
| Identifiant | NF-407 |
| Type de demande | `DEPLACEMENT` |
| Nature | Évolution |
| Rapporteur | Patrick Morel, responsable des voyages d'affaires (services généraux) |
| Priorité | Moyenne |
| Créé le | 2026-10-16 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux faire mon ordre de mission dans NeoFlow afin de faire réserver mon déplacement et, si besoin, obtenir une avance.

## Description (telle que reçue)

Bonjour,

Les ordres de mission sont aujourd'hui des formulaires Word envoyés par mail. Nous découvrons souvent les déplacements après coup, au moment de la note de frais, et nous n'avons aucune vision des dépenses à venir.

Ce que nous attendons :

- tout déplacement professionnel fait l'objet d'un ordre de mission dans NeoFlow avant le départ ;
- le train est la règle ; l'avion seulement pour les longs trajets ou l'étranger ; la voiture personnelle reste possible ;
- l'application estime le coût du déplacement (transport, hôtel, repas) ;
- le collaborateur peut demander une avance sur frais, qui ne peut pas dépasser 75 % du coût estimé ;
- certaines destinations à l'étranger sont déconseillées, voire interdites, selon les consignes de sécurité du groupe ;
- les demandes doivent être faites au moins une semaine avant le départ, pour que nous puissions réserver à de bons tarifs.

Le calcul doit être fiable : nous ne voulons pas d'écart avec ce qui sera remboursé ensuite.

Patrick Morel

## Pièces jointes

- Politique voyages 2025 (non jointe).
- Liste des pays déconseillés (mise à jour mensuelle par la sécurité groupe).

## Commentaires

**Sandrine Lambert, directrice commerciale — 2026-10-17**

> Mes commerciaux partent souvent le lendemain, quand un client les appelle. Il faut que ce soit possible sans passer systématiquement par une procédure d'urgence, sinon ils ne passeront pas par l'outil.

**Patrick Morel — 2026-10-17**

> Compris, à intégrer.
""",
    },
    {
        "doc_id": "NF-408",
        "title": 'NF-408 — Achats hors catalogue',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-408 — Achats hors catalogue

| Champ | Valeur |
|---|---|
| Identifiant | NF-408 |
| Type de demande | `ACHAT` |
| Nature | Évolution |
| Rapporteur | Hélène Dubreuil, directrice des achats |
| Priorité | Haute |
| Créé le | 2026-10-07 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que demandeur, je veux faire mes demandes d'achat hors catalogue dans NeoFlow afin qu'elles respectent la politique achats sans aller-retour avec la direction des achats.

## Description (telle que reçue)

Bonjour,

Notre politique achats n'est pas appliquée : des commandes partent sans mise en concurrence, chez des fournisseurs que nous ne connaissons pas, et nous le découvrons à réception de la facture.

Les règles à mettre en place :

- tout achat hors catalogue passe par une demande NeoFlow ;
- le fournisseur doit être référencé chez nous ;
- en dessous de 1 000 €, un devis suffit ; au-delà de 1 000 €, il en faut deux ; au-delà de 5 000 €, trois ;
- les gens ne doivent pas découper leurs achats pour passer sous les seuils ;
- chaque achat est imputé sur un code analytique ;
- certains fournisseurs référencés ont une mauvaise note qualité : il faudrait que le demandeur en soit averti.

Tous les montants de la politique sont exprimés HT.

Le contrôle doit être robuste.

Hélène Dubreuil
Directrice des achats

## Pièces jointes

- Politique achats v3 (non jointe).
- Export du référentiel fournisseurs (à demander à la comptabilité fournisseurs).

## Commentaires

**Julien Roche, contrôle de gestion — 2026-10-08**

> Pour éviter toute discussion avec les demandeurs, les seuils doivent s'apprécier en TTC, comme sur les factures qu'ils reçoivent. C'est ce que tout le monde regarde.

**Hélène Dubreuil — 2026-10-08**

> Je note.
""",
    },
    {
        "doc_id": "NF-409",
        "title": 'NF-409 — Déclaration et suivi des incidents internes',
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-409 — Déclaration et suivi des incidents internes

| Champ | Valeur |
|---|---|
| Identifiant | NF-409 |
| Type de demande | `INCIDENT` |
| Nature | Évolution |
| Rapporteur | Damien Roux, responsable du centre de services interne |
| Priorité | Haute |
| Créé le | 2026-10-19 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que collaborateur, je veux déclarer un incident dans NeoFlow afin qu'il soit pris en charge dans des délais connus.

## Description (telle que reçue)

Bonjour,

Les incidents (poste de travail, applications, réseau, locaux) arrivent aujourd'hui par téléphone et par mail. Nous n'avons aucun indicateur fiable et la direction nous reproche de ne pas tenir nos engagements, sans que nous puissions prouver le contraire.

Ce que nous voulons :

- le collaborateur déclare l'incident avec sa catégorie, son impact (lui seul, son équipe, tout le site) et son urgence ;
- la priorité, de P1 à P4, est déterminée à partir de l'impact et de l'urgence ;
- chaque priorité a un délai de prise en charge et un délai de résolution : par exemple un P1 doit être pris en charge en 30 minutes et résolu en 4 heures ;
- les délais courent 24 heures sur 24, un incident ne s'arrête pas la nuit ;
- si un délai est dépassé, l'incident est escaladé automatiquement ;
- pour les P1, il faut un numéro de téléphone pour rappeler la personne ;
- les doublons doivent pouvoir être rejetés.

Le temps de réponse de l'application doit être excellent, et les escalades doivent alerter rapidement les bonnes personnes.

Damien Roux

## Pièces jointes

- Matrice impact / urgence actuelle (tableur, non jointe).
- Engagements de service 2026 (document interne, non joint).

## Commentaires

**Damien Roux — 2026-10-20**

> Précision suite à la réunion avec les équipes support : tous nos délais sont exprimés en heures ouvrées, comme dans notre contrat de service avec les directions métier.

**Fabienne Noël, responsable de l'agence de Saint-Denis (La Réunion) — 2026-10-21**

> Nos horaires ne sont pas ceux de Lyon, merci d'en tenir compte.
""",
    },
    {
        "doc_id": "NF-410",
        "title": "NF-410 — Préparation de l'arrivée des nouveaux collaborateurs",
        "product": "NeoFlow",
        "version": "1.1",
        "text": """# NF-410 — Préparation de l'arrivée des nouveaux collaborateurs

| Champ | Valeur |
|---|---|
| Identifiant | NF-410 |
| Type de demande | `ONBOARDING` |
| Nature | Évolution |
| Rapporteur | Marion Petitjean, chargée d'intégration (DRH) |
| Priorité | Moyenne |
| Créé le | 2026-10-12 |
| Version cible | NeoFlow 1.1 |
| Statut | À analyser |

## User story

En tant que manager qui recrute, je veux préparer l'arrivée de mon nouveau collaborateur dans NeoFlow afin que tout soit prêt le premier jour.

## Description (telle que reçue)

Bonjour,

Un nouvel arrivant sur trois n'a pas son poste ou ses accès le premier jour. Les demandes partent dans tous les sens (DSI, services généraux, RH) et personne n'a de vision d'ensemble.

Ce que nous voulons :

- le manager crée une demande d'arrivée avec les informations du futur collaborateur et sa date d'arrivée ;
- la demande doit être faite au moins deux semaines avant l'arrivée ;
- une fois la demande validée, chaque service reçoit ses tâches (DSI : compte, poste, accès ; services généraux : badge ; RH : contrat, formation sécurité ; manager : parrain) ;
- certaines tâches dépendent d'autres (on ne peut pas ouvrir les accès avant que le compte existe) ;
- la liste des tâches dépend du département d'arrivée ;
- la demande est clôturée quand toutes les tâches sont faites ;
- si la date d'arrivée change, tout doit suivre.

Il faut un suivi en temps réel de l'avancement pour le manager et pour nous.

Marion Petitjean

## Pièces jointes

- Checklist d'intégration actuelle (document Word, non joint).

## Commentaires

**Cédric Aubert, responsable des indicateurs RH — 2026-10-14**

> Pour nos statistiques d'intégration, la demande doit être clôturée le jour même de l'arrivée du collaborateur, quel que soit l'état des tâches. Sinon nos délais d'intégration sont faussés.

**Marion Petitjean — 2026-10-14**

> D'accord, on l'ajoute au besoin.
""",
    },
    {
        "doc_id": "architecture-cycle",
        "title": 'Architecture de NeoFlow : cycle de vie et validation',
        "product": "NeoFlow",
        "version": "1.0",
        "text": """# Architecture de NeoFlow : cycle de vie et validation

## 4. Cycle de vie d'une demande

- Les transitions autorisées sont définies dans `StatutDemande.TRANSITIONS` et vérifiées par `Demande.changerStatut`. Toute autre transition lève `TransitionInvalideException` → **409**.
- La modification (`PUT`) n'est possible qu'au statut `BROUILLON`, sinon **409**.
- Modifier ou soumettre la demande d'un autre utilisateur → **403** (`AccessDeniedException` levée par le service).
- Chaque création, soumission, validation, refus et clôture écrit une ligne dans `evenement_demande` (`TypeEvenement` : `CREATION`, `SOUMISSION`, `VALIDATION`, `REFUS`, `CLOTURE`). La modification d'un brouillon n'est pas journalisée.
- Le circuit du socle comporte **un seul** valideur, quel que soit `niveauValidation` ; le niveau est calculé, enregistré et affiché.

## 5. Soumission : calcul du niveau de validation

`CircuitValidationService.calculerNiveau` convertit le montant `BigDecimal` (facultatif) en `Double`, en passant `0.0` quand il est absent, puis délègue au legacy. L'ancienneté est le nombre de mois révolus entre `collaborateur.date_entree` et la date du jour (horloge `Clock`) ; elle vaut 0 pour un login absent du référentiel.

## 6. Point d'extension des variantes

```java
public interface RegleMetierDemande {
    TypeDemande type();               // GENERIQUE = s'applique à toutes les demandes
    List<String> verifier(Demande d); // liste vide si conforme
}
```

- Toute implémentation annotée `@Component` est collectée par `RegleMetierRegistry` (injection de `List<RegleMetierDemande>`) : aucun enregistrement manuel.
- Le registre applique d'abord les règles `GENERIQUE`, puis celles du type de la demande, et concatène les messages.
- Moments d'appel : création et modification (demande au statut `BROUILLON`), soumission (demande au statut `SOUMISE`, `niveauValidation` calculé, pas encore enregistrée). Une règle distingue ces moments par `d.getStatut()`.
- Des erreurs produisent une `RegleMetierException`, rendue en **422** avec la propriété `erreurs`.
- `RegleGenerique` (socle) : la date de fin, si elle est renseignée, ne précède pas la date de début ; le montant, s'il est renseigné, est strictement positif.
""",
    },
    {
        "doc_id": "architecture-api",
        "title": 'Architecture de NeoFlow : API REST et sécurité',
        "product": "NeoFlow",
        "version": "1.0",
        "text": """# Architecture de NeoFlow : API REST et sécurité

## 7. API REST

| Méthode | Chemin | Rôle | Effet | Réponses |
|---|---|---|---|---|
| GET | `/api/demandes?statut=&type=&page=0&size=20` | authentifié | Liste paginée, page **0-based**, tri par date de création décroissante ; `size` de 1 à 100 | 200, 400 |
| GET | `/api/demandes/{id}` | authentifié | Détail | 200, 404 |
| GET | `/api/demandes/recherche?q=` | authentifié | Recherche par titre (50 résultats au plus, sans pagination) | 200 |
| POST | `/api/demandes` | DEMANDEUR | Crée en `BROUILLON` (`Location` renseigné) | 201, 400, 403, 422 |
| PUT | `/api/demandes/{id}` | DEMANDEUR (auteur) | Modifie un brouillon | 200, 400, 403, 404, 409, 422 |
| POST | `/api/demandes/{id}/soumettre` | DEMANDEUR (auteur) | `SOUMISE`, calcule `niveauValidation` | 200, 403, 404, 409, 422 |
| POST | `/api/demandes/{id}/valider` | VALIDEUR | `VALIDEE` | 200, 403, 404, 409 |
| POST | `/api/demandes/{id}/refuser` | VALIDEUR | `REFUSEE`, corps `{"motif": "..."}` obligatoire | 200, 400, 403, 404, 409 |
| POST | `/api/demandes/{id}/cloturer` | ADMIN | `CLOTUREE` | 200, 403, 404, 409 |
| GET | `/api/demandes/{id}/evenements` | authentifié | Historique chronologique | 200, 404 |
| GET | `/api/moi` | authentifié | `{login, roles, departement}` (utilisé par le frontend) | 200 |

Sans identifiants valides : **401**. Les règles d'accès par rôle sont déclarées dans `SecurityConfig` (par méthode HTTP et chemin) ; le contrôle « auteur de la demande » est fait dans `DemandeService`.

**Corps de création ou de modification** (`DemandeRequest`) :

```json
{ "type": "NOTE_DE_FRAIS", "titre": "Déjeuner client Lyon", "description": "…",
  "montant": 86.40, "dateDebut": "2026-10-08", "dateFin": null,
  "departement": null, "urgent": false }
```

`type`, `titre` (120 caractères au plus) et `dateDebut` sont obligatoires ; `montant` a au plus 2 décimales.

**Page de résultats** (format Spring Data `PagedModel`) :

```json
{ "content": [ { "id": 1, "type": "GENERIQUE", "statut": "BROUILLON", "...": "..." } ],
  "page": { "size": 20, "number": 0, "totalElements": 12, "totalPages": 1 } }
```

**Erreurs** : ProblemDetail (RFC 9457, `application/problem+json`) produit par `GlobalExceptionHandler`.

| Statut | `title` | Propriétés ajoutées |
|---|---|---|
| 400 | `Requête invalide` (Bean Validation) | `erreurs` : `"champ : message"` |
| 403 | `Accès refusé` (contrôle d'auteur) | — |
| 404 | `Demande introuvable` | — |
| 409 | `Transition de statut invalide` | — |
| 422 | `Règles métier non respectées` | `erreurs` : messages des règles |
| 500 | `Erreur interne` | `traceId` de la requête |

## 8. Sécurité

- HTTP Basic, sans session (`STATELESS`), CSRF désactivé (identifiants envoyés à chaque requête dans l'en-tête `Authorization`, pas de cookie).
- Comptes de démonstration déclarés dans `application.yml` (`neoflow.securite.utilisateurs`), mot de passe `neoflow` : `alice` (DEMANDEUR), `bob` (VALIDEUR), `admin` (ADMIN). Pas de hiérarchie de rôles : `admin` ne valide pas, `bob` ne crée pas.
- Le frontend envoie `X-Requested-With: XMLHttpRequest` : Spring Security répond alors 401 sans en-tête `WWW-Authenticate`, ce qui évite la fenêtre d'authentification native du navigateur.
- Accessibles sans authentification : `/actuator/**`, `/v3/api-docs/**`, `/swagger-ui/**`, `/swagger-ui.html`, `/error`. Toute autre route hors `/api/**` est refusée.
""",
    },
]


# Golden set pour le chunking : la réponse est considérée comme trouvée si un
# des chunks retournés contient la phrase "needle" (sous-chaîne exacte du doc).
CHUNK_GOLDEN: list[dict] = [
    {"q": "Comment les congés sont-ils demandés aujourd'hui ?", "doc_id": "NF-401", "needle": "Aujourd'hui les congés se demandent par mail au manager"},
    {"q": 'Peut-on poser une demi-journée de congé ?', "doc_id": "NF-401", "needle": 'on doit pouvoir poser des demi-journées'},
    {"q": 'Où sont les soldes de congés de référence ?', "doc_id": "NF-401", "needle": 'Les soldes de chacun sont dans le logiciel de paie'},
    {"q": 'Quand le solde doit-il être débité selon la paie ?', "doc_id": "NF-401", "needle": 'à la clôture de fin de mois'},
    {"q": 'Combien de notes de frais papier reçoit-on chaque mois ?', "doc_id": "NF-402", "needle": 'environ 600 notes de frais papier par mois'},
    {"q": 'Le justificatif est-il obligatoire pour chaque dépense ?', "doc_id": "NF-402", "needle": 'Le justificatif est obligatoire pour toutes les dépenses, sans exception'},
    {"q": 'Une dépense ancienne est-elle remboursée ?', "doc_id": "NF-402", "needle": 'Les dépenses trop anciennes ne sont pas remboursées (plus de trois mois)'},
    {"q": 'Dans quelles villes vont les commerciaux grands comptes ?', "doc_id": "NF-402", "needle": 'Genève et à Londres'},
    {"q": "Qu'a relevé l'audit ISO 27001 ?", "doc_id": "NF-406", "needle": 'une non-conformité majeure'},
    {"q": "Faut-il une double validation pour l'administration ?", "doc_id": "NF-406", "needle": "pour les droits d'administration, il faut une double validation"},
    {"q": 'Quels droits sont incompatibles ?', "doc_id": "NF-406", "needle": 'saisir en comptabilité et en paie'},
    {"q": 'Les accès en lecture ont-ils une date de fin ?', "doc_id": "NF-406", "needle": 'les accès en consultation sont permanents'},
    {"q": 'Quel est le moyen de transport par défaut ?', "doc_id": "NF-407", "needle": 'le train est la règle'},
    {"q": "Quel est le plafond de l'avance sur frais ?", "doc_id": "NF-407", "needle": 'ne peut pas dépasser 75 % du coût estimé'},
    {"q": 'Combien de temps avant le départ faire la demande ?', "doc_id": "NF-407", "needle": 'au moins une semaine avant le départ'},
    {"q": 'Que demandent les commerciaux qui partent le lendemain ?', "doc_id": "NF-407", "needle": "sans passer systématiquement par une procédure d'urgence"},
    {"q": 'Que se passe-t-il pour une transition de statut interdite ?', "doc_id": "architecture-cycle", "needle": 'Toute autre transition lève `TransitionInvalideException` → **409**'},
    {"q": 'Combien de valideurs dans le circuit du socle ?', "doc_id": "architecture-cycle", "needle": 'Le circuit du socle comporte **un seul** valideur'},
    {"q": "Comment est calculée l'ancienneté ?", "doc_id": "architecture-cycle", "needle": 'nombre de mois révolus entre `collaborateur.date_entree` et la date du jour'},
    {"q": 'Quel code renvoient des erreurs de règles métier ?', "doc_id": "architecture-cycle", "needle": 'rendue en **422** avec la propriété `erreurs`'},
    {"q": 'Combien de résultats renvoie la recherche par titre ?', "doc_id": "architecture-api", "needle": 'Recherche par titre (50 résultats au plus, sans pagination)'},
    {"q": 'Quels champs sont obligatoires à la création ?', "doc_id": "architecture-api", "needle": '`type`, `titre` (120 caractères au plus) et `dateDebut` sont obligatoires'},
    {"q": 'Le compte admin peut-il valider une demande ?', "doc_id": "architecture-api", "needle": 'Pas de hiérarchie de rôles : `admin` ne valide pas, `bob` ne crée pas'},
    {"q": 'Quelles routes sont accessibles sans authentification ?', "doc_id": "architecture-api", "needle": 'Accessibles sans authentification : `/actuator/**`'},
]


def get_docs() -> list[dict]:
    return DOCS


def get_chunk_golden() -> list[dict]:
    # Vérifie que chaque needle existe bien dans son document
    by_id = {d["doc_id"]: d["text"] for d in DOCS}
    for g in CHUNK_GOLDEN:
        assert g["needle"] in by_id[g["doc_id"]], g["needle"]
    return CHUNK_GOLDEN
