# -*- coding: utf-8 -*-
"""
Intégration finale du code pour le Groupe A.

Ce script permet l'acquisition de signaux depuis un fichier CSV,
le calcul de leurs propriétés, la saisie d'informations utilisateur
et l'exportation vers un nouveau fichier CSV.
"""

from datetime import datetime

import pandas as pd


class MonSignalGrpA:
    """
    Représente un signal numérique pour le projet du Groupe A.

    Gère l'extraction des données, le calcul des métriques temporelles,
    et l'exportation des résultats.
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

        Extrait la première colonne pour le temps et la deuxième pour
        les données, puis remplit les attributs internes `t` et `samples`.

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

    def ask_user_inputs(self):
        """Demande à l'utilisateur de renseigner le type et la source."""
        self.signal_type = input("Enter signal type (ex: Audio): ")
        self.signal_source = input("Enter signal source (ex: Micro): ")

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
        print(f"\nFichier sauvegardé avec succès : {filename}")

    def run(self, filename):
        """
        Exécute la séquence complète d'acquisition et de traitement.

        Args:
            filename (str): Le chemin d'accès au fichier CSV à analyser.
        """
        print("=== ACQUISITION ET TRAITEMENT DU SIGNAL ===\n")

        self.acquisition_signal(filename)
        self.traitement_signal()
        self.ask_user_inputs()
        self.export_to_csv()


# ==========================================
# Tests et Exécution
# ==========================================
if __name__ == "__main__":
    # Nom et localisation du fichier à lire
    nom_fichier = "U:\\Projet_prog\\Test\\m2_2025-2026\\Fichier_entree.csv"

    # On crée une instance de la classe
    mon_signal = MonSignalGrpA()

    # On lance le programme
    mon_signal.run(nom_fichier)

    # Affichage de vérification
    print("\n--- PROPRIÉTÉS DU SIGNAL ---")
    print(f"Type : {mon_signal.signal_type}")
    print(f"Source : {mon_signal.signal_source}")
    print(f"Taux d'échantillonnage : {mon_signal.sample_rate} Hz")
    print(f"Durée du signal : {mon_signal.duration} s")
    print(f"Timestamp : {mon_signal.timestamp}")
    print(f"Nombre d'échantillons : {len(mon_signal.samples)}")
    print(f"Aperçu des 5 premiers temps : {mon_signal.t[:5]}")
    print(f"Aperçu des 5 premiers samples : {mon_signal.samples[:5]}")