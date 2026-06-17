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
        Affiche les images du signal temporel et de la FFT.
        Les labels prennent la taille des images.
        """

        chemin_signal = self.comon_var.time_series_plot_path
        chemin_fft = self.comon_var.fft_plot_path

        # Test temporaire si les chemins communs sont vides
        if chemin_signal == "":
            chemin_signal = "test_signal.png"

        if chemin_fft == "":
            chemin_fft = "test_fft.png"

        print("Chemin signal :", chemin_signal)
        print("Chemin FFT :", chemin_fft)

        image_signal = QPixmap(chemin_signal)
        image_fft = QPixmap(chemin_fft)

        if image_signal.isNull():
            self.F_info_text.appendPlainText(
                f"Erreur : impossible de charger le signal : {chemin_signal}"
            )
        else:
            self.F_time_signal_label.setPixmap(image_signal)
            self.F_time_signal_label.setFixedSize(image_signal.size())

        if image_fft.isNull():
            self.F_info_text.appendPlainText(
                f"Erreur : impossible de charger la FFT : {chemin_fft}"
            )
        else:
            self.F_fft_signal_label.setPixmap(image_fft)
            self.F_fft_signal_label.setFixedSize(image_fft.size())

        self.F_info_text.appendPlainText(
            "Images chargées."
        )

        #self.adjustSize()

    def test_exporter(self):
        """
        Test du bouton Exporter.
        """

        print("Bouton Exporter cliqué")

        self.F_info_text.appendPlainText(
            "Test : le bouton Exporter fonctionne."
        )