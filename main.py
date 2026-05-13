# -*- coding: utf-8 -*-
"""
Projet M2 - Groupe A
Module : <nom_du_module>

Description
-----------
Fichier de développement principal du module.
Architecture basée sur :
- Python 3
- PyQt5
- Pandas
- SciPy
- Structure modulaire orientée objet (POO)

Auteur(s)
----------
- Tom Bottazzini
- <membres_du_groupe>

Date
-----
2026

Consignes du projet
-------------------
Le projet doit respecter les contraintes suivantes :

- Application Python modulaire en POO
- Utilisation de PyQt5
- Code documenté
- Respect des conventions PEP8 et PEP257
- Utilisation de Git pour le versionnement
- Architecture propre et maintenable
- L’IA doit être utilisée comme assistant technique
  et non comme générateur complet du projet

Technologies obligatoires :
- Python v3 uniquement
- PyQt5 Designer / pyuic5
- SciPy
- Pandas
- CSV / JSON

Bonnes pratiques imposées :
- Comprendre le code généré
- Tester systématiquement le code
- Documenter les fonctions/classes
- Éviter le Vibe Coding
"""

# ============================================================================
# IMPORTS STANDARD
# ============================================================================

import os
import sys
import json
import csv
from pathlib import Path

# ============================================================================
# IMPORTS SCIENTIFIQUES
# ============================================================================

import numpy as np
import pandas as pd
import scipy

# ============================================================================
# IMPORTS PYQT5
# ============================================================================

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QMessageBox
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# ============================================================================
# CONSTANTES
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent

# ============================================================================
# CLASSES
# ============================================================================


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application.
    """

    def __init__(self):
        """
        Initialisation de la fenêtre principale.
        """
        super().__init__()

        self.initialize_ui()

    def initialize_ui(self):
        """
        Configure l'interface utilisateur.
        """
        self.setWindowTitle("Projet M2 - Groupe A")
        self.resize(800, 600)


# ============================================================================
# FONCTIONS
# ============================================================================


def load_signals_matrix(file_path: str):
    """
    Charge une matrice numpy depuis un fichier .npy.

    Parameters
    ----------
    file_path : str
        Chemin du fichier.

    Returns
    -------
    numpy.ndarray
        Matrice chargée.
    """
    return np.load(file_path)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())