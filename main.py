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
import datetime
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from Dialog import Ui_Dialog

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
        """
        La fonction connexions Permet de connecter les signalaux et Slots

        Paramètres d'entrée :
        -------
        Aucun
        
        Returns
        -------
        None
        
        Effets
        -------
        Lors d'ppuis dans l'interface on appel des fonctions (slot)
        """
        # Connect the .clicked() signal with the .calculate() slot
        self.Generer.clicked.connect(self.calculate)
        # Connexion bouton
        self.Boutonparcourir.clicked.connect(self.ouvrir_fichier)
        

    def calculate(self):
        """
        La fonction calculate Permet de réaliser le coeur du projet.
        Lors de l'appuis sur le bouton générer cet fonction est appeler

        Paramètres d'entrée :
        -------
        Aucun
        
        Returns
        -------
        None
        
        Effets
        -------
        
        Extrais les donner 
        Appel la fonction de géneration du fichier 
        Réaliser le coeur du projet        
        """
        # Nom et localisation du fichier à lire
        #nom_fichier = "C:\Temp\M2_Progr\m2_2025-2026\Fichier_entree.csv"
        nom_fichier = self.AffichageURL.text()

        # On crée un objet "mon_signal" à partir de la classe Mon_Signal_GrpA
        mon_signal = MonSignalGrpA()

        # On appelle la méthode d'acquisition (Etape 1)
        try:
            mon_signal.acquisition_signal(nom_fichier)
        except Exception as e:
            print(f"Erreur : {e}")

        # On appelle la méthode de traitement (Etape 2)
        mon_signal.traitement_signal()
        
        # A remplir par Manal
        mon_signal.type = self.comboBox_Type.currentText()
        mon_signal.source = self.comboBox_Source.currentText()
        
        # AFFICHAGE POUR VERIFIER QUE TOUT FONCTIONNE
        print(" PROPRIÉTÉS DU SIGNAL :")
        print(f"Type : {mon_signal.type}")
        print(f"Source : {mon_signal.source}")
        
        print(f"Taux d'échantillonnage (sample_rate) : {mon_signal.sample_rate} Hz")
        self.Affichage_echantillon.setText(f"{mon_signal.sample_rate} Hz")
        
        print(f"Durée du signal (duration) : {mon_signal.duration} s")
        self.Affichage_duree_siganl.setText(f"{mon_signal.duration} s")
        
        print(f"Timestamp : {mon_signal.timestamp}")
        self.Affichage_uptdate.setText(f"{mon_signal.timestamp}")
        
        print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
        self.Affichage_nb_echantillon.setText(f"{len(mon_signal.samples)}")
        
        print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")


    def ouvrir_fichier(self):
        """
        La fonction ouvrir_fichier Permet d'ouvrir l'exporateur de fichier, pour sélection le fichier d'entrée
        Un filtre est appliquer pour ouvrire uniquement un fichier .csv

        Paramètres d'entrée :
        -------
        Aucun
        
        Returns
        -------
        None
            
        Effets
        -------
        Charge le fichier d'entrée
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
    def acquisition_signal(self, filename):
        """
        La fonction Acquisition_signal lit le fichier CSV contenant le signal.

        Paramètres d'entrée :
        -------
        filename : str (chemin du fichier + nom du fichier)
        
        Returns
        -------
        None

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
                ligne = ligne.strip() #enlever les espaces et retours à la ligne
                if not ligne: # Sécurité : ignorer les lignes vides
                    continue
                valeurs = ligne.split(",")  # Le séparateur est une virgule
                
                # On stocke les données dans les attributs de la classe (self)
                self.t.append(float(valeurs[0]))
                self.samples.append(float(valeurs[1]))

    # ETAPE 2 : TRAITEMENT DES DONNEES POUR CALCULER LES INFORMATIONS DU SIGNAL
    def traitement_signal(self):
        """
        La fonction Traitement_signal traite le signal.

        Paramètres d'entrée :
        -------
        Aucun
        
        Returns
        -------
        None

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
