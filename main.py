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

Technologies obligatoires :
- Python v3 uniquement
- PyQt5 Designer / pyuic5
- SciPy
- Pandas
- CSV

Bonnes pratiques imposées :
- Comprendre le code généré
- Tester systématiquement le code
- Documenter les fonctions/classes
- Éviter le Vibe Coding
"""

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import csv
from pathlib import Path

from PyQt5 import QtWidgets

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from Dialog import Ui_Dialog

import datetime # Import nécessaire pour le timestamp

# ============================================================================
# CONSTANTES
# ============================================================================


# ============================================================================
# CLASSES
# ============================================================================

class MainWindow(Ui_Dialog):
    """
    Fenêtre principale de l'application.
    """
    def __init__(self, dialog):
        Ui_Dialog.__init__(self)
        self.setupUi(dialog)
        self.connexions()

    def connexions(self):
        # Connect the .clicked() signal with the .calculate() slot
        self.Generer.clicked.connect(self.calculate)

    def calculate(self):
        # Nom et localisation du fichier à lire
        nom_fichier = "C:\Temp\M2_Progr\m2_2025-2026\Fichier_entree.csv"
        #nom_fichier = self.AffichageURL.text()

        # On crée un objet "mon_signal" à partir de la classe Mon_Signal_GrpA
        mon_signal = Mon_Signal_GrpA()

        # On appelle la méthode d'acquisition (Etape 1)
        mon_signal.Acquisition_signal(nom_fichier)

        # On appelle la méthode de traitement (Etape 2)
        mon_signal.Traitement_signal()
        
        # A remplir par Manal
        mon_signal.type = self.comboBox_Type.currentText()
        mon_signal.source = self.comboBox_Source.currentText()
        
        # AFFICHAGE POUR VERIFIER QUE TOUT FONCTIONNE
        print(" PROPRIÉTÉS DU SIGNAL :")
        print(f"Type : {mon_signal.type}")
        print(f"Source : {mon_signal.source}")
        print(f"Taux d'échantillonnage (sample_rate) : {mon_signal.sample_rate} Hz")
        print(f"Durée du signal (duration) : {mon_signal.duration} s")
        print(f"Timestamp : {mon_signal.timestamp}")
        print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
        print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")



class Mon_Signal_GrpA:
    
    # Le constructeur : il initialise les variables quand on crée le signal
    def __init__(self):
        self.type = ""
        self.source = ""
        self.sample_rate = 0
        self.duration = 0.0
        self.timestamp = ""
        self.samples = []
        
        # Variable interne du vecteur temps du signal 
        self.t = [] 

    # ETAPE 1 : EXTRACTION DES DONNEES
    def Acquisition_signal(self, filename):
        """
        La fonction Acquisition_signal lit le fichier CSV contenant le signal.

        Paramètres d'entrée :
        -------
        filename : str (chemin du fichier + nom du fichier)

        Effets
        -------
        On remplit les attributs suivants :
        - self.t : liste des temps
        - self.samples : liste des échantillons du signal
        """
        # On vide les listes au cas où on réutiliserait la fonction
        self.t = []
        self.samples = []
        
        with open(filename, "r") as f:
            next(f)  # saute la première ligne (les en-têtes)
            for ligne in f:
                ligne = ligne.strip()  # enlever les espaces et retours à la ligne
                if not ligne: # Sécurité : ignorer les lignes vides
                    continue
                valeurs = ligne.split(",")  # Le séparateur est une virgule
                
                # On stocke les données dans les attributs de la classe (self)
                self.t.append(float(valeurs[0]))
                self.samples.append(float(valeurs[1]))

    # ETAPE 2 : TRAITEMENT DES DONNEES POUR CALCULER LES INFORMATIONS DU SIGNAL
    def Traitement_signal(self):
        """
        La fonction Traitement_signal traite le signal.

        Paramètres d'entrée :
        -------
        Aucun

        Effets
        -------
        On remplit les attributs suivants :
        - self.sample_rate : Fréquence du signal
        - self.duration : Durée du signal
        - self.timestamp : Date de traitement du signal
        """
        # On s'assure qu'il y a au moins 2 points de mesures pour pouvoir faire des calculs
        if len(self.t) >= 2:
            # Taux d'échantillonnage (en Hz)
            dt = self.t[1] - self.t[0] # Période d'échantillonnage
            self.sample_rate = round(1.0 / dt) # 1 / dt donne la fréquence. "round()" arrondit à l'entier
            
            # Durée du signal (en secondes)
            self.duration = self.t[-1] - self.t[0] # t[-1] permet de récupérer le dernier élément
        else:
            self.sample_rate = 0
            self.duration = 0

        # Timestamp (Horodatage de l'extraction)
        # datetime.now() récupère la date/heure du PC
        # .replace(microsecond=0) pour ne pas afficher les microsecondes
        # .isoformat() formate les données au format iso (ex: 2026-05-13T15:55:00)
        self.timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        
        
# ============================================================================
# FONCTIONS
# ============================================================================


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = MainWindow(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
