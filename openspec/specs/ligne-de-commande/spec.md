# ligne-de-commande Specification

## Purpose
Utiliser le simulateur sans fenêtre via la commande `jeu-de-la-vie` (ou `python3 -m jeu_de_la_vie`).

## Requirements

### Requirement: Sous-commandes
La commande SHALL ouvrir l'interface graphique sans argument ou avec `interface`, lister les motifs intégrés par catégorie avec `motifs`, lister les règles connues avec `regles`, simuler sans fenêtre avec `simuler`, et afficher sa version avec `--version`.

#### Scenario: Liste des règles
- **WHEN** l'utilisateur lance `jeu-de-la-vie regles`
- **THEN** chaque règle connue est affichée avec sa notation et son nom

### Requirement: Simulation sans fenêtre
`simuler` SHALL accepter un nom de motif intégré, un chemin de fichier RLE ou `--aleatoire DENSITE` (avec `--graine` pour un résultat reproductible), et les options `-n` (100 par défaut), `--taille L[xC]`, `--regle`, `--tore`, `--coin` et `--jusqu-au-cycle`. Elle SHALL afficher un résumé : motif, univers, évolution de la population et, le cas échéant, le cycle détecté ou l'extinction.

#### Scenario: Planeur
- **WHEN** l'utilisateur lance `jeu-de-la-vie simuler planeur -n 8`
- **THEN** le résumé indique 5 → 5 cellules et « Vaisseau de période 4, se déplace de (+1, +1) »

#### Scenario: Arrêt au cycle
- **WHEN** `--jusqu-au-cycle` est donné et qu'un état se répète ou que la population s'éteint
- **THEN** la simulation s'arrête sans aller jusqu'à N générations

#### Scenario: Règle par défaut
- **WHEN** aucune `--regle` n'est donnée
- **THEN** la règle du motif est utilisée, sinon Conway

### Requirement: Sorties de la simulation
`simuler` SHALL pouvoir dessiner la grille finale dans le terminal (`--afficher`), l'exporter en PNG (`--png`, `--cote`) et l'enregistrer en RLE (`--rle`, avec la génération en commentaire).

#### Scenario: Export RLE
- **WHEN** l'utilisateur passe `--rle resultat.rle`
- **THEN** le fichier contient la grille finale, sa règle et un commentaire « Génération N »

### Requirement: Erreurs explicites
La commande MUST afficher `erreur : …` sur la sortie d'erreur et renvoyer le code 2 pour un motif inconnu, un fichier RLE illisible, un motif combiné à `--aleatoire` ou l'absence de motif ; les valeurs invalides de `--taille`, `--regle` et `--aleatoire` MUST être refusées dès l'analyse des arguments.

#### Scenario: Motif et aléatoire ensemble
- **WHEN** l'utilisateur lance `jeu-de-la-vie simuler planeur --aleatoire 0.3`
- **THEN** la commande échoue avec le code 2 et un message explicite
