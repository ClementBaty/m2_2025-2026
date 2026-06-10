from pathlib import Path
import json

class Donnee:
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
        pass

    def convertir_json_to_list(self):
        with open(self.fichier) as f:
            donnee = json.load(f)
        self.temps = []
        self.signal = []
        
        for point in donnee:
        
            self.temps.append(point['temps_s'])
            self.signal.append(point['signal'])
        