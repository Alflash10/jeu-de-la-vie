# Spec Delta

## Purpose

Fixer ce que la suite de tests du projet doit vérifier et garantir (exécution, couverture, propriétés, interface web, intégration continue), pour que chaque changement soit validé automatiquement.

## ADDED Requirements

### Requirement: Commande unique de tests Python
Les tests Python SHALL se lancer avec `pytest` depuis la racine du dépôt. Tous les tests unittest existants SHALL continuer de passer sans être supprimés.

#### Scenario: Tests existants conservés
- **WHEN** on lance `pytest`
- **THEN** les 75 tests existants sont collectés et passent, en plus des nouveaux

### Requirement: Seuil de couverture Python
La suite Python MUST échouer si la couverture des lignes du paquet `jeu_de_la_vie` hors `interface.py` passe sous 90 %, ou si celle de `interface.py` passe sous 70 %.

#### Scenario: Couverture insuffisante
- **WHEN** du code non testé fait passer la couverture du moteur sous 90 %
- **THEN** `pytest` termine en échec et affiche les lignes non couvertes

### Requirement: Tests de propriétés du moteur Python
La suite SHALL vérifier sur des grilles générées aléatoirement que le moteur Python donne le même résultat qu'un moteur naïf de référence (parcours de toutes les cellules), pour des règles B/S quelconques sans B0 et pour les deux topologies.

#### Scenario: Grille aléatoire
- **WHEN** Hypothesis génère une grille, une règle et une topologie
- **THEN** une génération du moteur et du moteur naïf donne les mêmes cellules vivantes

### Requirement: Tests de propriétés des formats et des règles
La suite SHALL vérifier par génération aléatoire que l'écriture puis la lecture RLE redonne les mêmes cellules (recadrées), et que l'affichage puis la relecture d'une règle redonne la même règle.

#### Scenario: Aller-retour RLE
- **WHEN** Hypothesis génère un ensemble de cellules
- **THEN** `lire_rle(ecrire_rle(cellules))` redonne ces cellules translatées dans le coin

### Requirement: Invariants d'historique et de cycles
La suite SHALL vérifier qu'annuler N étapes après N étapes rend l'état de départ, et qu'un cycle détecté est réel : avancer de la période redonne le même état, décalé du déplacement annoncé.

#### Scenario: Cycle annoncé
- **WHEN** le moteur annonce un cycle de période p et de déplacement d
- **THEN** avancer encore de p générations redonne l'état courant décalé de d

### Requirement: Tests du moteur TypeScript
Le moteur TypeScript SHALL avoir des tests unitaires de son API publique (grille, règles, historique, cycles, RLE, PNG) et des tests de propriétés équivalents à ceux du moteur Python, avec une couverture des lignes d'au moins 90 %.

#### Scenario: API publique
- **WHEN** les tests unitaires du moteur TypeScript tournent
- **THEN** chaque fonction exportée est exercée, y compris ses cas d'erreur

### Requirement: Tests des composants web
Les composants de l'interface web SHALL être testés dans un DOM simulé : commandes de simulation, choix de motif et de règle, messages d'erreur, raccourcis clavier et noms accessibles.

#### Scenario: Erreur de règle
- **WHEN** le test saisit `B0/S23` dans le champ de règle
- **THEN** le message d'erreur est présent et la règle courante est inchangée

### Requirement: Tests de bout en bout
Des tests de bout en bout SHALL piloter l'application construite dans un vrai navigateur : charger un motif, lancer et arrêter la lecture, dessiner, annuler, importer et exporter un RLE, ouvrir un lien de partage, et vérifier l'affichage à 360 px de large.

#### Scenario: Parcours principal
- **WHEN** le test charge le planeur et avance de 4 générations
- **THEN** l'application affiche la génération 4, une population de 5 et le vaisseau détecté

### Requirement: Intégration continue
Chaque push et chaque pull request SHALL lancer en CI : Ruff, les tests Python avec couverture (Python 3.10 et 3.13, interface Tkinter sous écran virtuel), la vérification des fixtures, le lint et les tests du moteur TypeScript et des composants, et les tests de bout en bout. Un seul échec MUST faire échouer la CI.

#### Scenario: Test web en échec
- **WHEN** un test de bout en bout échoue sur une pull request
- **THEN** la CI est en échec et conserve la trace et les captures du test

### Requirement: Tests reproductibles
Les tests aléatoires SHALL être reproductibles : chaque échec de test de propriétés SHALL afficher l'exemple minimal et la graine permettant de le rejouer.

#### Scenario: Échec de propriété
- **WHEN** un test de propriétés trouve un contre-exemple
- **THEN** la sortie montre l'exemple réduit et comment le rejouer
