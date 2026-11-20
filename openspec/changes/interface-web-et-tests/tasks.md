# Tasks

## 1. Outillage de tests Python

- [ ] 1.1 Ajouter dans `pyproject.toml` l'extra `dev` (pytest, pytest-cov, hypothesis, ruff) et `[tool.pytest.ini_options]` (`testpaths = ["tests"]`) ; vérifier que `pip install -e ".[dev]"` réussit et que `pytest` collecte et réussit les 75 tests existants
- [ ] 1.2 Ajouter `tests/conftest.py` avec les profils Hypothesis `dev` et `ci` (sélection par `HYPOTHESIS_PROFILE`, `print_blob=True`) ; vérifier avec `HYPOTHESIS_PROFILE=ci pytest -q`
- [ ] 1.3 Mesurer la couverture (`pytest --cov=jeu_de_la_vie --cov-report=term-missing`), puis configurer les deux seuils (moteur et formats ≥ 90 %, `interface.py` ≥ 70 %) ; vérifier qu'un seuil volontairement trop haut fait échouer la commande
- [ ] 1.4 Regrouper les tests de motifs connus de `tests/test_moteur.py` en un test pytest paramétré (motif → période, déplacement) sans perdre de cas ; vérifier que le nombre de cas passe ≥ l'ancien
- [ ] 1.5 Mettre à jour la section « Tests » du README (installation de l'extra `dev`, `pytest`, couverture) ; vérifier que les commandes documentées fonctionnent telles quelles

## 2. Tests de propriétés Python

- [ ] 2.1 Écrire `tests/reference.py` (moteur naïf qui parcourt toutes les cellules, bords fermés et tore) et `tests/test_proprietes.py` comparant une génération du moteur au moteur naïf, pour des grilles, des règles sans B0 et des topologies générées par Hypothesis ; vérifier que `pytest tests/test_proprietes.py` passe
- [ ] 2.2 Ajouter les propriétés RLE (aller-retour recadré, avec nom et règle) et règles (`Regle.depuis_texte(str(r)) == r`) ; vérifier en introduisant temporairement un bogue dans `ecrire_rle` que le test échoue avec un exemple réduit
- [ ] 2.3 Ajouter les invariants d'historique (N étapes puis N annulations → état initial) et de cycles (avancer de la période redonne l'état décalé du déplacement) ; vérifier que `pytest` passe sous le profil `ci`

## 3. Données partagées et fixtures de conformité

- [ ] 3.1 Écrire `scripts/generer_donnees_web.py` (bibliothèque standard) qui produit `web/src/donnees/motifs.json`, `web/src/donnees/regles.json` et `fixtures/conformite.json` de façon déterministe ; vérifier que deux exécutions successives donnent des fichiers identiques octet pour octet
- [ ] 3.2 Couvrir dans les fixtures chaque motif intégré, chaque règle connue, les deux topologies, un état aléatoire de graine fixe, les cas limites (cellules au bord d'un tore, S0), les RLE écrits par Python et les entrées invalides avec l'erreur attendue ; vérifier en comptant les cas par catégorie
- [ ] 3.3 Ajouter l'option `--verifier` (échec avec la commande de régénération si un fichier diffère) et `tests/test_conformite_fixtures.py` (le moteur Python rejoue ses fixtures) ; vérifier en modifiant à la main une fixture que les deux échouent
- [ ] 3.4 Documenter dans le README le rôle des fixtures et la commande de régénération ; vérifier que la commande documentée régénère les fichiers

## 4. Squelette de l'application web

- [ ] 4.1 Créer `web/` (Vite + React 18 + TypeScript strict, ESLint, Vitest, Testing Library, fast-check, vitest-canvas-mock, Playwright), avec des versions figées dans `package-lock.json` ; vérifier que `npm ci && npm run build && npm run lint && npx tsc --noEmit` réussissent
- [ ] 4.2 Configurer la couverture v8 de Vitest avec un seuil de 90 % sur `src/moteur/` et `base: "/jeu-de-la-vie/"` pour la construction ; vérifier que `npm test -- --coverage` s'exécute
- [ ] 4.3 Ignorer `web/node_modules/`, `web/dist/` et les rapports de test dans `.gitignore` ; vérifier avec `git status` après une construction

## 5. Moteur TypeScript : règles, grille, historique

- [ ] 5.1 Implémenter `web/src/moteur/regles.ts` (lecture B/S, S/B et ancienne notation, refus de B0 et des valeurs hors 0–8, règles connues chargées depuis `regles.json`, libellé) avec ses tests unitaires et de propriétés ; vérifier que `npm test regles` passe
- [ ] 5.2 Implémenter `web/src/moteur/grille.ts` (cellules en entiers, `allumer` / `eteindre` / `basculer` / `vider` / `placer` centré, `voisins`, `etape` renvoyant les changements, S0, tore) avec un moteur naïf TS et des tests fast-check de comparaison ; vérifier que `npm test grille` passe
- [ ] 5.3 Ajouter l'historique (`memoriser` / `annuler`, 1000 états au plus) avec ses tests d'invariant ; vérifier que `npm test grille` passe

## 6. Moteur TypeScript : cycles et conformité

- [ ] 6.1 Implémenter la détection des cycles (empreinte FNV-1a, vérification de l'état complet en cas de collision, empreinte de forme pour les vaisseaux, réinitialisation après modification, changement de règle ou de topologie) et `String(cycle)` identique au Python ; vérifier les tests unitaires (bloc, pulsar, pentadécathlon, planeur)
- [ ] 6.2 Écrire `web/src/moteur/conformite.test.ts`, qui rejoue chaque cas de `fixtures/conformite.json` (cellules, populations, cycle) ; vérifier que tous les cas passent et qu'une fixture altérée fait échouer le test en la nommant

## 7. Moteur TypeScript : formats

- [ ] 7.1 Implémenter `web/src/moteur/rle.ts` (lecture : en-tête, règle, `#N`, `#C`, répétitions, erreurs ; écriture recadrée avec longueur de ligne bornée) ; vérifier les tests unitaires, la propriété d'aller-retour et le rejeu des RLE et entrées invalides des fixtures
- [ ] 7.2 Implémenter `web/src/moteur/png.ts` (signature, IHDR, IDAT compressé via `CompressionStream` avec repli, IEND, CRC32, quadrillage) ; vérifier par un test qui décode l'image produite (CRC et couleur des pixels)
- [ ] 7.3 Vérifier que la couverture de `src/moteur/` dépasse 90 % avec `npm test -- --coverage`

## 8. Interface web : grille et simulation

- [ ] 8.1 Implémenter le hook `useSimulation` (possède la `Grille`, boucle `requestAnimationFrame`, vitesse de 1 à 60/s, arrêt automatique sur cycle ou extinction, suivant / précédent) avec ses tests ; vérifier que `npm test useSimulation` passe
- [ ] 8.2 Implémenter le composant `Grille` sur canevas (redessin incrémental, couleur des naissances, zoom molette / pincement / boutons, déplacement, recadrage) et les informations de survol ; vérifier par des tests de composant que le zoom ne change pas l'état de la grille
- [ ] 8.3 Implémenter le dessin au pointeur (le premier contact choisit de dessiner ou gommer, un `memoriser()` par trait) ; vérifier par un test qu'un trait s'annule en une fois
- [ ] 8.4 Implémenter `BarreCommandes` (lecture/pause, suivant, précédent, vitesse) avec noms accessibles ; vérifier par des tests Testing Library qui passent par les rôles

## 9. Interface web : motifs, règles, univers, analyse

- [ ] 9.1 Implémenter `PanneauMotifs` (catégories depuis `motifs.json`, règle imposée par le motif, agrandissement de la grille jusqu'à 300×300) ; vérifier par un test que le réplicateur bascule sur HighLife
- [ ] 9.2 Implémenter `PanneauUnivers` (règle connue ou saisie avec message d'erreur, taille de 30 à 300 avec motif recentré, tore, remplissage aléatoire de densité réglable) ; vérifier par un test que `B0/S23` affiche une erreur et conserve la règle
- [ ] 9.3 Implémenter `Analyse` (génération, population, courbe SVG, libellé du cycle) et `BarreEtat` ; vérifier par un test que le planeur affiche « Vaisseau de période 4, se déplace de (+1, +1) »

## 10. Interface web : fichiers, partage, clavier, thème

- [ ] 10.1 Implémenter l'ouverture d'un fichier `.rle`, le coller, l'enregistrement, la copie en RLE et le téléchargement PNG, avec message d'erreur pour un RLE invalide ; vérifier par des tests de composant que la grille reste inchangée sur erreur
- [ ] 10.2 Implémenter le lien de partage (`#rle=…&tore=1`) : création et restauration au chargement ; vérifier par un test d'aller-retour sur le canon de Gosper torique
- [ ] 10.3 Implémenter les raccourcis clavier (`⌘` sur macOS, inactifs pendant la saisie) ; vérifier par un test que `R` tapé dans le champ de règle ne remplit pas la grille
- [ ] 10.4 Implémenter les thèmes clair et sombre (système par défaut, choix mémorisé avec repli si `localStorage` est indisponible) et la mise en page à 360 px ; vérifier par un test du thème par défaut
- [ ] 10.5 Ajouter au README une section « Interface web » (lancement `npm run dev`, construction, fonctionnalités, raccourcis) ; vérifier que les commandes documentées fonctionnent telles quelles

## 11. Tests de bout en bout, CI et publication

- [ ] 11.1 Écrire les tests Playwright sur `vite preview` (planeur → génération 4, population 5, vaisseau détecté ; lecture et arrêt automatique ; dessin puis annulation ; import et export RLE ; lien de partage ; hors ligne après chargement), plus un projet mobile 360 px sans défilement horizontal ; vérifier que `npx playwright test` passe en local
- [ ] 11.2 Ajouter le test de fluidité (canon de Gosper 300×300, ≥ 30 générations/s, indicatif en CI) ; vérifier qu'il affiche le rythme mesuré
- [ ] 11.3 Étendre `.github/workflows/tests.yml` : couverture Python avec les seuils et `HYPOTHESIS_PROFILE=ci`, job `conformite` (`--verifier`), job `web` (lint, `tsc`, Vitest et couverture, construction), job `e2e` (traces et captures en artefacts en cas d'échec) ; vérifier sur une pull request que tous les jobs passent et qu'un test cassé exprès fait échouer la CI
- [ ] 11.4 Ajouter `.github/workflows/pages.yml` (construction puis publication sur GitHub Pages depuis `main`) et le lien et badge dans le README ; vérifier après fusion que le site publié s'ouvre et lance un planeur

## 12. Vérification finale

- [ ] 12.1 Vérifier que l'interface Tkinter et `jeu-de-la-vie simuler planeur -n 8 --afficher` se comportent comme avant (tests unittest existants verts, sortie de la commande identique)
- [ ] 12.2 Lancer `ruff check .`, `pytest` avec les seuils de couverture, `python scripts/generer_donnees_web.py --verifier`, puis dans `web/` `npm run lint`, `npx tsc --noEmit`, `npm test -- --coverage` et `npx playwright test` ; tout doit passer avant de cocher cette tâche

## Workflow follow-up

- Archiver le change (`/opsx:archive`) une fois la pull request relue et fusionnée.
- Vérifier après l'archivage que `openspec/specs/` contient `interface-web`, `conformite-moteurs` et `suite-de-tests`.
