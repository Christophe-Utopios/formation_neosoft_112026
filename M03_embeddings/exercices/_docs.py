from __future__ import annotations

# Documents longs de la base de connaissances Velora (format Markdown),
# utilisés pour comparer les stratégies de chunking.

DOCS: list[dict] = [
    {
        "doc_id": "guide-sso",
        "title": "Guide d'administration : authentification et SSO",
        "product": "Velora",
        "version": "3.2",
        "text": """# Guide d'administration : authentification et SSO

## Introduction

Ce guide s'adresse aux administrateurs Velora qui doivent connecter la plateforme au fournisseur d'identité de leur entreprise. Il couvre SAML 2.0, OpenID Connect, LDAP et l'authentification multi-facteurs. Les captures d'écran correspondent à la version 3.2 ; les menus de la version 3.0 sont légèrement différents mais les champs restent identiques.

Avant de commencer, vérifiez que vous disposez du rôle Administrateur de l'organisation. Le rôle Administrateur d'espace ne suffit pas pour modifier la configuration d'authentification.

## Choisir un protocole

Velora accepte trois protocoles de fédération. SAML 2.0 reste le plus répandu dans les grands comptes, notamment avec ADFS et les anciennes versions d'Okta. OpenID Connect est plus simple à configurer et c'est le choix recommandé pour tout nouveau déploiement. LDAP n'est conservé que pour les annuaires sur site qui ne peuvent pas exposer de fédération.

Un seul protocole peut être actif comme protocole principal. Pendant une migration, il est possible d'activer un second protocole en mode secours pendant 30 jours au maximum.

## Configurer SAML 2.0

Ouvrez Paramètres > Authentification > SAML. Renseignez l'URL de métadonnées de votre fournisseur d'identité. Si votre fournisseur ne publie pas d'URL de métadonnées, saisissez manuellement l'URL SSO, l'Entity ID et collez le certificat X.509 au format PEM.

Côté fournisseur d'identité, l'URL ACS à déclarer est https://auth.velora.io/saml/acs et l'audience attendue est urn:velora:sp. L'attribut NameID doit contenir l'adresse e-mail professionnelle de l'utilisateur, sinon la correspondance avec les comptes existants échoue.

Le certificat X.509 du fournisseur expire en général au bout d'un à trois ans. Velora envoie une alerte aux administrateurs 30 jours avant l'expiration du certificat. Pour un renouvellement sans coupure, ajoutez le nouveau certificat en certificat secondaire, puis basculez-le en principal une fois que le fournisseur signe avec lui.

## Configurer OpenID Connect

Ouvrez Paramètres > Authentification > OIDC. Saisissez l'issuer, le client_id et le client_secret fournis par votre fournisseur d'identité. Velora découvre automatiquement les autres points de terminaison via le document .well-known/openid-configuration.

L'URI de redirection à autoriser chez le fournisseur est https://auth.velora.io/oidc/callback. Les scopes demandés sont openid, email et profile. Le scope groups est optionnel et permet de synchroniser les groupes du fournisseur avec les rôles Velora.

## Configurer LDAP

La connexion LDAP nécessite un compte de service en lecture seule sur l'annuaire. Le Bind DN prend la forme CN=svc_velora,OU=Services,DC=entreprise,DC=fr. Utilisez de préférence LDAPS sur le port 636 ; le port 389 en clair est refusé par défaut depuis la version 3.1.

Le filtre de recherche par défaut est (&(objectClass=person)(mail={email})). La synchronisation des comptes s'exécute toutes les 4 heures et peut être lancée manuellement depuis la page de configuration.

## Authentification multi-facteurs

La MFA peut être rendue obligatoire pour toute l'organisation dans Paramètres > Sécurité > MFA obligatoire. Les méthodes acceptées sont les applications TOTP et les clés de sécurité FIDO2. Les SMS ne sont plus acceptés depuis janvier 2026 pour des raisons de sécurité.

Lorsqu'un utilisateur perd son second facteur, un administrateur peut générer un code de récupération à usage unique valable 24 heures depuis la fiche de l'utilisateur.

## Dépannage

Erreur « Invalid audience » : l'audience déclarée chez le fournisseur ne correspond pas à urn:velora:sp. Erreur « Clock skew » : l'horloge du fournisseur d'identité est décalée de plus de 5 minutes, synchronisez-la avec un serveur NTP. Boucle de redirection infinie : les cookies tiers sont bloqués par le navigateur, ajoutez auth.velora.io aux exceptions.
""",
    },
    {
        "doc_id": "guide-api",
        "title": "Référence développeur : API REST v3",
        "product": "Velora",
        "version": "3.2",
        "text": """# Référence développeur : API REST v3

## Vue d'ensemble

L'API REST v3 expose toutes les fonctions de Velora accessibles depuis l'interface. Les réponses sont au format JSON et encodées en UTF-8. La documentation interactive est publiée sur api.velora.io/docs et générée à partir de la spécification OpenAPI 3.1.

L'URL de base est https://api.velora.io/v3. Les appels sans TLS sont refusés.

## Authentification

Chaque requête doit porter un jeton dans l'en-tête Authorization sous la forme Bearer <token>. Les jetons d'accès ont une durée de vie de 15 minutes. Le jeton de rafraîchissement, lui, reste valable 30 jours et permet d'obtenir un nouveau jeton d'accès sans redemander les identifiants.

Pour les intégrations serveur à serveur, créez plutôt un jeton de service dans Paramètres > Intégrations > Jetons de service. Un jeton de service n'expire pas mais peut être révoqué à tout moment, et il est limité aux scopes choisis à sa création.

## Limites de débit

Chaque jeton est limité à 100 requêtes par minute, et chaque organisation à 1 000 requêtes par minute tous jetons confondus. Au-delà, l'API répond 429 Too Many Requests avec un en-tête Retry-After exprimé en secondes.

Les en-têtes X-RateLimit-Remaining et X-RateLimit-Reset sont renvoyés sur chaque réponse pour permettre aux clients de ralentir avant d'atteindre la limite.

## Pagination

Les listes sont paginées. La pagination par curseur est recommandée : passez la valeur du champ next_cursor de la réponse précédente dans le paramètre after. La pagination par offset avec page et page_size reste disponible mais devient lente au-delà de 10 000 lignes. La taille de page maximale est de 100 éléments.

## Exports en masse

Pour extraire de gros volumes, utilisez POST /v3/exports avec le paramètre format valant csv, json ou parquet. L'export est asynchrone : la réponse contient un identifiant de tâche, et GET /v3/exports/{id} renvoie l'état. Une fois l'export terminé, la réponse contient une URL signée valable une heure.

Un même compte ne peut pas lancer plus de 3 exports simultanés.

## Webhooks

Les webhooks se déclarent dans Paramètres > Intégrations > Webhooks avec une URL HTTPS. Les événements disponibles sont user.created, user.deleted, document.updated et alert.triggered. Chaque appel est signé par un HMAC SHA-256 transmis dans l'en-tête X-Signature ; vérifiez toujours cette signature avant de traiter le message.

En cas d'échec de livraison, Velora retente l'envoi 5 fois avec un délai croissant, puis désactive le webhook après 24 heures d'échecs consécutifs.

## Codes d'erreur

401 : jeton expiré ou invalide. 403 : droits insuffisants sur la ressource. 404 : ressource inexistante ou invisible pour ce jeton. 409 : conflit de version, la ressource a été modifiée entre la lecture et l'écriture. 429 : limite de débit atteinte. 503 : service temporairement surchargé, réessayez avec un backoff exponentiel.

Chaque réponse contient un en-tête X-Request-Id à communiquer au support pour toute investigation.
""",
    },
    {
        "doc_id": "guide-facturation",
        "title": "Facturation, plans et paiements",
        "product": "Velora",
        "version": "3.2",
        "text": """# Facturation, plans et paiements

## Les plans disponibles

Velora propose trois plans. Le plan Standard couvre jusqu'à 100 utilisateurs et 10 Go de stockage par utilisateur. Le plan Pro monte à 1 000 utilisateurs et ajoute les workflows personnalisés. Le plan Enterprise n'a pas de limite d'utilisateurs et inclut les clés de chiffrement gérées par le client, l'endpoint Prometheus et une rétention étendue des journaux.

## Comment la facture est calculée

La facturation est mensuelle et se fait au prorata des utilisateurs actifs. Un utilisateur est considéré comme actif s'il s'est connecté au moins une fois pendant le mois civil. Un compte jamais utilisé n'est donc pas facturé, mais il occupe une place dans la limite du plan.

Pour réduire la facture, désactivez les comptes des collaborateurs partis : un compte désactivé n'est ni facturé ni compté dans la limite.

## Changer de plan

Le changement se fait dans Paramètres > Facturation > Changer de plan. Une montée en gamme prend effet immédiatement et la différence est facturée au prorata des jours restants. Une descente en gamme prend effet à la prochaine date de facturation, pour ne pas couper des fonctions en cours de mois.

## Moyens de paiement

Les cartes Visa, Mastercard et American Express sont acceptées, ainsi que le prélèvement SEPA. Le virement bancaire est réservé au plan Enterprise avec un paiement à 30 jours fin de mois.

En cas d'échec de paiement par carte, trois nouvelles tentatives ont lieu sur 10 jours. Sans régularisation, l'organisation passe en lecture seule au 15e jour, puis est suspendue au 45e jour.

## Factures et informations fiscales

Les factures sont envoyées par e-mail à l'adresse de facturation et restent téléchargeables en PDF dans Paramètres > Facturation > Historique, sur les 7 dernières années.

Le numéro de TVA intracommunautaire se renseigne dans Paramètres > Organisation > Informations fiscales. Il est vérifié automatiquement auprès du service VIES de la Commission européenne ; en cas d'échec de vérification, la TVA française à 20 % est appliquée par défaut.

## Remboursements

Les paiements mensuels ne sont pas remboursables. Les paiements annuels peuvent être remboursés au prorata dans les 30 jours suivant le paiement, sur demande au support.
""",
    },
    {
        "doc_id": "guide-securite",
        "title": "Sécurité, conformité et sauvegardes",
        "product": "Velora",
        "version": "3.2",
        "text": """# Sécurité, conformité et sauvegardes

## Hébergement et localisation des données

Velora est hébergé en France, dans les datacenters OVHcloud de Roubaix avec un site de secours à Strasbourg. Les données ne quittent jamais l'Union européenne, y compris pour les sauvegardes et les journaux techniques.

La plateforme est certifiée ISO 27001 et qualifiée HDS pour l'hébergement de données de santé sur le plan Enterprise.

## Chiffrement

Les données sont chiffrées au repos en AES-256 et en transit en TLS 1.3. Sur le plan Enterprise, l'organisation peut fournir ses propres clés (Customer-Managed Keys) via un KMS compatible ; la révocation de la clé rend les données illisibles en moins de 5 minutes.

## RGPD

Un accord de traitement des données (DPA) peut être signé électroniquement dans Paramètres > Conformité. Le droit à l'effacement est appliqué sous 30 jours après la suppression d'un compte. Le droit à la portabilité est assuré par l'export complet des données d'un utilisateur, livré sous forme d'archive ZIP par e-mail en moins de 24 heures.

## Journaux d'audit

Toutes les connexions, lectures de documents sensibles et modifications de configuration sont enregistrées dans le journal d'audit. La rétention est de 12 mois sur les plans Standard et Pro, et de 24 mois sur Enterprise. Le journal est exportable au format JSON Lines via l'API ou depuis l'interface, et peut être poussé vers un SIEM par syslog.

## Sauvegardes et restauration

Une sauvegarde incrémentale est réalisée chaque nuit et une sauvegarde complète chaque dimanche. Les sauvegardes sont conservées 30 jours, ou 90 jours sur le plan Enterprise.

La restauration à un instant donné (point-in-time) est possible à la minute près sur les 7 derniers jours. Elle se demande au support et s'effectue dans une organisation de recette, pour ne jamais écraser les données de production sans validation.

## Tests d'intrusion et divulgation

Un test d'intrusion externe est mené deux fois par an. Les synthèses sont disponibles sous accord de confidentialité. Les chercheurs en sécurité peuvent signaler une vulnérabilité à security@velora.io ; le programme de divulgation coordonnée prévoit une réponse sous 72 heures.
""",
    },
    {
        "doc_id": "guide-rapports",
        "title": "Rapports et tableaux de bord",
        "product": "Velora",
        "version": "3.1",
        "text": """# Rapports et tableaux de bord

## Créer un rapport

Un rapport se crée depuis Rapports > Nouveau. Choisissez une source de données, les indicateurs, puis la période. Les rapports peuvent être ponctuels ou planifiés.

## Rapports planifiés

Le modèle hebdomadaire envoie le rapport chaque lundi à 8 h par défaut. Le jour, l'heure et la liste des destinataires se modifient dans l'onglet Planification. Les heures s'entendent dans le fuseau horaire de l'organisation, réglé par défaut sur Europe/Paris dans Paramètres > Organisation.

Un rapport planifié dont le propriétaire est désactivé continue d'être envoyé pendant 30 jours, puis est mis en pause. Pensez à transférer la propriété des rapports avant le départ d'un collaborateur.

## Formats d'export

Les rapports s'exportent en PDF, XLSX ou CSV. Le PDF inclut les graphiques et un filigrane au nom de l'organisation. Le XLSX conserve les formules pour permettre l'analyse hors ligne. Le CSV n'exporte que les données brutes, sans mise en forme.

## Partager un rapport

Un rapport peut être partagé avec une personne extérieure par un lien public. Le lien porte obligatoirement une date d'expiration, de 90 jours au maximum. Un mot de passe peut être ajouté ; il est fortement recommandé dès que le rapport contient des données personnelles.

## Le rapport n'est pas arrivé

Vérifiez d'abord que les destinataires sont toujours actifs. Consultez ensuite les journaux d'envoi dans Paramètres > Logs > Email. Les rejets temporaires (boîte pleine, serveur indisponible) sont retentés 3 fois sur 24 heures. Les rejets définitifs retirent automatiquement l'adresse de la liste après 3 échecs.

## Limites

Un rapport ne peut pas dépasser 500 000 lignes de données source. Au-delà, utilisez l'export en masse de l'API. Le calcul d'un rapport est interrompu au bout de 10 minutes ; le service répond alors une erreur 503 sur /api/reports et il faut réduire la période ou ajouter des filtres.
""",
    },
    {
        "doc_id": "guide-mobile-cli",
        "title": "Application mobile et outil en ligne de commande",
        "product": "Velora Mobile",
        "version": "2.5",
        "text": """# Application mobile et outil en ligne de commande

## Application mobile

L'application Velora Mobile est disponible sur iOS 16 et plus, et sur Android 12 et plus. Elle se télécharge uniquement depuis l'App Store et le Google Play Store ; aucun APK n'est distribué en dehors du store.

La connexion utilise le même SSO que l'application web. Si la MFA est obligatoire dans l'organisation, elle l'est aussi sur mobile.

## Mode hors ligne

Les documents consultés au cours des 7 derniers jours restent accessibles sans connexion. Les modifications faites hors ligne sont synchronisées au retour du réseau ; en cas de conflit, la version du serveur est conservée et la version mobile est enregistrée comme copie.

## Notifications

Les notifications push se règlent dans l'application, menu Paramètres > Notifications, par type d'événement : alertes, mentions et rapports. Ces réglages sont propres à chaque utilisateur et ne sont pas synchronisés avec les préférences e-mail.

## Outil en ligne de commande

velora-cli s'installe avec Homebrew sur macOS (brew install velora-cli), avec apt sur Debian et Ubuntu, ou en téléchargeant le binaire depuis le portail support pour Windows. La version actuelle est la 1.5.

L'authentification se fait avec velora-cli login, qui ouvre le navigateur pour le SSO puis stocke un jeton dans le trousseau du système.

## Commandes courantes

velora-cli users list affiche les utilisateurs de l'organisation. velora-cli reports export --id <id> télécharge un rapport. velora-cli backup create déclenche une sauvegarde manuelle, limitée à une par jour. L'option --json rend toutes les sorties exploitables par script.

## Mise à jour

La CLI vérifie à chaque lancement si une nouvelle version existe et affiche un avertissement. La commande velora-cli self-update installe la dernière version stable.
""",
    },
]


# Golden set pour le chunking : la réponse est considérée comme trouvée si un
# des chunks retournés contient la phrase "needle" (sous-chaîne exacte du doc).
CHUNK_GOLDEN: list[dict] = [
    {"q": "Quelle URL ACS déclarer chez le fournisseur SAML ?", "doc_id": "guide-sso", "needle": "https://auth.velora.io/saml/acs"},
    {"q": "Quand est-on prévenu de l'expiration du certificat du fournisseur d'identité ?", "doc_id": "guide-sso", "needle": "30 jours avant l'expiration du certificat"},
    {"q": "Peut-on encore utiliser le port 389 pour l'annuaire ?", "doc_id": "guide-sso", "needle": "le port 389 en clair est refusé par défaut"},
    {"q": "Les codes par SMS sont-ils acceptés pour la double authentification ?", "doc_id": "guide-sso", "needle": "Les SMS ne sont plus acceptés"},
    {"q": "Que faire en cas d'erreur de décalage d'horloge à la connexion ?", "doc_id": "guide-sso", "needle": "décalée de plus de 5 minutes"},
    {"q": "Combien de temps reste valable le refresh token ?", "doc_id": "guide-api", "needle": "reste valable 30 jours"},
    {"q": "Comment savoir combien de requêtes il me reste avant d'être bloqué ?", "doc_id": "guide-api", "needle": "X-RateLimit-Remaining"},
    {"q": "Combien d'exports peut-on lancer en parallèle ?", "doc_id": "guide-api", "needle": "plus de 3 exports simultanés"},
    {"q": "Que se passe-t-il si mon endpoint de webhook est en panne ?", "doc_id": "guide-api", "needle": "désactive le webhook après 24 heures"},
    {"q": "Que signifie une erreur 409 ?", "doc_id": "guide-api", "needle": "409 : conflit de version"},
    {"q": "Est-ce qu'un compte jamais utilisé est facturé ?", "doc_id": "guide-facturation", "needle": "Un compte jamais utilisé n'est donc pas facturé"},
    {"q": "Que se passe-t-il si la carte bancaire est refusée ?", "doc_id": "guide-facturation", "needle": "passe en lecture seule au 15e jour"},
    {"q": "Quelle TVA si mon numéro intracommunautaire n'est pas validé ?", "doc_id": "guide-facturation", "needle": "la TVA française à 20 % est appliquée"},
    {"q": "Puis-je être remboursé d'un abonnement annuel ?", "doc_id": "guide-facturation", "needle": "remboursés au prorata dans les 30 jours"},
    {"q": "Où se trouve le site de secours ?", "doc_id": "guide-securite", "needle": "un site de secours à Strasbourg"},
    {"q": "Que se passe-t-il si on révoque notre propre clé de chiffrement ?", "doc_id": "guide-securite", "needle": "illisibles en moins de 5 minutes"},
    {"q": "Peut-on restaurer les données à une minute précise ?", "doc_id": "guide-securite", "needle": "à la minute près sur les 7 derniers jours"},
    {"q": "Où signaler une faille de sécurité ?", "doc_id": "guide-securite", "needle": "security@velora.io"},
    {"q": "Que devient un rapport planifié quand son propriétaire quitte l'entreprise ?", "doc_id": "guide-rapports", "needle": "continue d'être envoyé pendant 30 jours"},
    {"q": "Durée maximale d'un lien de partage public ?", "doc_id": "guide-rapports", "needle": "de 90 jours au maximum"},
    {"q": "Pourquoi mon rapport renvoie une erreur 503 ?", "doc_id": "guide-rapports", "needle": "interrompu au bout de 10 minutes"},
    {"q": "Que devient une modification faite hors ligne en cas de conflit ?", "doc_id": "guide-mobile-cli", "needle": "la version du serveur est conservée"},
    {"q": "Peut-on installer l'application Android hors du store ?", "doc_id": "guide-mobile-cli", "needle": "aucun APK n'est distribué"},
    {"q": "Comment mettre à jour l'outil en ligne de commande ?", "doc_id": "guide-mobile-cli", "needle": "velora-cli self-update"},
]


def get_docs() -> list[dict]:
    return DOCS


def get_chunk_golden() -> list[dict]:
    # Vérifie que chaque needle existe bien dans son document
    by_id = {d["doc_id"]: d["text"] for d in DOCS}
    for g in CHUNK_GOLDEN:
        assert g["needle"] in by_id[g["doc_id"]], g["needle"]
    return CHUNK_GOLDEN
