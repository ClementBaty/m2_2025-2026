# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:07:31 2026

@author: kd08185z
"""
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
import sys


class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"C:\Users\kd08185z\m2_2025-2026\interface_graphique.ui", self)


app = QApplication(sys.argv)
fenetre = FenetrePrincipale()
fenetre.show()
