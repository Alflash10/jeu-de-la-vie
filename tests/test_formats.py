"""Tests des règles B/S, du format RLE et de l'export PNG."""

import struct
import unittest
import zlib

from jeu_de_la_vie.image import png
from jeu_de_la_vie.moteur import Grille
from jeu_de_la_vie.motifs import MOTIFS, chercher
from jeu_de_la_vie.regles import CONWAY, REGLES_CONNUES, Regle, RegleInvalide
from jeu_de_la_vie.rle import LARGEUR_LIGNE, FormatRLEInvalide, ecrire_rle, lire_rle


class TestRegles(unittest.TestCase):
    def test_lecture_notation_bs(self):
        r = Regle.depuis_texte("B36/S23")
        self.assertEqual((r.naissance, r.survie), ({3, 6}, {2, 3}))

    def test_casse_espaces_et_notations_alternatives(self):
        for texte in ("b3/s23", " B3 / S23 ", "S23/B3", "23/3"):
            with self.subTest(texte=texte):
                self.assertEqual(Regle.depuis_texte(texte), CONWAY)

    def test_regle_connue_garde_son_nom(self):
        self.assertEqual(Regle.depuis_texte("b36/s23").nom, "HighLife")
        self.assertEqual(CONWAY.libelle, "Conway (B3/S23)")

    def test_survie_vide(self):
        self.assertEqual(str(Regle.depuis_texte("B2/S")), "B2/S")

    def test_aller_retour_texte(self):
        for regle in REGLES_CONNUES:
            with self.subTest(regle=regle):
                self.assertEqual(Regle.depuis_texte(str(regle)), regle)

    def test_regles_invalides(self):
        for texte in ("", "B9/S23", "Conway", "B3/S2/3", "B0/S23"):
            with self.subTest(texte=texte), self.assertRaises(RegleInvalide):
                Regle.depuis_texte(texte)


class TestRLE(unittest.TestCase):
    PLANEUR = "#N Planeur\n#C Un commentaire\nx = 3, y = 3, rule = B3/S23\nbob$2bo$3o!\n"

    def test_lecture(self):
        motif = lire_rle(self.PLANEUR)
        self.assertEqual(sorted(motif.cellules), sorted(MOTIFS["Planeur"].cellules))
        self.assertEqual(motif.nom, "Planeur")
        self.assertEqual(motif.regle, CONWAY)
        self.assertEqual(motif.commentaires, ("Un commentaire",))

    def test_lignes_vides_multiples_et_corps_sur_plusieurs_lignes(self):
        motif = lire_rle("x = 2, y = 4\no$\n2$\nbo!")
        self.assertEqual(motif.cellules, [(0, 0), (3, 1)])
        self.assertIsNone(motif.regle)

    def test_tout_ce_qui_suit_le_point_d_exclamation_est_ignore(self):
        self.assertEqual(lire_rle("x = 1, y = 1\no!\nce texte est ignoré").cellules, [(0, 0)])

    def test_aller_retour_sur_tous_les_motifs(self):
        for motif in MOTIFS.values():
            with self.subTest(motif=motif.nom):
                texte = ecrire_rle(motif.cellules, motif.regle, motif.nom)
                relu = lire_rle(texte)
                self.assertEqual(sorted(relu.cellules), sorted(motif.cellules))
                self.assertEqual(relu.nom, motif.nom)

    def test_ecriture_compacte(self):
        texte = ecrire_rle(MOTIFS["Planeur"].cellules, CONWAY)
        self.assertEqual(texte, "x = 3, y = 3, rule = B3/S23\nbo$2bo$3o!\n")

    def test_ecriture_recadre_le_motif(self):
        texte = ecrire_rle([(10, 20), (10, 21)])
        self.assertEqual(texte.splitlines(), ["x = 2, y = 1", "2o!"])

    def test_lignes_vides_fusionnees(self):
        self.assertIn("o3$o", ecrire_rle([(0, 0), (3, 0)]))

    def test_longueur_des_lignes(self):
        texte = ecrire_rle(MOTIFS["Canon à planeurs de Gosper"].cellules)
        self.assertTrue(all(len(ligne) <= LARGEUR_LIGNE for ligne in texte.splitlines()))

    def test_motif_vide(self):
        self.assertEqual(lire_rle(ecrire_rle([])).cellules, [])

    def test_erreurs(self):
        for texte in ("bob$2bo$3o!", "x = 3, y = 3\nbo?b!"):
            with self.subTest(texte=texte), self.assertRaises(FormatRLEInvalide):
                lire_rle(texte)


class TestMotifs(unittest.TestCase):
    def test_recherche_tolerante(self):
        self.assertEqual(chercher("pentadecathlon").nom, "Pentadécathlon")
        self.assertEqual(chercher("Vaisseau léger").nom, "Vaisseau léger (LWSS)")
        with self.assertRaises(KeyError):
            chercher("inexistant")

    def test_chaque_motif_a_une_description_et_des_cellules(self):
        for motif in MOTIFS.values():
            with self.subTest(motif=motif.nom):
                self.assertTrue(motif.cellules)
                self.assertTrue(motif.description)


def lire_png(donnees):
    """Décode un PNG RVB 8 bits non filtré (celui que produit image.png)."""
    assert donnees[:8] == b"\x89PNG\r\n\x1a\n"
    pos, blocs = 8, {}
    while pos < len(donnees):
        (longueur,) = struct.unpack(">I", donnees[pos:pos + 4])
        type_bloc = donnees[pos + 4:pos + 8]
        contenu = donnees[pos + 8:pos + 8 + longueur]
        (crc,) = struct.unpack(">I", donnees[pos + 8 + longueur:pos + 12 + longueur])
        assert crc == zlib.crc32(type_bloc + contenu) & 0xFFFFFFFF, "CRC invalide"
        blocs[type_bloc] = blocs.get(type_bloc, b"") + contenu
        pos += 12 + longueur
    largeur, hauteur = struct.unpack(">II", blocs[b"IHDR"][:8])
    brut = zlib.decompress(blocs[b"IDAT"])
    taille_ligne = 1 + 3 * largeur
    pixels = [[tuple(brut[y * taille_ligne + 1 + 3 * x: y * taille_ligne + 4 + 3 * x]) for x in range(largeur)]
              for y in range(hauteur)]
    return largeur, hauteur, pixels, set(blocs)


class TestPNG(unittest.TestCase):
    def test_dimensions_et_blocs(self):
        largeur, hauteur, _, blocs = lire_png(png(3, 5, [], cote=4))
        self.assertEqual((largeur, hauteur), (20, 12))
        self.assertEqual(blocs, {b"IHDR", b"IDAT", b"IEND"})

    def test_couleurs_des_cellules(self):
        noir, blanc = (0, 0, 0), (255, 255, 255)
        _, _, pixels, _ = lire_png(png(2, 2, [(0, 1)], cote=3, quadrillage=False, fond=blanc, vivante=noir))
        self.assertEqual(pixels[1][4], noir)    # cellule (0, 1)
        self.assertEqual(pixels[1][1], blanc)   # cellule (0, 0)
        self.assertEqual(pixels[4][4], blanc)   # cellule (1, 1)

    def test_quadrillage(self):
        _, _, pixels, _ = lire_png(png(2, 2, [], cote=4, ligne=(1, 2, 3)))
        self.assertEqual(pixels[0][2], (1, 2, 3))   # bord supérieur
        self.assertEqual(pixels[2][4], (1, 2, 3))   # bord gauche de la 2ᵉ colonne
        self.assertNotEqual(pixels[2][2], (1, 2, 3))

    def test_cote_invalide(self):
        with self.assertRaises(ValueError):
            png(1, 1, [], cote=0)

    def test_export_depuis_une_grille(self):
        g = Grille(10, 12)
        g.placer(MOTIFS["Planeur"].cellules)
        largeur, hauteur, _, _ = lire_png(png(g.lignes, g.colonnes, g.vivantes, cote=2))
        self.assertEqual((largeur, hauteur), (24, 20))


if __name__ == "__main__":
    unittest.main()
