from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
from pathlib import Path

from F_1___Common_Structure import COMMONCLASS
from F_extracteur_de_Donnee import Donnee
from PyQt5.QtWidgets import QTableWidgetItem


class FenetrePrincipale(COMMONCLASS):
    def __init__(self,comon_var):
        super().__init__()
        loadUi(r"F_Ui\F_Interface_1.ui", self)
        self.comon_var = comon_var
        self.affichage_graph.clicked.connect(lambda: self.go_to("graphique"))

        self.url_input.setText(self.comon_var.chemin)
        self.url_bouton.clicked.connect(self.choose_files_csv_json_pyqt5)

        self.url_input.editingFinished.connect(self.verif_chemin)

        self.init_voyant(self.voy_url)
        self.init_voyant(self.LED_1)

        self.comboBox.currentIndexChanged.connect(self.maj_led)
        self.tableWidget.setStyleSheet("QTableWidget::item:selected { background-color: #1a73e8; color: white; }")
        
    def showEvent(self, event):
        """
        détécte l'affichage de l'écran puis executes les fonction voulues a l'affichage ex : reffrech,...
        """
        super().showEvent(event)
        print("La fenêtre PRINCIPAL vient d'être affichée")
        self.verif_chemin()

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
            self.comon_var.analysis_init()
            
    def extraction_data(self,fichier):
        d = Donnee(str(fichier))
        if d.FichierValide:
            self.comon_var.donnees = d.donnees
            ancien_index = self.comboBox.currentIndex()
            """J'ai rajouté ancien_index pour garder l'index sélectionné 
            après le changement de fenêtre."""
            self.comboBox.clear()
            for point in d.donnees:
                self.comboBox.addItem(str(point['sample_id']))
            if ancien_index < len(d.donnees):
                self.comboBox.setCurrentIndex(ancien_index)
                
            colonnes = ['sample_id', 'label', 'confidence', 'fft_plot_path', 'time_series_plot_path', 'is_anomaly', 'anomaly_reason']
            self.tableWidget.setColumnCount(len(colonnes))
            self.tableWidget.setRowCount(len(d.donnees))
            self.tableWidget.setHorizontalHeaderLabels(colonnes)

            for i in range(len(d.donnees)):
                for j in range(len(colonnes)):
                    valeur = d.donnees[i][colonnes[j]]
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(valeur)))
                    self.tableWidget.resizeColumnsToContents()
                
    def maj_led(self, index):
        point = self.comon_var.donnees[index]
        if point['is_anomaly'] == 'True':
            self.set_voyant_color(self.LED_1, "red")
        else:
            self.set_voyant_color(self.LED_1, "green")
        self.tableWidget.selectRow(index)