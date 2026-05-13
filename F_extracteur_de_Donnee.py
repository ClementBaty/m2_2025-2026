from pathlib import Path

class Donnee:
    def __init__(self,chemin):
        self.FichierValide = None
        fichier = Path(chemin)

        if fichier.exists():
            self.FichierValide = True
        else: self.FichierValide = False

        self.extention = fichier.suffix
        print(self.extention)
