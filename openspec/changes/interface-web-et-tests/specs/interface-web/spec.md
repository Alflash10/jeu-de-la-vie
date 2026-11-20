# Spec Delta

## Purpose

Offrir une interface web moderne du Jeu de la Vie, exécutée entièrement dans le navigateur, pour dessiner, simuler, analyser et partager des motifs sans installation.

## ADDED Requirements

### Requirement: Exécution sans serveur
L'application SHALL fonctionner comme un site statique : toute la simulation SHALL se faire dans le navigateur, sans appel réseau après le chargement de la page.

#### Scenario: Hors ligne après chargement
- **WHEN** la page est chargée puis la connexion réseau coupée
- **THEN** la simulation, le dessin, l'import et l'export continuent de fonctionner

### Requirement: Contrôle de la simulation
L'application SHALL proposer lecture/pause, génération suivante, génération précédente (au moins 1000 états d'historique) et une vitesse réglable de 1 à 60 générations par seconde. La lecture SHALL s'arrêter seule quand un état se répète ou que la population s'éteint.

#### Scenario: Arrêt automatique
- **WHEN** la lecture tourne sur un bloc
- **THEN** elle s'arrête et l'application indique « Stable »

#### Scenario: Retour arrière
- **WHEN** l'utilisateur avance de 3 générations puis recule de 3
- **THEN** la grille et le numéro de génération sont ceux du départ

### Requirement: Dessin à la souris et au toucher
L'application SHALL basculer une cellule au clic ou au toucher, et dessiner ou gommer en glissant. Le premier contact SHALL déterminer s'il s'agit de dessiner ou de gommer. Un trait entier SHALL s'annuler en une seule fois.

#### Scenario: Gommer en glissant
- **WHEN** l'utilisateur commence un glissement sur une cellule vivante
- **THEN** toutes les cellules traversées deviennent mortes

#### Scenario: Annuler un trait
- **WHEN** l'utilisateur dessine un trait puis annule une fois
- **THEN** la grille revient à l'état d'avant le trait

### Requirement: Informations de survol
L'application SHALL afficher la position et le nombre de voisines vivantes de la cellule sous le pointeur.

#### Scenario: Survol
- **WHEN** le pointeur survole une cellule qui a 3 voisines vivantes
- **THEN** la barre d'état affiche sa ligne, sa colonne et « 3 voisines »

### Requirement: Zoom et déplacement
L'application SHALL permettre de zoomer (molette, pincement, boutons) et de déplacer la vue, sans modifier l'état de la grille, et SHALL proposer un bouton pour recadrer la vue sur toute la grille.

#### Scenario: Zoom sans effet sur la simulation
- **WHEN** l'utilisateur zoome puis lance une génération
- **THEN** le résultat est identique à celui obtenu sans zoom

### Requirement: Motifs, règles et univers
L'application SHALL proposer tous les motifs intégrés par catégorie, le choix d'une règle connue ou la saisie d'une règle B/S, une grille de 30×30 à 300×300, des bords fermés ou toriques, et un remplissage aléatoire de densité réglable. Une règle invalide SHALL être signalée sans être appliquée.

#### Scenario: Règle invalide
- **WHEN** l'utilisateur saisit `B0/S23`
- **THEN** un message d'erreur s'affiche et la règle courante est conservée

#### Scenario: Motif imposant sa règle
- **WHEN** l'utilisateur charge le réplicateur HighLife
- **THEN** la règle passe à HighLife (B36/S23)

#### Scenario: Motif trop grand
- **WHEN** un motif chargé ne tient pas dans la grille
- **THEN** la grille s'agrandit pour le contenir, dans la limite de 300×300

### Requirement: Analyse en direct
L'application SHALL afficher la génération, la population, une courbe de population et la nature du cycle détecté, avec les mêmes libellés que le moteur Python (par exemple « Oscillateur de période 15 », « Vaisseau de période 4, se déplace de (+1, +1) »). Les naissances SHALL être affichées dans une couleur distincte.

#### Scenario: Vaisseau détecté
- **WHEN** un planeur évolue sur une grille à bords fermés
- **THEN** l'application affiche « Vaisseau de période 4, se déplace de (+1, +1) »

### Requirement: Import et export RLE
L'application SHALL ouvrir un fichier `.rle`, accepter du RLE collé, et enregistrer ou copier le motif courant en RLE avec sa règle. Un RLE invalide SHALL produire un message d'erreur sans modifier la grille.

#### Scenario: Coller un RLE invalide
- **WHEN** l'utilisateur colle un texte sans en-tête `x = …, y = …`
- **THEN** un message d'erreur s'affiche et la grille est inchangée

### Requirement: Export PNG
L'application SHALL télécharger une image PNG de la grille courante.

#### Scenario: Téléchargement
- **WHEN** l'utilisateur exporte en PNG
- **THEN** un fichier PNG valide aux dimensions de la grille est téléchargé

### Requirement: Lien de partage
L'application SHALL produire un lien contenant le motif courant, sa règle et la topologie, et ouvrir ce lien SHALL restaurer cet état.

#### Scenario: Ouvrir un lien partagé
- **WHEN** un utilisateur ouvre un lien de partage d'un canon de Gosper torique
- **THEN** la grille affiche ce canon, avec la même règle et des bords toriques

### Requirement: Raccourcis clavier
L'application SHALL reprendre les raccourcis de l'interface Tkinter : `Espace`, `→`/`N`, `←`/`Ctrl+Z`, `+`/`-`, `R`, `C`, `Ctrl+O`, `Ctrl+S`, `Ctrl+C`, `Ctrl+V`, `Ctrl+E` (`⌘` sur macOS). Les raccourcis SHALL être inactifs pendant la saisie dans un champ texte.

#### Scenario: Saisie de règle
- **WHEN** l'utilisateur tape `R` dans le champ de règle
- **THEN** la grille n'est pas remplie au hasard

### Requirement: Thème et accessibilité
L'application SHALL proposer un thème clair et un thème sombre (par défaut celui du système), être utilisable entièrement au clavier, donner un nom accessible à chaque commande et rester utilisable sur un écran de 360 px de large.

#### Scenario: Thème du système
- **WHEN** le système est en mode sombre et qu'aucun choix n'a été fait
- **THEN** l'application s'affiche en thème sombre

#### Scenario: Petit écran
- **WHEN** la page est affichée sur 360 px de large
- **THEN** toutes les commandes restent accessibles sans défilement horizontal

### Requirement: Fluidité
L'application SHALL afficher au moins 30 générations par seconde pour un canon de Gosper sur une grille 300×300 sur un ordinateur de bureau courant.

#### Scenario: Grande grille
- **WHEN** un canon de Gosper tourne à 60 générations par seconde sur 300×300
- **THEN** le rythme mesuré dépasse 30 générations par seconde
