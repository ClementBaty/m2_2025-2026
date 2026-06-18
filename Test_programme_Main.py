# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 15:49:41 2026

@author: on07659z
"""

import sys
import os
import numpy as np
import pandas as pd

from scipy import signal

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QVBoxLayout
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from interface import Ui_MainWindow


# CRÉATION D'UN SIGNAL TEST SI BESOIN

def creer_signal_test():
    Fe = 1000
    duree = 2

    t = np.linspace(0, duree, Fe * duree)

    signal_test = (
        np.sin(2 * np.pi * 10 * t)
        + 0.5 * np.sin(2 * np.pi * 100 * t)
    )

    data = pd.DataFrame({
        "temps": t,
        "signal": signal_test
    })

    data.to_csv("signal_test.csv", index=False)


# LECTURE ET SAUVEGARDE CSV

def lire_signal_csv(chemin):
    data = pd.read_csv(chemin)

    if "signal" in data.columns:
        return data["signal"].values
    else:
        return data.iloc[:, -1].values


def sauvegarder_signal_csv(signal_filtre, chemin):
    data = pd.DataFrame({
        "signal_filtre": signal_filtre
    })

    data.to_csv(chemin, index=False)


# FONCTIONS DE FILTRAGE

def filtre_passe_bas(signal_entree, frequence_coupure, frequence_echantillonnage, ordre):
    nyquist = frequence_echantillonnage / 2
    fc_normale = frequence_coupure / nyquist

    b, a = signal.butter(ordre, fc_normale, btype="low")
    return signal.filtfilt(b, a, signal_entree)


def filtre_passe_haut(signal_entree, frequence_coupure, frequence_echantillonnage, ordre):
    nyquist = frequence_echantillonnage / 2
    fc_normale = frequence_coupure / nyquist

    b, a = signal.butter(ordre, fc_normale, btype="high")
    return signal.filtfilt(b, a, signal_entree)


def filtre_passe_bande(signal_entree, frequence_basse, frequence_haute, frequence_echantillonnage, ordre):
    nyquist = frequence_echantillonnage / 2

    f_basse_normale = frequence_basse / nyquist
    f_haute_normale = frequence_haute / nyquist

    b, a = signal.butter(
        ordre,
        [f_basse_normale, f_haute_normale],
        btype="band"
    )

    return signal.filtfilt(b, a, signal_entree)


# CLASSE PRINCIPALE

class ApplicationFiltre(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.signal_original = None
        self.signal_filtre = None

        self.frequence_echantillonnage = 1000
        self.frequence_coupure = 50

        self.frequence_basse = 20
        self.frequence_haute = 80

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.ui.graph_widget.setLayout(layout)

        self.ui.btn_load.clicked.connect(self.charger_signal)
        self.ui.btn_apply.clicked.connect(self.appliquer_filtre)
        self.ui.Btn_save.clicked.connect(self.sauvegarder_signal)

        self.ui.spinBox.setMinimum(1)
        self.ui.spinBox.setMaximum(2)
        self.ui.spinBox.setValue(1)

    def charger_signal(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Charger un signal CSV",
            "",
            "Fichiers CSV (*.csv)"
        )

        if fichier:
            self.signal_original = lire_signal_csv(fichier)
            self.afficher_signal(self.signal_original, "Signal original")
            QMessageBox.information(self, "Succès", "Signal chargé avec succès")

    def appliquer_filtre(self):
        if self.signal_original is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger un signal")
            return

        type_filtre = self.ui.comboBox.currentText()
        ordre = self.ui.spinBox.value()

        if type_filtre == "Filtre passe bas":
            self.signal_filtre = filtre_passe_bas(
                self.signal_original,
                self.frequence_coupure,
                self.frequence_echantillonnage,
                ordre
            )

        elif type_filtre == "Filtre passe haut":
            self.signal_filtre = filtre_passe_haut(
                self.signal_original,
                self.frequence_coupure,
                self.frequence_echantillonnage,
                ordre
            )

        elif type_filtre == "Filtre passe bande":
            self.signal_filtre = filtre_passe_bande(
                self.signal_original,
                self.frequence_basse,
                self.frequence_haute,
                self.frequence_echantillonnage,
                ordre
            )

        self.afficher_signal(self.signal_filtre, "Signal filtré")
        QMessageBox.information(self, "Succès", "Filtre appliqué avec succès")

    def sauvegarder_signal(self):
        if self.signal_filtre is None:
            QMessageBox.warning(self, "Erreur", "Aucun signal filtré à sauvegarder")
            return

        fichier, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le signal filtré",
            "signal_filtre.csv",
            "Fichiers CSV (*.csv)"
        )

        if fichier:
            sauvegarder_signal_csv(self.signal_filtre, fichier)
            QMessageBox.information(self, "Succès", "Signal sauvegardé avec succès")

    def afficher_signal(self, signal_data, titre):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        ax.plot(signal_data)
        ax.set_title(titre)
        ax.set_xlabel("Échantillons")
        ax.set_ylabel("Amplitude")
        ax.grid()

        self.canvas.draw()


# LANCEMENT DU PROGRAMME
if __name__ == "__main__":

    if not os.path.exists("signal_test.csv"):
        creer_signal_test()

    app = QApplication(sys.argv)
    fenetre = ApplicationFiltre()
    fenetre.show()
    sys.exit(app.exec_())