from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi


class Fenetregraphique(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi(r"F_Ui\F_graph_window.ui", self)

        self.F_quit_button.clicked.connect(self.close)
        self.F_refresh_button.clicked.connect(self.test_images)
        self.F_export_button.clicked.connect(self.test_exporter)

        self.F_info_text.setPlainText("Fenêtre graphique ouverte.")

    def test_images(self):
        """
        Affiche les images de test dans les deux labels.
        Les labels s'adaptent automatiquement à la taille des images.
        """
    
        image_signal = QPixmap("test_signal.png")
        image_fft = QPixmap("test_fft.png")
    
        self.F_time_signal_label.setPixmap(image_signal)
        self.F_time_signal_label.adjustSize()
    
        self.F_fft_signal_label.setPixmap(image_fft)
        self.F_fft_signal_label.adjustSize()
    
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