"""Export d'une grille en image PNG, sans bibliothèque externe.

Un PNG n'est qu'une suite de blocs (« chunks ») : un en-tête IHDR décrivant
l'image, des données IDAT compressées avec zlib, et un bloc final IEND. Chaque
bloc se termine par un CRC32. Les modules standard ``zlib`` et ``struct``
suffisent donc à produire une image valide.
"""

import struct
import zlib
from typing import Iterable, Tuple

Couleur = Tuple[int, int, int]

FOND: Couleur = (250, 250, 250)
VIVANTE: Couleur = (31, 41, 55)
LIGNE: Couleur = (229, 231, 235)


def _bloc(type_bloc: bytes, donnees: bytes) -> bytes:
    crc = zlib.crc32(type_bloc + donnees) & 0xFFFFFFFF
    return struct.pack(">I", len(donnees)) + type_bloc + donnees + struct.pack(">I", crc)


def png(lignes: int, colonnes: int, vivantes: Iterable[Tuple[int, int]], cote: int = 8,
        quadrillage: bool = True, fond: Couleur = FOND, vivante: Couleur = VIVANTE,
        ligne: Couleur = LIGNE) -> bytes:
    """Renvoie le contenu d'un fichier PNG représentant la grille."""
    if cote < 1:
        raise ValueError("le côté d'une cellule doit valoir au moins 1 pixel")
    vivantes = set(vivantes)
    largeur, hauteur = colonnes * cote, lignes * cote
    quadrillage = quadrillage and cote >= 4
    px_fond, px_vivante, px_ligne = bytes(fond), bytes(vivante), bytes(ligne)

    brut = bytearray()
    for i in range(lignes):
        # Une ligne de cellules donne `cote` lignes de pixels ; on construit les
        # deux variantes possibles (bord supérieur quadrillé ou non) une fois.
        pixels_plein = bytearray()
        pixels_bord = bytearray()
        for j in range(colonnes):
            couleur = px_vivante if (i, j) in vivantes else px_fond
            bord = px_ligne if quadrillage else couleur
            pixels_plein += bord + couleur * (cote - 1)
            pixels_bord += (px_ligne if quadrillage else couleur) * cote
        for k in range(cote):
            brut.append(0)  # filtre PNG « aucun » pour cette ligne
            brut += pixels_bord if (k == 0 and quadrillage) else pixels_plein

    entete = struct.pack(">IIBBBBB", largeur, hauteur, 8, 2, 0, 0, 0)  # 8 bits, RVB
    return (b"\x89PNG\r\n\x1a\n" + _bloc(b"IHDR", entete)
            + _bloc(b"IDAT", zlib.compress(bytes(brut), 9)) + _bloc(b"IEND", b""))


def enregistrer_png(grille, chemin: str, cote: int = 8, quadrillage: bool = True) -> None:
    with open(chemin, "wb") as f:
        f.write(png(grille.lignes, grille.colonnes, grille.vivantes, cote, quadrillage))
