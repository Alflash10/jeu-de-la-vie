# Spec Delta

## Purpose

Garantir que le moteur TypeScript de l'interface web et ses données donnent exactement les mêmes résultats que le moteur Python, qui reste la référence du projet.

## ADDED Requirements

### Requirement: Moteur Python de référence
Le moteur Python SHALL rester la référence : en cas de désaccord entre les deux moteurs, c'est le comportement Python, décrit par `moteur-simulation`, `regles-bs` et `formats-fichiers`, qui fait foi.

#### Scenario: Désaccord détecté
- **WHEN** le moteur TypeScript donne un résultat différent d'une fixture Python
- **THEN** le test de conformité échoue et désigne la fixture concernée

### Requirement: Fixtures de conformité générées
Le projet SHALL générer depuis le moteur Python un jeu de fixtures versionné. Chaque fixture SHALL indiquer le motif, la règle, la taille, la topologie et le nombre de générations, ainsi que le résultat attendu : cellules vivantes finales, population à chaque génération et cycle détecté.

#### Scenario: Couverture des fixtures
- **WHEN** les fixtures sont générées
- **THEN** elles couvrent chaque motif intégré, chaque règle connue, les deux topologies et au moins un état aléatoire de graine fixée

### Requirement: Fixtures à jour
La CI MUST échouer si les fixtures ou les données partagées versionnées diffèrent de celles que produirait le moteur Python actuel.

#### Scenario: Moteur Python modifié sans régénération
- **WHEN** un changement du moteur Python modifie un résultat sans que les fixtures aient été régénérées
- **THEN** la CI échoue en indiquant la commande de régénération

### Requirement: Rejeu par le moteur TypeScript
Le moteur TypeScript SHALL reproduire exactement chaque fixture : mêmes cellules finales, mêmes populations et même cycle (début, période, déplacement).

#### Scenario: Canon de Gosper
- **WHEN** le moteur TypeScript rejoue la fixture du canon de Gosper sur 120 générations
- **THEN** ses cellules et populations sont identiques à celles du moteur Python

### Requirement: Données partagées
Les motifs intégrés et les règles connues affichés par l'application web SHALL provenir d'un export généré depuis les modules Python, et non d'une copie écrite à la main.

#### Scenario: Nouveau motif Python
- **WHEN** un motif est ajouté côté Python et les données régénérées
- **THEN** il apparaît dans l'application web sans autre modification

### Requirement: Conformité des formats
Les lecteurs et écrivains RLE des deux moteurs SHALL être interopérables : un RLE écrit par l'un SHALL être lu par l'autre avec les mêmes cellules, le même nom et la même règle. Les mêmes entrées invalides SHALL être refusées des deux côtés.

#### Scenario: RLE croisé
- **WHEN** le RLE écrit par Python pour chaque motif intégré est lu par le moteur TypeScript
- **THEN** les cellules, le nom et la règle obtenus sont identiques

#### Scenario: Règle refusée des deux côtés
- **WHEN** les deux moteurs lisent `B0/S23`
- **THEN** les deux la refusent
