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

    def showEvent(self, event):
        super().showEvent(event)
        self.afficher_images()

    def afficher_images(self):
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