from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi

from F_1___Common_Structure import COMMONCLASS


class Fenetregraphique(COMMONCLASS):
    def __init__(self, comon_var):
        super().__init__()

        loadUi(r"F_Ui\F_graph_window.ui", self)

        self.comon_var = comon_var

        self.F_quit_button.clicked.connect(
            lambda: self.go_to("general")
        )

        self.F_refresh_button.clicked.connect(
            self.afficher_images
        )

        self.F_export_button.clicked.connect(
            self.test_exporter
        )

        self.F_info_text.setPlainText("Fenêtre graphique ouverte.")

    def showEvent(self, event):
        """
        Détecte l'affichage de la fenêtre graphique.
        """
        super().showEvent(event)
        print("La fenêtre GRAPHIQUE vient d'être affichée")

        self.afficher_images()

    def afficher_images(self):
        """
        Affiche les images du signal temporel et de la FFT
        à partir des chemins stockés dans comon_var.
        """

        chemin_signal = self.comon_var.time_series_plot_path
        chemin_fft = self.comon_var.fft_plot_path

        if chemin_signal == "" or chemin_fft == "":
            self.F_info_text.appendPlainText(
                "Erreur : les chemins des images ne sont pas définis."
            )
            return

        image_signal = QPixmap(chemin_signal)
        image_fft = QPixmap(chemin_fft)

        if image_signal.isNull():
            self.F_info_text.appendPlainText(
                f"Erreur : impossible de charger le signal : {chemin_signal}"
            )
        else:
            self.F_time_signal_label.setPixmap(image_signal)
            self.F_time_signal_label.resize(image_signal.size())

        if image_fft.isNull():
            self.F_info_text.appendPlainText(
                f"Erreur : impossible de charger la FFT : {chemin_fft}"
            )
        else:
            self.F_fft_signal_label.setPixmap(image_fft)
            self.F_fft_signal_label.resize(image_fft.size())

        self.F_info_text.appendPlainText(
            "Images chargées depuis les variables communes."
        )

    def test_exporter(self):
        """
        Test du bouton Exporter.
        """

        print("Bouton Exporter cliqué")

        self.F_info_text.appendPlainText(
            "Test : le bouton Exporter fonctionne."
        )