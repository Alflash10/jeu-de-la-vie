"""Lecture et écriture du format RLE (*Run Length Encoded*).

C'est le format standard des motifs du Jeu de la Vie (utilisé par Golly et
LifeWiki). Exemple, un planeur :

    #N Planeur
    x = 3, y = 3, rule = B3/S23
    bob$2bo$3o!

``b`` = cellule morte, ``o`` = cellule vivante, ``$`` = fin de ligne,
``!`` = fin du motif, et un nombre devant un symbole le répète.
"""

import re
from typing import Iterable, List, NamedTuple, Optional, Tuple

from .regles import Regle

Cellule = Tuple[int, int]

LARGEUR_LIGNE = 70  # convention du format


class FormatRLEInvalide(ValueError):
    pass


class MotifRLE(NamedTuple):
    cellules: List[Cellule]
    nom: Optional[str] = None
    regle: Optional[Regle] = None
    commentaires: Tuple[str, ...] = ()


_ENTETE = re.compile(r"\s*x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)\s*(?:,\s*rule\s*=\s*(\S+))?\s*$", re.I)


def lire_rle(texte: str) -> MotifRLE:
    nom = None
    regle = None
    commentaires = []
    corps = []
    entete_vue = False

    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if ligne.startswith("#"):
            balise, _, contenu = ligne[1:].partition(" ")
            if balise == "N":
                nom = contenu.strip() or None
            elif balise in ("C", "c"):
                commentaires.append(contenu.strip())
            continue
        if not entete_vue:
            m = _ENTETE.match(ligne)
            if m:
                entete_vue = True
                if m.group(3):
                    regle = Regle.depuis_texte(m.group(3))
                continue
            raise FormatRLEInvalide("en-tête « x = …, y = … » manquant")
        corps.append(ligne)

    if not entete_vue:
        raise FormatRLEInvalide("en-tête « x = …, y = … » manquant")

    cellules = []
    i = j = 0
    nombre = ""
    for car in "".join(corps):
        if car.isdigit():
            nombre += car
            continue
        n = int(nombre) if nombre else 1
        nombre = ""
        if car == "!":
            break
        if car == "$":
            i += n
            j = 0
        elif car in "b.":
            j += n
        elif car.isalpha():  # « o », ou tout état vivant d'un format multi-états
            cellules.extend((i, j + k) for k in range(n))
            j += n
        elif car.isspace():
            continue
        else:
            raise FormatRLEInvalide(f"caractère inattendu : « {car} »")
    return MotifRLE(cellules, nom, regle, tuple(commentaires))


def ecrire_rle(cellules: Iterable[Cellule], regle: Optional[Regle] = None,
               nom: Optional[str] = None, commentaires: Iterable[str] = ()) -> str:
    """Écrit les cellules au format RLE, recadrées sur leur boîte englobante."""
    cellules = set(cellules)
    lignes_texte = []
    if nom:
        lignes_texte.append(f"#N {nom}")
    lignes_texte.extend(f"#C {c}" for c in commentaires)

    regle_txt = f", rule = {regle}" if regle else ""
    if not cellules:
        lignes_texte.append(f"x = 0, y = 0{regle_txt}")
        lignes_texte.append("!")
        return "\n".join(lignes_texte) + "\n"

    i0 = min(i for i, _ in cellules)
    j0 = min(j for _, j in cellules)
    hauteur = max(i for i, _ in cellules) - i0 + 1
    largeur = max(j for _, j in cellules) - j0 + 1
    lignes_texte.append(f"x = {largeur}, y = {hauteur}{regle_txt}")

    # 1) suite de « jetons » (nombre, symbole), lignes vides fusionnées dans les $
    jetons: List[Tuple[int, str]] = []

    def ajouter(n: int, symbole: str) -> None:
        if jetons and jetons[-1][1] == symbole:
            jetons[-1] = (jetons[-1][0] + n, symbole)
        else:
            jetons.append((n, symbole))

    for i in range(hauteur):
        if i:
            ajouter(1, "$")
        ligne = [(i + i0, j + j0) in cellules for j in range(largeur)]
        while ligne and not ligne[-1]:  # les cellules mortes en fin de ligne sont implicites
            ligne.pop()
        for vivante in ligne:
            ajouter(1, "o" if vivante else "b")
    jetons.append((1, "!"))

    # 2) mise en ligne sans dépasser LARGEUR_LIGNE caractères
    courante = ""
    for n, symbole in jetons:
        morceau = (str(n) if n > 1 else "") + symbole
        if len(courante) + len(morceau) > LARGEUR_LIGNE:
            lignes_texte.append(courante)
            courante = ""
        courante += morceau
    lignes_texte.append(courante)
    return "\n".join(lignes_texte) + "\n"
