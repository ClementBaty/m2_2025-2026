# -*- coding: utf-8 -*-
"""
Created on Wed May 13 16:33:56 2026

@author: ss06384z
"""

import datetime # Import nécessaire pour le timestamp

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


# ==========================================
# Tests
# ==========================================

# Nom et localisation du fichier à lire
nom_fichier = "U:\\Projet_prog\\Test\\m2_2025-2026\\Fichier_entree.csv"

# On crée un objet "mon_signal" à partir de la classe Mon_Signal_GrpA
mon_signal = Mon_Signal_GrpA()

# On appelle la méthode d'acquisition (Etape 1)
mon_signal.Acquisition_signal(nom_fichier)

# On appelle la méthode de traitement (Etape 2)
mon_signal.Traitement_signal()

# A remplir par Manal
mon_signal.type = "audio"
mon_signal.source = "microphone"

# AFFICHAGE POUR VERIFIER QUE TOUT FONCTIONNE
print(" PROPRIÉTÉS DU SIGNAL :")
print(f"Type : {mon_signal.type}")
print(f"Source : {mon_signal.source}")
print(f"Taux d'échantillonnage (sample_rate) : {mon_signal.sample_rate} Hz")
print(f"Durée du signal (duration) : {mon_signal.duration} s")
print(f"Timestamp : {mon_signal.timestamp}")
print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")