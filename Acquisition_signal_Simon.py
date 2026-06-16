# -*- coding: utf-8 -*-
"""
Intégration finale du code pour le Groupe A
"""

import pandas as pd
from datetime import datetime

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
        """Lit le fichier CSV contenant le signal et remplit self.t et self.samples"""
        self.t = []
        self.samples = []
        
        with open(filename, "r") as f:
            next(f)  # saute la première ligne (les en-têtes)
            for ligne in f:
                ligne = ligne.strip()
                if not ligne: 
                    continue
                valeurs = ligne.split(",")
                
                self.t.append(float(valeurs[0]))
                self.samples.append(float(valeurs[1]))

    # ETAPE 2 : TRAITEMENT DES DONNEES
    def Traitement_signal(self):
        """Calcule la fréquence, la durée et le timestamp à partir des données"""
        if len(self.t) >= 2:
            dt = self.t[1] - self.t[0] 
            self.sample_rate = round(1.0 / dt) 
            self.duration = self.t[-1] - self.t[0]
        else:
            self.sample_rate = 0
            self.duration = 0

        # Comme on a importé "datetime" directement, on écrit juste datetime.now()
        self.timestamp = datetime.now().replace(microsecond=0).isoformat()
        
    def ask_user_inputs(self):
        """Demande UNIQUEMENT les informations manquantes à l'utilisateur."""
        self.type = input("Enter signal type (ex: Audio): ")
        self.source = input("Enter signal source (ex: Micro): ")

    def export_to_csv(self, filename="Output_GroupeA.csv"):
        """Sauvegarde toutes les données réelles dans un nouveau fichier CSV avec pandas."""
        data = []

        for index, value in enumerate(self.samples):
            data.append(
                {
                    "timestamp": self.timestamp,
                    "type": self.type,
                    "source": self.source,
                    "sample_rate": self.sample_rate,
                    "duration": self.duration,
                    "sample_index": index,
                    "time": self.t[index],  # Ajout du vecteur temps de ton code !
                    "samples": value        # Correction du bug de ton collègue
                }
            )

        dataframe = pd.DataFrame(data)
        dataframe.to_csv(filename, index=False)
        print(f"\nFichier sauvegardé avec succès : {filename}")

    def run(self, filename):
        """Lance toutes les étapes du programme de manière logique."""
        print("=== ACQUISITION ET TRAITEMENT DU SIGNAL ===\n")

        # 1. On lit le fichier CSV de base (ton code)
        self.Acquisition_signal(filename)
        
        # 2. On calcule les infos (ton code)
        self.Traitement_signal()
        
        # 3. On demande le type et la source (code du collègue modifié)
        self.ask_user_inputs()
        
        # 4. On exporte le résultat complet (code du collègue corrigé)
        self.export_to_csv()


# ==========================================
# Tests
# ==========================================

# Nom et localisation du fichier à lire
nom_fichier = "U:\\Projet_prog\\Test\\m2_2025-2026\\Fichier_entree.csv"

# On crée un objet "mon_signal" à partir de la classe
mon_signal = Mon_Signal_GrpA()

# On lance le "chef d'orchestre" qui va tout faire dans l'ordre
mon_signal.run(nom_fichier)

# AFFICHAGE POUR VERIFIER QUE TOUT FONCTIONNE
print("\n--- PROPRIÉTÉS DU SIGNAL ---")
print(f"Type : {mon_signal.type}")
print(f"Source : {mon_signal.source}")
print(f"Taux d'échantillonnage (sample_rate) : {mon_signal.sample_rate} Hz")
print(f"Durée du signal (duration) : {mon_signal.duration} s")
print(f"Timestamp : {mon_signal.timestamp}")
print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")