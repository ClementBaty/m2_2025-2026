"""Fenêtre graphique du groupe F.

Ce module contient la classe Fenetregraphique, utilisée pour afficher
les images du signal temporel et de la transformée de Fourier (FFT).
Les chemins des images sont récupérés depuis l'objet comon_var partagé
avec les autres fenêtres de l'application.
"""

from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi

from F_1___Common_Structure import COMMONCLASS
from F_1_B_1_Image_Zoom import ImageZoom

class Fenetregraphique(COMMONCLASS):
    """Fenêtre dédiée à l'affichage des graphiques d'analyse."""

    def __init__(self, comon_var):
        """Initialise la fenêtre graphique.

        Args:
            comon_var: Objet partagé contenant les chemins des images
                à afficher et les informations extraites du fichier
                d'analyse.
        """
        super().__init__()
        loadUi(r"F_Ui\F_graph_window.ui", self)
        self.comon_var = comon_var
        self.labels()
        self.F_quit_button.clicked.connect(lambda: self.go_to("general"))
        self.F_refresh_button.clicked.connect(self.afficher_images)

    def labels(self):
        for attr in ["F_time_signal_label", "F_fft_signal_label"]:
            old_label = getattr(self, attr)
            new_widget = ImageZoom(self)
            new_widget.setGeometry(old_label.geometry())
            old_label.hide()
            new_widget.show()
            setattr(self, attr, new_widget)


    def showEvent(self, event):
        """Actualise les images à chaque affichage de la fenêtre.

        Args:
            event: Événement Qt déclenché lors de l'affichage.
        """
        super().showEvent(event)
        self.afficher_images()

    def afficher_images(self):
        """Affiche les images du signal temporel et de la FFT.

        Les chemins sont récupérés depuis self.comon_var.
        Si les chemins sont vides, des images de test sont utilisées
        afin de permettre un fonctionnement minimal de l'interface.
        """
        chemin_signal = self.comon_var.time_series_plot_path
        chemin_fft = self.comon_var.fft_plot_path

        if chemin_signal == "":
            chemin_signal = "test_signal.png"

        if chemin_fft == "":
            chemin_fft = "test_fft.png"

        image_signal = QPixmap(chemin_signal)
        image_fft = QPixmap(chemin_fft)

        if not image_signal.isNull():
            self.F_time_signal_label.setPixmap(image_signal)
            self.F_time_signal_label.resize(image_signal.size())

        if not image_fft.isNull():
            self.F_fft_signal_label.setPixmap(image_fft)
            self.F_fft_signal_label.resize(image_fft.size())