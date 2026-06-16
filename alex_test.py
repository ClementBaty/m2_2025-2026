# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:08:49 2026

@author: ga08007z
"""

"""
Petit programme de test pour simuler l'acquisition d'un signal.

Le programme demande des informations à l'utilisateur,
génère des valeurs aléatoires puis les enregistre
dans un fichier CSV.

Auteur :

- Alex Grapin
- audioGroupe A
"""

from datetime import datetime
import random
import pandas as pd


class SignalAcquisition:
    """
    Classe permet l'acquisition d'un signal.
    """

    def __init__(self):
        """
        Initialise les variables de la classe.
        """
        self.type = None
        self.source = None
        self.sample_rate = None
        self.duration = None
        self.timestamp = None
        self.samples = []

    def ask_user_inputs(self):
        """
        Demande les informations du signal à l'utilisateur.
        """
        self.type = input("Enter signal type (ex: Audio): ")
        self.source = input("Enter signal source (ex: Micro): ")

        self.sample_rate = float(input("Enter sample rate in Hz (ex: 1000): "))
        self.duration = float(input("Enter duration in seconds (ex: 5): "))

    def generate_timestamp(self):
        """
        Récupère la date et l'heure actuelle
        
        style: YYYY-MM-DD HH:MM:SS
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_fake_samples(self):
        """
        Génère des valeurs aléatoires pour simuler un signal.
        """
        number_of_samples = int(self.sample_rate * self.duration)

        self.samples = []
        for _ in range(number_of_samples):
            self.samples.append(random.uniform(-1.0, 1.0))

    def export_to_csv(self, filename="Output_GroupeA.csv"):
        """
        Sauvegarde les données dans un fichier CSV avec pandas.

        Le fichier CSV contient:
        - timestamp
        - type
        - source
        - sample_rate
        - duration
        - sample_index
        - samples

        Parameters
        ----------
        filename : str
            Nom du fichier CVS en sortie.
        """
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
                    "samples": samples,
                }
            )

        dataframe = pd.DataFrame(data)
        dataframe.to_csv(filename, index=False)

        print(f"\nFile saved successfully: {filename}")

    def run(self):
        """
        Lance toutes les étapes du programme.
        """
        print("=== RAW SIGNAL ACQUISITION TEST ===\n")

        # Demande les informations du signal
        self.ask_user_inputs()
        
        # Récupère la date actuelle
        self.generate_timestamp()
        
        # Crée des données aléatoires
        self.generate_fake_samples()
        
        # Sauvegarde les données dans un fichier CSV
        self.export_to_csv()


if __name__ == "__main__":
    acquisition = SignalAcquisition()
    acquisition.run()