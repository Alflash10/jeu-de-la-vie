# formats-fichiers Specification

## Purpose
Échanger des motifs avec les autres logiciels au format RLE (Golly, LifeWiki) et exporter la grille en image PNG, sans bibliothèque externe.

## Requirements

### Requirement: Lecture RLE
Le système SHALL lire un motif RLE : en-tête `x = …, y = …` avec règle optionnelle `rule = …`, nom (`#N`), commentaires (`#C`/`#c`), et corps encodé (`b`/`.` morte, lettre vivante, `$` fin de ligne, `!` fin du motif, nombres de répétition).

#### Scenario: Règle enregistrée avec le motif
- **WHEN** on lit un RLE dont l'en-tête contient `rule = B36/S23`
- **THEN** le motif obtenu porte la règle HighLife

#### Scenario: En-tête manquant
- **WHEN** le texte ne contient pas d'en-tête `x = …, y = …`
- **THEN** une erreur `FormatRLEInvalide` est levée

#### Scenario: Caractère inattendu
- **WHEN** le corps contient un symbole non reconnu
- **THEN** une erreur `FormatRLEInvalide` nomme ce caractère

### Requirement: Écriture RLE
Le système SHALL écrire les cellules au format RLE, recadrées sur leur boîte englobante, avec nom, commentaires et règle optionnels, et des lignes de longueur bornée.

#### Scenario: Aller-retour
- **WHEN** on écrit puis relit n'importe quel motif intégré
- **THEN** on retrouve les mêmes cellules (à une translation près)

### Requirement: Export PNG
Le système SHALL produire un PNG valide (signature, blocs IHDR, IDAT compressé avec zlib, IEND, chacun avec son CRC32) où chaque cellule occupe un carré d'au moins 1 pixel de côté, avec quadrillage optionnel.

#### Scenario: Côté invalide
- **WHEN** on demande un côté de cellule inférieur à 1
- **THEN** une `ValueError` est levée

#### Scenario: Image décodable
- **WHEN** on exporte une grille
- **THEN** les CRC sont corrects et les pixels des cellules vivantes ont la couleur attendue
