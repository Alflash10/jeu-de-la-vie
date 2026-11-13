"""Interface graphique Tkinter du Jeu de la Vie."""

import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Iterable, List, Optional, Set, Tuple

from . import __version__
from .image import enregistrer_png
from .moteur import Grille
from .motifs import CATEGORIES, MOTIFS
from .regles import CONWAY, REGLES_CONNUES, Regle, RegleInvalide
from .rle import FormatRLEInvalide, MotifRLE, ecrire_rle, lire_rle

Cellule = Tuple[int, int]

TAILLES = (30, 50, 75, 100, 150)    # tailles de grille proposées (carrées)
TAILLE_DEFAUT = 50
TAILLE_CANEVAS = 720                 # côté maximal du canevas, en pixels
DENSITE_ALEATOIRE = 0.25             # proportion de cellules vivantes en mode aléatoire
POINTS_GRAPHIQUE = 200               # générations affichées dans la courbe de population

COULEURS = {
    "fond": "#fafafa",
    "ligne": "#e5e7eb",
    "vivante": "#1f2937",
    "naissance": "#2563eb",
    "courbe": "#2563eb",
    "erreur": "#b91c1c",
}

REGLES_TEXTE = (
    "Chaque cellule a 8 voisines. À chaque génération, dans le Jeu de la Vie de "
    "Conway (règle B3/S23) :\n\n"
    "• une cellule morte avec exactement 3 voisines vivantes naît ;\n"
    "• une cellule vivante avec 2 ou 3 voisines vivantes survit ;\n"
    "• toutes les autres meurent ou restent mortes.\n\n"
    "La notation B/S permet d'essayer d'autres univers : B36/S23 (HighLife) "
    "fait naître aussi les cellules à 6 voisines, B2/S (Seeds) fait tout "
    "mourir à chaque tour sauf les naissances, etc. Choisissez-en une dans "
    "la liste ou tapez la vôtre puis Entrée."
)


class Application:
    def __init__(self, racine: tk.Tk):
        self.racine = racine
        racine.title("Jeu de la Vie")
        racine.resizable(False, False)
        self.mac = racine.tk.call("tk", "windowingsystem") == "aqua"
        self.mod = "Command" if self.mac else "Control"
        self.mod_txt = "⌘" if self.mac else "Ctrl+"

        self.taille = tk.StringVar(value=self._libelle_taille(TAILLE_DEFAUT))
        self.tore = tk.BooleanVar(value=False)
        self.colorer_naissances = tk.BooleanVar(value=True)
        self.vitesse = tk.IntVar(value=10)          # générations par seconde
        self.regle_txt = tk.StringVar(value=CONWAY.libelle)

        self.en_lecture = False
        self._minuterie = None
        self._etat_dessin: Optional[bool] = None    # True = on dessine, False = on gomme
        self._naissances: Set[Cellule] = set()      # cellules nées à la dernière génération
        self._populations: List[Tuple[int, int]] = []   # (génération, population)
        self._dossier = os.getcwd()

        self.grille = Grille(TAILLE_DEFAUT, TAILLE_DEFAUT, tore=self.tore.get())
        self._construire_menus()
        self._construire_interface()
        self._construire_canevas()
        self._lier_raccourcis()
        self._noter_population()
        self.placer_motif("Canon à planeurs de Gosper", memoriser=False)

    # ================================================================= menus

    def _construire_menus(self):
        barre = tk.Menu(self.racine)
        m = self.mod_txt

        fichier = tk.Menu(barre, tearoff=False)
        fichier.add_command(label="Ouvrir un motif RLE…", accelerator=f"{m}O", command=self.ouvrir)
        fichier.add_command(label="Enregistrer en RLE…", accelerator=f"{m}S", command=self.enregistrer)
        fichier.add_command(label="Exporter en PNG…", accelerator=f"{m}E", command=self.exporter_png)
        fichier.add_separator()
        fichier.add_command(label="Quitter", accelerator=f"{m}Q", command=self.racine.destroy)
        barre.add_cascade(label="Fichier", menu=fichier)

        edition = tk.Menu(barre, tearoff=False)
        edition.add_command(label="Annuler", accelerator=f"{m}Z", command=self.annuler)
        edition.add_separator()
        edition.add_command(label="Copier en RLE", accelerator=f"{m}C", command=self.copier_rle)
        edition.add_command(label="Coller un motif RLE", accelerator=f"{m}V", command=self.coller_rle)
        edition.add_separator()
        edition.add_command(label="Remplissage aléatoire", accelerator="R", command=self.remplir_aleatoirement)
        edition.add_command(label="Effacer la grille", accelerator="C", command=self.effacer)
        barre.add_cascade(label="Édition", menu=edition)

        motifs = tk.Menu(barre, tearoff=False)
        for categorie, noms in CATEGORIES.items():
            sous_menu = tk.Menu(motifs, tearoff=False)
            for nom in noms:
                sous_menu.add_command(label=nom, command=lambda n=nom: self.placer_motif(n))
            motifs.add_cascade(label=categorie, menu=sous_menu)
        barre.add_cascade(label="Motifs", menu=motifs)

        aide = tk.Menu(barre, tearoff=False)
        aide.add_command(label="Règles du jeu", command=lambda: messagebox.showinfo("Règles du jeu", REGLES_TEXTE))
        aide.add_command(label="Raccourcis clavier", command=self._afficher_raccourcis)
        aide.add_command(label="À propos", command=lambda: messagebox.showinfo(
            "À propos", f"Jeu de la Vie {__version__}\n\nAlexandre Bourgine et Leul.\n"
                        "Projet NSI repris et étendu."))
        barre.add_cascade(label="Aide", menu=aide)

        self.racine.config(menu=barre)

    def _afficher_raccourcis(self):
        m = self.mod_txt
        messagebox.showinfo("Raccourcis clavier", "\n".join([
            "Espace\tlecture / pause",
            "→ ou N\tgénération suivante",
            f"← ou {m}Z\tannuler (génération précédente)",
            "+ / −\tplus vite / moins vite",
            "R\tremplissage aléatoire",
            "C\teffacer la grille",
            f"{m}O / {m}S\touvrir / enregistrer un motif RLE",
            f"{m}C / {m}V\tcopier / coller un motif RLE",
            f"{m}E\texporter en PNG",
            "",
            "Clic : allumer ou éteindre une cellule.",
            "Clic maintenu : dessiner (ou gommer si la première cellule était vivante).",
        ]))

    # ============================================================ interface

    def _construire_interface(self):
        self.canevas = tk.Canvas(self.racine, background=COULEURS["fond"], highlightthickness=0)
        self.canevas.grid(row=0, column=0, padx=12, pady=(12, 4))
        self.canevas.bind("<Button-1>", self._clic)
        self.canevas.bind("<B1-Motion>", self._glisser)
        self.canevas.bind("<ButtonRelease-1>", self._relacher)
        self.canevas.bind("<Motion>", self._survoler)
        self.canevas.bind("<Leave>", lambda _e: self.label_position.config(text=""))

        panneau = ttk.Frame(self.racine, padding=(0, 12, 12, 0))
        panneau.grid(row=0, column=1, sticky="n")

        # --- Simulation
        self.bouton_lecture = ttk.Button(panneau, text="▶  Lecture", command=self.basculer_lecture)
        self.bouton_lecture.pack(fill="x")
        ligne = ttk.Frame(panneau)
        ligne.pack(fill="x", pady=(6, 0))
        self.bouton_annuler = ttk.Button(ligne, text="◀  Précédente", command=self.annuler)
        self.bouton_annuler.pack(side="left", expand=True, fill="x")
        ttk.Button(ligne, text="Suivante  ▶", command=self.avancer).pack(
            side="left", expand=True, fill="x", padx=(6, 0))

        ttk.Label(panneau, text="Vitesse (générations / s)").pack(anchor="w", pady=(12, 0))
        tk.Scale(panneau, from_=1, to=60, orient="horizontal", variable=self.vitesse,
                 showvalue=True, length=240).pack(fill="x")

        # --- Statistiques
        stats = ttk.Frame(panneau)
        stats.pack(fill="x", pady=(10, 0))
        self.label_generation = ttk.Label(stats, text="Génération : 0")
        self.label_generation.pack(anchor="w")
        self.label_population = ttk.Label(stats, text="Population : 0")
        self.label_population.pack(anchor="w")
        self.graphique = tk.Canvas(panneau, width=240, height=64, background="white",
                                   highlightthickness=1, highlightbackground=COULEURS["ligne"])
        self.graphique.pack(fill="x", pady=(6, 0))
        self.courbe = self.graphique.create_line(0, 0, 0, 0, fill=COULEURS["courbe"], width=2)
        self.label_cycle = ttk.Label(panneau, text="", wraplength=240, justify="left")
        self.label_cycle.pack(anchor="w", pady=(6, 0))

        ttk.Separator(panneau).pack(fill="x", pady=10)

        # --- Univers
        ttk.Label(panneau, text="Règle (notation B/S)").pack(anchor="w")
        self.choix_regle = ttk.Combobox(panneau, textvariable=self.regle_txt,
                                        values=[r.libelle for r in REGLES_CONNUES])
        self.choix_regle.pack(fill="x")
        self.choix_regle.bind("<<ComboboxSelected>>", lambda _e: self._appliquer_regle())
        self.choix_regle.bind("<Return>", lambda _e: self._appliquer_regle())
        self.choix_regle.bind("<FocusOut>", lambda _e: self._appliquer_regle())

        ttk.Label(panneau, text="Taille de la grille").pack(anchor="w", pady=(8, 0))
        choix_taille = ttk.Combobox(panneau, textvariable=self.taille, state="readonly",
                                    values=[self._libelle_taille(t) for t in TAILLES])
        choix_taille.pack(fill="x")
        choix_taille.bind("<<ComboboxSelected>>", lambda _e: self.changer_taille(self._taille_choisie()))

        ttk.Checkbutton(panneau, text="Bords reliés (tore)", variable=self.tore,
                        command=self._changer_tore).pack(anchor="w", pady=(8, 0))
        ttk.Checkbutton(panneau, text="Colorer les naissances", variable=self.colorer_naissances,
                        command=self._redessiner_tout).pack(anchor="w")

        ttk.Separator(panneau).pack(fill="x", pady=10)
        ligne = ttk.Frame(panneau)
        ligne.pack(fill="x")
        ttk.Button(ligne, text="Aléatoire", command=self.remplir_aleatoirement).pack(side="left", expand=True, fill="x")
        ttk.Button(ligne, text="Effacer", command=self.effacer).pack(side="left", expand=True, fill="x", padx=(6, 0))

        # --- Barre d'état
        barre = ttk.Frame(self.racine, padding=(12, 0, 12, 8))
        barre.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.label_message = tk.Label(barre, text="", anchor="w")
        self.label_message.pack(side="left", fill="x", expand=True)
        self._couleur_texte = self.label_message.cget("foreground")
        self.label_position = ttk.Label(barre, text="", anchor="e")
        self.label_position.pack(side="right")

    def _construire_canevas(self):
        """(Re)crée un rectangle par cellule. Ensuite, on ne fait que changer
        leur couleur : c'est bien plus rapide que de tout redessiner."""
        g = self.grille
        self.cote = max(3, TAILLE_CANEVAS // max(g.lignes, g.colonnes))
        self.canevas.delete("all")
        self.canevas.config(width=g.colonnes * self.cote, height=g.lignes * self.cote)
        contour = COULEURS["ligne"] if self.cote >= 8 else ""
        c = self.cote
        self.rectangles = [
            [self.canevas.create_rectangle(j * c, i * c, (j + 1) * c, (i + 1) * c,
                                           fill=COULEURS["fond"], outline=contour)
             for j in range(g.colonnes)]
            for i in range(g.lignes)
        ]
        self._naissances = set()
        self._redessiner_tout()

    def _lier_raccourcis(self):
        r, m = self.racine, self.mod

        def touche(sequence, action):
            # Les raccourcis à une lettre ne doivent pas se déclencher pendant
            # la saisie d'une règle dans la liste déroulante.
            def gestionnaire(event):
                if isinstance(event.widget, (tk.Entry, ttk.Entry)):
                    return None
                action()
                return "break"
            r.bind(sequence, gestionnaire)

        touche("<space>", self.basculer_lecture)
        touche("<Right>", self.avancer)
        touche("<n>", self.avancer)
        touche("<Left>", self.annuler)
        touche("<r>", self.remplir_aleatoirement)
        touche("<c>", self.effacer)
        touche("<plus>", lambda: self.vitesse.set(min(60, self.vitesse.get() + 5)))
        touche("<equal>", lambda: self.vitesse.set(min(60, self.vitesse.get() + 5)))
        touche("<minus>", lambda: self.vitesse.set(max(1, self.vitesse.get() - 5)))
        touche(f"<{m}-z>", self.annuler)
        touche(f"<{m}-c>", self.copier_rle)
        touche(f"<{m}-v>", self.coller_rle)
        r.bind(f"<{m}-o>", lambda _e: self.ouvrir())
        r.bind(f"<{m}-s>", lambda _e: self.enregistrer())
        r.bind(f"<{m}-e>", lambda _e: self.exporter_png())
        r.bind(f"<{m}-q>", lambda _e: self.racine.destroy())

    # ============================================================ affichage

    def _peindre(self, cellules: Iterable[Cellule]):
        g, naissances = self.grille, self._naissances
        colorer = self.colorer_naissances.get()
        for cellule in cellules:
            if cellule not in g:
                couleur = COULEURS["fond"]
            elif colorer and cellule in naissances:
                couleur = COULEURS["naissance"]
            else:
                couleur = COULEURS["vivante"]
            i, j = cellule
            self.canevas.itemconfigure(self.rectangles[i][j], fill=couleur)

    def _redessiner_tout(self):
        g = self.grille
        self._peindre((i, j) for i in range(g.lignes) for j in range(g.colonnes))
        self._maj_infos()

    def _maj_infos(self):
        g = self.grille
        self.label_generation.config(text=f"Génération : {g.generation}")
        self.label_population.config(text=f"Population : {len(g)}")
        self.label_cycle.config(text=str(g.cycle) if g.cycle else "")
        self.bouton_annuler.state(["!disabled"] if g.peut_annuler() else ["disabled"])
        self._dessiner_courbe()

    def _noter_population(self):
        """Met à jour la courbe de population pour la génération courante.

        Les points des générations « futures » (après un retour en arrière)
        sont oubliés ; le point de la génération courante est remplacé s'il
        existe déjà (modification à la main)."""
        g = self.grille
        pops = self._populations
        while pops and pops[-1][0] > g.generation:
            pops.pop()
        if pops and pops[-1][0] == g.generation:
            pops[-1] = (g.generation, len(g))
        else:
            pops.append((g.generation, len(g)))
            del pops[:-POINTS_GRAPHIQUE]

    def _dessiner_courbe(self):
        points = [p for _, p in self._populations]
        largeur = int(self.graphique["width"])
        hauteur = int(self.graphique["height"])
        if len(points) < 2:
            self.graphique.coords(self.courbe, 0, hauteur - 2, 0, hauteur - 2)
            return
        maxi = max(max(points), 1)
        pas = largeur / (POINTS_GRAPHIQUE - 1)
        coords = []
        for k, p in enumerate(points):
            coords += [k * pas, hauteur - 4 - (hauteur - 8) * p / maxi]
        self.graphique.coords(self.courbe, *coords)

    def message(self, texte: str, erreur: bool = False):
        self.label_message.config(text=texte, foreground=COULEURS["erreur"] if erreur else self._couleur_texte)

    # =========================================================== simulation

    def avancer(self):
        anciennes_naissances = self._naissances
        changements = self.grille.etape()
        self._naissances = {c for c in changements if c in self.grille}
        self._peindre(changements | anciennes_naissances)
        self._noter_population()
        self._maj_infos()
        if self.en_lecture and (not self.grille.vivantes or
                                (self.grille.cycle and self.grille.cycle.nature == "stable")):
            # Plus rien ne bouge : inutile de continuer.
            self.basculer_lecture()

    def annuler(self):
        if not self.grille.peut_annuler():
            return
        self._arreter()
        changements = self.grille.annuler()
        anciennes_naissances = self._naissances
        self._naissances = set()
        self._peindre(changements | anciennes_naissances)
        self._noter_population()
        self._maj_infos()

    def basculer_lecture(self):
        self.en_lecture = not self.en_lecture
        self.bouton_lecture.config(text="⏸  Pause" if self.en_lecture else "▶  Lecture")
        if self.en_lecture:
            self.message("")
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

    # ===================================================== modifications

    def _remplacer(self, cellules: Iterable[Cellule], centrer: bool, memoriser: bool = True):
        """Remplace tout le contenu de la grille (motif, aléatoire, fichier…)."""
        self._arreter()
        if memoriser:
            self.grille.memoriser()
        self.grille.placer(cellules, centrer=centrer)
        self._naissances = set()
        self._populations = []
        self._noter_population()
        self._redessiner_tout()

    def effacer(self):
        self._remplacer([], centrer=False)
        self.message("Grille effacée.")

    def remplir_aleatoirement(self):
        g = self.grille
        self._remplacer([(i, j) for i in range(g.lignes) for j in range(g.colonnes)
                         if random.random() < DENSITE_ALEATOIRE], centrer=False)
        self.message(f"Remplissage aléatoire ({DENSITE_ALEATOIRE:.0%} de cellules vivantes).")

    def placer_motif(self, nom: str, memoriser: bool = True):
        motif = MOTIFS[nom]
        if motif.regle is not None and motif.regle != self.grille.regle:
            self._definir_regle(motif.regle)
        self._agrandir_si_besoin(motif.cellules)
        self._remplacer(motif.cellules, centrer=True, memoriser=memoriser)
        self.message(f"{motif.nom} : {motif.description}")

    def _charger(self, motif: MotifRLE, origine: str):
        if not motif.cellules:
            self.message(f"{origine} : motif vide.", erreur=True)
            return
        if not self._agrandir_si_besoin(motif.cellules):
            return
        if motif.regle is not None:
            self._definir_regle(motif.regle)
        self._remplacer(motif.cellules, centrer=True)
        hauteur = max(i for i, _ in motif.cellules) + 1
        largeur = max(j for _, j in motif.cellules) + 1
        nom = f"« {motif.nom} »" if motif.nom else "Motif"
        self.message(f"{nom} chargé depuis {origine} ({largeur}×{hauteur}, {len(motif.cellules)} cellules).")

    def _agrandir_si_besoin(self, cellules: List[Cellule]) -> bool:
        """Agrandit la grille si le motif n'y tient pas. Renvoie False s'il est
        trop grand pour la plus grande taille proposée."""
        hauteur = max(i for i, _ in cellules) - min(i for i, _ in cellules) + 1
        largeur = max(j for _, j in cellules) - min(j for _, j in cellules) + 1
        besoin = max(hauteur, largeur) + 4  # un peu de marge autour
        if besoin <= self.grille.lignes:
            return True
        for t in TAILLES:
            if t >= besoin:
                self.changer_taille(t)
                return True
        messagebox.showerror("Motif trop grand",
                             f"Ce motif mesure {largeur}×{hauteur} cellules ; la plus grande grille "
                             f"proposée fait {TAILLES[-1]}×{TAILLES[-1]}.")
        return False

    def changer_taille(self, n: int):
        """Change la taille de la grille en gardant le motif centré."""
        self._arreter()
        ancienne = self.grille
        decalage = (n - ancienne.lignes) // 2
        self.grille = Grille(n, n, tore=self.tore.get(), regle=ancienne.regle,
                             vivantes=[(i + decalage, j + decalage) for i, j in ancienne.vivantes])
        self.grille.generation = ancienne.generation
        self.taille.set(self._libelle_taille(n))
        self._construire_canevas()

    def _changer_tore(self):
        self.grille.tore = self.tore.get()
        self._maj_infos()

    def _definir_regle(self, regle: Regle):
        self.grille.changer_regle(regle)
        self.regle_txt.set(regle.libelle)

    def _appliquer_regle(self):
        texte = self.regle_txt.get().strip()
        # Une entrée de la liste se présente sous la forme « Nom (B3/S23) ».
        if texte.endswith(")") and "(" in texte:
            texte = texte[texte.rindex("(") + 1:-1]
        try:
            regle = Regle.depuis_texte(texte)
        except RegleInvalide as e:
            self.message(str(e), erreur=True)
            self.regle_txt.set(self.grille.regle.libelle)
            return
        if regle != self.grille.regle:
            self._definir_regle(regle)
            self._maj_infos()
            self.message(f"Règle : {regle.libelle}")
        else:
            self.regle_txt.set(self.grille.regle.libelle)
        self.canevas.focus_set()

    # ============================================================ fichiers

    def ouvrir(self):
        chemin = filedialog.askopenfilename(
            title="Ouvrir un motif", initialdir=self._dossier,
            filetypes=[("Motifs RLE", "*.rle"), ("Tous les fichiers", "*")])
        if not chemin:
            return
        self._dossier = os.path.dirname(chemin)
        try:
            with open(chemin, encoding="utf-8", errors="replace") as f:
                motif = lire_rle(f.read())
        except (OSError, FormatRLEInvalide, RegleInvalide) as e:
            messagebox.showerror("Impossible d'ouvrir le motif", str(e))
            return
        self._charger(motif, os.path.basename(chemin))

    def enregistrer(self):
        if not self.grille.vivantes:
            self.message("La grille est vide : rien à enregistrer.", erreur=True)
            return
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer le motif", initialdir=self._dossier, defaultextension=".rle",
            filetypes=[("Motifs RLE", "*.rle")])
        if not chemin:
            return
        self._dossier = os.path.dirname(chemin)
        nom = os.path.splitext(os.path.basename(chemin))[0]
        texte = ecrire_rle(self.grille.vivantes, self.grille.regle, nom,
                           [f"Génération {self.grille.generation}, créé avec Jeu de la Vie {__version__}"])
        try:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        except OSError as e:
            messagebox.showerror("Impossible d'enregistrer", str(e))
            return
        self.message(f"Motif enregistré dans {os.path.basename(chemin)}.")

    def exporter_png(self):
        chemin = filedialog.asksaveasfilename(
            title="Exporter en image", initialdir=self._dossier, defaultextension=".png",
            filetypes=[("Image PNG", "*.png")])
        if not chemin:
            return
        self._dossier = os.path.dirname(chemin)
        try:
            enregistrer_png(self.grille, chemin, cote=max(4, self.cote))
        except OSError as e:
            messagebox.showerror("Impossible d'exporter", str(e))
            return
        self.message(f"Image enregistrée dans {os.path.basename(chemin)}.")

    def copier_rle(self):
        if not self.grille.vivantes:
            self.message("La grille est vide : rien à copier.", erreur=True)
            return
        self.racine.clipboard_clear()
        self.racine.clipboard_append(ecrire_rle(self.grille.vivantes, self.grille.regle))
        self.message("Motif copié au format RLE dans le presse-papiers.")

    def coller_rle(self):
        try:
            texte = self.racine.clipboard_get()
        except tk.TclError:
            self.message("Le presse-papiers est vide.", erreur=True)
            return
        try:
            motif = lire_rle(texte)
        except (FormatRLEInvalide, RegleInvalide) as e:
            self.message(f"Le presse-papiers ne contient pas de motif RLE valide : {e}", erreur=True)
            return
        self._charger(motif, "le presse-papiers")

    # =============================================================== souris

    def _cellule_sous(self, event) -> Optional[Cellule]:
        i, j = event.y // self.cote, event.x // self.cote
        return (i, j) if self.grille.dans_grille(i, j) else None

    def _clic(self, event):
        self.canevas.focus_set()
        cellule = self._cellule_sous(event)
        if cellule is None:
            return
        self.grille.memoriser()
        # Le premier clic décide si l'on dessine ou si l'on gomme en glissant.
        self._etat_dessin = cellule not in self.grille
        self._appliquer(cellule)

    def _glisser(self, event):
        self._survoler(event)
        cellule = self._cellule_sous(event)
        if cellule is not None and self._etat_dessin is not None:
            self._appliquer(cellule)

    def _relacher(self, _event):
        self._etat_dessin = None

    def _appliquer(self, cellule: Cellule):
        if self._etat_dessin:
            self.grille.allumer(*cellule)
        else:
            self.grille.eteindre(*cellule)
        self._naissances.discard(cellule)
        self._peindre([cellule])
        self._noter_population()
        self._maj_infos()

    def _survoler(self, event):
        cellule = self._cellule_sous(event)
        if cellule is None:
            self.label_position.config(text="")
        else:
            i, j = cellule
            self.label_position.config(text=f"ligne {i}, colonne {j} · {self.grille.voisins(i, j)} voisine(s)")

    # =============================================================== outils

    @staticmethod
    def _libelle_taille(n: int) -> str:
        return f"{n} × {n}"

    def _taille_choisie(self) -> int:
        return int(self.taille.get().split("×")[0])


def lancer() -> None:
    racine = tk.Tk()
    Application(racine)
    racine.mainloop()
