"""Bibliothèque de motifs classiques.

Chaque motif est dessiné en texte : ``O`` pour une cellule vivante, ``.`` pour
une cellule morte. C'est bien plus lisible (et moins sujet aux erreurs) qu'une
liste de coordonnées écrite à la main. Un motif peut aussi imposer sa règle :
le réplicateur, par exemple, n'existe que dans HighLife.
"""

from typing import Dict, List, NamedTuple, Optional, Tuple

from .regles import Regle

Cellule = Tuple[int, int]


def lire(dessin: str) -> List[Cellule]:
    """Convertit un dessin texte en liste de coordonnées (ligne, colonne)."""
    return [
        (i, j)
        for i, ligne in enumerate(dessin.strip("\n").splitlines())
        for j, car in enumerate(ligne.strip())
        if car == "O"
    ]


class Motif(NamedTuple):
    nom: str
    categorie: str
    cellules: List[Cellule]
    description: str
    regle: Optional[Regle] = None


_DEFINITIONS = [
    # ---------------------------------------------------------------- stables
    ("Bloc", "Stables", "Le plus petit motif stable.", None, """
        OO
        OO
    """),
    ("Ruche", "Stables", "Motif stable très fréquent.", None, """
        .OO.
        O..O
        .OO.
    """),
    ("Pain", "Stables", "Motif stable de 7 cellules.", None, """
        .OO.
        O..O
        .O.O
        ..O.
    """),
    # ----------------------------------------------------------- oscillateurs
    ("Clignotant", "Oscillateurs", "Oscillateur de période 2, le plus petit.", None, """
        OOO
    """),
    ("Crapaud", "Oscillateurs", "Oscillateur de période 2.", None, """
        .OOO
        OOO.
    """),
    ("Balise", "Oscillateurs", "Oscillateur de période 2.", None, """
        OO..
        OO..
        ..OO
        ..OO
    """),
    ("Pulsar", "Oscillateurs", "Oscillateur de période 3.", None, """
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
    ("Galaxie de Kok", "Oscillateurs", "Oscillateur de période 8.", None, """
        OOOOOO.OO
        OOOOOO.OO
        .......OO
        OO.....OO
        OO.....OO
        OO.....OO
        OO.......
        OO.OOOOOO
        OO.OOOOOO
    """),
    ("Pentadécathlon", "Oscillateurs", "Oscillateur de période 15.", None, """
        ..O....O..
        OO.OOOO.OO
        ..O....O..
    """),
    # -------------------------------------------------------------- vaisseaux
    ("Planeur", "Vaisseaux", "Se déplace d'une case en diagonale toutes les 4 générations.", None, """
        .O.
        ..O
        OOO
    """),
    ("Vaisseau léger (LWSS)", "Vaisseaux", "Se déplace de 2 cases toutes les 4 générations.", None, """
        O..O.
        ....O
        O...O
        .OOOO
    """),
    ("Vaisseau moyen (MWSS)", "Vaisseaux", "Grand frère du LWSS, même vitesse.", None, """
        ...O..
        .O...O
        O.....
        O....O
        OOOOO.
    """),
    # ------------------------------------------------------------ mathusalems
    ("R-pentomino", "Mathusalems", "5 cellules qui évoluent pendant 1103 générations.", None, """
        .OO
        OO.
        .O.
    """),
    ("Diehard", "Mathusalems", "Disparaît complètement après 130 générations.", None, """
        ......O.
        OO......
        .O...OOO
    """),
    ("Gland", "Mathusalems", "7 cellules qui évoluent pendant 5206 générations.", None, """
        .O.....
        ...O...
        OO..OOO
    """),
    # ----------------------------------------------------------------- canons
    ("Canon à planeurs de Gosper", "Canons",
     "Premier motif à croissance infinie connu (1970) : un planeur toutes les 30 générations.", None, """
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
    # ------------------------------------------------------- autres règles
    ("Réplicateur", "Autres règles",
     "Dans HighLife (B36/S23), ce motif se recopie tous les 12 générations.", "B36/S23", """
        ..OOO
        .O..O
        O...O
        O..O.
        OOO..
    """),
]

MOTIFS: Dict[str, Motif] = {}
CATEGORIES: Dict[str, List[str]] = {}
for _nom, _categorie, _description, _regle, _dessin in _DEFINITIONS:
    MOTIFS[_nom] = Motif(_nom, _categorie, lire(_dessin), _description,
                         Regle.depuis_texte(_regle) if _regle else None)
    CATEGORIES.setdefault(_categorie, []).append(_nom)


def chercher(nom: str) -> Motif:
    """Retrouve un motif sans tenir compte de la casse ni des accents simples."""
    def cle(texte: str) -> str:
        return texte.lower().translate(str.maketrans("éèêàç", "eeeac")).replace(" ", "-")

    for motif in MOTIFS.values():
        if cle(motif.nom) == cle(nom) or cle(motif.nom).startswith(cle(nom) + "-("):
            return motif
    raise KeyError(f"motif inconnu : {nom}")
