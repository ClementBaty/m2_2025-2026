from pathlib import Path
import json
import csv


class Donnee:
    """
    class permettant l'extraction des donné issue du fichier selectionner.
    detect automatiquement lextention du fichier (.csv ou .json) et active la fonction de recuperation adapter.
    renvoir une liste de donnée
    """
    def __init__(self, chemin):
        self.existe = None
        self.fichier = Path(chemin)

        if self.fichier.exists():
            self.FichierValide = True
        else:
            self.FichierValide = False

        self.extention = self.fichier.suffix
        if self.extention == ('.csv' or '.CSV'):
            self.convertir_csv_to_list()
        if self.extention == ('.json' or '.JSON'):
            self.convertir_json_to_list()

    def convertir_csv_to_list(self):
        with open(self.fichier) as f:
            lecteur = csv.DictReader(f)
            self.donnees = []

            for point in lecteur:
                self.donnees.append(point)

    def convertir_json_to_list(self):
        with open(self.fichier) as f:
            self.donnees = json.load(f)
        