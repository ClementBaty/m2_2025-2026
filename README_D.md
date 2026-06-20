# Groupe D — Classificateur de type de fichier

**Auteurs :** Szymon SIDORKIEWICZ, Mame DIONG, Sokhna THIAM, Ouail Kassa BAGHDOUCHE
**Module :** M2 T3I ALTERNANCE 2026
**Roles :** Szymon - Recherche des methodes de classification des fichiers par Machine Learning. Integration des methodes de classification a l'interface.
Mame: Recherche des methodes de classification par methode algorithmique (Seuils)
Sokhna: Creation de la premiere version de l'interface moderne
Ouail:

## Table des matières

- [Fonctionnement](#fonctionnement)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement](#lancement)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)

## Fonctionnement

Ce module fournit une interface graphique (PyQt5) permettant de déterminer la
nature d'un signal (`AUDIO`, `IMAGE`, `NOISE`, `TEXT` et d'autres) à partir des
caractéristiques avancées fournies par le **Groupe C** (spectre de fréquence,
statistiques, motifs/pics détectés) sous forme de fichiers `features.csv`.

Deux méthodes de classification sont disponibles, au choix de l'utilisateur :

1. **Comparaison à la base de données (KNN)** : les indicateurs les plus
   discriminants sont sélectionnés automatiquement (Fisher Score + Sequential
   Backward Selection), puis un algorithme des k plus proches voisins compare
   l'échantillon aux fichiers de référence enregistrés dans `DATABASE/`.
2. **Algorithmique (par seuils)** : un système de règles attribue un score à
   chacun des quatre types à partir de plages de valeurs observées
   (centroïde spectral, écart-type, kurtosis, asymétrie, énergie RMS, etc.),
   sans nécessiter de base de données.

Le résultat (type détecté, confiance, score par classe) s'affiche dans
l'onglet **Test** et peut être exporté vers `processed_data.csv`, le fichier
livrable attendu par le **Groupe E**. L'onglet **Base de données** permet de
créer des catégories et d'y importer des fichiers de référence. 

L'onglet **Journal** affiche en temps réel les messages de traitement (indicateurs
retenus, imports, erreurs…).

La logique métier (`classification_backend.py`) est indépendante de
l'interface (`gui.py`) et peut être testée seule, sans lancer l'application
graphique.

## Prérequis

- **Python 3.11 ou supérieur** (développé et testé avec Python 3.13)
- `pip` à jour
- Teste et valide seulement sur Windows 11

## Installation

1. Récupérer le dépôt et se placer sur la branche du groupe :

   ```bash
   git clone https://github.com/ClementBaty/m2_2025-2026.git
   cd m2_2025-2026
   git checkout branche_D
   ```

2. (Recommandé) Créer un environnement virtuel dédié :

   ```bash
   python -m venv venv
   ```

   Activation :

   ```bash
   # Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```

3. Installer les **dépendances** :

    PyQt5>=5.15 --> Interface
    pandas>=2.0 --> Gestion des ficheirs .csv
    numpy>=1.24 --> Calculatoire
    scikit-learn>=1.3   --> Creation du modele ML KNN
    mlxtend>=0.22   --> Machine learning extensions; SFS, SBS, Fisher Score


   Le projet repose sur les bibliothèques suivantes :

   | Bibliothèque   | Rôle                                                    |
   |----------------|----------------------------------------------------------|
   | `PyQt5`        | Interface graphique (fenêtre, onglets, widgets)          |
   | `pandas`       | Lecture/écriture des fichiers `features.csv` et `.csv`   |
   | `numpy`        | Calculs numériques (Fisher Score, statistiques)          |
   | `scikit-learn` | Classification KNN, normalisation (`StandardScaler`)     |
   | `mlxtend`      | Sélection séquentielle d'indicateurs (SBS)               |

## Lancement

Une fois les dépendances installées, démarrer l'application avec :

```bash
python traitements.py
```

Au premier lancement, les dossiers `SAMPLE/` et `DATABASE/` sont créés
automatiquement s'ils n'existent pas, et la base de référence
(`DATABASE/reference.csv`) est (re)générée à partir des catégories déjà
présentes.

## Utilisation

1. **Onglet Test** : choisir un fichier `features.csv` (un exemple est fourni
   dans `SAMPLE/`), puis cliquer sur **« Comparer à la base de données »** ou
   **« Algorithmique »** pour lancer la classification. Le résultat s'affiche
   avec le type détecté, le pourcentage de confiance et le détail par classe.
   Le bouton « Exporter processed_data.csv » enregistre le résultat pour le
   Groupe E.
2. **Onglet Base de données** : créer une catégorie (10 caractères max, 7
   catégories max - hardcode, sujet a changer eventuellement) puis importer des fichiers `features.csv` de référence
   pour chacune. Au moins 3 catégories et 5 échantillons par catégorie sont
   recommandés pour que la méthode KNN soit fiable.
3. **Onglet Journal** : suit en direct les opérations effectuées (sélection
   des indicateurs, imports, erreurs éventuelles).

## Structure du projet

```
traitements.py              # Point d'entrée (python traitements.py)
gui.py                       # Interface graphique PyQt5 (3 onglets)
classification_backend.py    # Logique métier : base de données, KNN, règles, export
SAMPLE/                       # Fichiers features.csv d'exemple à tester
DATABASE/                     # Catégories de référence + reference.csv généré
processed_data.csv           # Résultat exporté pour le Groupe E
```
