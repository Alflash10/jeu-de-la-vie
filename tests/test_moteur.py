import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from moteur import Grille  # noqa: E402
from motifs import MOTIFS, lire  # noqa: E402


def decaler(cellules, di, dj):
    return {(i + di, j + dj) for i, j in cellules}


class TestRegles(unittest.TestCase):
    def test_cellule_isolee_meurt(self):
        g = Grille(5, 5, vivantes=[(2, 2)])
        g.etape()
        self.assertEqual(len(g), 0)

    def test_naissance_avec_trois_voisins(self):
        g = Grille(5, 5, vivantes=[(1, 1), (1, 2), (2, 1)])
        g.etape()
        self.assertIn((2, 2), g)

    def test_surpopulation(self):
        # La cellule centrale a 4 voisines : elle meurt.
        g = Grille(5, 5, vivantes=[(2, 2), (1, 2), (3, 2), (2, 1), (2, 3)])
        g.etape()
        self.assertNotIn((2, 2), g)

    def test_comptage_des_voisins(self):
        g = Grille(3, 3, vivantes=[(0, 0), (0, 1), (2, 2)])
        self.assertEqual(g.voisins(1, 1), 3)
        self.assertEqual(g.voisins(0, 0), 1)


class TestMotifs(unittest.TestCase):
    def test_bloc_stable(self):
        bloc = {(1, 1), (1, 2), (2, 1), (2, 2)}
        g = Grille(4, 4, vivantes=bloc)
        changements = g.etape()
        self.assertEqual(changements, frozenset())
        self.assertEqual(g.vivantes, bloc)

    def test_clignotant_periode_2(self):
        g = Grille(5, 5)
        g.placer(MOTIFS["Clignotant"])
        depart = set(g.vivantes)
        g.etape()
        self.assertNotEqual(g.vivantes, depart)
        g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_pulsar_periode_3(self):
        g = Grille(17, 17)
        g.placer(MOTIFS["Pulsar"])
        depart = set(g.vivantes)
        for _ in range(3):
            g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_planeur_se_deplace_en_diagonale(self):
        g = Grille(20, 20)
        g.placer(MOTIFS["Planeur"], centrer=False)
        depart = set(g.vivantes)
        for _ in range(4):
            g.etape()
        self.assertEqual(g.vivantes, decaler(depart, 1, 1))
        self.assertEqual(g.generation, 4)

    def test_canon_de_gosper_tire_des_planeurs(self):
        g = Grille(60, 60)
        g.placer(MOTIFS["Canon à planeurs de Gosper"], centrer=False)
        depart = len(g)
        for _ in range(30):  # période du canon
            g.etape()
        self.assertEqual(len(g), depart + 5)  # un planeur (5 cellules) de plus


class TestBords(unittest.TestCase):
    def test_tore_relie_les_bords(self):
        g = Grille(5, 5, tore=True, vivantes=[(0, 0)])
        self.assertEqual(len(list(g._voisines(0, 0))), 8)
        self.assertIn((4, 4), set(g._voisines(0, 0)))

    def test_planeur_traverse_le_bord_du_tore(self):
        g = Grille(8, 8, tore=True)
        g.placer(MOTIFS["Planeur"], centrer=False)
        depart = set(g.vivantes)
        for _ in range(4 * 8):  # 8 déplacements d'une case = un tour complet
            g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_sans_tore_le_planeur_se_fige_dans_le_coin(self):
        g = Grille(8, 8, tore=False)
        g.placer(MOTIFS["Planeur"], centrer=False)
        for _ in range(40):
            g.etape()
        self.assertEqual(g.vivantes, {(6, 6), (6, 7), (7, 6), (7, 7)})  # un bloc

    def test_cellules_hors_grille_ignorees(self):
        g = Grille(3, 3, vivantes=[(5, 5), (-1, 0), (1, 1)])
        self.assertEqual(g.vivantes, {(1, 1)})


class TestOutils(unittest.TestCase):
    def test_lire_dessin(self):
        self.assertEqual(lire(".O\nO."), [(0, 1), (1, 0)])

    def test_placer_centre_le_motif(self):
        g = Grille(5, 5)
        g.placer([(0, 0)])
        self.assertEqual(g.vivantes, {(2, 2)})

    def test_vider_remet_la_generation_a_zero(self):
        g = Grille(5, 5, vivantes=[(1, 1)])
        g.etape()
        g.vider()
        self.assertEqual((len(g), g.generation), (0, 0))


if __name__ == "__main__":
    unittest.main()
