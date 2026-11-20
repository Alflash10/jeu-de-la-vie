# Proposal

## Why

L'interface Tkinter fonctionne mais reste datée, limitée au bureau (pas de zoom, pas de tactile, pas de thème sombre) et impossible à partager par un simple lien. Le projet gagnerait à une interface web moderne, utilisable dans n'importe quel navigateur et publiable en ligne. En parallèle, la suite de tests (75 tests unittest) ne mesure pas sa couverture et ne vérifie que des exemples choisis à la main. Une deuxième implémentation du moteur rend indispensable une garantie automatique que les deux moteurs restent identiques.

## What Changes

- Nouvelle **application web React + TypeScript**, entièrement exécutée dans le navigateur (site statique, sans serveur), dans un dossier `web/` séparé du paquet Python.
- **Portage du moteur en TypeScript** : grille creuse, règles B/S, bords fermés ou toriques, historique, détection des cycles, lecture/écriture RLE, export PNG. Le moteur Python reste la référence.
- **Données partagées** : les motifs intégrés et les règles connues sont exportés depuis Python en JSON et consommés par l'application web, pour ne pas les dupliquer à la main.
- **Fixtures de conformité** générées par le moteur Python (motif, règle, taille, topologie, N générations → cellules attendues, cycle attendu) et rejouées par le moteur TypeScript.
- Parité fonctionnelle avec Tkinter (simulation, dessin, motifs, règles, univers, analyse, RLE, PNG, raccourcis), plus des **améliorations** : rendu sur canevas avec zoom et déplacement, tactile, thème clair/sombre, lien de partage contenant le motif.
- **Tkinter est conservé**, sans changement de comportement. Il reste l'interface par défaut de `jeu-de-la-vie`.
- **Suite de tests Python** : passage à pytest (les tests unittest existants continuent de tourner), paramétrage, tests de propriétés avec Hypothesis (allers-retours RLE, invariants des règles, comparaison avec un moteur naïf de référence), et **seuil de couverture** imposé en CI.
- **Suite de tests web** : tests unitaires et de propriétés du moteur TypeScript, tests de son API publique, tests des composants React, tests de bout en bout dans un vrai navigateur.
- **CI** étendue : tests web, conformité Python ↔ TypeScript, publication du site statique (GitHub Pages) depuis `main`.
- Hypothèse retenue : comme il n'y a pas de serveur HTTP, les « tests d'API » demandés portent sur l'API publique du moteur TypeScript et sur le contrat de conformité entre les deux moteurs.

## Capabilities

### New Capabilities
- `interface-web` : application web exécutée dans le navigateur. Simulation, dessin, motifs, règles, univers, analyse, fichiers, partage, zoom, tactile et thème.
- `conformite-moteurs` : garantie que le moteur TypeScript et les données de l'application web donnent exactement les mêmes résultats que le moteur Python de référence.
- `suite-de-tests` : exigences sur la suite de tests du projet (exécution, couverture minimale, tests de propriétés, tests web et de bout en bout, CI).

### Modified Capabilities
<!-- Aucune : le moteur Python, les règles, les formats, la ligne de commande et l'interface Tkinter gardent leur comportement. -->

## Impact

- **Nouveau code** : `web/` (React, TypeScript, Vite) et un script de génération des données et des fixtures (`scripts/`).
- **Dépendances** : le paquet Python reste sans dépendance à l'exécution. Des dépendances de développement s'ajoutent : pytest, pytest-cov et Hypothesis côté Python, et la chaîne npm côté web (React, Vite, Vitest, Testing Library, Playwright, fast-check). Cela assouplit la règle « bibliothèque standard uniquement » pour les outils de développement et pour `web/`.
- **Tests** : `tests/` passe à pytest. Une configuration pytest est ajoutée dans `pyproject.toml`.
- **CI** : `.github/workflows/` gagne des jobs web, conformité et déploiement Pages.
- **Documentation** : README (section interface web, commandes de tests, lien vers le site).
