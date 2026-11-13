import unittest

from jeu_de_la_vie.moteur import Cycle, Grille
from jeu_de_la_vie.motifs import MOTIFS, lire
from jeu_de_la_vie.regles import Regle


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
        g.placer(MOTIFS["Clignotant"].cellules)
        depart = set(g.vivantes)
        g.etape()
        self.assertNotEqual(g.vivantes, depart)
        g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_pulsar_periode_3(self):
        g = Grille(17, 17)
        g.placer(MOTIFS["Pulsar"].cellules)
        depart = set(g.vivantes)
        for _ in range(3):
            g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_planeur_se_deplace_en_diagonale(self):
        g = Grille(20, 20)
        g.placer(MOTIFS["Planeur"].cellules, centrer=False)
        depart = set(g.vivantes)
        for _ in range(4):
            g.etape()
        self.assertEqual(g.vivantes, decaler(depart, 1, 1))
        self.assertEqual(g.generation, 4)

    def test_canon_de_gosper_tire_des_planeurs(self):
        g = Grille(60, 60)
        g.placer(MOTIFS["Canon à planeurs de Gosper"].cellules, centrer=False)
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
        g.placer(MOTIFS["Planeur"].cellules, centrer=False)
        depart = set(g.vivantes)
        for _ in range(4 * 8):  # 8 déplacements d'une case = un tour complet
            g.etape()
        self.assertEqual(g.vivantes, depart)

    def test_sans_tore_le_planeur_se_fige_dans_le_coin(self):
        g = Grille(8, 8, tore=False)
        g.placer(MOTIFS["Planeur"].cellules, centrer=False)
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


class TestHistorique(unittest.TestCase):
    def test_annuler_revient_a_la_generation_precedente(self):
        g = Grille(10, 10)
        g.placer(MOTIFS["Planeur"].cellules)
        etats = [set(g.vivantes)]
        for _ in range(5):
            g.etape()
            etats.append(set(g.vivantes))
        for attendu in reversed(etats[:-1]):
            changements = g.annuler()
            self.assertEqual(g.vivantes, attendu)
            self.assertTrue(changements)
        self.assertEqual(g.generation, 0)
        self.assertFalse(g.peut_annuler())
        self.assertEqual(g.annuler(), frozenset())

    def test_annuler_une_modification_manuelle(self):
        g = Grille(5, 5, vivantes=[(1, 1)])
        g.memoriser()
        g.allumer(2, 2)
        g.annuler()
        self.assertEqual(g.vivantes, {(1, 1)})

    def test_historique_borne(self):
        from jeu_de_la_vie.moteur import TAILLE_HISTORIQUE
        g = Grille(5, 5)
        for _ in range(TAILLE_HISTORIQUE + 50):
            g.memoriser()
        annulations = 0
        while g.peut_annuler():
            g.annuler()
            annulations += 1
        self.assertEqual(annulations, TAILLE_HISTORIQUE)


class TestDetectionDesCycles(unittest.TestCase):
    def evoluer(self, nom, lignes=40, colonnes=40, maximum=100, tore=False):
        motif = MOTIFS[nom]
        g = Grille(lignes, colonnes, tore=tore, regle=motif.regle or Regle.depuis_texte("B3/S23"))
        g.placer(motif.cellules)
        for _ in range(maximum):
            g.etape()
            if g.cycle:
                break
        return g.cycle

    def test_motif_stable(self):
        self.assertEqual(self.evoluer("Ruche"), Cycle(0, 1))
        self.assertEqual(self.evoluer("Ruche").nature, "stable")

    def test_periodes_des_oscillateurs(self):
        attendues = {"Clignotant": 2, "Crapaud": 2, "Balise": 2, "Pulsar": 3,
                     "Galaxie de Kok": 8, "Pentadécathlon": 15}
        for nom, periode in attendues.items():
            with self.subTest(motif=nom):
                cycle = self.evoluer(nom)
                self.assertEqual((cycle.nature, cycle.periode), ("oscillateur", periode))

    def test_vaisseaux(self):
        self.assertEqual(self.evoluer("Planeur"), Cycle(0, 4, (1, 1)))
        lwss = self.evoluer("Vaisseau léger (LWSS)")
        self.assertEqual((lwss.nature, lwss.periode, abs(lwss.deplacement[1])), ("vaisseau", 4, 2))

    def test_population_eteinte_pas_de_cycle_avant(self):
        g = Grille(60, 60)
        g.placer(MOTIFS["Diehard"].cellules)
        g.avancer(129)
        self.assertGreater(len(g), 0)
        self.assertIsNone(g.cycle)
        g.etape()
        self.assertEqual(len(g), 0)  # le diehard disparaît à la génération 130

    def test_modification_efface_le_cycle(self):
        g = Grille(10, 10)
        g.placer(MOTIFS["Bloc"].cellules)
        g.etape()
        self.assertIsNotNone(g.cycle)
        g.allumer(0, 0)
        self.assertIsNone(g.cycle)

    def test_texte_du_cycle(self):
        self.assertIn("période 2", str(Cycle(0, 2)))
        self.assertIn("Stable", str(Cycle(3, 1)))
        self.assertIn("(+1, +1)", str(Cycle(0, 4, (1, 1))))


class TestAutresRegles(unittest.TestCase):
    def test_replicateur_highlife_se_recopie(self):
        motif = MOTIFS["Réplicateur"]
        self.assertEqual(str(motif.regle), "B36/S23")
        g = Grille(60, 60, regle=motif.regle)
        g.placer(motif.cellules)
        g.avancer(12)
        self.assertEqual(len(g), 2 * len(motif.cellules))  # deux copies

    def test_seeds_rien_ne_survit(self):
        g = Grille(10, 10, regle=Regle.depuis_texte("B2/S"), vivantes=[(4, 4), (4, 5)])
        g.etape()
        self.assertTrue(g.vivantes)
        self.assertFalse(g.vivantes & {(4, 4), (4, 5)})

    def test_vie_sans_mort_garde_les_cellules_isolees(self):
        g = Grille(10, 10, regle=Regle.depuis_texte("B3/S012345678"), vivantes=[(5, 5)])
        g.etape()
        self.assertEqual(g.vivantes, {(5, 5)})


if __name__ == "__main__":
    unittest.main()
