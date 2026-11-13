"""Moteur du Jeu de la Vie, indépendant de toute interface.

La grille est représentée par l'ensemble des cellules vivantes, sous forme de
coordonnées ``(ligne, colonne)``. Ce choix (« ensemble creux ») rend chaque
génération proportionnelle au nombre de cellules vivantes et non à la taille
de la grille : une grille 200×200 presque vide se calcule instantanément.

Le moteur sait aussi :

* revenir en arrière (historique borné) ;
* reconnaître qu'un état a déjà été vu, ce qui permet de détecter les motifs
  stables, les oscillateurs et les vaisseaux (motifs qui se répètent en se
  déplaçant).
"""

from collections import Counter, deque
from typing import Dict, FrozenSet, Iterable, Iterator, NamedTuple, Optional, Set, Tuple

from .regles import CONWAY, Regle

Cellule = Tuple[int, int]

# Les 8 directions du voisinage de Moore.
VOISINAGE = [(di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)]

TAILLE_HISTORIQUE = 1000


class Cycle(NamedTuple):
    """Répétition détectée : l'état de la génération ``debut`` revient tous
    les ``periode`` tours, décalé de ``deplacement`` (``(0, 0)`` si le motif
    reste sur place)."""

    debut: int
    periode: int
    deplacement: Tuple[int, int] = (0, 0)

    @property
    def nature(self) -> str:
        if self.deplacement != (0, 0):
            return "vaisseau"
        return "stable" if self.periode == 1 else "oscillateur"

    def __str__(self) -> str:
        if self.nature == "stable":
            return f"Stable depuis la génération {self.debut}"
        if self.nature == "oscillateur":
            return f"Oscillateur de période {self.periode} (depuis la génération {self.debut})"
        di, dj = self.deplacement
        return f"Vaisseau de période {self.periode}, se déplace de ({di:+d}, {dj:+d})"


class Grille:
    """Grille finie de ``lignes`` × ``colonnes`` cellules.

    Si ``tore`` est vrai, les bords se rejoignent (ce qui sort à droite rentre
    à gauche, etc.). Sinon, tout ce qui se trouve hors de la grille est mort.
    """

    def __init__(self, lignes: int, colonnes: int, tore: bool = False,
                 vivantes: Iterable[Cellule] = (), regle: Regle = CONWAY):
        if lignes <= 0 or colonnes <= 0:
            raise ValueError("la grille doit avoir au moins une ligne et une colonne")
        self.lignes = lignes
        self.colonnes = colonnes
        self.regle = regle
        self._tore = tore
        self.generation = 0
        self.vivantes: Set[Cellule] = set()
        self._historique: deque = deque(maxlen=TAILLE_HISTORIQUE)
        self._vus: Dict[int, int] = {}                          # empreinte exacte → génération
        self._formes: Dict[int, Tuple[int, Cellule]] = {}       # empreinte de forme → (génération, origine)
        self.cycle: Optional[Cycle] = None
        for cellule in vivantes:
            self.allumer(*cellule)

    # ------------------------------------------------------------ accès

    def __contains__(self, cellule: Cellule) -> bool:
        return cellule in self.vivantes

    def __len__(self) -> int:
        """Population : nombre de cellules vivantes."""
        return len(self.vivantes)

    @property
    def tore(self) -> bool:
        return self._tore

    @tore.setter
    def tore(self, valeur: bool) -> None:
        self._tore = valeur
        self._oublier_cycles()

    def changer_regle(self, regle: Regle) -> None:
        self.regle = regle
        self._oublier_cycles()

    def dans_grille(self, i: int, j: int) -> bool:
        return 0 <= i < self.lignes and 0 <= j < self.colonnes

    def boite(self) -> Optional[Tuple[int, int, int, int]]:
        """Plus petit rectangle contenant les cellules vivantes :
        ``(ligne_min, colonne_min, ligne_max, colonne_max)``, ou ``None``."""
        if not self.vivantes:
            return None
        lignes = [i for i, _ in self.vivantes]
        colonnes = [j for _, j in self.vivantes]
        return min(lignes), min(colonnes), max(lignes), max(colonnes)

    # ------------------------------------------------------ modification
    # Toute modification manuelle invalide la détection de cycles. Pour
    # pouvoir l'annuler, l'appelant enregistre l'état avec memoriser() avant.

    def allumer(self, i: int, j: int) -> None:
        if self.dans_grille(i, j) and (i, j) not in self.vivantes:
            self.vivantes.add((i, j))
            self._oublier_cycles()

    def eteindre(self, i: int, j: int) -> None:
        if (i, j) in self.vivantes:
            self.vivantes.discard((i, j))
            self._oublier_cycles()

    def basculer(self, i: int, j: int) -> None:
        if (i, j) in self.vivantes:
            self.eteindre(i, j)
        else:
            self.allumer(i, j)

    def vider(self) -> None:
        self.vivantes.clear()
        self.generation = 0
        self._oublier_cycles()

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
            hauteur = max(i for i, _ in motif) - min(i for i, _ in motif) + 1
            largeur = max(j for _, j in motif) - min(j for _, j in motif) + 1
            di = (self.lignes - hauteur) // 2 - min(i for i, _ in motif)
            dj = (self.colonnes - largeur) // 2 - min(j for _, j in motif)
        for i, j in motif:
            self.allumer(i + di, j + dj)

    # -------------------------------------------------------- historique

    def memoriser(self) -> None:
        """Enregistre l'état courant pour pouvoir y revenir avec annuler()."""
        self._historique.append((frozenset(self.vivantes), self.generation))

    def peut_annuler(self) -> bool:
        return bool(self._historique)

    def annuler(self) -> FrozenSet[Cellule]:
        """Revient à l'état mémorisé précédent. Renvoie les cellules modifiées
        (ensemble vide s'il n'y a rien à annuler)."""
        if not self._historique:
            return frozenset()
        vivantes, generation = self._historique.pop()
        changements = frozenset(self.vivantes ^ vivantes)
        self.vivantes = set(vivantes)
        self.generation = generation
        self._oublier_cycles()
        return changements

    # -------------------------------------------------------- simulation

    def voisins(self, i: int, j: int) -> int:
        """Nombre de voisins vivants de la cellule (i, j)."""
        return sum(1 for v in self._voisines(i, j) if v in self.vivantes)

    def _voisines(self, i: int, j: int) -> Iterator[Cellule]:
        for di, dj in VOISINAGE:
            vi, vj = i + di, j + dj
            if self._tore:
                yield vi % self.lignes, vj % self.colonnes
            elif 0 <= vi < self.lignes and 0 <= vj < self.colonnes:
                yield vi, vj

    def etape(self) -> FrozenSet[Cellule]:
        """Avance d'une génération et renvoie les cellules qui ont changé d'état."""
        if not self._vus:
            self._noter_etat()  # état de départ, après une modification manuelle
        self.memoriser()

        naissance, survie = self.regle.naissance, self.regle.survie
        vivantes = self.vivantes
        compte = Counter(v for cellule in vivantes for v in self._voisines(*cellule))
        suivantes = {
            cellule for cellule, n in compte.items()
            if (n in survie if cellule in vivantes else n in naissance)
        }
        if 0 in survie:
            # Une cellule vivante sans aucune voisine n'apparaît pas dans le
            # compte : on la traite à part.
            suivantes |= {c for c in vivantes if c not in compte}

        changements = frozenset(vivantes ^ suivantes)
        self.vivantes = suivantes
        self.generation += 1
        self._noter_etat()
        return changements

    def avancer(self, n: int) -> None:
        """Avance de ``n`` générations (sans renvoyer les changements)."""
        for _ in range(n):
            self.etape()

    # ------------------------------------------------- détection de cycles

    def _oublier_cycles(self) -> None:
        self._vus.clear()
        self._formes.clear()
        self.cycle = None

    def _noter_etat(self) -> None:
        if self.cycle is not None:
            return
        etat = frozenset(self.vivantes)
        empreinte = hash(etat)
        if empreinte in self._vus:
            debut = self._vus[empreinte]
            self.cycle = Cycle(debut, self.generation - debut)
            return
        self._vus[empreinte] = self.generation

        # Même forme, ailleurs dans la grille : c'est un vaisseau. (Sur un tore
        # le motif finit par revenir à sa place : c'est alors l'empreinte
        # exacte qui le détecte, comme un oscillateur de grande période.)
        boite = self.boite()
        if boite is None:
            return
        i0, j0 = boite[0], boite[1]
        forme = hash(frozenset((i - i0, j - j0) for i, j in etat))
        if forme in self._formes:
            debut, (pi, pj) = self._formes[forme]
            self.cycle = Cycle(debut, self.generation - debut, (i0 - pi, j0 - pj))
            return
        self._formes[forme] = (self.generation, (i0, j0))
