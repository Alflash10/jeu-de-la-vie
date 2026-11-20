# regles-bs Specification

## Purpose
Décrire les automates cellulaires « à la Vie » en notation B/S (*Birth / Survival*) et fournir une liste de règles connues.

## Requirements

### Requirement: Lecture de la notation B/S
Le système SHALL lire une règle au format `B<chiffres>/S<chiffres>` sans tenir compte de la casse ni des espaces, et SHALL accepter aussi les notations `S…/B…` et l'ancienne notation `survie/naissance` sans lettres (par exemple `23/3`).

#### Scenario: Notation standard
- **WHEN** on lit `b36 / s23`
- **THEN** la règle obtenue est HighLife (B36/S23)

#### Scenario: Ancienne notation
- **WHEN** on lit `23/3`
- **THEN** la règle obtenue est Conway (B3/S23)

#### Scenario: Texte illisible
- **WHEN** on lit `abc`
- **THEN** une erreur `RegleInvalide` est levée avec un exemple de format attendu

### Requirement: Règles non prises en charge
Le système MUST refuser les règles contenant 0 dans B, que la grille creuse ne peut pas représenter, ainsi que tout nombre de voisines hors de 0 à 8.

#### Scenario: Règle B0
- **WHEN** on lit `B0/S23`
- **THEN** une erreur `RegleInvalide` est levée

### Requirement: Règles connues nommées
Le système SHALL proposer les règles Conway, HighLife, Seeds, Day & Night, Vie sans mort, Labyrinthe, Morley et Replicator ; lire le texte d'une règle connue SHALL renvoyer la règle avec son nom.

#### Scenario: Libellé
- **WHEN** on affiche la règle B3/S23
- **THEN** son libellé est « Conway (B3/S23) »
