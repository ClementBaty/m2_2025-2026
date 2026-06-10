from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
from pathlib import Path

from F_1___Common_Structure import COMMONCLASS

class FenetrePrincipale(COMMONCLASS):
    def __init__(self,comon_var):
        super().__init__()
        loadUi(r"F_Ui\F_Interface_1.ui", self)
        self.comon_var = comon_var
        print(self.comon_var)
        self.affichage_graph.clicked.connect(lambda: self.go_to("graphique"))


        self.url_input.setText(self.comon_var.chemin)
        self.url_bouton.clicked.connect(self.choose_files_csv_json_pyqt5)



        self.url_input.editingFinished.connect(self.verif_chemin)

        self.init_voyant(self.voy_url)

    def showEvent(self, event):
        """
        détécte l'affichage de l'écran puis executes les fonction voulues a l'affichage ex : reffrech,...
        """
        super().showEvent(event)
        print("La fenêtre PRINCIPAL vient d'être affichée")

    def action_bouton(self):
        print("Bouton cliqué")

    def choose_files_csv_json_pyqt5(self):
        """
        Ouvre une fenêtre de sélection.
        Le fichier sélectionné doit être un fichier CSV ou JSON.

        Retourne :
            str : chemin du fichier sélectionné
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner un fichier",
            "",
            "Fichiers JSON ou CSV (*.json *.csv)"
        )

        self.chemin = file_path
        self.url_input.setText(self.chemin)
        self.verif_chemin()

    def verif_chemin(self):
        self.fichier = Path(self.url_input.text())
        if self.fichier.exists():
            self.set_voyant_color(self.voy_url, "green")
            self.extraction_data(self.fichier)
        else:
            self.set_voyant_color(self.voy_url, "red")
    def extraction_data(self,fichier):
        pass