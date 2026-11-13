# Jeu de la Vie 🧬

[![Tests](https://github.com/Alflash10/jeu-de-la-vie/actions/workflows/tests.yml/badge.svg)](https://github.com/Alflash10/jeu-de-la-vie/actions/workflows/tests.yml)

Implémentation du **Jeu de la Vie de John Conway** en Python, avec une interface
graphique Tkinter. Aucune dépendance externe : uniquement la bibliothèque standard.

## Règles

Chaque cellule a 8 voisines. À chaque génération (règle **B3/S23**) :

| Situation | Voisines vivantes | Résultat |
|---|---|---|
| Cellule vivante | moins de 2 | meurt (isolement) |
| Cellule vivante | 2 ou 3 | survit |
| Cellule vivante | plus de 3 | meurt (surpopulation) |
| Cellule morte | exactement 3 | naît |

## Fonctionnalités

- **Lecture / pause** avec vitesse réglable (1 à 60 générations par seconde), ou avancée génération par génération
- **Dessin à la souris** : cliquer pour allumer ou éteindre une cellule, maintenir et glisser pour dessiner ou gommer
- **Bibliothèque de motifs classiques** : oscillateurs (clignotant, crapaud, balise, pulsar, pentadécathlon), vaisseaux (planeur, LWSS), mathusalems (R-pentomino, diehard, gland) et le **canon à planeurs de Gosper**
- **Remplissage aléatoire** et effacement de la grille
- Grilles **30×30, 50×50 ou 100×100**
- **Bords reliés (tore)** activables : ce qui sort d'un côté rentre de l'autre
- Compteurs de **génération** et de **population**
- Arrêt automatique de la lecture quand plus rien ne bouge

### Raccourcis clavier

| Touche | Action |
|---|---|
| `Espace` | lecture / pause |
| `→` ou `N` | génération suivante |
| `R` | remplissage aléatoire |
| `C` | effacer la grille |

## Lancer le programme

```bash
python3 jeu_de_la_vie.py
```

Tkinter est fourni avec Python sur Windows et avec l'installateur de python.org.
Avec le Python de Homebrew sur macOS, il faut l'ajouter : `brew install python-tk`.
Sous Debian/Ubuntu : `sudo apt install python3-tk`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Les tests vérifient les règles et le comportement de motifs connus : un bloc
reste stable, le clignotant a une période de 2 et le pulsar de 3, le planeur se
décale d'une case en diagonale toutes les 4 générations, le canon de Gosper tire
un nouveau planeur toutes les 30 générations, et un planeur fait le tour complet
d'une grille torique. Ils s'exécutent à chaque push grâce à GitHub Actions.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `moteur.py` | La simulation, sans aucune dépendance à l'interface |
| `motifs.py` | Les motifs classiques, dessinés en texte (`O` = vivante, `.` = morte) |
| `jeu_de_la_vie.py` | L'interface Tkinter |
| `tests/` | Les tests unitaires |

### Choix techniques

- **Grille creuse.** Le moteur ne stocke que l'ensemble des cellules vivantes.
  Une génération compte les voisines de ces cellules uniquement (avec un
  `Counter`) : son coût dépend du nombre de cellules vivantes, pas de la taille
  de la grille.
- **Affichage incrémental.** Chaque cellule est un rectangle créé une seule
  fois. À chaque génération, le moteur renvoie seulement les cellules qui ont
  changé d'état, et seules celles-ci sont recolorées. On évite ainsi de tout
  redessiner, ce qui garde la grille 100×100 fluide.
- **Moteur séparé de l'interface**, ce qui permet de le tester sans ouvrir de
  fenêtre.

## Auteurs

- Alexandre Bourgine
- Leul (partenaire de projet)

Projet de lycée, spécialité NSI (Numérique et Sciences Informatiques), repris et
amélioré ensuite.
