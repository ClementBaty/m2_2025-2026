from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
import sys
from PyQt5.uic import loadUi


class Fenetregraphique(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"F_Ui\F_graph_window.ui", self)

        self.F_quit_button.clicked.connect(self.close)

        # Boutons de test
        self.F_refresh_button.clicked.connect(self.test_actualiser)
        self.F_export_button.clicked.connect(self.test_exporter)

        # Texte affiché au démarrage de la fenêtre graphique
        self.F_info_text.setPlainText("Fenêtre graphique ouverte.")

    def test_actualiser(self):
        """
        Test du bouton Actualiser.
        """

        print("Bouton Actualiser cliqué")

        self.F_info_text.appendPlainText(
            "Test : le bouton Actualiser fonctionne."
        )

    def test_exporter(self):
        """
        Test du bouton Exporter.
        """

        print("Bouton Exporter cliqué")

        self.F_info_text.appendPlainText(
            "Test : le bouton Exporter fonctionne."
        )

