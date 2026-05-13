# -*- coding: utf-8 -*-
"""
Projet M2 - Groupe A
Module : Acquisition des Signaux

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
- Manal BETTAOUI
- Alex GRAPIN
- Simon SILVESTRE
- Tom BOTTAZZINI


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
- CSV

Bonnes pratiques imposées :
- Comprendre le code généré
- Tester systématiquement le code
- Documenter les fonctions/classes
- Éviter le Vibe Coding
"""

# ============================================================================
# IMPORTS STANDARD
# ============================================================================

import sys
import csv
from pathlib import Path


# ============================================================================
# IMPORTS PYQT5
# ============================================================================
from PyQt5 import QtWidgets

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from Dialog import Ui_Dialog

# ============================================================================
# CONSTANTES
# ============================================================================


# ============================================================================
# CLASSES
# ============================================================================


class MainWindow(Ui_Dialog):
    """
    Fenêtre principale de l'application.
    """
    def __init__(self, dialog):
        Ui_Dialog.__init__(self)
        self.setupUi(dialog)
        self.connexions()
    
    def connexions(self):
        # Connect the .clicked() signal with the .calculate() slot
        self.pushButton.clicked.connect(self.calculate)


# ============================================================================
# FONCTIONS
# ============================================================================





# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
