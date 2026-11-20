# moteur-simulation Specification

## Purpose
Calculer l'évolution d'une grille finie de cellules selon une règle B/S, revenir en arrière et reconnaître les motifs stables, les oscillateurs et les vaisseaux, sans aucune dépendance à l'interface.

## Requirements

### Requirement: Grille finie creuse
Le moteur SHALL représenter une grille de L × C cellules (L, C ≥ 1) par l'ensemble de ses cellules vivantes, de sorte que le coût d'une génération dépende du nombre de cellules vivantes et non de la taille de la grille.

#### Scenario: Taille invalide
- **WHEN** une grille est créée avec 0 ligne ou 0 colonne
- **THEN** une `ValueError` est levée

#### Scenario: Cellule hors grille
- **WHEN** on allume une cellule située hors de la grille
- **THEN** la grille reste inchangée

### Requirement: Calcul d'une génération
Chaque génération SHALL appliquer la règle de la grille au voisinage de Moore (8 voisines) : une cellule morte naît si son nombre de voisines vivantes appartient à B, une cellule vivante survit s'il appartient à S. L'étape SHALL renvoyer l'ensemble des cellules dont l'état a changé.

#### Scenario: Planeur sous Conway
- **WHEN** un planeur avance de 4 générations avec la règle B3/S23
- **THEN** il retrouve sa forme décalée d'une case en diagonale

#### Scenario: Survie sans voisine (S0)
- **WHEN** la règle contient 0 dans S et qu'une cellule vivante est isolée
- **THEN** elle survit à la génération suivante

### Requirement: Bords fermés ou toriques
La grille SHALL proposer deux topologies : bords fermés (tout ce qui est hors de la grille est mort) et tore (les bords opposés sont reliés).

#### Scenario: Voisinage sur un tore
- **WHEN** la grille est torique
- **THEN** une cellule du bord gauche compte comme voisines les cellules du bord droit

### Requirement: Historique d'annulation borné
Le moteur SHALL mémoriser les états précédents (au plus 1000) et permettre de revenir au dernier état mémorisé, en renvoyant les cellules modifiées.

#### Scenario: Génération précédente
- **WHEN** on fait une étape puis qu'on annule
- **THEN** les cellules vivantes et le numéro de génération redeviennent ceux d'avant l'étape

#### Scenario: Rien à annuler
- **WHEN** on annule sans historique
- **THEN** l'ensemble des changements renvoyé est vide

### Requirement: Détection des cycles
Le moteur SHALL détecter la répétition d'un état à partir d'empreintes (sans conserver les états) et en déduire sa nature : stable (période 1), oscillateur (période > 1) ou vaisseau (même forme déplacée, avec son déplacement). Toute modification manuelle, tout changement de règle ou de topologie SHALL réinitialiser la détection.

#### Scenario: Oscillateur
- **WHEN** un pulsar évolue sous Conway
- **THEN** un cycle de période 3 est détecté

#### Scenario: Vaisseau
- **WHEN** un planeur évolue sur une grille à bords fermés suffisamment grande
- **THEN** un cycle de période 4 avec un déplacement de (+1, +1) est détecté

#### Scenario: Modification manuelle
- **WHEN** l'utilisateur bascule une cellule après la détection d'un cycle
- **THEN** le cycle détecté est oublié
