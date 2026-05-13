from pathlib import Path


class Donnee:
    def __init__(self, chemin):
        self.existe = None
        fichier = Path(chemin)

        if fichier.exists():
            self.FichierValide = True
        else:
            self.FichierValide = False

        self.extention = fichier.suffix
        if self.extention == ('.csv' or '.CSV'):
            self.convertir_csv_to_list()
        if self.extention == ('.json' or '.JSON'):
            self.convertir_json_to_list()

    def convertir_csv_to_list(self):
        pass

    def convertir_json_to_list(self):
        pass
