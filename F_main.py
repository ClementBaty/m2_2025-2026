from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi

import sys

from F_extracteur_de_Donnee import Donnee
from F_FenetreGraphique import Fenetregraphique
from F_1___ComonStructure import COMMONCLASS
from F_1_A_Fenetre_Principale import FenetrePrincipale






app = QApplication(sys.argv)
fenetre = FenetrePrincipale()
fenetre.show()
sys.exit(app.exec_())
