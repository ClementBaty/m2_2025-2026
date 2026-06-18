# -*- coding: utf-8 -*-
"""
Projet M2 - Groupe A
Module : Acquisition des Signaux

Description
-----------
Fichier de développement principal du module.
Architecture basée sur :
- Python 3
- PyQt5
- Pandas
- SciPy
- Structure modulaire orientée objet (POO)

Auteur(s)
----------
- Manal BETTAOUI
- Alex GRAPIN
- Simon SILVESTRE
- Tom BOTTAZZINI

Date
-----
2026

Consignes du projet
-------------------
Le projet doit respecter les contraintes suivantes :
- Application Python modulaire en POO
- Utilisation de PyQt5
- Code documenté
- Respect des conventions PEP8 et PEP257
- Utilisation de Git pour le versionnement
- Architecture propre et maintenable
- L’IA doit être utilisée comme assistant technique
  et non comme générateur complet du projet
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
from datetime import datetime

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from Dialog import Ui_Dialog

# ============================================================================
# CLASSES
# ============================================================================

class MainWindow(Ui_Dialog):
    """
    Fenêtre principale de l'application PyQt5.
    """
    def __init__(self, dialog):
        Ui_Dialog.__init__(self)
        self.setupUi(dialog)
        self.connexions()

    def connexions(self):
        """
        Connecte les signaux (clics) de l'interface aux fonctions (slots).

        Returns
        -------
        None
        """
        # Connect the .clicked() signal with the .calculate() slot
        self.Generer.clicked.connect(self.calculate)
        # Connexion bouton
        self.Boutonparcourir.clicked.connect(self.ouvrir_fichier)

    def calculate(self):
        """
        Réalise le cœur du traitement lors de l'appui sur le bouton "Générer".

        Extrait les données du CSV, effectue les calculs, met à jour 
        l'affichage de l'interface utilisateur et exporte le fichier résultat.

        Returns
        -------
        None
        """
        # Nom et localisation du fichier à lire depuis l'interface
        nom_fichier = self.AffichageURL.text()

        # Sécurité : vérifier qu'un fichier a bien été sélectionné
        if not nom_fichier:
            print("Veuillez sélectionner un fichier avant de générer.")
            return

        # On crée un objet "mon_signal" à partir de la classe MonSignalGrpA
        mon_signal = MonSignalGrpA()

        try:
            # 1. Acquisition et Traitement (Etape 1 et 2)
            mon_signal.acquisition_signal(nom_fichier)
            mon_signal.traitement_signal()
            
            # 2. Récupération des choix de l'utilisateur depuis l'interface (GUI)
            # Utilisation de signal_type et signal_source pour respecter ta classe
            mon_signal.signal_type = self.comboBox_Type.currentText()
            mon_signal.signal_source = self.comboBox_Source.currentText()
            
            # 3. AFFICHAGE POUR VERIFIER QUE TOUT FONCTIONNE (Console + GUI)
            print("--- PROPRIÉTÉS DU SIGNAL ---")
            print(f"Type : {mon_signal.signal_type}")
            print(f"Source : {mon_signal.signal_source}")
            
            print(f"Taux d'échantillonnage : {mon_signal.sample_rate} Hz")
            self.Affichage_echantillon.setText(f"{mon_signal.sample_rate} Hz")
            
            print(f"Durée du signal : {mon_signal.duration} s")
            self.Affichage_duree_siganl.setText(f"{mon_signal.duration} s")
            
            print(f"Timestamp : {mon_signal.timestamp}")
            self.Affichage_uptdate.setText(f"{mon_signal.timestamp}")
            
            print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
            self.Affichage_nb_echantillon.setText(f"{len(mon_signal.samples)}")
            
            print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")

            # 4. Exportation du fichier résultat avec toutes les données compilées
            mon_signal.export_to_csv("Output_GroupeA.csv")

        except Exception as e:
            print(f"Erreur lors du traitement : {e}")

    def ouvrir_fichier(self):
        """
        Ouvre l'explorateur de fichiers pour sélectionner le fichier d'entrée.
        Un filtre est appliqué pour n'ouvrir que les fichiers .csv.

        Returns
        -------
        None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Choisir un fichier",
            "",
            "Tous les fichiers (*csv*)"
        )
        
        if file_path:
            self.AffichageURL.setText(file_path)


class MonSignalGrpA:
    """
    Représente un signal numérique pour le projet du Groupe A.

    Gère l'extraction des données, le calcul des métriques temporelles,
    et l'exportation des résultats via Pandas.
    """

    def __init__(self):
        """Initialise les attributs du signal avec des valeurs par défaut."""
        self.signal_type = ""
        self.signal_source = ""
        self.sample_rate = 0
        self.duration = 0.0
        self.timestamp = ""
        self.samples = []
        self.t = []

    def acquisition_signal(self, filename):
        """
        Lit le fichier CSV spécifié et extrait les données du signal.

        Args:
            filename (str): Le chemin d'accès complet au fichier CSV.
        """
        self.t = []
        self.samples = []

        with open(filename, "r", encoding="utf-8") as f:
            next(f)  # Saute la ligne des en-têtes
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                valeurs = ligne.split(",")

                self.t.append(float(valeurs[0]))
                self.samples.append(float(valeurs[1]))

    def traitement_signal(self):
        """
        Calcule la fréquence, la durée et formate les données.

        Les valeurs temporelles et les échantillons sont arrondis à
        4 décimales pour un export propre. Génère également l'horodatage.
        """
        if len(self.t) >= 2:
            dt = self.t[1] - self.t[0]
            self.sample_rate = round(1.0 / dt)
            self.duration = round(self.t[-1] - self.t[0], 4)
        else:
            self.sample_rate = 0
            self.duration = 0

        # Arrondi à 4 décimales via liste en compréhension
        self.t = [round(temps, 4) for temps in self.t]
        self.samples = [round(valeur, 4) for valeur in self.samples]

        self.timestamp = datetime.now().replace(microsecond=0).isoformat()

    def export_to_csv(self, filename="Output_GroupeA.csv"):
        """
        Sauvegarde les données du signal dans un fichier CSV.

        Args:
            filename (str): Nom du fichier de sortie. Par défaut
                'Output_GroupeA.csv'.
        """
        data = []

        for index, value in enumerate(self.samples):
            data.append(
                {
                    "timestamp": self.timestamp,
                    "type": self.signal_type,
                    "source": self.signal_source,
                    "sample_rate": self.sample_rate,
                    "duration": self.duration,
                    "sample_index": index,
                    "time": self.t[index],
                    "samples": value
                }
            )

        dataframe = pd.DataFrame(data)
        dataframe.to_csv(filename, index=False)
        print(f"\nFichier de sortie généré avec succès : {filename}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = MainWindow(Dialog)
    Dialog.show()
    sys.exit(app.exec_())