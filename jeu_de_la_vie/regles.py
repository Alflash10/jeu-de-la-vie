"""Règles d'automates cellulaires « à la Vie », en notation B/S.

La notation ``B3/S23`` signifie : une cellule morte naît (*Birth*) si elle a
exactement 3 voisines vivantes, une cellule vivante survit (*Survival*) si elle
en a 2 ou 3. Le Jeu de la Vie de Conway n'est qu'une règle parmi d'autres :
changer ces deux listes donne des univers très différents.
"""

import re
from typing import Dict, FrozenSet, Iterable, Optional

# Règles connues indexées par leur texte, remplies en bas du module : la
# lecture d'une règle connue renvoie ainsi l'objet nommé (« Conway »…).
_PAR_TEXTE: Dict[str, "Regle"] = {}


class RegleInvalide(ValueError):
    """Texte de règle qui ne respecte pas la notation B/S."""


class Regle:
    __slots__ = ("naissance", "survie", "nom")

    def __init__(self, naissance: Iterable[int], survie: Iterable[int], nom: Optional[str] = None):
        self.naissance: FrozenSet[int] = frozenset(naissance)
        self.survie: FrozenSet[int] = frozenset(survie)
        for n in self.naissance | self.survie:
            if not 0 <= n <= 8:
                raise RegleInvalide(f"nombre de voisines impossible : {n} (attendu entre 0 et 8)")
        if 0 in self.naissance:
            # Avec B0, chaque cellule morte de l'univers infini naîtrait : la
            # grille « creuse » du moteur ne peut pas représenter ce cas.
            raise RegleInvalide("les règles avec B0 ne sont pas prises en charge")
        self.nom = nom

    @classmethod
    def depuis_texte(cls, texte: str) -> "Regle":
        """Lit une règle au format ``B3/S23`` (casse et espaces indifférents).

        Accepte aussi l'ancienne notation ``S/B`` sans lettres, par exemple
        ``23/3`` pour Conway.
        """
        brut = texte.replace(" ", "").upper()
        if brut in _PAR_TEXTE:
            return _PAR_TEXTE[brut]
        m = re.fullmatch(r"B([0-8]*)/S([0-8]*)", brut) or re.fullmatch(r"S([0-8]*)/B([0-8]*)", brut)
        if m:
            if brut.startswith("B"):
                naissance, survie = m.group(1), m.group(2)
            else:
                survie, naissance = m.group(1), m.group(2)
        else:
            m = re.fullmatch(r"([0-8]*)/([0-8]*)", brut)
            if not m:
                raise RegleInvalide(f"règle illisible : « {texte} » (exemple attendu : B3/S23)")
            survie, naissance = m.group(1), m.group(2)
        return cls((int(c) for c in naissance), (int(c) for c in survie))

    def __str__(self) -> str:
        return "B{}/S{}".format("".join(map(str, sorted(self.naissance))),
                                "".join(map(str, sorted(self.survie))))

    def __repr__(self) -> str:
        return f"Regle({str(self)!r})"

    def __eq__(self, autre) -> bool:
        return isinstance(autre, Regle) and (self.naissance, self.survie) == (autre.naissance, autre.survie)

    def __hash__(self) -> int:
        return hash((self.naissance, self.survie))

    @property
    def libelle(self) -> str:
        """Texte affiché dans l'interface, par exemple « Conway (B3/S23) »."""
        return f"{self.nom} ({self})" if self.nom else str(self)


def _r(texte: str, nom: str) -> Regle:
    regle = Regle.depuis_texte(texte)
    regle.nom = nom
    _PAR_TEXTE[str(regle)] = regle
    return regle


CONWAY = _r("B3/S23", "Conway")

# Règles connues, dans l'ordre où elles sont proposées dans l'interface.
REGLES_CONNUES = [
    CONWAY,
    _r("B36/S23", "HighLife"),
    _r("B2/S", "Seeds"),
    _r("B3678/S34678", "Day & Night"),
    _r("B3/S012345678", "Vie sans mort"),
    _r("B3/S12345", "Labyrinthe"),
    _r("B368/S245", "Morley"),
    _r("B1357/S1357", "Replicator"),
]

