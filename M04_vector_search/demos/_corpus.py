from __future__ import annotations

# Corpus partagé entre les démos M03, M04 et M05 : 50 extraits de la documentation
# du projet NeoFlow (fil-rouge/neoflow/docs : tickets NF-401 à NF-410, ARCHITECTURE.md)
# et des règles du module legacy. Entreprise et données fictives (Groupe Velmora).
# Champs : product (NeoFlow), version (1.0 = socle livré, 1.1 = évolutions demandées),
# category (type de demande ou thème technique), title.

CHUNKS: list[dict] = [
    # Congés (NF-401)
    {"id": 1, "content": "Aujourd'hui les congés se demandent par mail au manager, qui transfère à la DRH, qui ressaisit dans le tableur de suivi puis dans la paie. On perd des demandes et on a régulièrement des erreurs de solde.", "product": "NeoFlow", "version": "1.1", "category": "conges", "title": "Congés : situation actuelle"},
    {"id": 2, "content": "Les collaborateurs posent leurs congés payés, RTT et congés sans solde dans NeoFlow. Le solde est vérifié avant l'envoi, les jours sont comptés en jours ouvrés, les demi-journées sont possibles et on ne peut pas poser deux fois les mêmes jours.", "product": "NeoFlow", "version": "1.1", "category": "conges", "title": "Congés : règles de dépôt"},
    {"id": 3, "content": "Le manager valide ou refuse la demande de congé. Il faut respecter un délai de prévenance raisonnable, sauf cas exceptionnels. Les soldes de référence sont dans le logiciel de paie.", "product": "NeoFlow", "version": "1.1", "category": "conges", "title": "Congés : validation"},
    {"id": 4, "content": "Gestionnaire paie : le solde ne doit être débité qu'une fois les congés intégrés dans la paie, à la clôture de fin de mois. Sinon on a des écarts entre NeoFlow et les bulletins.", "product": "NeoFlow", "version": "1.1", "category": "conges", "title": "Congés : débit du solde"},

    # Notes de frais (NF-402)
    {"id": 5, "content": "Environ 600 notes de frais papier par mois, avec les tickets agrafés. Une note de frais regroupe plusieurs dépenses : repas, hôtel, transport, kilomètres, divers.", "product": "NeoFlow", "version": "1.1", "category": "frais", "title": "Notes de frais : besoin"},
    {"id": 6, "content": "Chaque dépense est remboursée selon le barème déjà présent dans l'application, repris de l'ancien intranet et validé par la direction financière. Le justificatif est obligatoire pour toutes les dépenses, sans exception.", "product": "NeoFlow", "version": "1.1", "category": "frais", "title": "Notes de frais : barème et justificatif"},
    {"id": 7, "content": "Les dépenses de plus de trois mois ne sont pas remboursées. Le remboursement doit être exact au centime près. Une même dépense ne doit pas pouvoir être remboursée deux fois.", "product": "NeoFlow", "version": "1.1", "category": "frais", "title": "Notes de frais : délais et doublons"},
    {"id": 8, "content": "Comptable fournisseurs : pour les petites dépenses comme le parking ou les péages, on ne demande jamais le justificatif, ce serait ingérable pour tout le monde.", "product": "NeoFlow", "version": "1.1", "category": "frais", "title": "Notes de frais : parking et péages"},
    {"id": 9, "content": "Barème 2023 du calcul legacy : repas plafonné à 25,50 €, hôtel à 110 € par nuit majoré de 30 % à l'étranger, indemnité kilométrique de 0,636 € par km, autres dépenses plafonnées à 50 €, majoration de 10 % à l'étranger hors hôtel.", "product": "NeoFlow", "version": "1.0", "category": "frais", "title": "Barème de remboursement 2023"},

    # Matériel IT (NF-403)
    {"id": 10, "content": "La DSI référence un catalogue de matériel : portables, écrans, stations d'accueil, casques. Le collaborateur choisit dans le catalogue, il ne saisit pas de prix, et on ne commande pas un article retiré du catalogue.", "product": "NeoFlow", "version": "1.1", "category": "materiel", "title": "Matériel : catalogue"},
    {"id": 11, "content": "Chaque équipe a un budget matériel annuel à ne pas dépasser, consommé dès l'envoi de la demande. Un seul PC portable par personne, sauf renouvellement. Les prix du catalogue changent tous les trimestres.", "product": "NeoFlow", "version": "1.1", "category": "materiel", "title": "Matériel : budget et portable"},
    {"id": 12, "content": "Direction des achats : on ne doit compter dans le budget matériel que ce qui est validé, sinon une équipe se retrouve bloquée par des demandes qui seront refusées ensuite.", "product": "NeoFlow", "version": "1.1", "category": "materiel", "title": "Matériel : budget validé"},

    # Salles (NF-404)
    {"id": 13, "content": "Réserver une salle de réunion pour un créneau donné, par demi-heure. Impossible de réserver une salle déjà prise, et le nombre de participants doit tenir dans la salle. On indique le besoin de visio ou d'écran.", "product": "NeoFlow", "version": "1.1", "category": "salle", "title": "Salles : réservation"},
    {"id": 14, "content": "Toutes les réservations sont validées par les services généraux, mais les petites salles de moins de 6 places doivent être confirmées immédiatement. Les réunions récurrentes se réservent chaque semaine, sur tous les sites dont Saint-Denis de La Réunion.", "product": "NeoFlow", "version": "1.1", "category": "salle", "title": "Salles : validation"},

    # Formation (NF-405)
    {"id": 15, "content": "Chaque collaborateur dispose d'un budget formation de 2 500 € par an. Les formations du catalogue sont prioritaires, les formations hors catalogue sont possibles sur devis, et certaines exigent d'en avoir suivi une autre avant.", "product": "NeoFlow", "version": "1.1", "category": "formation", "title": "Formation : budget et catalogue"},
    {"id": 16, "content": "Pas plus de 3 formations par an et par personne. Une demande de formation se fait au moins trois semaines avant le début de la session. Les montants sont exprimés TTC.", "product": "NeoFlow", "version": "1.1", "category": "formation", "title": "Formation : limites et délai"},

    # Accès applicatifs (NF-406)
    {"id": 17, "content": "L'audit ISO 27001 de septembre a relevé une non-conformité majeure : impossible de dire qui a autorisé les accès à la comptabilité et à la paie. Toutes les demandes d'accès passent désormais par NeoFlow.", "product": "NeoFlow", "version": "1.1", "category": "acces", "title": "Accès : audit ISO 27001"},
    {"id": 18, "content": "La demande d'accès précise l'application et le niveau de droits : lecture, contribution ou administration. Le manager valide, les droits d'administration exigent une double validation, et personne ne valide sa propre demande.", "product": "NeoFlow", "version": "1.1", "category": "acces", "title": "Accès : niveaux et validation"},
    {"id": 19, "content": "Tous les accès sont limités dans le temps. Un collaborateur ne cumule pas des droits incompatibles, par exemple saisir en comptabilité et en paie. Tout est tracé : qui a demandé, qui a validé, quand.", "product": "NeoFlow", "version": "1.1", "category": "acces", "title": "Accès : durée et séparation"},
    {"id": 20, "content": "DSI : pour les accès en lecture, il ne faut pas imposer de date de fin, les accès en consultation sont permanents.", "product": "NeoFlow", "version": "1.1", "category": "acces", "title": "Accès : lecture permanente"},

    # Déplacements (NF-407)
    {"id": 21, "content": "Tout déplacement professionnel fait l'objet d'un ordre de mission dans NeoFlow avant le départ. Le train est la règle, l'avion seulement pour les longs trajets ou l'étranger, la voiture personnelle reste possible.", "product": "NeoFlow", "version": "1.1", "category": "deplacement", "title": "Déplacements : ordre de mission"},
    {"id": 22, "content": "L'application estime le coût du déplacement. Le collaborateur peut demander une avance sur frais, qui ne peut pas dépasser 75 % du coût estimé. Les demandes se font au moins une semaine avant le départ.", "product": "NeoFlow", "version": "1.1", "category": "deplacement", "title": "Déplacements : avance et délai"},
    {"id": 23, "content": "Certaines destinations à l'étranger sont déconseillées, voire interdites, selon les consignes de sécurité du groupe. La liste des pays est mise à jour chaque mois.", "product": "NeoFlow", "version": "1.1", "category": "deplacement", "title": "Déplacements : pays déconseillés"},
    {"id": 24, "content": "Directrice commerciale : mes commerciaux partent souvent le lendemain, quand un client les appelle. Il faut que ce soit possible sans procédure d'urgence systématique.", "product": "NeoFlow", "version": "1.1", "category": "deplacement", "title": "Déplacements : départ le lendemain"},

    # Achats (NF-408)
    {"id": 25, "content": "Tout achat hors catalogue passe par une demande NeoFlow, auprès d'un fournisseur référencé. En dessous de 1 000 € un devis suffit, au-delà de 1 000 € il en faut deux, au-delà de 5 000 € trois. Les montants sont HT.", "product": "NeoFlow", "version": "1.1", "category": "achat", "title": "Achats : devis"},
    {"id": 26, "content": "Les demandeurs ne doivent pas découper leurs achats pour passer sous les seuils. Chaque achat est imputé sur un code analytique, et le demandeur est averti si le fournisseur a une mauvaise note qualité.", "product": "NeoFlow", "version": "1.1", "category": "achat", "title": "Achats : fractionnement et analytique"},

    # Incidents (NF-409)
    {"id": 27, "content": "Le collaborateur déclare l'incident avec sa catégorie, son impact (lui seul, son équipe, tout le site) et son urgence. La priorité, de P1 à P4, est déterminée à partir de l'impact et de l'urgence.", "product": "NeoFlow", "version": "1.1", "category": "incident", "title": "Incidents : priorité"},
    {"id": 28, "content": "Un incident P1 doit être pris en charge en 30 minutes et résolu en 4 heures. Les délais courent 24 heures sur 24. Un délai dépassé déclenche une escalade automatique, et un P1 exige un numéro de téléphone.", "product": "NeoFlow", "version": "1.1", "category": "incident", "title": "Incidents : délais P1"},

    # Onboarding (NF-410)
    {"id": 29, "content": "Un nouvel arrivant sur trois n'a pas son poste ou ses accès le premier jour. Le manager crée une demande d'arrivée au moins deux semaines avant la date d'arrivée.", "product": "NeoFlow", "version": "1.1", "category": "onboarding", "title": "Onboarding : délai"},
    {"id": 30, "content": "Une fois l'arrivée validée, chaque service reçoit ses tâches : DSI pour le compte, le poste et les accès, services généraux pour le badge, RH pour le contrat et la formation sécurité, manager pour le parrain.", "product": "NeoFlow", "version": "1.1", "category": "onboarding", "title": "Onboarding : tâches par service"},

    # Niveau de validation (module legacy)
    {"id": 31, "content": "Le niveau de validation, de 1 à 3, est calculé à la soumission par RegleValidationLegacy, via CircuitValidationService, à partir du type, du montant, de l'ancienneté, du département et de l'urgence.", "product": "NeoFlow", "version": "1.0", "category": "validation", "title": "Calcul du niveau de validation"},
    {"id": 32, "content": "Notes de frais et déplacements : niveau 2 au-delà de 1 000 €, niveau 3 à partir de 5 000 €. Un collaborateur de moins de six mois d'ancienneté passe au niveau 2 (NF-112).", "product": "NeoFlow", "version": "1.0", "category": "validation", "title": "Niveaux : frais et déplacements"},
    {"id": 33, "content": "Achats : niveau 2 à partir de 1 000 €, niveau 3 au-delà de 5 000 €. Matériel informatique : niveau 2 au-delà de 1 500 €, niveau 1 pour la DSI.", "product": "NeoFlow", "version": "1.0", "category": "validation", "title": "Niveaux : achats et matériel"},
    {"id": 34, "content": "Accès applicatif : niveau 2, sauf pour la DSI qui valide ses propres accès au niveau 1. Congés : niveau 1, niveau 2 pour moins de trois mois d'ancienneté. Formation : niveau 2 si le montant avec TVA dépasse 2 400 €.", "product": "NeoFlow", "version": "1.0", "category": "validation", "title": "Niveaux : accès, congés, formation"},
    {"id": 35, "content": "Une demande urgente monte d'un niveau, sauf pour la DSI (NF-287). Règle historique de 2016 (NF-301) : le vendredi à partir de 14 h, toute demande chiffrée passe au niveau 2 minimum. Le niveau ne dépasse jamais 3.", "product": "NeoFlow", "version": "1.0", "category": "validation", "title": "Urgence et règle du vendredi"},

    # Cycle de vie et règles du socle
    {"id": 36, "content": "Une demande est créée en BROUILLON et modifiable par son auteur. Soumise, elle passe en SOUMISE. Le valideur la passe en VALIDEE ou REFUSEE, puis l'administrateur la passe en CLOTUREE.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Cycle de vie d'une demande"},
    {"id": 37, "content": "Une transition de statut non autorisée renvoie 409. Modifier une demande qui n'est plus en brouillon renvoie aussi 409. Modifier ou soumettre la demande d'un autre utilisateur renvoie 403.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Transitions refusées"},
    {"id": 38, "content": "Chaque création, soumission, validation, refus et clôture écrit une ligne dans le journal evenement_demande. La modification d'un brouillon n'est pas journalisée.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Journal d'audit"},
    {"id": 39, "content": "Le circuit du socle comporte un seul valideur, quel que soit le niveau de validation : le niveau est calculé, enregistré et affiché.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Un seul valideur"},
    {"id": 40, "content": "Chaque variante ajoute ses règles en implémentant RegleMetierDemande. Le registre applique les règles génériques puis celles du type ; des erreurs métier renvoient 422 avec la liste des erreurs.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Règles métier des variantes"},
    {"id": 41, "content": "Règle générique du socle : la date de fin, si elle est renseignée, ne précède pas la date de début, et le montant, s'il est renseigné, est strictement positif.", "product": "NeoFlow", "version": "1.0", "category": "cycle", "title": "Règle générique"},

    # API REST
    {"id": 42, "content": "GET /api/demandes renvoie la liste paginée des demandes, filtrable par statut et type. La page est numérotée à partir de 0, size va de 1 à 100, tri par date de création décroissante.", "product": "NeoFlow", "version": "1.0", "category": "api", "title": "API : liste des demandes"},
    {"id": 43, "content": "GET /api/demandes/recherche?q= recherche par titre et renvoie 50 résultats au plus, sans pagination.", "product": "NeoFlow", "version": "1.0", "category": "api", "title": "API : recherche par titre"},
    {"id": 44, "content": "POST /api/demandes crée une demande en BROUILLON, réservé au rôle DEMANDEUR. Le type, le titre (120 caractères au plus) et la date de début sont obligatoires, le montant a au plus 2 décimales.", "product": "NeoFlow", "version": "1.0", "category": "api", "title": "API : création"},
    {"id": 45, "content": "POST /api/demandes/{id}/valider est réservé au VALIDEUR, /refuser exige un corps avec un motif, /cloturer est réservé à l'ADMIN. GET /api/demandes/{id}/evenements renvoie l'historique.", "product": "NeoFlow", "version": "1.0", "category": "api", "title": "API : transitions"},
    {"id": 46, "content": "Les erreurs suivent le format ProblemDetail : 400 requête invalide, 403 accès refusé, 404 demande introuvable, 409 transition de statut invalide, 422 règles métier non respectées, 500 erreur interne avec le traceId.", "product": "NeoFlow", "version": "1.0", "category": "api", "title": "API : codes d'erreur"},

    # Sécurité, observabilité, exploitation
    {"id": 47, "content": "Authentification HTTP Basic sans session. Comptes de démonstration : alice (DEMANDEUR), bob (VALIDEUR), admin (ADMIN). Pas de hiérarchie de rôles : admin ne valide pas, bob ne crée pas.", "product": "NeoFlow", "version": "1.0", "category": "securite", "title": "Sécurité et rôles"},
    {"id": 48, "content": "Les logs sont structurés au format ECS avec traceId et spanId. Les traces partent en OTLP vers Jaeger, consultable sur le port 16686, service neoflow-backend.", "product": "NeoFlow", "version": "1.0", "category": "exploitation", "title": "Observabilité"},
    {"id": 49, "content": "Profil dev : PostgreSQL et traces vers Jaeger. Profil dev-h2 : base H2 en mémoire, pour un poste sans Docker (make backend-h2). Profil test : H2 pour les tests d'intégration.", "product": "NeoFlow", "version": "1.0", "category": "exploitation", "title": "Profils d'exécution"},
    {"id": 50, "content": "NeoFlow remplace l'intranet de 2014, les fichiers Excel et les validations par mail du Groupe Velmora : 4 000 salariés, 14 agences, environ 25 000 demandes par an.", "product": "NeoFlow", "version": "1.0", "category": "exploitation", "title": "Présentation de NeoFlow"},
]


# Golden set court : requête -> id du chunk attendu.
# Les requêtes reformulent volontairement le texte (pas de copier-coller).
GOLDEN: list[tuple[str, int]] = [
    ("Pourquoi mon solde de congés n'a pas bougé après la validation ?", 4),
    ("Je peux poser une demi-journée ?", 2),
    ("C'est combien le remboursement d'un déjeuner ?", 9),
    ("Faut-il garder le ticket de parking ?", 8),
    ("J'ai retrouvé une facture d'il y a quatre mois, elle sera remboursée ?", 7),
    ("Je voudrais un deuxième ordinateur portable", 11),
    ("Est-ce qu'une petite salle de réunion est confirmée tout de suite ?", 14),
    ("Combien de formations puis-je suivre dans l'année ?", 16),
    ("Qui doit valider un accès administrateur à la paie ?", 18),
    ("Mon accès en consultation va-t-il expirer ?", 20),
    ("Je pars demain chez un client, c'est trop tard pour la mission ?", 24),
    ("Mon avance peut-elle couvrir tout le voyage ?", 22),
    ("Combien de devis pour une prestation à 3 000 € ?", 25),
    ("Le réseau est coupé pour tout le site, en combien de temps c'est réparé ?", 28),
    ("Un nouveau arrive dans mon équipe, je dois faire la demande quand ?", 29),
    ("Pourquoi ma note de frais de 1 200 € demande deux validations ?", 32),
    ("Pourquoi ma demande du vendredi après-midi monte d'un niveau ?", 35),
    ("Je ne peux plus modifier ma demande déjà envoyée, pourquoi ?", 37),
    ("How do I list my requests through the API?", 42),
    ("What does HTTP error 422 mean in NeoFlow?", 46),
]


def get_corpus() -> list[dict]:
    return CHUNKS


def get_golden() -> list[tuple[str, int]]:
    return GOLDEN
