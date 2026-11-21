# tournoi.py -- Organisation d'un tournoi sportif (Sujet 3)
# Application en console : inscrire des equipes, generer le calendrier,
# enregistrer les scores et afficher le classement.


import json
import os
from datetime import datetime


# Le fichier de sauvegarde (dans le meme dossier que le programme).
FICHIER_DONNEES = "tournoi.json"

VICTOIRE_POINTS = 3
NUL_POINTS = 1
DEFAITE_POINTS = 0

MIN_JOUEURS = 5
MAX_JOUEURS = 11

POSTES = ["Gardien", "Defenseur", "Milieu", "Attaquant"]


class Joueur:

    def __init__(self, identifiant, nom, poste, numero):
        self.id = identifiant
        self.nom = nom
        self.poste = poste
        self.numero = numero

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "poste": self.poste,
            "numero": self.numero,
        }

    @classmethod
    def from_dict(cls, donnees):
        return cls(donnees["id"], donnees["nom"],
                   donnees["poste"], donnees["numero"])

    def __str__(self):
        return f"{self.nom} ({self.poste}, n°{self.numero})"


class Equipe:

    def __init__(self, identifiant, nom):
        self.id = identifiant
        self.nom = nom
        # Liste des joueurs : on passe par les methodes pour la modifier.
        self._joueurs = []

    def ajouter_joueur(self, joueur):
        if len(self._joueurs) >= MAX_JOUEURS:
            raise ValueError(
                f"L'equipe {self.nom} est complete "
                f"({MAX_JOUEURS} joueurs maximum).")
        for autre in self._joueurs:
            if autre.numero == joueur.numero:
                raise ValueError(
                    f"Le numero {joueur.numero} est deja pris dans "
                    f"l'equipe {self.nom} ({autre.nom}).")
        self._joueurs.append(joueur)

    def joueurs(self):
        return list(self._joueurs)

    def effectif(self):
        return len(self._joueurs)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "joueurs": [joueur.to_dict() for joueur in self._joueurs],
        }

    @classmethod
    def from_dict(cls, donnees):
        equipe = cls(donnees["id"], donnees["nom"])
        for donnees_joueur in donnees["joueurs"]:
            equipe._joueurs.append(Joueur.from_dict(donnees_joueur))
        return equipe

    def __str__(self):
        return f"{self.nom} ({self.effectif()} joueurs)"


class Match:

    def __init__(self, identifiant, id_equipe_domicile,
                 id_equipe_exterieur, journee):
        self.id = identifiant
        self.id_equipe_domicile = id_equipe_domicile
        self.id_equipe_exterieur = id_equipe_exterieur
        self.journee = journee
        self.score_domicile = None
        self.score_exterieur = None
        self.joue = False

    def enregistrer_score(self, score_domicile, score_exterieur):
        if self.joue:
            raise ValueError(
                "Ce match a deja ete joue. Utilisez la correction "
                "de score pour le modifier.")
        self._verifier_scores(score_domicile, score_exterieur)
        self.score_domicile = score_domicile
        self.score_exterieur = score_exterieur
        self.joue = True

    def corriger_score(self, score_domicile, score_exterieur):
        if not self.joue:
            raise ValueError(
                "Ce match n'a pas encore ete joue. Utilisez "
                "l'enregistrement de score.")
        self._verifier_scores(score_domicile, score_exterieur)
        self.score_domicile = score_domicile
        self.score_exterieur = score_exterieur

    def _verifier_scores(self, score_domicile, score_exterieur):
        for score in (score_domicile, score_exterieur):
            if not isinstance(score, int):
                raise ValueError("Les scores doivent etre des nombres entiers.")
            if score < 0:
                raise ValueError("Un score ne peut pas etre negatif.")

    def to_dict(self):
        return {
            "id": self.id,
            "id_equipe_domicile": self.id_equipe_domicile,
            "id_equipe_exterieur": self.id_equipe_exterieur,
            "journee": self.journee,
            "score_domicile": self.score_domicile,
            "score_exterieur": self.score_exterieur,
            "joue": self.joue,
        }

    @classmethod
    def from_dict(cls, donnees):
        match = cls(donnees["id"], donnees["id_equipe_domicile"],
                    donnees["id_equipe_exterieur"], donnees["journee"])
        match.score_domicile = donnees["score_domicile"]
        match.score_exterieur = donnees["score_exterieur"]
        match.joue = donnees["joue"]
        return match


class Tournoi:

    def __init__(self, nom="Mon tournoi"):
        self.nom = nom
        self.equipes = []
        self.matchs = []
        # Compteurs pour les identifiants (sauvegardes aussi).
        self.prochain_id_equipe = 1
        self.prochain_id_joueur = 1
        self.prochain_id_match = 1

    def trouver_equipe(self, identifiant):
        for equipe in self.equipes:
            if equipe.id == identifiant:
                return equipe
        return None

    def trouver_match(self, identifiant):
        for match in self.matchs:
            if match.id == identifiant:
                return match
        return None

    def nom_equipe(self, identifiant):
        equipe = self.trouver_equipe(identifiant)
        if equipe is None:
            return "?"
        return equipe.nom

    def inscrire_equipe(self, nom):
        nom = nom.strip()
        if not nom:
            raise ValueError("Le nom de l'equipe ne peut pas etre vide.")
        for equipe in self.equipes:
            if equipe.nom.lower() == nom.lower():
                raise ValueError(
                    f"L'equipe « {nom} » est deja inscrite.")
        equipe = Equipe(self.prochain_id_equipe, nom)
        self.prochain_id_equipe += 1
        self.equipes.append(equipe)
        self.sauvegarder()
        return equipe

    def ajouter_joueur(self, id_equipe, nom, poste, numero):
        equipe = self.trouver_equipe(id_equipe)
        if equipe is None:
            raise ValueError("Equipe introuvable.")
        if poste not in POSTES:
            raise ValueError("Poste invalide. Postes possibles : "
                             + ", ".join(POSTES) + ".")
        if not isinstance(numero, int):
            raise ValueError("Le numero doit etre un nombre entier.")
        if numero < 1 or numero > 99:
            raise ValueError("Le numero doit etre entre 1 et 99.")
        joueur = Joueur(self.prochain_id_joueur, nom.strip(), poste, numero)
        # La verification des regles (effectif, numero) se fait dans
        # ajouter_joueur de l'equipe, avant toute modification.
        equipe.ajouter_joueur(joueur)
        self.prochain_id_joueur += 1
        self.sauvegarder()
        return joueur

    def generer_calendrier(self, confirmer_regeneration=False):
        if len(self.equipes) < 2:
            raise ValueError(
                "Il faut au moins 2 equipes pour generer le calendrier.")
        for equipe in self.equipes:
            if equipe.effectif() < MIN_JOUEURS:
                raise ValueError(
                    f"L'equipe {equipe.nom} n'a que "
                    f"{equipe.effectif()} joueurs (minimum "
                    f"{MIN_JOUEURS}).")
        if self.matchs:
            deja_joue = False
            for match in self.matchs:
                if match.joue:
                    deja_joue = True
            if deja_joue:
                raise ValueError(
                    "Le calendrier ne peut pas etre regenere : "
                    "des matchs ont deja ete joues.")
            if not confirmer_regeneration:
                raise ValueError(
                    "Un calendrier existe deja. Confirmez la "
                    "regeneration pour remplacer les matchs non joues.")

        # On efface l'ancien calendrier (aucun match joue a ce stade).
        self.matchs = []

        equipes = []
        for equipe in self.equipes:
            equipes.append(equipe.id)
        if len(equipes) % 2 == 1:
            equipes.append(None)  # None = equipe exemptee
        nombre = len(equipes)
        nombre_journees = nombre - 1

        for journee in range(1, nombre_journees + 1):
            for i in range(nombre // 2):
                domicile = equipes[i]
                exterieur = equipes[nombre - 1 - i]
                if domicile is None or exterieur is None:
                    continue  # une equipe exemptee ce creneau-ci
                match = Match(self.prochain_id_match,
                              domicile, exterieur, journee)
                self.prochain_id_match += 1
                self.matchs.append(match)
            # Rotation du cercle : la premiere equipe reste fixe,
            # les autres tournent d'un cran.
            equipes = [equipes[0]] + [equipes[-1]] + equipes[1:-1]

        self.sauvegarder()
        return len(self.matchs), nombre_journees

    def enregistrer_score(self, id_match, score_domicile, score_exterieur):
        match = self.trouver_match(id_match)
        if match is None:
            raise ValueError("Match introuvable.")
        # Toutes les verifications sont faites dans la methode du
        # match, avant toute modification des donnees.
        match.enregistrer_score(score_domicile, score_exterieur)
        self.sauvegarder()
        return match

    def corriger_score(self, id_match, score_domicile, score_exterieur):
        match = self.trouver_match(id_match)
        if match is None:
            raise ValueError("Match introuvable.")
        match.corriger_score(score_domicile, score_exterieur)
        self.sauvegarder()
        return match

    def classement(self):
        stats = {}
        for equipe in self.equipes:
            stats[equipe.id] = {
                "equipe": equipe,
                "points": 0,
                "joues": 0,
                "gagnes": 0,
                "nuls": 0,
                "perdus": 0,
                "buts_pour": 0,
                "buts_contre": 0,
                "difference": 0,
            }
        for match in self.matchs:
            if not match.joue:
                continue
            dom = stats[match.id_equipe_domicile]
            ext = stats[match.id_equipe_exterieur]
            dom["joues"] += 1
            ext["joues"] += 1
            dom["buts_pour"] += match.score_domicile
            dom["buts_contre"] += match.score_exterieur
            ext["buts_pour"] += match.score_exterieur
            ext["buts_contre"] += match.score_domicile
            if match.score_domicile > match.score_exterieur:
                dom["points"] += VICTOIRE_POINTS
                dom["gagnes"] += 1
                ext["perdus"] += 1
            elif match.score_domicile < match.score_exterieur:
                ext["points"] += VICTOIRE_POINTS
                ext["gagnes"] += 1
                dom["perdus"] += 1
            else:
                dom["points"] += NUL_POINTS
                ext["points"] += NUL_POINTS
                dom["nuls"] += 1
                ext["nuls"] += 1
        for ligne in stats.values():
            ligne["difference"] = (ligne["buts_pour"]
                                   - ligne["buts_contre"])
        # Tri : points, puis difference de buts, puis buts marques,
        # puis nom (pour un affichage stable).
        lignes = sorted(stats.values(),
                        key=lambda l: (-l["points"], -l["difference"],
                                       -l["buts_pour"],
                                       l["equipe"].nom))
        return lignes

    def matchs_restants(self):
        restants = []
        for match in self.matchs:
            if not match.joue:
                restants.append(match)
        restants.sort(key=lambda m: (m.journee, m.id))
        return restants

    def equipes_triees(self):
        return sorted(self.equipes, key=lambda e: e.nom.lower())

    def match_texte(self, match):
        dom = self.nom_equipe(match.id_equipe_domicile)
        ext = self.nom_equipe(match.id_equipe_exterieur)
        if match.joue:
            return (f"J{match.journee} - {dom} {match.score_domicile} - "
                    f"{match.score_exterieur} {ext}")
        return f"J{match.journee} - {dom} contre {ext} (a jouer)"

    def to_dict(self):
        equipes_liste = []
        for equipe in self.equipes:
            equipes_liste.append(equipe.to_dict())
        matchs_liste = []
        for match in self.matchs:
            matchs_liste.append(match.to_dict())
        return {
            "nom": self.nom,
            "prochain_id_equipe": self.prochain_id_equipe,
            "prochain_id_joueur": self.prochain_id_joueur,
            "prochain_id_match": self.prochain_id_match,
            "equipes": equipes_liste,
            "matchs": matchs_liste,
        }

    @classmethod
    def from_dict(cls, donnees):
        tournoi = cls(donnees.get("nom", "Mon tournoi"))
        tournoi.prochain_id_equipe = donnees["prochain_id_equipe"]
        tournoi.prochain_id_joueur = donnees["prochain_id_joueur"]
        tournoi.prochain_id_match = donnees["prochain_id_match"]
        for donnees_equipe in donnees["equipes"]:
            tournoi.equipes.append(Equipe.from_dict(donnees_equipe))
        for donnees_match in donnees["matchs"]:
            tournoi.matchs.append(Match.from_dict(donnees_match))
        return tournoi

    def sauvegarder(self):
        with open(FICHIER_DONNEES, "w", encoding="utf-8") as fichier:
            json.dump(self.to_dict(), fichier, ensure_ascii=False, indent=2)


def charger_tournoi():
    if not os.path.exists(FICHIER_DONNEES):
        print("Aucune donnee trouvee : on commence un nouveau tournoi.")
        return Tournoi()
    try:
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
        tournoi = Tournoi.from_dict(donnees)
        print(f"Donnees chargees : {len(tournoi.equipes)} equipes, "
              f"{len(tournoi.matchs)} matchs.")
        return tournoi
    except Exception:
        horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
        sauvegarde = f"{FICHIER_DONNEES}.corrompu-{horodatage}"
        os.rename(FICHIER_DONNEES, sauvegarde)
        print("Le fichier de donnees est invalide ou incomplet.")
        print(f"Il a ete conserve sous le nom : {sauvegarde}")
        print("On demarre un tournoi vide.")
        return Tournoi()


# Fonctions pour demander des choses a l'utilisateur

def demander_texte(message):
    while True:
        texte = input(message).strip()
        if texte:
            return texte
        print("La saisie ne peut pas etre vide. Reessayez.")


def demander_entier(message, minimum=None, maximum=None):
    while True:
        texte = input(message).strip()
        try:
            valeur = int(texte)
        except ValueError:
            print("Veuillez entrer un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"Le nombre doit etre au moins {minimum}.")
            continue
        if maximum is not None and valeur > maximum:
            print(f"Le nombre doit etre au plus {maximum}.")
            continue
        return valeur


def demander_choix(message, choix_possibles):
    while True:
        valeur = demander_entier(message)
        if valeur in choix_possibles:
            return valeur
        print(f"Choix invalide. Choix possibles : {choix_possibles}.")


def afficher_titre(tournoi):
    print()
    print("=" * 60)
    print(f"  TOURNOI : {tournoi.nom}")
    print("=" * 60)
    joues = 0
    for match in tournoi.matchs:
        if match.joue:
            joues += 1
    print(f"  Equipes : {len(tournoi.equipes)}  |  "
          f"Matchs : {joues}/{len(tournoi.matchs)} joues")
    print("=" * 60)


def afficher_menu():
    print()
    print("  1. Inscrire une equipe")
    print("  2. Ajouter un joueur a une equipe")
    print("  3. Generer le calendrier")
    print("  4. Enregistrer un score")
    print("  5. Corriger un score")
    print("  6. Voir le classement")
    print("  7. Matchs restants")
    print("  0. Quitter")
    print()


def choisir_equipe(tournoi, message="Numero de l'equipe : "):
    if not tournoi.equipes:
        print("Aucune equipe inscrite pour le moment.")
        return None
    print()
    for equipe in tournoi.equipes_triees():
        print(f"  {equipe.id}. {equipe} ")
    identifiants = []
    for equipe in tournoi.equipes:
        identifiants.append(equipe.id)
    identifiant = demander_choix(message, identifiants)
    return tournoi.trouver_equipe(identifiant)


def action_inscrire_equipe(tournoi):
    print("\n--- Inscrire une equipe ---")
    nom = demander_texte("Nom de l'equipe : ")
    try:
        equipe = tournoi.inscrire_equipe(nom)
    except ValueError as erreur:
        print(f"Refuse : {erreur}")
        return
    print(f"Equipe « {equipe.nom} » inscrite (id {equipe.id}).")


def action_ajouter_joueur(tournoi):
    print("\n--- Ajouter un joueur ---")
    equipe = choisir_equipe(tournoi)
    if equipe is None:
        return
    nom = demander_texte("Nom du joueur : ")
    print("Postes :")
    for i, poste in enumerate(POSTES, start=1):
        print(f"  {i}. {poste}")
    numero_poste = demander_choix("Numero du poste : ",
                                  list(range(1, len(POSTES) + 1)))
    poste = POSTES[numero_poste - 1]
    numero = demander_entier("Numero de maillot (1 a 99) : ", 1, 99)
    try:
        joueur = tournoi.ajouter_joueur(equipe.id, nom, poste, numero)
    except ValueError as erreur:
        print(f"Refuse : {erreur}")
        return
    print(f"{joueur} ajoute a {equipe.nom}.")


def action_generer_calendrier(tournoi):
    print("\n--- Generer le calendrier ---")
    calendrier_existe = False
    match_joue = False
    for match in tournoi.matchs:
        calendrier_existe = True
        if match.joue:
            match_joue = True
    if calendrier_existe and not match_joue:
        print("Un calendrier existe deja, mais aucun match n'a ete joue.")
        reponse = input("Voulez-vous le remplacer ? (o/n) : ").strip().lower()
        if reponse != "o":
            print("Generation annulee.")
            return
        confirmer = True
    else:
        confirmer = False
    try:
        nombre_matchs, nombre_journees = tournoi.generer_calendrier(confirmer)
    except ValueError as erreur:
        print(f"Refuse : {erreur}")
        return
    print(f"Calendrier genere : {nombre_matchs} matchs, "
          f"{nombre_journees} journees.")
    for match in tournoi.matchs:
        print(f"  {match.id}. {tournoi.match_texte(match)}")


def choisir_match(tournoi, joues):
    if joues:
        liste = []
        for match in tournoi.matchs:
            if match.joue:
                liste.append(match)
        titre = "Matchs joues"
    else:
        liste = []
        for match in tournoi.matchs:
            if not match.joue:
                liste.append(match)
        titre = "Matchs a jouer"
    if not liste:
        print(f"Aucun match dans « {titre} ».")
        return None
    print(f"\n--- {titre} ---")
    for match in liste:
        print(f"  {match.id}. {tournoi.match_texte(match)}")
    identifiants = []
    for match in liste:
        identifiants.append(match.id)
    identifiant = demander_choix("Numero du match : ", identifiants)
    return tournoi.trouver_match(identifiant)


def action_enregistrer_score(tournoi):
    print("\n--- Enregistrer un score ---")
    match = choisir_match(tournoi, joues=False)
    if match is None:
        return
    dom = tournoi.nom_equipe(match.id_equipe_domicile)
    ext = tournoi.nom_equipe(match.id_equipe_exterieur)
    score_dom = demander_entier(f"Score de {dom} : ", minimum=0)
    score_ext = demander_entier(f"Score de {ext} : ", minimum=0)
    try:
        tournoi.enregistrer_score(match.id, score_dom, score_ext)
    except ValueError as erreur:
        print(f"Refuse : {erreur}")
        return
    print(f"Score enregistre : {tournoi.match_texte(match)}")


def action_corriger_score(tournoi):
    print("\n--- Corriger un score ---")
    match = choisir_match(tournoi, joues=True)
    if match is None:
        return
    print(f"Score actuel : {tournoi.match_texte(match)}")
    dom = tournoi.nom_equipe(match.id_equipe_domicile)
    ext = tournoi.nom_equipe(match.id_equipe_exterieur)
    score_dom = demander_entier(f"Nouveau score de {dom} : ", minimum=0)
    score_ext = demander_entier(f"Nouveau score de {ext} : ", minimum=0)
    try:
        tournoi.corriger_score(match.id, score_dom, score_ext)
    except ValueError as erreur:
        print(f"Refuse : {erreur}")
        return
    print(f"Score corrige : {tournoi.match_texte(match)}")
    print("Le classement a ete recalcule automatiquement.")


def action_classement(tournoi):
    print("\n--- Classement ---")
    if not tournoi.equipes:
        print("Aucune equipe inscrite.")
        return
    lignes = tournoi.classement()
    print("Rang  Equipe         Pts  J   G   N   P   BP   BC   Diff")
    rang = 1
    for ligne in lignes:
        equipe = ligne["equipe"]
        print(f"{rang:<6}{equipe.nom:<15}{ligne['points']:<5}"
              f"{ligne['joues']:<4}{ligne['gagnes']:<4}{ligne['nuls']:<4}"
              f"{ligne['perdus']:<4}{ligne['buts_pour']:<5}"
              f"{ligne['buts_contre']:<5}{ligne['difference']:<6}")
        rang += 1
    print()
    print("Pts = points, J = joues, G = gagnes, N = nuls, P = perdus,")
    print("BP = buts pour, BC = buts contre, Diff = difference de buts.")
    print("Bareme : victoire 3 points, nul 1 point, defaite 0 point.")


def action_matchs_restants(tournoi):
    print("\n--- Matchs restants ---")
    restants = tournoi.matchs_restants()
    if not restants:
        if not tournoi.matchs:
            print("Aucun match : le calendrier n'a pas ete genere.")
        else:
            print("Tous les matchs ont ete joues. Tournoi termine !")
        return
    print(f"Il reste {len(restants)} matchs a jouer :")
    for match in restants:
        print(f"  {match.id}. {tournoi.match_texte(match)}")


def main():
    tournoi = charger_tournoi()
    while True:
        try:
            afficher_titre(tournoi)
            afficher_menu()
            choix = demander_choix("Votre choix : ",
                                  list(range(0, 8)))
            if choix == 0:
                tournoi.sauvegarder()
                print("\nDonnees sauvegardees. A bientot !")
                break
            elif choix == 1:
                action_inscrire_equipe(tournoi)
            elif choix == 2:
                action_ajouter_joueur(tournoi)
            elif choix == 3:
                action_generer_calendrier(tournoi)
            elif choix == 4:
                action_enregistrer_score(tournoi)
            elif choix == 5:
                action_corriger_score(tournoi)
            elif choix == 6:
                action_classement(tournoi)
            elif choix == 7:
                action_matchs_restants(tournoi)
            input("\nAppuyez sur Entree pour continuer...")
        except (KeyboardInterrupt, EOFError):
            tournoi.sauvegarder()
            print("\n\nDonnees sauvegardees. A bientot !")
            break


if __name__ == "__main__":
    main()
