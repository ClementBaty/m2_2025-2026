"""Fenêtre graphique du groupe F.

Ce module contient la classe Fenetregraphique, utilisée pour afficher
les images du signal temporel et de la transformée de Fourier (FFT).
Les chemins des images sont récupérés depuis l'objet comon_var partagé
avec les autres fenêtres de l'application.
"""
from pathlib import Path

from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QScrollArea, QSizePolicy

from F_0_B_Common_Structure import COMMONCLASS
from F_2_B_Image_Zoom import ImageZoom


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
        loadUi(r"F_Ui\F_Interface_2_Affichage.ui", self)

        self.comon_var = comon_var

        self.labels()

        self.F_quit_button.clicked.connect(lambda: self.go_to("general"))
        self.F_refresh_button.clicked.connect(self.refresh)

    def showEvent(self, event):
        """Actualise les images à chaque affichage de la fenêtre.
        Args:
            event: Événement Qt déclenché lors de l'affichage.
        """
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        """fonction permetant de chager et de lancer les affichages des image, text."""
        self.afficher_images()
        text = ""
        if self.comon_var.label != "":
            text += f"label : {self.comon_var.label}\n"
        if self.comon_var.label != 0:
            text += f"confidence : {self.comon_var.confidence}\n"
        if self.comon_var.anomaly_reason != "":
            text += f"anomaly reason : {self.comon_var.anomaly_reason}\n"
        self.text_box_specification.setText(text)

    def labels(self):
        for attr in ["F_time_signal_label", "F_fft_signal_label"]:
            old_label = getattr(self, attr)
            parent = old_label.parent()
            layout = parent.layout()

            new_widget = ImageZoom()

            scroll = QScrollArea()
            scroll.setWidget(new_widget)
            scroll.setWidgetResizable(False)

            scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            scroll.setFixedSize(old_label.size())

            index = layout.indexOf(old_label)

            if index != -1:
                layout.replaceWidget(old_label, scroll)

            old_label.hide()
            old_label.deleteLater()

            setattr(self, attr, new_widget)

    def afficher_images(self):
        """
        Affiche les images du signal temporel et de la FFT.

        Les chemins sont récupérés depuis self.comon_var.
        Si les chemins sont vides ou inexistant, une image 'image not found' apparait
        afin de permettre un fonctionnement minimal de l'interface.
        """
        chemin_signal = self.comon_var.time_series_plot_path
        chemin_fft = self.comon_var.fft_plot_path

        if chemin_signal == "" or not Path(chemin_signal).exists():
            chemin_signal = "F_ERREUR_IMAGE_NOT_FOUND.png"

        if chemin_fft == "" or not Path(chemin_fft).exists():
            chemin_fft = "F_ERREUR_IMAGE_NOT_FOUND.png"

        image_signal = QPixmap(chemin_signal)
        image_fft = QPixmap(chemin_fft)

        if not image_signal.isNull():
            self.F_time_signal_label.setPixmap(image_signal)

        if not image_fft.isNull():
            self.F_fft_signal_label.setPixmap(image_fft)
