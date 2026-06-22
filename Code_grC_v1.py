# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:21:05 2026

@author: noell
"""

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

"""
interface qt designer groupe c

ce programme permet d'extraire des caractéristiques avancées
à partir d'un fichier csv ou json

le fichier d'entrée peut être un csv ou un json

la fréquence d'échantillonnage peut être donnée manuellement

si la fréquence manuelle n'est pas donnée, le programme essaye de la calculer
avec la colonne temps

si aucune colonne temps n'existe, le programme utilise la valeur par défaut
44100 hz pour éviter une erreur

installation :
pip install pyqt5 numpy pandas scipy

lancement :
python interface_extraction_features_qt_v2.py
"""

# importation des modules utiles pour lire les fichiers et gérer le programme
import json
import os
import sys

# importation des bibliothèques pour les calculs et le traitement des données
import numpy as np
import pandas as pd

# importation des fonctions utilisées pour détecter les pics et calculer les statistiques
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

# importation des éléments pyqt5 pour l'interface graphique
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


# fréquence d'échantillonnage utilisée par défaut si aucune autre fréquence n'est trouvée
DEFAULT_FS = 44100


def load_input_file(input_path):
    """charge un fichier csv ou json et retourne un dataframe."""

    # on récupère l'extension du fichier choisi
    extension = os.path.splitext(input_path)[1].lower()

    # si le fichier est un csv, on le lit directement avec pandas
    if extension == ".csv":
        return pd.read_csv(input_path)

    # si le fichier est un json, on l'ouvre puis on le transforme en dataframe
    if extension == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # si le json contient une liste, on peut directement créer un dataframe
        if isinstance(data, list):
            return pd.DataFrame(data)

        # si le json contient un dictionnaire, on cherche les données à l'intérieur
        if isinstance(data, dict):
            for key in ["data", "signal", "samples", "values"]:
                if key in data:
                    value = data[key]

                    # si la valeur est une liste de dictionnaires, on la transforme en tableau
                    if isinstance(value, list):
                        if len(value) > 0 and isinstance(value[0], dict):
                            return pd.DataFrame(value)

                        # si la valeur est une simple liste de nombres, on crée une colonne
                        return pd.DataFrame({"sample_value": value})

            # si aucune clé spéciale n'est trouvée, on transforme directement le dictionnaire
            return pd.DataFrame(data)

        # si le json n'a pas une forme connue, on affiche une erreur
        raise ValueError("Format JSON non reconnu.")

    # si le fichier n'est pas un csv ou un json, on affiche une erreur
    raise ValueError("Format non accepté. Veuillez choisir un fichier CSV ou JSON.")


def detect_columns(df):
    """détecte automatiquement les colonnes temps, fréquence et signal."""

    # on récupère les noms des colonnes du fichier
    cols = list(df.columns)

    # au début, aucune colonne n'est encore trouvée
    time_col = None
    freq_col = None
    signal_col = None

    # on parcourt toutes les colonnes pour essayer de reconnaître leur rôle
    for col in cols:
        c = str(col).lower()

        # si le nom contient time ou temps, on considère que c'est la colonne temps
        if "time" in c or "temps" in c:
            time_col = col

        # si le nom contient freq ou fréquence, on considère que c'est la colonne fréquence
        if "freq" in c or "frequence" in c or "frequency" in c:
            freq_col = col

        # si le nom ressemble à une colonne de signal, on la garde comme signal
        if "sample" in c or "value" in c or "signal" in c or "amplitude" in c:
            signal_col = col

    # si aucune colonne signal n'a été trouvée avec le nom, on cherche une colonne numérique
    if signal_col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # si on a au moins deux colonnes numériques et une colonne temps ou fréquence
        # on prend la deuxième colonne comme signal
        if len(numeric_cols) >= 2 and (time_col is not None or freq_col is not None):
            signal_col = numeric_cols[1]

        # sinon on prend la première colonne numérique disponible
        elif len(numeric_cols) >= 1:
            signal_col = numeric_cols[0]

    # on retourne les colonnes trouvées
    return time_col, freq_col, signal_col


def extract_features(input_path, output_base, fs=None, export_csv=True, export_json=True):
    # on charge le fichier choisi par l'utilisateur
    df = load_input_file(input_path)

    # on vérifie que le fichier n'est pas vide
    if df.empty:
        raise ValueError("Le fichier d'entrée est vide.")

    # on détecte automatiquement les colonnes utiles
    time_col, freq_col, signal_col = detect_columns(df)

    # si aucune colonne signal n'est trouvée, on arrête le programme
    if signal_col is None:
        raise ValueError("Impossible de trouver une colonne numérique pour le signal.")

    # on convertit la colonne signal en valeurs numériques
    df[signal_col] = pd.to_numeric(df[signal_col], errors="coerce")

    # on supprime les lignes où le signal n'est pas valide
    df = df.dropna(subset=[signal_col])

    # il faut au moins deux valeurs pour pouvoir analyser le signal
    if len(df) < 2:
        raise ValueError("Il faut au moins 2 échantillons pour analyser le signal.")

    # cette variable indique d'où vient la fréquence d'échantillonnage
    fs_source = "non nécessaire"

    # cas où le fichier contient déjà une colonne de fréquence
    if freq_col is not None:
        # on convertit la colonne fréquence en valeurs numériques
        df[freq_col] = pd.to_numeric(df[freq_col], errors="coerce")

        # on garde seulement les lignes valides
        df = df.dropna(subset=[freq_col, signal_col])

        # ici on sait que le signal est déjà sous forme spectrale
        signal_type = "spectral"

        # les fréquences viennent directement du fichier
        fft_freqs = df[freq_col].to_numpy()

        # les amplitudes viennent de la colonne signal
        fft_vals = df[signal_col].to_numpy()

        # ici il n'y a pas de signal temporel à analyser
        signal = None

    # cas où le fichier contient un signal temporel
    else:
        # on indique que le signal est temporel
        signal_type = "temporal"

        # on récupère les valeurs du signal
        signal = df[signal_col].to_numpy()

        # on centre le signal en retirant sa moyenne
        signal_centered = signal - np.mean(signal)

        # on récupère le nombre d'échantillons
        n = len(signal_centered)

        # si la fréquence n'est pas donnée, on essaye de la calculer avec la colonne temps
        if fs is None and time_col is not None:
            # on convertit la colonne temps en valeurs numériques
            df[time_col] = pd.to_numeric(df[time_col], errors="coerce")

            # on récupère les valeurs de temps valides
            time_values = df[time_col].dropna().to_numpy()

            # il faut au moins deux valeurs de temps pour calculer le pas de temps
            if len(time_values) >= 2:
                dt = np.median(np.diff(time_values))

                # si le pas de temps est positif, on calcule la fréquence
                if dt > 0:
                    fs = 1 / dt
                    fs_source = "calculée automatiquement avec la colonne temps"

        # si aucune fréquence n'est disponible, on utilise la valeur par défaut
        if fs is None:
            fs = DEFAULT_FS
            fs_source = "valeur par défaut 44100 Hz utilisée"

        # si une fréquence a été donnée par l'utilisateur, on l'indique
        elif fs_source == "non nécessaire":
            fs_source = "indiquée manuellement"

        # on calcule le module de la transformée de fourier
        fft_vals = np.abs(np.fft.rfft(signal_centered))

        # on calcule les fréquences associées au spectre
        fft_freqs = np.fft.rfftfreq(n, 1 / fs)

    # si toutes les amplitudes sont nulles, le centroïde spectral vaut zéro
    if np.sum(fft_vals) == 0:
        spectral_centroid = 0

    # sinon on calcule le centroïde spectral
    else:
        spectral_centroid = float(np.sum(fft_freqs * fft_vals) / np.sum(fft_vals))

    # on cherche les pics dans le spectre
    peak_indices, _ = find_peaks(fft_vals)

    # on garde seulement les pics avec une fréquence positive
    peak_indices = np.array([i for i in peak_indices if fft_freqs[i] > 0])

    # si aucun pic n'est trouvé, on met des indices à zéro
    if len(peak_indices) == 0:
        top = np.array([0, 0, 0])

    # sinon on prend les trois pics les plus importants
    else:
        top = peak_indices[np.argsort(fft_vals[peak_indices])[-3:]]

    # si on a moins de trois pics, on complète avec zéro
    while len(top) < 3:
        top = np.append(top, 0)

    # on trie les pics du plus grand au plus petit
    top = top[np.argsort(fft_vals[top])[::-1]]

    # si le signal est temporel, on calcule aussi les statistiques temporelles
    if signal_type == "temporal":
        mean_val = float(np.mean(signal))
        std_val = float(np.std(signal))
        kurt_val = float(kurtosis(signal))
        skew_val = float(skew(signal))
        rms_val = float(np.sqrt(np.mean(signal ** 2)))
        nb_samples = int(len(signal))

    # si le signal est déjà spectral, ces statistiques ne sont pas calculées
    else:
        mean_val = None
        std_val = None
        kurt_val = None
        skew_val = None
        rms_val = None
        nb_samples = int(len(fft_vals))

    # on regroupe toutes les caractéristiques dans un dictionnaire
    features = {
        "sample_id": os.path.basename(input_path),
        "input_format": os.path.splitext(input_path)[1].lower().replace(".", ""),
        "signal_type": signal_type,
        "nb_samples": nb_samples,
        "sampling_frequency_hz": None if fs is None else float(fs),
        "sampling_frequency_source": fs_source,
        "spectral_centroid": spectral_centroid,
        "mean": mean_val,
        "std_dev": std_val,
        "kurtosis": kurt_val,
        "skewness": skew_val,
        "rms": rms_val,
    }

    # on ajoute les informations des trois pics principaux
    for i in range(3):
        idx = int(top[i])
        features[f"peak_index_{i}"] = idx
        features[f"peak_amplitude_{i}"] = float(fft_vals[idx])
        features[f"fft_magnitude_{i}"] = float(fft_vals[idx])
        features[f"fft_frequency_{i}"] = float(fft_freqs[idx])

    # liste des fichiers créés
    output_files = []

    # si l'utilisateur veut exporter en csv, on crée le fichier csv
    if export_csv:
        csv_path = output_base + ".csv"
        pd.DataFrame([features]).to_csv(csv_path, index=False)
        output_files.append(csv_path)

    # si l'utilisateur veut exporter en json, on crée le fichier json
    if export_json:
        json_path = output_base + ".json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=4, ensure_ascii=False)
        output_files.append(json_path)

    # on retourne les caractéristiques et les fichiers créés
    return features, output_files


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # on récupère le chemin du fichier ui créé avec qt designer
        ui_path = os.path.join(os.path.dirname(__file__), "interface_extraction_features_qt_v2.ui")

        # on charge l'interface graphique
        uic.loadUi(ui_path, self)

        # on met le dossier courant comme dossier de sortie par défaut
        self.outputFolderLineEdit.setText(os.getcwd())

        # bouton pour choisir le fichier d'entrée
        self.browseInputButton.clicked.connect(self.choose_input_file)

        # bouton pour choisir le dossier de sortie
        self.browseOutputButton.clicked.connect(self.choose_output_folder)

        # bouton pour lancer l'extraction
        self.runButton.clicked.connect(self.run_extraction)

        # case à cocher pour activer ou désactiver la fréquence manuelle
        self.manualFsCheckBox.stateChanged.connect(self.update_fs_state)

        # on met à jour l'état du champ fréquence au lancement
        self.update_fs_state()

    def update_fs_state(self):
        # le champ fréquence est activé seulement si la case est cochée
        self.fsLineEdit.setEnabled(self.manualFsCheckBox.isChecked())

    def choose_input_file(self):
        # ouverture d'une fenêtre pour choisir un fichier csv ou json
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le fichier d'entrée",
            "",
            "Fichiers CSV ou JSON (*.csv *.json);;Fichiers CSV (*.csv);;Fichiers JSON (*.json);;Tous les fichiers (*)"
        )

        # si un fichier est choisi, on affiche son chemin dans l'interface
        if path:
            self.inputPathLineEdit.setText(path)

    def choose_output_folder(self):
        # ouverture d'une fenêtre pour choisir le dossier de sortie
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie")

        # si un dossier est choisi, on affiche son chemin dans l'interface
        if folder:
            self.outputFolderLineEdit.setText(folder)

    def run_extraction(self):
        try:
            # on récupère le chemin du fichier d'entrée
            input_path = self.inputPathLineEdit.text().strip()

            # on récupère le chemin du dossier de sortie
            output_folder = self.outputFolderLineEdit.text().strip()

            # si aucun fichier n'est choisi, on affiche une erreur
            if not input_path:
                QMessageBox.critical(self, "Erreur", "Veuillez choisir un fichier CSV ou JSON.")
                return

            # si aucun dossier de sortie n'est choisi, on affiche une erreur
            if not output_folder:
                QMessageBox.critical(self, "Erreur", "Veuillez choisir un dossier de sortie.")
                return

            # il faut choisir au moins un format de sortie
            if not self.exportCsvCheckBox.isChecked() and not self.exportJsonCheckBox.isChecked():
                QMessageBox.critical(self, "Erreur", "Veuillez choisir au moins un format de sortie.")
                return

            # par défaut, la fréquence n'est pas donnée manuellement
            fs = None

            # si la case fréquence manuelle est cochée, on lit la valeur saisie
            if self.manualFsCheckBox.isChecked():
                fs_text = self.fsLineEdit.text().strip()

                # si une valeur est écrite, on la convertit en nombre
                if fs_text:
                    fs = float(fs_text)

            # nom de base des fichiers de sortie
            output_base = os.path.join(output_folder, "features_output")

            # lancement de l'extraction des caractéristiques
            features, output_files = extract_features(
                input_path=input_path,
                output_base=output_base,
                fs=fs,
                export_csv=self.exportCsvCheckBox.isChecked(),
                export_json=self.exportJsonCheckBox.isChecked()
            )

            # on vide la zone de résultat avant d'afficher les nouvelles informations
            self.resultTextEdit.clear()

            # message de réussite
            self.resultTextEdit.append("Extraction terminée avec succès.\n")

            # affichage des fichiers créés
            self.resultTextEdit.append("Fichiers créés :")
            for file in output_files:
                self.resultTextEdit.append(f"- {file}")

            # affichage des caractéristiques calculées
            self.resultTextEdit.append("\nRésumé des caractéristiques :")
            for key, value in features.items():
                self.resultTextEdit.append(f"{key} : {value}")

            # message final pour prévenir l'utilisateur
            QMessageBox.information(self, "Succès", "Extraction terminée avec succès.")

        except Exception as e:
            # si une erreur arrive, elle est affichée dans une fenêtre
            QMessageBox.critical(self, "Erreur", str(e))

            # on vide la zone de résultat
            self.resultTextEdit.clear()

            # on affiche aussi l'erreur dans l'interface
            self.resultTextEdit.append(f"Erreur : {e}")


#prog
if __name__ == "__main__":
    # création de l'application qt
    app = QApplication(sys.argv)

    # création de la fenêtre principale
    window = MainWindow()

    # affichage de la fenêtre
    window.show()

    # lancement de la boucle de l'application
    sys.exit(app.exec_())