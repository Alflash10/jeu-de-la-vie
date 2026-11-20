# interface-graphique Specification

## Purpose
Offrir une fenêtre Tkinter pour dessiner, simuler, analyser et échanger des motifs.

## Requirements

### Requirement: Contrôle de la simulation
L'interface SHALL permettre lecture/pause, génération suivante, génération précédente (historique du moteur) et une vitesse de 1 à 60 générations par seconde. La lecture SHALL s'arrêter seule quand tout est figé.

#### Scenario: Retour arrière
- **WHEN** l'utilisateur appuie sur `←` ou `Ctrl+Z` (`⌘Z` sur macOS)
- **THEN** la grille revient à l'état précédent

### Requirement: Dessin à la souris
L'interface SHALL basculer une cellule au clic et dessiner ou gommer au clic maintenu ; la barre d'état SHALL indiquer la position et le nombre de voisines de la cellule survolée.

#### Scenario: Annuler un dessin
- **WHEN** l'utilisateur dessine un trait puis annule
- **THEN** la grille revient à l'état d'avant le trait

### Requirement: Motifs et univers
L'interface SHALL proposer les motifs intégrés par catégorie, le choix de la règle (liste ou saisie B/S), une grille de 30×30 à 150×150, des bords fermés ou toriques et un remplissage aléatoire. Le motif courant SHALL rester centré quand la taille change, et la grille SHALL s'agrandir si un motif chargé ne tient pas.

#### Scenario: Motif trop grand
- **WHEN** l'utilisateur charge un motif plus grand que la grille
- **THEN** la grille s'agrandit pour le contenir

### Requirement: Analyse en direct
L'interface SHALL afficher la génération, la population, une courbe de population et la nature du cycle détecté (stable, oscillateur, vaisseau), et colorer les naissances.

#### Scenario: Oscillateur détecté
- **WHEN** un pentadécathlon tourne
- **THEN** l'interface affiche « Oscillateur de période 15 »

### Requirement: Fichiers et presse-papiers
L'interface SHALL ouvrir et enregistrer des motifs RLE (`Ctrl+O` / `Ctrl+S`), copier et coller du RLE (`Ctrl+C` / `Ctrl+V`) et exporter en PNG (`Ctrl+E`) ; ouvrir un motif portant une règle SHALL basculer sur cette règle.

#### Scenario: Coller depuis LifeWiki
- **WHEN** l'utilisateur colle un motif RLE HighLife
- **THEN** le motif s'affiche et la règle passe à HighLife

### Requirement: Affichage incrémental
L'interface SHALL ne recolorer à chaque génération que les cellules dont l'état a changé.

#### Scenario: Canon sur grande grille
- **WHEN** un canon tourne sur une grille 150×150
- **THEN** seuls les rectangles des cellules modifiées sont recolorés
