# Signal Analysis Dashboard

## Description du Branche_E

Ce projet est une application Python avec interface graphique PyQt5 permettant d'analyser des données de signaux déjà extraites dans un fichier CSV ou JSON.

L'objectif principal est de visualiser les échantillons, détecter les anomalies à partir de seuils réglables, afficher les spectres FFT, et représenter la séparation des classes dans un espace 3D.

Au départ, le projet était séparé en deux parties :

- `analyzer_beta.py` : partie backend, contenant les fonctions d'analyse et de traitement.
- `main_beta.py` : partie frontend, contenant l'interface graphique PyQt5.

Après évolution du projet, les deux parties ont été fusionnées dans un seul fichier principal :

```text
analyzer.py
