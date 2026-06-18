#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:56:09 2026

@author: matrix
"""
import sys
import pandas as pd
import numpy as np
from scipy import signal # Pour les filtres
from PyQt5.QtWidgets import QApplication, QMainWindow
from interface_ui import Ui_MainWindow # Ton fichier converti

class PreprocessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialisation des variables
        self.raw_data = None
        self.filtered_data = None

        # Connexion des boutons aux fonctions
        self.ui.btn_load.clicked.connect(self.load_signal)
        self.ui.btn_apply.clicked.connect(self.apply_filter)
        self.ui.btn_save.clicked.connect(self.save_csv)

    def load_signal(self):
        # Logique pour charger le .json ou .csv
        pass

    def apply_filter(self):
        # Logique : Nettoyage + Filtrage (Butterworth par ex.)
        pass

    def save_csv(self):
        # Sauvegarde au format standardisé
        pass