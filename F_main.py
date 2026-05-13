from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

import F_extracteur_de_Donnee
from F_extracteur_de_Donnee import *

from PyQt5.QtWidgets import QApplication, QFileDialog
import sys


def choose_files_csv_json_pyqt5():
    """
    Ouvre une fenêtre de sélection.
    Le fichier sélectionné doit être un fichier CSV ou JSON.

    Retourne :
        str : chemin du fichier sélectionné
    """

    # Création de l'application si elle n'existe pas
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Sélectionner un fichier",
        "",
        "Fichiers JSON ou CSV (*.json *.csv)"
    )

    return file_path


chemin = None

#if buton_setting_path.push():
chemin = choose_files_csv_json_pyqt5()

if chemin is not None:
    F_extracteur_de_Donnee.Donnee(chemin)
    pass
