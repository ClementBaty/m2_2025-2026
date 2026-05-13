from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
import sys

from F_extracteur_de_Donnee import Donnee
from F_FenetreGraphique import Fenetregraphique

class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"F_Ui\F_Interface_1.ui", self)

        self.fenetreGraphique = Fenetregraphique()

        self.chemin = "test"
        self.fichier = None

        self.url_input.setText(self.chemin)

        self.url_bouton.clicked.connect(self.choose_files_csv_json_pyqt5)
        self.affichage_graph.clicked.connect(self.graph)
        #self.F_quit_button.clicked.connect(self.close)

        """
        if self.chemin is not None:
            self.fichier = F_extracteur_de_Donnee.Donnee(self.chemin)
            pass
        if self.fichier.existe:
            print("Fichier valide")
        else:
            print("Fichier non valide")
        """
    def action_bouton(self):
        print("Bouton cliqué")

    def choose_files_csv_json_pyqt5(self):
        """
        Ouvre une fenêtre de sélection.
        Le fichier sélectionné doit être un fichier CSV ou JSON.

        Retourne :
            str : chemin du fichier sélectionné
        """

        # Création de l'application si elle n'existe pas
        app = QApplication.instance()

        if app is None:
            app = QApplication(sys.argv)

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner un fichier",
            "",
            "Fichiers JSON ou CSV (*.json *.csv)"
        )

        self.chemin = file_path
        self.url_input.setText(self.chemin)
    def graph(self):

        self.fenetreGraphique.show()


app = QApplication(sys.argv)
fenetre = FenetrePrincipale()
fenetre.show()
sys.exit(app.exec_())
