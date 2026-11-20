# Design

## Context

Voir `proposal.md` pour la motivation. État actuel utile :

- Le paquet `jeu_de_la_vie/` est en Python pur, sans dépendance. `moteur.py` est déjà indépendant de l'interface : grille creuse (`set` de `(ligne, colonne)`), voisines comptées avec un `Counter`, historique `deque(maxlen=1000)`, cycles détectés par empreintes exactes et par empreintes de forme recadrée.
- `motifs.py` décrit les 17 motifs en texte (`O` / `.`), avec une catégorie, une description et parfois une règle. `regles.py` contient les 8 règles connues.
- Les tests sont en unittest (`tests/test_*.py`). La CI fait Ruff + tests sous Xvfb (Python 3.10 et 3.13) + installation du paquet.
- La règle du projet « bibliothèque standard uniquement » vise l'exécution du paquet. Ce changement l'assouplit seulement pour les outils de développement et pour `web/`.

## Goals / Non-Goals

**Goals:**
- Une application web statique, avec un moteur TypeScript strictement conforme au moteur Python.
- Une seule source pour les motifs et les règles : Python.
- Une suite de tests qui attrape les régressions du moteur par génération aléatoire, et pas seulement sur des exemples.

**Non-Goals:**
- Pas de serveur, de compte utilisateur ni de stockage distant.
- Pas de support de B0, de règles non totalistes ou multi-états (comme côté Python).
- Pas de refonte ni de suppression de l'interface Tkinter. Pas de réécriture complète des tests unittest existants.
- Pas de grille infinie : la grille reste finie (au plus 300×300 côté web).

## Decisions

### D1. Monorepo : `web/` à côté du paquet Python
`web/` contient l'application (Vite + React 18 + TypeScript strict), avec son propre `package.json`. Le paquet Python et `pyproject.toml` n'en dépendent pas : `pip install .` n'embarque rien du web.
*Alternative écartée* : un dépôt séparé. Les fixtures et les données partagées devraient alors être synchronisées entre deux dépôts, ce qui casse la garantie de conformité.

### D2. Moteur TypeScript sans React : `web/src/moteur/`
Le moteur est un module TypeScript pur (aucun import React ni DOM, sauf l'encodeur PNG, qui produit des `Uint8Array`). Il calque l'API Python : `Grille`, `Regle`, `Cycle`, `lireRle`, `ecrireRle`, `png`. Les messages et libellés (`String(cycle)`) sont identiques au caractère près, ce qui permet de les comparer aux fixtures.
- Cellule codée en entier `i * colonnes + j` dans un `Set<number>` (plus rapide qu'une chaîne `"i,j"`). Le comptage des voisines utilise un `Map<number, number>`, ou un `Uint8Array` de la taille de la grille quand la population est forte.
- Empreintes de cycles : le `hash(frozenset)` Python n'est pas reproductible côté JS. Le moteur TS calcule sa propre empreinte (FNV-1a sur la liste triée des cellules), puis compare l'état complet en cas de collision. Seuls la période, le début et le déplacement doivent correspondre à Python, pas les empreintes elles-mêmes.
*Alternative écartée* : Pyodide (choix de l'utilisateur : port en TypeScript), pour le temps de chargement et la fluidité.

### D3. Génération des données et des fixtures depuis Python
Le script `scripts/generer_donnees_web.py` (bibliothèque standard uniquement) écrit :
- `web/src/donnees/motifs.json` et `regles.json`, générés à partir de `MOTIFS`, `CATEGORIES` et `REGLES_CONNUES` ;
- `fixtures/conformite.json` : pour chaque cas, motif, règle, taille, topologie, N, cellules finales triées, population à chaque génération et cycle `{debut, periode, deplacement}` ou `null`. Il contient aussi les RLE écrits par Python pour les allers-retours croisés, et une liste d'entrées invalides (RLE et règles) avec le type d'erreur attendu.
Les fichiers générés sont versionnés. `--verifier` régénère en mémoire et échoue si le contenu diffère (utilisé en CI). La sortie est déterministe : clés triées, cellules triées, graines fixes.
*Alternative écartée* : générer les fichiers à la construction du site. La construction web dépendrait alors de Python, et les fixtures ne seraient plus relues en revue de code.

### D4. Rendu sur `<canvas>` et boucle d'animation
Le rendu se fait sur un seul canevas 2D. Il ne redessine que les cellules qui ont changé (le moteur renvoie les changements, comme en Python), avec un redessin complet au zoom ou au déplacement. La boucle `requestAnimationFrame` accumule le temps et appelle `etape()` selon la vitesse choisie. L'état React ne contient que les métadonnées (génération, population, cycle, réglages), jamais l'ensemble des cellules, pour éviter des rendus React à chaque génération.
*Alternative écartée* : un élément DOM ou SVG par cellule (90 000 nœuds en 300×300). Le moteur dans un Web Worker est reporté : à n'ajouter que si l'exigence de fluidité n'est pas tenue.

### D5. Structure de l'application
- `src/moteur/` : moteur pur. `src/donnees/` : JSON générés.
- `src/etat/` : un hook `useSimulation` qui possède l'instance `Grille`, la boucle d'animation et l'historique des traits (un `memoriser()` au début de chaque trait).
- `src/composants/` : `Grille` (canevas, pointeur, zoom), `BarreCommandes`, `PanneauMotifs`, `PanneauUnivers`, `Analyse` (courbe en SVG simple, sans bibliothèque de graphiques), `BarreEtat`.
- Thème : variables CSS, `prefers-color-scheme` par défaut, choix mémorisé dans `localStorage`. CSS simple (modules CSS), sans framework d'interface, pour garder le paquet léger.
- Lien de partage : `#rle=<RLE encodé en base64url>&tore=1`. Le RLE porte déjà la règle. Les lecteurs existants servent à l'analyse, sans nouveau format.

### D6. Tests Python : pytest au-dessus de l'existant
- `pyproject.toml` : `[project.optional-dependencies] dev = ["pytest", "pytest-cov", "hypothesis", "ruff"]` et `[tool.pytest.ini_options]` (`testpaths = ["tests"]`). Le seuil de couverture est appliqué par `--cov-fail-under` en CI, avec deux mesures : le moteur et les formats hors interface (90 %), et `interface.py` (70 %).
- Les fichiers unittest restent tels quels (pytest les exécute). Les nouveaux tests sont écrits en style pytest : `tests/test_proprietes.py` (Hypothesis), `tests/test_conformite_fixtures.py` (le moteur Python relit ses propres fixtures), `tests/reference.py` (moteur naïf qui parcourt toutes les cellules).
- Les tests de motifs connus de `test_moteur.py` sont regroupés dans un test paramétré (motif → période, déplacement), sans perdre de cas.
- Hypothesis : profil `ci` (plus d'exemples, `derandomize=False`, `print_blob=True`) et profil `dev` (rapide), sélectionnés par la variable `HYPOTHESIS_PROFILE`.

### D7. Tests web
- **Vitest** pour le moteur (unitaires + propriétés avec **fast-check**, comparaison à un moteur naïf TS) et pour le rejeu de `fixtures/conformite.json`. Couverture v8 avec un seuil de 90 % sur `src/moteur/`.
- **Testing Library** (jsdom) pour les composants. Le canevas est simulé (`vitest-canvas-mock`). Les interactions passent par `@testing-library/user-event`, avec des requêtes par rôle et nom accessible.
- **Playwright** (Chromium en CI) pour les tests de bout en bout sur `vite preview`, plus un projet « mobile 360 px ». Les traces et captures sont gardées en artefacts quand un test échoue. Le test de fluidité mesure le rythme réel ; il est marqué comme indicatif en CI (machines partagées) et strict en local.
- Lint : ESLint (configuration TypeScript recommandée) et `tsc --noEmit`.

### D8. CI et déploiement
`tests.yml` garde ses jobs et gagne :
- `conformite` : `python scripts/generer_donnees_web.py --verifier` ;
- `web` : `npm ci`, lint, `tsc`, Vitest avec couverture, construction ;
- `e2e` : Playwright sur le site construit ;
- `pages.yml`, sur `main` uniquement : construction puis publication sur GitHub Pages (`base` Vite = `/jeu-de-la-vie/`).

## Risks / Trade-offs

- [Deux moteurs à maintenir] → Fixtures générées, vérification en CI et règle « le Python fait foi » (spec `conformite-moteurs`). Toute évolution du moteur passe d'abord par Python.
- [Écarts subtils : ordre d'itération, modulo négatif en JS, S0] → Cas dédiés dans les fixtures (tore avec cellules au bord, règle `B3/S012345678`), et tests de propriétés contre le moteur naïf des deux côtés.
- [Empreintes de cycle différentes entre les deux langages] → On compare uniquement (début, période, déplacement). L'état complet est vérifié en cas de collision côté TS, donc il n'y a pas de faux cycle.
- [Poids de l'outillage npm pour un projet « sans dépendance »] → Isolé dans `web/`. Le paquet Python et son installation restent inchangés, et le README sépare les deux usages.
- [Tests de bout en bout fragiles en CI] → Attentes sur l'état visible (texte de génération) plutôt que des délais fixes, nouvelles tentatives limitées à 1, et traces gardées.
- [Seuil de couverture Tkinter difficile à tenir] → Seuil séparé et plus bas (70 %), à réévaluer après mesure.

## Migration Plan

1. Ajouter les outils pytest sans toucher aux tests ; vérifier que les 75 tests passent avec `pytest`.
2. Ajouter le script de génération et les fixtures, puis le job `conformite`.
3. Construire le moteur TS jusqu'à ce que les fixtures passent, puis l'interface.
4. Activer la publication Pages en dernier. Retour arrière : désactiver `pages.yml`. Rien ne change pour les utilisateurs de `pip install .` ni de Tkinter.

## Open Questions

- Le seuil de 70 % pour `interface.py` sera ajusté (à la hausse si possible) après la première mesure de couverture. Cela ne change ni les specs ni les tâches.
