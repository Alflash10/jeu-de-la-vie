"""Moteur du Jeu de la Vie de Conway, indépendant de toute interface.

La grille est représentée par l'ensemble des cellules vivantes, sous forme de
coordonnées ``(ligne, colonne)``. Ce choix (« ensemble creux ») rend chaque
génération proportionnelle au nombre de cellules vivantes et non à la taille
de la grille : une grille 100×100 presque vide se calcule instantanément.
"""

from collections import Counter
from typing import FrozenSet, Iterable, Set, Tuple

Cellule = Tuple[int, int]

# Les 8 directions du voisinage de Moore.
VOISINAGE = [(di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)]


class Grille:
    """Grille finie de ``lignes`` × ``colonnes`` cellules.

    Si ``tore`` est vrai, les bords se rejoignent (ce qui sort à droite rentre
    à gauche, etc.). Sinon, tout ce qui se trouve hors de la grille est mort.
    """

    def __init__(self, lignes: int, colonnes: int, tore: bool = False,
                 vivantes: Iterable[Cellule] = ()):
        if lignes <= 0 or colonnes <= 0:
            raise ValueError("la grille doit avoir au moins une ligne et une colonne")
        self.lignes = lignes
        self.colonnes = colonnes
        self.tore = tore
        self.generation = 0
        self.vivantes: Set[Cellule] = set()
        for cellule in vivantes:
            self.allumer(*cellule)

    # ------------------------------------------------------------ accès

    def __contains__(self, cellule: Cellule) -> bool:
        return cellule in self.vivantes

    def __len__(self) -> int:
        """Population : nombre de cellules vivantes."""
        return len(self.vivantes)

    def dans_grille(self, i: int, j: int) -> bool:
        return 0 <= i < self.lignes and 0 <= j < self.colonnes

    def allumer(self, i: int, j: int) -> None:
        if self.dans_grille(i, j):
            self.vivantes.add((i, j))

    def eteindre(self, i: int, j: int) -> None:
        self.vivantes.discard((i, j))

    def basculer(self, i: int, j: int) -> None:
        if (i, j) in self.vivantes:
            self.eteindre(i, j)
        else:
            self.allumer(i, j)

    def vider(self) -> None:
        self.vivantes.clear()
        self.generation = 0

    # ------------------------------------------------------- simulation

    def voisins(self, i: int, j: int) -> int:
        """Nombre de voisins vivants de la cellule (i, j)."""
        return sum(1 for v in self._voisines(i, j) if v in self.vivantes)

    def _voisines(self, i: int, j: int):
        for di, dj in VOISINAGE:
            vi, vj = i + di, j + dj
            if self.tore:
                yield vi % self.lignes, vj % self.colonnes
            elif self.dans_grille(vi, vj):
                yield vi, vj

    def etape(self) -> FrozenSet[Cellule]:
        """Avance d'une génération et renvoie les cellules qui ont changé d'état.

        Règles (B3/S23) : une cellule morte avec exactement 3 voisins naît ;
        une cellule vivante avec 2 ou 3 voisins survit ; les autres meurent.
        """
        compte = Counter(v for cellule in self.vivantes for v in self._voisines(*cellule))
        suivantes = {
            cellule for cellule, n in compte.items()
            if n == 3 or (n == 2 and cellule in self.vivantes)
        }
        changements = frozenset(self.vivantes ^ suivantes)
        self.vivantes = suivantes
        self.generation += 1
        return changements

    # ---------------------------------------------------------- motifs

    def placer(self, motif: Iterable[Cellule], centrer: bool = True) -> None:
        """Remplace le contenu de la grille par ``motif``.

        Le motif est donné en coordonnées relatives ; s'il est centré, il est
        déplacé au milieu de la grille. Les cellules qui ne tiennent pas dans la
        grille sont ignorées.
        """
        motif = list(motif)
        self.vider()
        if not motif:
            return
        di = dj = 0
        if centrer:
            hauteur = max(i for i, _ in motif) + 1
            largeur = max(j for _, j in motif) + 1
            di = (self.lignes - hauteur) // 2
            dj = (self.colonnes - largeur) // 2
        for i, j in motif:
            self.allumer(i + di, j + dj)
