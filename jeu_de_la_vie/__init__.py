"""Jeu de la Vie de Conway : moteur, motifs, format RLE et interface Tkinter."""

__version__ = "2.0.0"

from .moteur import Cycle, Grille  # noqa: E402
from .regles import CONWAY, REGLES_CONNUES, Regle  # noqa: E402

__all__ = ["CONWAY", "Cycle", "Grille", "REGLES_CONNUES", "Regle", "__version__"]
