from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi

from F_1___Common_Structure import COMMONCLASS


class Fenetregraphique(COMMONCLASS):
    def __init__(self,comon_var):
        super().__init__()

        loadUi(r"F_Ui\F_graph_window.ui", self)

        self.comon_var = comon_var

        self.F_quit_button.clicked.connect(lambda: self.go_to("general"))

        self.F_refresh_button.clicked.connect(self.test_images)
        self.F_export_button.clicked.connect(self.test_exporter)

        self.F_info_text.setPlainText("Fenêtre graphique ouverte.")

    def showEvent(self, event):
        """
        détécte l'affichage de l'écran puis executes les fonction voulues a l'affichage ex : reffrech,...
        """
        super().showEvent(event)
        print("La fenêtre GRAPHIQUE vient d'être affichée")

    def test_images(self):
        """
        Affiche des images de test dans les deux zones prévues.
        """

        self.F_time_signal_label.setPixmap(
            QPixmap("test_signal.png")
        )

        self.F_fft_signal_label.setPixmap(
            QPixmap("test_fft.png")
        )

        self.F_info_text.appendPlainText(
            "Images de test chargées."
        )

    def test_exporter(self):
        """
        Test du bouton Exporter.
        """

        print("Bouton Exporter cliqué")

        self.F_info_text.appendPlainText(
            "Test : le bouton Exporter fonctionne."
        )