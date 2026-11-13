"""Bibliothèque de motifs classiques du Jeu de la Vie.

Chaque motif est dessiné en texte : ``O`` pour une cellule vivante, ``.`` pour
une cellule morte. C'est bien plus lisible (et moins sujet aux erreurs) qu'une
liste de coordonnées écrite à la main.
"""

from typing import Dict, List, Tuple


def lire(dessin: str) -> List[Tuple[int, int]]:
    """Convertit un dessin texte en liste de coordonnées (ligne, colonne)."""
    lignes = [l for l in dessin.strip("\n").splitlines()]
    return [
        (i, j)
        for i, ligne in enumerate(lignes)
        for j, car in enumerate(ligne.strip())
        if car == "O"
    ]


# Nom affiché → (catégorie, dessin)
_DESSINS = {
    # --- Oscillateurs
    "Clignotant": ("Oscillateurs", """
        OOO
    """),
    "Crapaud": ("Oscillateurs", """
        .OOO
        OOO.
    """),
    "Balise": ("Oscillateurs", """
        OO..
        OO..
        ..OO
        ..OO
    """),
    "Pulsar": ("Oscillateurs", """
        ..OOO...OOO..
        .............
        O....O.O....O
        O....O.O....O
        O....O.O....O
        ..OOO...OOO..
        .............
        ..OOO...OOO..
        O....O.O....O
        O....O.O....O
        O....O.O....O
        .............
        ..OOO...OOO..
    """),
    "Pentadécathlon": ("Oscillateurs", """
        ..O....O..
        OO.OOOO.OO
        ..O....O..
    """),
    # --- Vaisseaux
    "Planeur": ("Vaisseaux", """
        .O.
        ..O
        OOO
    """),
    "Vaisseau léger (LWSS)": ("Vaisseaux", """
        O..O.
        ....O
        O...O
        .OOOO
    """),
    # --- Mathusalems (petits motifs à très longue évolution)
    "R-pentomino": ("Mathusalems", """
        .OO
        OO.
        .O.
    """),
    "Diehard": ("Mathusalems", """
        ......O.
        OO......
        .O...OOO
    """),
    "Gland": ("Mathusalems", """
        .O.....
        ...O...
        OO..OOO
    """),
    # --- Canons
    "Canon à planeurs de Gosper": ("Canons", """
        ........................O...........
        ......................O.O...........
        ............OO......OO............OO
        ...........O...O....OO............OO
        OO........O.....O...OO..............
        OO........O...O.OO....O.O...........
        ..........O.....O.......O...........
        ...........O...O....................
        ............OO......................
    """),
}

MOTIFS: Dict[str, List[Tuple[int, int]]] = {nom: lire(d) for nom, (_, d) in _DESSINS.items()}

CATEGORIES: Dict[str, List[str]] = {}
for _nom, (_categorie, _) in _DESSINS.items():
    CATEGORIES.setdefault(_categorie, []).append(_nom)
