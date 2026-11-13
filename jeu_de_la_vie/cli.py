"""Ligne de commande : lance l'interface, ou simule sans fenêtre.

Exemples :

    python -m jeu_de_la_vie                                  # interface graphique
    python -m jeu_de_la_vie motifs                           # liste des motifs
    python -m jeu_de_la_vie simuler planeur -n 8 --afficher
    python -m jeu_de_la_vie simuler gosper -n 120 --png canon.png
    python -m jeu_de_la_vie simuler motif.rle --jusqu-au-cycle
    python -m jeu_de_la_vie simuler --aleatoire 0.3 --graine 42 --taille 80 --regle B36/S23 -n 500
"""

import argparse
import os
import random
import sys
from typing import List, Optional, TextIO

from . import __version__
from .image import enregistrer_png
from .moteur import Grille
from .motifs import CATEGORIES, MOTIFS, chercher
from .regles import CONWAY, REGLES_CONNUES, Regle, RegleInvalide
from .rle import FormatRLEInvalide, ecrire_rle, lire_rle

LARGEUR_AFFICHAGE_MAX = 120
MARGE = 10


def _taille(texte: str):
    """« 80 » ou « 60x100 » → (lignes, colonnes)."""
    morceaux = texte.lower().replace("×", "x").split("x")
    try:
        valeurs = [int(m) for m in morceaux]
    except ValueError:
        raise argparse.ArgumentTypeError(f"taille invalide : {texte} (exemples : 80, 60x100)") from None
    if len(valeurs) == 1:
        valeurs *= 2
    if len(valeurs) != 2 or min(valeurs) < 1:
        raise argparse.ArgumentTypeError(f"taille invalide : {texte} (exemples : 80, 60x100)")
    return tuple(valeurs)


def _regle(texte: str) -> Regle:
    try:
        return Regle.depuis_texte(texte)
    except RegleInvalide as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def _densite(texte: str) -> float:
    valeur = float(texte)
    if not 0 < valeur <= 1:
        raise argparse.ArgumentTypeError("la densité doit être comprise entre 0 (exclu) et 1")
    return valeur


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="jeu-de-la-vie",
        description="Jeu de la Vie de Conway. Sans argument, ouvre l'interface graphique.",
    )
    parseur.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sous = parseur.add_subparsers(dest="commande")

    sous.add_parser("interface", help="ouvrir l'interface graphique (par défaut)")
    sous.add_parser("motifs", help="lister les motifs intégrés")
    sous.add_parser("regles", help="lister les règles connues")

    sim = sous.add_parser("simuler", help="simuler sans fenêtre et afficher le résultat",
                          description="Simule un motif sans interface graphique.")
    sim.add_argument("motif", nargs="?",
                     help="nom d'un motif intégré (ex. planeur, gosper) ou chemin d'un fichier .rle")
    sim.add_argument("-n", "--generations", type=int, default=100, metavar="N",
                     help="nombre de générations (défaut : 100)")
    sim.add_argument("--taille", type=_taille, metavar="L[xC]",
                     help="taille de la grille (défaut : celle du motif plus une marge)")
    sim.add_argument("--regle", type=_regle, help="règle B/S, ex. B36/S23 (défaut : celle du motif, sinon Conway)")
    sim.add_argument("--tore", action="store_true", help="relier les bords de la grille")
    sim.add_argument("--coin", action="store_true",
                     help="placer le motif en haut à gauche (2 cases de marge) au lieu de le centrer")
    sim.add_argument("--aleatoire", type=_densite, metavar="DENSITE",
                     help="remplir la grille au hasard (ex. 0.3) au lieu d'un motif")
    sim.add_argument("--graine", type=int, help="graine du hasard, pour un résultat reproductible")
    sim.add_argument("--jusqu-au-cycle", action="store_true", dest="jusqu_au_cycle",
                     help="s'arrêter dès qu'un état se répète (au plus N générations)")
    sim.add_argument("--afficher", action="store_true", help="dessiner la grille finale dans le terminal")
    sim.add_argument("--png", metavar="FICHIER", help="exporter la grille finale en PNG")
    sim.add_argument("--cote", type=int, default=6, metavar="PX", help="taille d'une cellule dans le PNG (défaut : 6)")
    sim.add_argument("--rle", metavar="FICHIER", help="enregistrer la grille finale au format RLE")
    return parseur


def main(argv: Optional[List[str]] = None, sortie: TextIO = sys.stdout) -> int:
    args = construire_parseur().parse_args(argv)

    if args.commande in (None, "interface"):
        from .interface import lancer  # import tardif : Tkinter n'est utile qu'ici
        lancer()
        return 0

    if args.commande == "motifs":
        for categorie, noms in CATEGORIES.items():
            print(categorie, file=sortie)
            for nom in noms:
                print(f"  {nom:30} {MOTIFS[nom].description}", file=sortie)
        return 0

    if args.commande == "regles":
        for regle in REGLES_CONNUES:
            print(f"  {str(regle):15} {regle.nom}", file=sortie)
        return 0

    return simuler(args, sortie)


def _erreur(message: str) -> int:
    print(f"erreur : {message}", file=sys.stderr)
    return 2


def simuler(args, sortie: TextIO) -> int:
    nom, cellules, regle = None, [], None
    if args.aleatoire is not None:
        if args.motif:
            return _erreur("choisir soit un motif, soit --aleatoire, pas les deux")
        nom = f"aléatoire ({args.aleatoire:.0%})"
    elif not args.motif:
        return _erreur("indiquer un motif (voir « motifs ») ou --aleatoire")
    elif os.path.isfile(args.motif):
        try:
            with open(args.motif, encoding="utf-8", errors="replace") as f:
                motif = lire_rle(f.read())
        except (OSError, FormatRLEInvalide, RegleInvalide) as e:
            return _erreur(f"{args.motif} : {e}")
        nom, cellules, regle = motif.nom or os.path.basename(args.motif), motif.cellules, motif.regle
    else:
        try:
            motif = _motif_par_nom(args.motif)
        except KeyError as e:
            return _erreur(f"{e.args[0]} (voir « python -m jeu_de_la_vie motifs »)")
        nom, cellules, regle = motif.nom, motif.cellules, motif.regle

    regle = args.regle or regle or CONWAY
    if args.taille:
        lignes, colonnes = args.taille
    elif cellules:
        lignes = max(i for i, _ in cellules) + 1 + 2 * MARGE
        colonnes = max(j for _, j in cellules) + 1 + 2 * MARGE
    else:
        lignes = colonnes = 50

    grille = Grille(lignes, colonnes, tore=args.tore, regle=regle)
    if args.aleatoire is not None:
        hasard = random.Random(args.graine)
        grille.placer([(i, j) for i in range(lignes) for j in range(colonnes)
                       if hasard.random() < args.aleatoire], centrer=False)
    elif args.coin:
        grille.placer([(i + 2, j + 2) for i, j in cellules], centrer=False)
    else:
        grille.placer(cellules)
    depart = len(grille)

    for _ in range(max(0, args.generations)):
        grille.etape()
        if args.jusqu_au_cycle and (grille.cycle or not grille.vivantes):
            break

    bords = "tore" if args.tore else "bords fermés"
    print(f"Motif      : {nom}", file=sortie)
    print(f"Univers    : {lignes}×{colonnes}, {bords}, règle {regle.libelle}", file=sortie)
    print(f"Population : {depart} → {len(grille)} cellules en {grille.generation} générations", file=sortie)
    if grille.cycle:
        print(f"Évolution  : {grille.cycle}", file=sortie)
    elif not grille.vivantes:
        print("Évolution  : la population s'est éteinte", file=sortie)

    if args.afficher:
        print(file=sortie)
        print(dessiner(grille), file=sortie)
    if args.png:
        enregistrer_png(grille, args.png, cote=args.cote)
        print(f"Image PNG  : {args.png}", file=sortie)
    if args.rle:
        with open(args.rle, "w", encoding="utf-8") as f:
            f.write(ecrire_rle(grille.vivantes, regle, nom, [f"Génération {grille.generation}"]))
        print(f"Fichier RLE: {args.rle}", file=sortie)
    return 0


def _motif_par_nom(nom: str):
    alias = {"gosper": "Canon à planeurs de Gosper", "lwss": "Vaisseau léger (LWSS)",
             "mwss": "Vaisseau moyen (MWSS)", "kok": "Galaxie de Kok"}
    return MOTIFS[alias[nom.lower()]] if nom.lower() in alias else chercher(nom)


def dessiner(grille: Grille) -> str:
    """Représentation texte de la zone occupée de la grille."""
    boite = grille.boite()
    if boite is None:
        return "(grille vide)"
    i0, j0, i1, j1 = boite
    j1 = min(j1, j0 + LARGEUR_AFFICHAGE_MAX - 1)
    return "\n".join(
        "".join("█" if (i, j) in grille else "·" for j in range(j0, j1 + 1))
        for i in range(i0, i1 + 1)
    )
