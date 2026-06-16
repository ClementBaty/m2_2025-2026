# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 23:31:15 2026

@author: Xelo
"""

from F_1___Common_Structure import COMONVAR
from F_extracteur_de_Donnee import Donnee

comon_var = COMONVAR()
d = Donnee("analysis.csv")

if d.FichierValide:
    comon_var.donnees = d.donnees
    print("nombre d'échantillons :", len(comon_var.donnees))
    print("premier échantillon :", comon_var.donnees[0])
    print("label du 3e :", comon_var.donnees[2]['label'])
    print("anomalie du 3e :", comon_var.donnees[2]['anomaly_reason'])
else:
    print("Fichier pas trouvé")