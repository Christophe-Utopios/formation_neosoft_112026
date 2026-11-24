from __future__ import annotations

# Maquette de l'API NeoFlow partagée entre les démos M06 (et réutilisée en M07, M08).
# Données reprises de fil-rouge/neoflow (V2__donnees_demo.sql), en mémoire, sans
# serveur : chaque fonction imite un appel REST (GET /api/demandes, POST /api/demandes...).

COLLABORATEURS: dict[str, dict] = {
    "alice": {"login": "alice", "nom": "Alice Martin", "departement": "COMMERCIAL", "date_entree": "2021-03-15"},
    "bob": {"login": "bob", "nom": "Bob Durand", "departement": "FINANCE", "date_entree": "2018-09-01"},
    "admin": {"login": "admin", "nom": "Admin NeoFlow", "departement": "DSI", "date_entree": "2016-01-04"},
    "chloe": {"login": "chloe", "nom": "Chloé Bernard", "departement": "DSI", "date_entree": "2025-06-02"},
    "karim": {"login": "karim", "nom": "Karim Haddad", "departement": "RH", "date_entree": "2023-11-20"},
    "claire": {"login": "claire", "nom": "Claire Petit", "departement": "DSI", "date_entree": "2026-07-01"},
    "david": {"login": "david", "nom": "David Moreau", "departement": "RH", "date_entree": "2019-02-18"},
    "emma": {"login": "emma", "nom": "Emma Leroy", "departement": "MARKETING", "date_entree": "2026-10-05"},
    "farid": {"login": "farid", "nom": "Farid Benali", "departement": "ACHATS", "date_entree": "2023-05-15"},
}

DEMANDES: dict[int, dict] = {
    1: {"id": 1, "demandeur": "alice", "type": "GENERIQUE", "titre": "Badge d'accès au parking B2", "montant": None, "statut": "BROUILLON", "niveau_validation": None},
    2: {"id": 2, "demandeur": "alice", "type": "NOTE_DE_FRAIS", "titre": "Déjeuner client Lyon", "montant": 86.40, "statut": "SOUMISE", "niveau_validation": 1},
    3: {"id": 3, "demandeur": "alice", "type": "MATERIEL_IT", "titre": "Second écran 27 pouces", "montant": 329.00, "statut": "VALIDEE", "niveau_validation": 1},
    4: {"id": 4, "demandeur": "alice", "type": "CONGES", "titre": "Congés de fin d'année", "montant": None, "statut": "SOUMISE", "niveau_validation": 1},
    5: {"id": 5, "demandeur": "alice", "type": "FORMATION", "titre": "Formation Kubernetes avancé", "montant": 1850.00, "statut": "REFUSEE", "niveau_validation": 1},
    6: {"id": 6, "demandeur": "alice", "type": "ACHAT", "titre": "Licences IntelliJ IDEA (5 postes)", "montant": 1250.00, "statut": "SOUMISE", "niveau_validation": 2},
    7: {"id": 7, "demandeur": "alice", "type": "DEPLACEMENT", "titre": "Mission client Nantes", "montant": 640.00, "statut": "BROUILLON", "niveau_validation": None},
    8: {"id": 8, "demandeur": "alice", "type": "INCIDENT", "titre": "VPN inaccessible depuis le site de Lille", "montant": None, "statut": "SOUMISE", "niveau_validation": 2},
    9: {"id": 9, "demandeur": "alice", "type": "RESERVATION_SALLE", "titre": "Salle Everest pour l'atelier de cadrage", "montant": None, "statut": "CLOTUREE", "niveau_validation": 1},
    10: {"id": 10, "demandeur": "alice", "type": "ACCES_APPLICATIF", "titre": "Accès en lecture au CRM", "montant": None, "statut": "SOUMISE", "niveau_validation": 2},
    11: {"id": 11, "demandeur": "alice", "type": "ONBOARDING", "titre": "Arrivée d'Emma Leroy (Marketing)", "montant": None, "statut": "VALIDEE", "niveau_validation": 1},
    12: {"id": 12, "demandeur": "alice", "type": "NOTE_DE_FRAIS", "titre": "Hôtel salon Vivatech", "montant": 412.50, "statut": "CLOTUREE", "niveau_validation": 1},
}


def trouver_collaborateur(nom: str) -> dict | None:
    """Recherche un collaborateur par login ou par nom (exact ou contenant)."""
    nom_lower = nom.lower()
    for c in COLLABORATEURS.values():
        if nom_lower in (c["login"], c["nom"].lower()) or nom_lower in c["nom"].lower():
            return c
    return None


def get_collaborateur(login: str) -> dict | None:
    return COLLABORATEURS.get(login)


def compter_demandes(login: str, statut: str = "SOUMISE") -> int:
    return sum(1 for d in DEMANDES.values() if d["demandeur"] == login and d["statut"] == statut)


def lister_demandes(login: str, statut: str = "SOUMISE") -> list[dict]:
    return [d for d in DEMANDES.values() if d["demandeur"] == login and d["statut"] == statut]


def creer_brouillon(login: str, type_demande: str, titre: str, montant: float | None = None) -> dict:
    new_id = max(DEMANDES) + 1 if max(DEMANDES) >= 100 else 100
    demande = {"id": new_id, "demandeur": login, "type": type_demande, "titre": titre,
               "montant": montant, "statut": "BROUILLON", "niveau_validation": None}
    DEMANDES[new_id] = demande
    return demande
