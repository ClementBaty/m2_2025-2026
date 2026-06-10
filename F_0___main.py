from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi

import sys

from F_1___Common_Structure import COMONVAR
from F_1_A_Fenetre_Principale import FenetrePrincipale
from F_1_B_Fenetre_Graphique import Fenetregraphique


def interface_init():
    app = QApplication(sys.argv)
    comon_var = COMONVAR()
    fenetre1 = FenetrePrincipale(comon_var)
    fenetre2 = Fenetregraphique(comon_var)

    # on donne accès aux autres fenêtres
    fenetre1.fenetres = {
        "general": fenetre1,
        "graphique": fenetre2,
    }

    fenetre1.fenetres = fenetre1.fenetres

    fenetre1.show()

    sys.exit(app.exec_())




interface_init()


