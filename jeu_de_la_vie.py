"""Jeu de la Vie de Conway — interface graphique Tkinter.

Lancer :  python jeu_de_la_vie.py

Raccourcis :
    Espace   lecture / pause
    →  ou N  avancer d'une génération
    R        remplissage aléatoire
    C        effacer la grille
    Clic     allumer / éteindre une cellule (maintenir et glisser pour dessiner)
"""

import random
import tkinter as tk
from tkinter import messagebox, ttk

from moteur import Grille
from motifs import CATEGORIES, MOTIFS

TAILLES = (30, 50, 100)          # tailles de grille proposées (carrées)
TAILLE_CANEVAS = 720             # côté maximal du canevas, en pixels
DENSITE_ALEATOIRE = 0.25         # proportion de cellules vivantes en mode aléatoire

COULEUR_FOND = "#fafafa"
COULEUR_VIVANTE = "#1f2937"
COULEUR_LIGNE = "#e5e7eb"

REGLES = (
    "Chaque cellule a 8 voisines. À chaque génération :\n\n"
    "• une cellule vivante avec 2 ou 3 voisines vivantes survit ;\n"
    "• une cellule vivante avec moins de 2 voisines meurt (isolement) ;\n"
    "• une cellule vivante avec plus de 3 voisines meurt (surpopulation) ;\n"
    "• une cellule morte avec exactement 3 voisines naît.\n\n"
    "Raccourcis : Espace = lecture/pause, → = une génération, "
    "R = aléatoire, C = effacer."
)


class Application:
    def __init__(self, racine: tk.Tk):
        self.racine = racine
        racine.title("Jeu de la Vie")
        racine.resizable(False, False)

        self.taille = tk.IntVar(value=TAILLES[0])
        self.tore = tk.BooleanVar(value=True)
        self.vitesse = tk.IntVar(value=10)          # générations par seconde
        self.en_lecture = False
        self._minuterie = None
        self._etat_dessin = None                    # True = on dessine, False = on gomme

        self.grille = Grille(self.taille.get(), self.taille.get(), tore=self.tore.get())
        self._construire_interface()
        self._construire_canevas()
        self._lier_raccourcis()

    # ============================================================ interface

    def _construire_interface(self):
        self.canevas = tk.Canvas(self.racine, background=COULEUR_FOND,
                                 highlightthickness=0)
        self.canevas.grid(row=0, column=0, padx=12, pady=12)
        self.canevas.bind("<Button-1>", self._clic)
        self.canevas.bind("<B1-Motion>", self._glisser)
        self.canevas.bind("<ButtonRelease-1>", lambda _e: setattr(self, "_etat_dessin", None))

        panneau = ttk.Frame(self.racine, padding=(0, 12, 12, 12))
        panneau.grid(row=0, column=1, sticky="n")

        # --- Commandes de simulation
        self.bouton_lecture = ttk.Button(panneau, text="▶  Lecture", command=self.basculer_lecture)
        self.bouton_lecture.pack(fill="x")
        ttk.Button(panneau, text="Génération suivante", command=self.avancer).pack(fill="x", pady=(6, 0))

        ttk.Label(panneau, text="Vitesse (générations / s)").pack(anchor="w", pady=(14, 0))
        tk.Scale(panneau, from_=1, to=60, orient="horizontal", variable=self.vitesse,
                 showvalue=True, length=200).pack(fill="x")

        # --- Compteurs
        compteurs = ttk.Frame(panneau)
        compteurs.pack(fill="x", pady=(12, 0))
        self.label_generation = ttk.Label(compteurs, text="Génération : 0")
        self.label_generation.pack(anchor="w")
        self.label_population = ttk.Label(compteurs, text="Population : 0")
        self.label_population.pack(anchor="w")

        ttk.Separator(panneau).pack(fill="x", pady=12)

        # --- Contenu de la grille
        ttk.Label(panneau, text="Motif").pack(anchor="w")
        bouton_motifs = ttk.Menubutton(panneau, text="Choisir un motif…")
        menu_motifs = tk.Menu(bouton_motifs, tearoff=False)
        for categorie, noms in CATEGORIES.items():
            sous_menu = tk.Menu(menu_motifs, tearoff=False)
            for nom in noms:
                sous_menu.add_command(label=nom, command=lambda n=nom: self.placer_motif(n))
            menu_motifs.add_cascade(label=categorie, menu=sous_menu)
        bouton_motifs["menu"] = menu_motifs
        bouton_motifs.pack(fill="x")

        ligne = ttk.Frame(panneau)
        ligne.pack(fill="x", pady=(6, 0))
        ttk.Button(ligne, text="Aléatoire", command=self.remplir_aleatoirement).pack(side="left", expand=True, fill="x")
        ttk.Button(ligne, text="Effacer", command=self.effacer).pack(side="left", expand=True, fill="x", padx=(6, 0))

        ttk.Separator(panneau).pack(fill="x", pady=12)

        # --- Réglages de la grille
        ttk.Label(panneau, text="Taille de la grille").pack(anchor="w")
        tailles = ttk.Frame(panneau)
        tailles.pack(fill="x")
        for t in TAILLES:
            ttk.Radiobutton(tailles, text=f"{t}×{t}", value=t, variable=self.taille,
                            command=self.changer_taille).pack(side="left", padx=(0, 6))
        ttk.Checkbutton(panneau, text="Bords reliés (tore)", variable=self.tore,
                        command=self._changer_tore).pack(anchor="w", pady=(8, 0))

        ttk.Separator(panneau).pack(fill="x", pady=12)
        ttk.Button(panneau, text="Règles", command=lambda: messagebox.showinfo("Règles du jeu", REGLES)).pack(fill="x")

    def _construire_canevas(self):
        """(Re)crée un rectangle par cellule. On ne fera ensuite que changer leur
        couleur, ce qui est bien plus rapide que tout redessiner à chaque tour."""
        g = self.grille
        self.cote = max(4, TAILLE_CANEVAS // max(g.lignes, g.colonnes))
        self.canevas.delete("all")
        self.canevas.config(width=g.colonnes * self.cote, height=g.lignes * self.cote)
        contour = COULEUR_LIGNE if self.cote >= 8 else ""
        self.rectangles = [
            [
                self.canevas.create_rectangle(
                    j * self.cote, i * self.cote, (j + 1) * self.cote, (i + 1) * self.cote,
                    fill=COULEUR_FOND, outline=contour)
                for j in range(g.colonnes)
            ]
            for i in range(g.lignes)
        ]
        self._redessiner_tout()

    def _lier_raccourcis(self):
        self.racine.bind("<space>", lambda _e: self.basculer_lecture())
        self.racine.bind("<Right>", lambda _e: self.avancer())
        self.racine.bind("<n>", lambda _e: self.avancer())
        self.racine.bind("<r>", lambda _e: self.remplir_aleatoirement())
        self.racine.bind("<c>", lambda _e: self.effacer())

    # ============================================================ affichage

    def _peindre(self, cellules):
        for i, j in cellules:
            couleur = COULEUR_VIVANTE if (i, j) in self.grille else COULEUR_FOND
            self.canevas.itemconfigure(self.rectangles[i][j], fill=couleur)

    def _redessiner_tout(self):
        g = self.grille
        self._peindre((i, j) for i in range(g.lignes) for j in range(g.colonnes))
        self._maj_compteurs()

    def _maj_compteurs(self):
        self.label_generation.config(text=f"Génération : {self.grille.generation}")
        self.label_population.config(text=f"Population : {len(self.grille)}")

    # ============================================================ simulation

    def avancer(self):
        changements = self.grille.etape()
        self._peindre(changements)
        self._maj_compteurs()
        if not changements and self.en_lecture:
            # Plus rien ne bouge (grille vide ou figée) : inutile de continuer.
            self.basculer_lecture()

    def basculer_lecture(self):
        self.en_lecture = not self.en_lecture
        self.bouton_lecture.config(text="⏸  Pause" if self.en_lecture else "▶  Lecture")
        if self.en_lecture:
            self._boucle()
        elif self._minuterie is not None:
            self.racine.after_cancel(self._minuterie)
            self._minuterie = None

    def _boucle(self):
        if not self.en_lecture:
            return
        self.avancer()
        if self.en_lecture:
            delai = max(1, 1000 // self.vitesse.get())
            self._minuterie = self.racine.after(delai, self._boucle)

    def _arreter(self):
        if self.en_lecture:
            self.basculer_lecture()

    # ============================================================ actions

    def effacer(self):
        self._arreter()
        self.grille.vider()
        self._redessiner_tout()

    def remplir_aleatoirement(self):
        self._arreter()
        g = self.grille
        g.placer(
            [(i, j) for i in range(g.lignes) for j in range(g.colonnes)
             if random.random() < DENSITE_ALEATOIRE],
            centrer=False,
        )
        self._redessiner_tout()

    def placer_motif(self, nom):
        self._arreter()
        self.grille.placer(MOTIFS[nom])
        self._redessiner_tout()

    def changer_taille(self):
        self._arreter()
        n = self.taille.get()
        self.grille = Grille(n, n, tore=self.tore.get())
        self._construire_canevas()

    def _changer_tore(self):
        self.grille.tore = self.tore.get()

    # ============================================================ souris

    def _cellule_sous(self, event):
        i, j = event.y // self.cote, event.x // self.cote
        return (i, j) if self.grille.dans_grille(i, j) else None

    def _clic(self, event):
        cellule = self._cellule_sous(event)
        if cellule is None:
            return
        # Le premier clic décide si on dessine ou si on gomme pendant le glisser.
        self._etat_dessin = cellule not in self.grille
        self._appliquer(cellule)

    def _glisser(self, event):
        cellule = self._cellule_sous(event)
        if cellule is not None and self._etat_dessin is not None:
            self._appliquer(cellule)

    def _appliquer(self, cellule):
        if self._etat_dessin:
            self.grille.allumer(*cellule)
        else:
            self.grille.eteindre(*cellule)
        self._peindre([cellule])
        self._maj_compteurs()


def main():
    racine = tk.Tk()
    Application(racine)
    racine.mainloop()


if __name__ == "__main__":
    main()
