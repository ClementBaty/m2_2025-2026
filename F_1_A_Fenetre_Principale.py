from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
import sys
from PyQt5.uic import loadUi

from F_FenetreGraphique import Fenetregraphique
from pathlib import Path
class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"F_Ui\F_Interface_1.ui", self)
        # self.F_quit_button.clicked.connect(self.close)
        self.fenetreGraphique = Fenetregraphique()

        self.chemin = "analysis.json"
        self.verif_url()

        self.url_input.setText(self.chemin)
        self.url_bouton.clicked.connect(self.choose_files_csv_json_pyqt5)
        self.affichage_graph.clicked.connect(self.graph)


        self.url_input.editingFinished.connect(self.verif_url)


    def action_bouton(self):
        print("Bouton cliqué")

    def choose_files_csv_json_pyqt5(self):
        """
        Ouvre une fenêtre de sélection.
        Le fichier sélectionné doit être un fichier CSV ou JSON.

        Retourne :
            str : chemin du fichier sélectionné
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner un fichier",
            "",
            "Fichiers JSON ou CSV (*.json *.csv)"
        )

        self.chemin = file_path
        self.url_input.setText(self.chemin)
        self.verif_url()

    def graph(self):

        self.fenetreGraphique.show()

    def verif_url(self):
        self.fichier = Path(self.url_input.text())
        if self.fichier.exists():
            self.voy_url.setStyleSheet("background-color: rgb(0, 255, 0);")
        else:
            self.voy_url.setStyleSheet("background-color: rgb(255, 0, 0);")