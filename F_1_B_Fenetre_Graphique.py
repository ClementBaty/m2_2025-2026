from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi


<<<<<<< HEAD
class Fenetregraphique(QMainWindow):
    def __init__(self):
=======

class Fenetregraphique(COMMONCLASS):
    def __init__(self,comon_var):
>>>>>>> 9a5eefb3c41af701cb4fd6f10a7c156658ed2c5e
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