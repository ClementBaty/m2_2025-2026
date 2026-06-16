# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(689, 460)

        self.Bullenom = QtWidgets.QTextBrowser(Dialog)
        self.Bullenom.setGeometry(QtCore.QRect(10, 380, 281, 51))
        self.Bullenom.setObjectName("Bullenom")

        self.BulleTitre = QtWidgets.QTextBrowser(Dialog)
        self.BulleTitre.setGeometry(QtCore.QRect(10, 10, 281, 51))
        self.BulleTitre.setObjectName("BulleTitre")

        self.AffichageURL = QtWidgets.QLineEdit(Dialog)
        self.AffichageURL.setGeometry(QtCore.QRect(40, 90, 511, 20))
        self.AffichageURL.setObjectName("AffichageURL")

        self.Boutonparcourir = QtWidgets.QPushButton(Dialog)
        self.Boutonparcourir.setGeometry(QtCore.QRect(560, 90, 41, 21))
        self.Boutonparcourir.setObjectName("Boutonparcourir")

        # Connexion bouton
        self.Boutonparcourir.clicked.connect(self.ouvrir_fichier)

        self.Lien = QtWidgets.QLabel(Dialog)
        self.Lien.setGeometry(QtCore.QRect(20, 70, 47, 13))
        self.Lien.setObjectName("Lien")

        self.Type = QtWidgets.QLabel(Dialog)
        self.Type.setGeometry(QtCore.QRect(10, 130, 91, 16))
        self.Type.setObjectName("Type")

        self.Source = QtWidgets.QLabel(Dialog)
        self.Source.setGeometry(QtCore.QRect(10, 180, 47, 13))
        self.Source.setObjectName("Source")

        self.comboBox_Type = QtWidgets.QComboBox(Dialog)
        self.comboBox_Type.setGeometry(QtCore.QRect(50, 150, 181, 22))
        self.comboBox_Type.setObjectName("comboBox_Type")
        self.comboBox_Type.addItem("")
        self.comboBox_Type.addItem("")
        self.comboBox_Type.addItem("")
        self.comboBox_Type.addItem("")

        self.comboBox_Source = QtWidgets.QComboBox(Dialog)
        self.comboBox_Source.setGeometry(QtCore.QRect(50, 200, 181, 22))
        self.comboBox_Source.setObjectName("comboBox_Source")
        self.comboBox_Source.addItem("")
        self.comboBox_Source.addItem("")
        self.comboBox_Source.addItem("")
        self.comboBox_Source.addItem("")
        self.comboBox_Source.addItem("")

        self.Exit = QtWidgets.QPushButton(Dialog)
        self.Exit.setGeometry(QtCore.QRect(580, 400, 75, 23))
        self.Exit.setObjectName("Exit")

        self.Generer = QtWidgets.QPushButton(Dialog)
        self.Generer.setGeometry(QtCore.QRect(580, 360, 75, 23))
        self.Generer.setObjectName("Generer")

        self.Bulle_taux_echantillon = QtWidgets.QLabel(Dialog)
        self.Bulle_taux_echantillon.setGeometry(QtCore.QRect(350, 140, 131, 21))
        self.Bulle_taux_echantillon.setObjectName("Bulle_taux_echantillon")

        self.Affichage_echantillon = QtWidgets.QLabel(Dialog)
        self.Affichage_echantillon.setGeometry(QtCore.QRect(480, 140, 61, 20))
        self.Affichage_echantillon.setText("")
        self.Affichage_echantillon.setObjectName("Affichage_echantillon")

        self.Bulle_enregistrement = QtWidgets.QLabel(Dialog)
        self.Bulle_enregistrement.setGeometry(QtCore.QRect(350, 170, 131, 21))
        self.Bulle_enregistrement.setObjectName("Bulle_enregistrement")

        self.Affichage_uptdate = QtWidgets.QLabel(Dialog)
        self.Affichage_uptdate.setGeometry(QtCore.QRect(490, 170, 61, 20))
        self.Affichage_uptdate.setText("")
        self.Affichage_uptdate.setObjectName("Affichage_uptdate")

        self.Affichage_nb_echantillon = QtWidgets.QLabel(Dialog)
        self.Affichage_nb_echantillon.setGeometry(QtCore.QRect(480, 200, 61, 20))
        self.Affichage_nb_echantillon.setText("")
        self.Affichage_nb_echantillon.setObjectName("Affichage_nb_echantillon")

        self.Bulle_nb_echantillon = QtWidgets.QLabel(Dialog)
        self.Bulle_nb_echantillon.setGeometry(QtCore.QRect(350, 200, 131, 21))
        self.Bulle_nb_echantillon.setObjectName("Bulle_nb_echantillon")

        self.Bulle_duree_du_signal = QtWidgets.QLabel(Dialog)
        self.Bulle_duree_du_signal.setGeometry(QtCore.QRect(350, 230, 131, 21))
        self.Bulle_duree_du_signal.setObjectName("Bulle_duree_du_signal")

        self.Affichage_duree_siganl = QtWidgets.QLabel(Dialog)
        self.Affichage_duree_siganl.setGeometry(QtCore.QRect(480, 230, 61, 20))
        self.Affichage_duree_siganl.setText("")
        self.Affichage_duree_siganl.setObjectName("Affichage_duree_siganl")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    # Fonction bouton parcourir
    def ouvrir_fichier(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Choisir un fichier",
            "",
            "Tous les fichiers (*.*)"
        )

        if file_path:
            self.AffichageURL.setText(file_path)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Bullenom.setHtml(_translate("Dialog", "<html>...</html>"))
        self.BulleTitre.setHtml(_translate("Dialog", "<html>...</html>"))
        self.Boutonparcourir.setText(_translate("Dialog", "..."))
        self.Lien.setText(_translate("Dialog", "Lien :"))
        self.Type.setText(_translate("Dialog", "Type de Signal :"))
        self.Source.setText(_translate("Dialog", "Sources :"))

        self.comboBox_Type.setItemText(0, _translate("Dialog", "Entrer Texte"))
        self.comboBox_Type.setItemText(1, _translate("Dialog", "Audio"))
        self.comboBox_Type.setItemText(2, _translate("Dialog", "Vidéo"))
        self.comboBox_Type.setItemText(3, _translate("Dialog", "Image"))

        self.comboBox_Source.setItemText(0, _translate("Dialog", "Entrer Texte"))
        self.comboBox_Source.setItemText(1, _translate("Dialog", "Microphone"))
        self.comboBox_Source.setItemText(2, _translate("Dialog", "Capteurs"))
        self.comboBox_Source.setItemText(3, _translate("Dialog", "Caméra"))
        self.comboBox_Source.setItemText(4, _translate("Dialog", "Fichier"))

        self.Exit.setText(_translate("Dialog", "Exit"))
        self.Generer.setText(_translate("Dialog", "Générer"))
        self.Bulle_taux_echantillon.setText(_translate("Dialog", "Taux d'échantillonage : "))
        self.Bulle_enregistrement.setText(_translate("Dialog", "Derniere enregistrement :"))
        self.Bulle_nb_echantillon.setText(_translate("Dialog", "Nombre d'échantillon : "))
        self.Bulle_duree_du_signal.setText(_translate("Dialog", "Durée du signal"))