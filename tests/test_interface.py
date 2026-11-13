"""Tests de l'interface : ils pilotent la vraie fenêtre Tkinter.

Ils sont ignorés automatiquement si Tkinter ou un affichage est indisponible
(en CI, ils tournent dans un écran virtuel grâce à xvfb).
"""

import os
import unittest
from unittest import mock

try:
    import tkinter as tk

    _racine_test = tk.Tk()
    _racine_test.destroy()
    TK_DISPONIBLE = True
except Exception:  # pas de module _tkinter, ou pas d'écran
    if os.environ.get("EXIGER_TK"):  # en CI : on veut un échec, pas des tests ignorés
        raise
    TK_DISPONIBLE = False


@unittest.skipUnless(TK_DISPONIBLE, "Tkinter ou affichage indisponible")
class TestInterface(unittest.TestCase):
    def setUp(self):
        from jeu_de_la_vie.interface import Application

        self.racine = tk.Tk()
        self.racine.withdraw()
        self.app = Application(self.racine)
        self.app._arreter()

    def tearDown(self):
        self.app._arreter()
        self.racine.destroy()

    def couleur(self, i, j):
        return self.app.canevas.itemcget(self.app.rectangles[i][j], "fill")

    def clic(self, i, j, glisser_vers=()):
        c = self.app.cote
        evenement = mock.Mock(x=j * c + c // 2, y=i * c + c // 2)
        self.app._clic(evenement)
        for gi, gj in glisser_vers:
            self.app._glisser(mock.Mock(x=gj * c + c // 2, y=gi * c + c // 2))
        self.app._relacher(evenement)

    def test_demarre_avec_le_canon_de_gosper(self):
        self.assertEqual(len(self.app.grille), 36)
        self.assertIn("Gosper", self.app.label_message.cget("text"))

    def test_avancer_et_annuler(self):
        depart = set(self.app.grille.vivantes)
        for _ in range(5):
            self.app.avancer()
        self.assertEqual(self.app.grille.generation, 5)
        for _ in range(5):
            self.app.annuler()
        self.assertEqual(self.app.grille.vivantes, depart)
        self.assertEqual(self.app.grille.generation, 0)

    def test_affichage_suit_la_grille(self):
        self.app.avancer()
        for i in range(self.app.grille.lignes):
            for j in range(self.app.grille.colonnes):
                vivante = (i, j) in self.app.grille
                self.assertEqual(self.couleur(i, j) != "#fafafa", vivante, (i, j))

    def test_naissances_colorees(self):
        self.app.placer_motif("Clignotant")
        self.app.avancer()
        nees = self.app._naissances
        self.assertEqual(len(nees), 2)
        for i, j in nees:
            self.assertEqual(self.couleur(i, j), "#2563eb")

    def test_clic_et_dessin(self):
        self.app.effacer()
        self.clic(1, 1, glisser_vers=[(1, 2), (1, 3)])
        self.assertEqual(self.app.grille.vivantes, {(1, 1), (1, 2), (1, 3)})
        self.clic(1, 1, glisser_vers=[(1, 2)])  # commence sur une cellule vivante : gomme
        self.assertEqual(self.app.grille.vivantes, {(1, 3)})
        self.app.annuler()
        self.assertEqual(self.app.grille.vivantes, {(1, 1), (1, 2), (1, 3)})

    def test_clic_hors_grille_sans_erreur(self):
        self.app._clic(mock.Mock(x=10_000, y=10_000))

    def test_lecture_s_arrete_quand_tout_est_stable(self):
        self.app.placer_motif("Bloc")
        self.app.basculer_lecture()
        self.app.avancer()
        self.assertFalse(self.app.en_lecture)
        self.assertIn("Stable", self.app.label_cycle.cget("text"))

    def test_changer_de_regle(self):
        self.app.regle_txt.set("B36/S23")
        self.app._appliquer_regle()
        self.assertEqual(str(self.app.grille.regle), "B36/S23")
        self.assertEqual(self.app.regle_txt.get(), "HighLife (B36/S23)")
        self.app.regle_txt.set("n'importe quoi")
        self.app._appliquer_regle()
        self.assertEqual(str(self.app.grille.regle), "B36/S23")  # inchangée

    def test_motif_avec_sa_propre_regle(self):
        self.app.placer_motif("Réplicateur")
        self.assertEqual(str(self.app.grille.regle), "B36/S23")

    def test_changer_de_taille_garde_le_motif(self):
        self.app.placer_motif("Planeur")
        avant = len(self.app.grille)
        self.app.changer_taille(100)
        self.assertEqual((self.app.grille.lignes, len(self.app.grille)), (100, avant))

    def test_grand_motif_agrandit_la_grille(self):
        self.app.changer_taille(30)
        self.app.placer_motif("Canon à planeurs de Gosper")
        self.assertGreaterEqual(self.app.grille.lignes, 40)

    def test_copier_coller_rle(self):
        self.app.placer_motif("Pulsar")
        depart = set(self.app.grille.vivantes)
        self.app.copier_rle()
        self.app.effacer()
        self.app.coller_rle()
        self.assertEqual(self.app.grille.vivantes, depart)

    def test_coller_un_texte_invalide(self):
        self.racine.clipboard_clear()
        self.racine.clipboard_append("pas un motif")
        self.app.coller_rle()
        self.assertEqual(self.app.label_message.cget("foreground"), "#b91c1c")

    def test_courbe_de_population(self):
        for _ in range(10):
            self.app.avancer()
        self.assertEqual(len(self.app._populations), 11)
        self.app.annuler()
        self.assertEqual(self.app._populations[-1][0], 9)


if __name__ == "__main__":
    unittest.main()
