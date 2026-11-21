# Mini-projet CIN104 — Organisation d'un tournoi sportif (Sujet 3)

## Sujet

**Sujet 3 — Organisation d'un tournoi sportif.**

Développer une application pour organiser un championnat et suivre ses
résultats : inscrire les équipes et leurs joueurs, générer les
rencontres (chaque équipe affronte toutes les autres une seule fois),
organiser les matchs par créneaux, enregistrer et corriger les scores,
et calculer le classement.

## Objectif

Développer une application de gestion en console qui mobilise les
notions étudiées : variables, conditions, boucles, listes,
dictionnaires, fonctions et programmation orientée objet.

## Participants

- **Carl Owens Junior Sillien**
- Yvena Isidor

## Règles du tournoi

- **Barème :** victoire = 3 points, match nul = 1 point, défaite = 0 point.
- **Effectif :** minimum 5 joueurs, maximum 11 joueurs par équipe.
- **Calendrier :** aller simple, chaque équipe affronte toutes les
  autres une seule fois (méthode du cercle). Avec un nombre impair
  d'équipes, une équipe est exemptée à chaque journée.
- **Classement :** points, puis différence de buts, puis buts marqués.

## Comment lancer l'application

Prérequis : Python 3 (aucune bibliothèque externe nécessaire).

```bash
python3 tournoi.py
```

Au premier lancement, le tournoi est vide. Les données sont
sauvegardées automatiquement dans `tournoi.json`, dans le même
dossier que le programme, après chaque modification.

## Essayer avec les données de démonstration

Le fichier `donnees_demo.json` contient un tournoi déjà rempli :
5 équipes (Aigles, Lions, Panthères, Tigres, Étoiles), 38 joueurs,
un calendrier de 10 matchs sur 5 journées, dont 6 déjà joués.

```bash
cp donnees_demo.json tournoi.json
python3 tournoi.py
```

Pour repartir de zéro, supprimez simplement `tournoi.json` :

```bash
rm tournoi.json
python3 tournoi.py
```

## Fonctionnalités (menu)

- 1 : Inscrire une équipe
- 2 : Ajouter un joueur à une équipe
- 3 : Générer le calendrier
- 4 : Enregistrer un score
- 5 : Corriger un score
- 6 : Voir le classement
- 7 : Matchs restants
- 0 : Quitter (les données sont sauvegardées)

## Fichiers du projet

- `tournoi.py` : le code source de l'application (un seul fichier)
- `donnees_demo.json` : données de démonstration (5 équipes, 10 matchs)
- `tournoi.json` : données sauvegardées (créé automatiquement)
- `rapport.pdf` : le rapport du projet (2 à 3 pages)
- `README.md` : ce fichier

## Conception

- **Classes :** `Joueur`, `Equipe`, `Match`, `Tournoi`.
- **Composition :** un `Tournoi` contient des `Equipe` et des
  `Match` ; une `Equipe` contient ses `Joueur`. L'héritage n'est
  pas utilisé : le sujet ne l'exige pas (voir le rapport).
- **Sauvegarde JSON :** chargement au démarrage, sauvegarde après
  chaque modification, reconstruction des objets au chargement,
  compteurs d'identifiants conservés (pas de doublons après
  redémarrage). Un fichier invalide est renommé
  (`tournoi.json.corrompu-AAAAMMJJ-HHMMSS`) et jamais écrasé.
- **Fiabilité :** chaque opération est vérifiée entièrement avant
  toute modification. Une opération refusée (équipe en double,
  12e joueur, score négatif, match déjà joué...) ne modifie rien.
