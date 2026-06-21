# Signal Analysis Dashboard — Branche_E

## Description du projet

Ce projet correspond au travail réalisé dans la branche `branche_E` du dépôt `m2_2025-2026`.

Il s'agit d'une application Python avec interface graphique développée avec **PyQt5**.
L'objectif est d'analyser des données de signaux déjà extraites dans un fichier CSV ou JSON, puis de visualiser ces données à travers plusieurs graphes et indicateurs.

L'application permet notamment de :

* charger un fichier de données ;
* afficher des indicateurs sur les signaux ;
* détecter automatiquement des anomalies ;
* afficher le signal temporel reconstruit ;
* afficher le spectre FFT ;
* visualiser la séparation des classes avec un graphe 3D ;
* exporter les résultats de l'analyse.

Le but principal est de fournir une interface claire pour analyser rapidement des échantillons de signaux audio ou bruités, tout en gardant une logique de traitement simple et compréhensible.

---

## Évolution du projet

Au début du développement, le projet était séparé en deux parties :

* `analyzer_beta.py` : partie backend, contenant les fonctions d'analyse, de traitement et de calcul.
* `main_beta.py` : partie frontend, contenant l'interface graphique PyQt5.

Cette séparation permettait de distinguer clairement :

* la logique de traitement des données ;
* l'affichage graphique ;
* la gestion des boutons, tableaux et onglets.

Après plusieurs tests, nous avons décidé de fusionner les deux parties dans un seul fichier principal :

```text
analyzer.py
```

Ce choix permet d'avoir une version plus simple à exécuter et plus facile à présenter.
Le fichier `analyzer.py` contient maintenant à la fois :

* le backend ;
* le frontend ;
* la logique de détection d'anomalies ;
* les fonctions de visualisation ;
* la génération des graphes FFT ;
* l'algorithme SBS pour choisir les meilleurs axes du graphe 3D.

Cette version finale est donc plus compacte et plus directe :

```text
un seul fichier principal
une seule interface
une seule logique complète
```

---

## Objectif de l'application

L'objectif de l'application est de faciliter l'analyse de signaux à partir d'un fichier contenant des features déjà calculées.

L'application ne traite pas directement un signal brut au départ.
Elle utilise des colonnes déjà présentes dans le fichier d'entrée, comme :

* RMS ;
* énergie ;
* moyenne ;
* kurtosis ;
* skewness ;
* fréquence dominante ;
* confiance ;
* label.

À partir de ces informations, l'application permet d'identifier les échantillons suspects et de mieux comprendre la séparation entre les classes.

---

## Technologies utilisées

Le projet utilise les bibliothèques suivantes :

```text
Python
PyQt5
NumPy
Pandas
Matplotlib
SciPy
```

Rôle de chaque bibliothèque :

* **Python** : langage principal du projet.
* **PyQt5** : création de l'interface graphique.
* **Pandas** : lecture et manipulation des fichiers CSV/JSON.
* **NumPy** : calculs numériques.
* **Matplotlib** : génération des graphes.
* **SciPy** : calcul de la FFT.

---

## Structure actuelle du projet

La structure actuelle du projet est la suivante :

```text
M2_2025-2026/
│
├── analyzer.py              # Code principal : backend + interface graphique
├── analyzer_beta.py         # Ancienne version backend / version de test
├── analyzer_functions.py    # Ancienne séparation des fonctions backend
├── main_beta.py             # Ancienne interface séparée
├── main.py                  # Ancienne version ou fichier temporaire
│
├── processed_data.csv       # Exemple de fichier d'entrée
├── analysis_results.csv     # Fichier de résultats exporté
│
├── plots/
│   ├── fft_0.png
│   ├── fft_1.png
│   ├── fft_2.png
│   └── fft_3.png
│
├── Ui/
│   ├── Ui_1.png
│   ├── Ui_2.png
│   └── UI_3.png
│
├── README.md
└── README_E.md
```

Le fichier important pour exécuter l'application finale est :

```text
analyzer.py
```

---

## Fichier d'entrée attendu

L'application accepte un fichier au format :

```text
.csv
.json
```

Le fichier doit contenir les colonnes suivantes :

```text
sample_id
label
confidence
mean
std_dev
kurtosis
skewness
rms
dominant_frequency_hz
energy
```

Description des colonnes :

| Colonne                 | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `sample_id`             | Identifiant de l'échantillon                    |
| `label`                 | Classe de l'échantillon                         |
| `confidence`            | Niveau de confiance associé à la classification |
| `mean`                  | Moyenne du signal                               |
| `std_dev`               | Écart-type du signal                            |
| `kurtosis`              | Indicateur statistique lié aux pics du signal   |
| `skewness`              | Indicateur d'asymétrie du signal                |
| `rms`                   | Valeur RMS du signal                            |
| `dominant_frequency_hz` | Fréquence dominante du signal                   |
| `energy`                | Énergie du signal                               |

---

## Fonctionnement général

Le fonctionnement global de l'application est le suivant :

```text
Chargement du fichier CSV/JSON
        ↓
Vérification des colonnes
        ↓
Application des seuils d'anomalie
        ↓
Mise à jour des métriques globales
        ↓
Affichage des graphes
        ↓
Affichage du tableau des échantillons
        ↓
Sélection d'un échantillon
        ↓
Affichage du signal temporel et de la FFT
```

---

## Interface graphique

L'interface est organisée en trois onglets principaux.

### 1. Data / Settings

Cet onglet permet de :

* charger un fichier CSV ou JSON ;
* charger des données de démonstration ;
* exporter les résultats ;
* modifier les seuils de détection d'anomalies ;
* afficher des métriques globales.

Les seuils réglables sont :

* seuil minimum de confiance ;
* fréquence maximale ;
* RMS maximal ;
* kurtosis maximale.

---

### 2. Dashboard Charts

Cet onglet contient les visualisations globales :

* confiance par échantillon ;
* fréquence dominante ;
* séparation 3D avec SBS ;
* répartition des labels.

Le graphe 3D permet de visualiser les échantillons dans un espace composé des trois meilleures features sélectionnées automatiquement.

---

### 3. Samples / Details

Cet onglet contient :

* un tableau des échantillons ;
* un filtre par label ;
* un filtre par état : anomalie ou normal ;
* les détails d'un échantillon sélectionné ;
* le signal temporel reconstruit ;
* le spectre FFT de l'échantillon.

---

## Détection d'anomalies

La détection d'anomalies est basée sur des règles simples.

Un échantillon peut être considéré comme anomalie si :

* la confiance est faible et la fréquence dominante est élevée ;
* la valeur RMS est trop grande ;
* la kurtosis est trop élevée ;
* l'énergie est anormalement faible.

Exemples de raisons d'anomalie :

```text
Low confidence and high frequency noise
RMS amplitude too high
Abnormal kurtosis
Suspiciously low energy
```

Ces règles sont simples, mais elles permettent d'avoir une première classification rapide des échantillons suspects.

---

## Signal temporel reconstruit

L'application reconstruit un signal temporel simple à partir de :

* la moyenne ;
* la valeur RMS ;
* la fréquence dominante.

Le signal reconstruit est utilisé pour afficher une représentation temporelle de l'échantillon sélectionné.

Ce signal n'est pas forcément le signal original exact.
Il sert surtout à visualiser le comportement général de l'échantillon à partir des features disponibles.

---

## FFT

Pour chaque échantillon, l'application calcule et affiche un spectre FFT à partir du signal temporel reconstruit.

La FFT permet de visualiser les composantes fréquentielles du signal.

L'application sauvegarde aussi des images FFT dans le dossier :

```text
plots/
```

Exemple :

```text
plots/fft_0.png
plots/fft_1.png
plots/fft_2.png
plots/fft_3.png
```

---

## Séparation 3D avec SBS

Une amélioration importante ajoutée dans cette version est le graphe 3D avec sélection automatique des axes.

Au lieu de choisir manuellement deux axes comme :

```text
RMS vs Energy
```

l'application utilise maintenant l'algorithme **SBS** pour choisir automatiquement les trois meilleures features.

SBS signifie :

```text
Sequential Backward Selection
```

Le principe est le suivant :

1. on commence avec toutes les features disponibles ;
2. on teste la séparation entre les classes ;
3. on retire progressivement la feature la moins utile ;
4. on continue jusqu'à garder seulement trois features ;
5. ces trois features sont utilisées comme axes du graphe 3D.

---

## Features utilisées par SBS

L'algorithme SBS utilise uniquement les colonnes déjà présentes dans le fichier chargé :

```text
mean
std_dev
kurtosis
skewness
rms
dominant_frequency_hz
energy
```

Aucune nouvelle feature n'est recalculée pour le graphe 3D.

Avant l'application du SBS, les features sont normalisées afin d'éviter qu'une variable avec de grandes valeurs numériques, comme l'énergie ou la fréquence, domine les autres features.

---

## Score de séparation

Le score utilisé dans le SBS compare :

* la distance entre les centres des classes ;
* la dispersion des points à l'intérieur de chaque classe.

Un bon choix de features doit donc donner :

```text
classes éloignées entre elles
points proches à l'intérieur de chaque classe
```

L'objectif est d'obtenir une meilleure séparation visuelle dans l'espace 3D.

---

## Export des résultats

L'application permet d'exporter un fichier :

```text
analysis_results.csv
```

Ce fichier contient :

| Colonne                 | Description                               |
| ----------------------- | ----------------------------------------- |
| `sample_id`             | Identifiant de l'échantillon              |
| `label`                 | Classe de l'échantillon                   |
| `confidence`            | Confiance associée                        |
| `fft_plot_path`         | Chemin vers l'image FFT                   |
| `time_series_plot_path` | Chemin vers le signal temporel            |
| `is_anomaly`            | Indique si l'échantillon est une anomalie |
| `anomaly_reason`        | Raison de l'anomalie                      |

---

## Installation

Installer les dépendances nécessaires avec :

```bash
pip install numpy pandas matplotlib scipy PyQt5
```
---
## Version finale

La version finale utilisée pour la présentation est :

```text
analyzer.py
```

Ce fichier regroupe :

* l'interface ;
* les traitements ;
* les graphes ;
* la FFT ;
* la détection d'anomalies ;
* le SBS ;
* le graphe 3D.

---

## Conclusion

Cette branche présente une application complète d'analyse de signaux avec interface graphique.

Le projet montre l'évolution d'une architecture séparée backend/frontend vers une version unifiée plus simple à exécuter et à présenter.

L'ajout du graphe 3D avec SBS permet d'améliorer la visualisation de la séparation entre les classes, en choisissant automatiquement les axes les plus pertinents.
