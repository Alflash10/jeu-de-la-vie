# Jeu de la Vie 🧬

Implémentation du **Jeu de la Vie de Conway** avec interface graphique Tkinter, en Python.

## Règles du Jeu de la Vie

Une cellule vit ou meurt selon le nombre de voisins vivants :
- **< 2 voisins** → meurt (isolement)
- **2 ou 3 voisins** → survit
- **> 3 voisins** → meurt (surpopulation)
- **Exactement 3 voisins** → naît (reproduction)

## Fonctionnalités

- Grille 30×30 interactive
- Clic pour activer/désactiver des cellules
- Bouton **Start/Stop** pour lancer/arrêter la simulation
- Bouton **Reset** pour vider la grille

## Lancer le programme

```bash
python jeu_de_la_vie.py
```

Tkinter est inclus par défaut avec Python.

## Concepts illustrés

- Automate cellulaire
- Simulation discrète pas-à-pas
- Algorithme de comptage de voisins (8-connectivité)
- Interface graphique avec Canvas Tkinter

## Auteurs

- Alexandre BOURGINE  
- Leul (partenaire de projet)

Projet lycée — NSI (Numérique et Sciences Informatiques)
