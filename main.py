"""
FICHIER GROUPE D
Szymon, Mame, Sokhna M2 T3I ALTERNANCE 2026
Fichier initial du projet
Objectif: 
    *Classer les signaux (ex : audio vs bruit, vidéo vs image fixe)
    *Appliquer des algorithmes simples (ex : k-NN, seuil sur des caractéristiques)
    *Produire des données structurées pour l’analyse finale.

Entrées: features.json/csv:

Sorties: processed_data.csv contenant :
        *Label de classification (ex : "type": "audio").
        *Score de confiance (ex : "confidence": 0.95).

Livrables:
*Code Python traitements.py pour le traitement avancé
*Fichier processed_data.csv/json
*Fichier expliquant les outils et calculs utilisés
"""

import random
import os
