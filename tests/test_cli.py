"""Tests de la ligne de commande."""

import contextlib
import io
import os
import tempfile
import unittest

from jeu_de_la_vie.cli import main
from jeu_de_la_vie.rle import lire_rle


def executer(*args):
    sortie, erreurs = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(erreurs):
        try:
            code = main(list(args), sortie=sortie)
        except SystemExit as e:  # erreurs d'arguments levées par argparse
            code = e.code
    return code, sortie.getvalue(), erreurs.getvalue()


class TestCLI(unittest.TestCase):
    def test_liste_des_motifs(self):
        code, sortie, _ = executer("motifs")
        self.assertEqual(code, 0)
        self.assertIn("Canon à planeurs de Gosper", sortie)

    def test_liste_des_regles(self):
        code, sortie, _ = executer("regles")
        self.assertEqual(code, 0)
        self.assertIn("B36/S23", sortie)

    def test_simuler_un_planeur(self):
        code, sortie, _ = executer("simuler", "planeur", "-n", "8", "--afficher")
        self.assertEqual(code, 0)
        self.assertIn("5 → 5 cellules en 8 générations", sortie)
        self.assertIn("Vaisseau de période 4", sortie)
        self.assertIn("·█·\n··█\n███", sortie)

    def test_jusqu_au_cycle(self):
        code, sortie, _ = executer("simuler", "pulsar", "-n", "1000", "--jusqu-au-cycle")
        self.assertEqual(code, 0)
        self.assertIn("en 3 générations", sortie)
        self.assertIn("Oscillateur de période 3", sortie)

    def test_extinction(self):
        _, sortie, _ = executer("simuler", "diehard", "-n", "200", "--taille", "60", "--jusqu-au-cycle")
        self.assertIn("130 générations", sortie)
        self.assertIn("s'est éteinte", sortie)

    def test_aleatoire_reproductible(self):
        args = ("simuler", "--aleatoire", "0.3", "--graine", "7", "--taille", "30x40", "-n", "20")
        self.assertEqual(executer(*args)[1], executer(*args)[1])
        self.assertIn("30×40", executer(*args)[1])

    def test_regle_du_motif_et_regle_forcee(self):
        _, sortie, _ = executer("simuler", "replicateur", "-n", "0")
        self.assertIn("HighLife (B36/S23)", sortie)
        _, sortie, _ = executer("simuler", "replicateur", "-n", "0", "--regle", "B3/S23")
        self.assertIn("Conway (B3/S23)", sortie)

    def test_export_puis_relecture(self):
        with tempfile.TemporaryDirectory() as dossier:
            rle, image = os.path.join(dossier, "g.rle"), os.path.join(dossier, "g.png")
            code, _, _ = executer("simuler", "gosper", "-n", "30", "--taille", "60x80",
                                  "--rle", rle, "--png", image)
            self.assertEqual(code, 0)
            with open(image, "rb") as f:
                self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")
            with open(rle, encoding="utf-8") as f:
                self.assertEqual(len(lire_rle(f.read()).cellules), 36 + 5)  # canon + 1 planeur
            code, sortie, _ = executer("simuler", rle, "-n", "0")
            self.assertEqual(code, 0)
            self.assertIn("41 → 41", sortie)

    def test_coin(self):
        from jeu_de_la_vie.image import VIVANTE
        from tests.test_formats import lire_png

        with tempfile.TemporaryDirectory() as dossier:
            image = os.path.join(dossier, "b.png")
            executer("simuler", "bloc", "-n", "0", "--coin", "--taille", "8", "--cote", "4", "--png", image)
            with open(image, "rb") as f:
                _, _, pixels, _ = lire_png(f.read())
        cellule = lambda i, j: pixels[4 * i + 2][4 * j + 2]  # noqa: E731
        self.assertEqual([cellule(2, 2), cellule(3, 3)], [VIVANTE, VIVANTE])
        self.assertNotEqual(cellule(1, 1), VIVANTE)

    def test_erreurs(self):
        self.assertEqual(executer("simuler", "inexistant")[0], 2)
        self.assertEqual(executer("simuler")[0], 2)
        self.assertEqual(executer("simuler", "planeur", "--aleatoire", "0.5")[0], 2)
        self.assertEqual(executer("simuler", "planeur", "--regle", "B9")[0], 2)
        self.assertEqual(executer("simuler", "planeur", "--taille", "abc")[0], 2)


if __name__ == "__main__":
    unittest.main()
