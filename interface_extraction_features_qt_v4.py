# -*- coding: utf-8 -*-
"""
Version 4 - Interface Qt Designer avec affichage des signaux dans l'interface

Ce programme permet :
- de charger un fichier CSV ou JSON ;
- de détecter automatiquement les colonnes temps, fréquence et signal ;
- de calculer des indicateurs temporels et fréquentiels ;
- d'exporter les résultats en CSV et/ou JSON ;
- d'afficher les signaux directement dans l'interface.

Installation :
pip install pyqt5 numpy pandas scipy matplotlib

Lancement :
python interface_extraction_features_qt_v4.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd

from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# fréquence d'échantillonnage utilisée par défaut si aucune autre fréquence n'est trouvée
DEFAULT_FS = 44100


# -----------------------------------------------------------------------------
# Chargement du fichier d'entrée
# -----------------------------------------------------------------------------
def load_input_file(input_path):
    """Charge un fichier CSV ou JSON et retourne un DataFrame."""

    extension = os.path.splitext(input_path)[1].lower()

    if extension == ".csv":
        return pd.read_csv(input_path)

    if extension == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return pd.DataFrame(data)

        if isinstance(data, dict):
            for key in ["data", "signal", "samples", "values"]:
                if key in data:
                    value = data[key]

                    if isinstance(value, list):
                        if len(value) > 0 and isinstance(value[0], dict):
                            return pd.DataFrame(value)

                        return pd.DataFrame({"sample_value": value})

            return pd.DataFrame(data)

        raise ValueError("Format JSON non reconnu.")

    raise ValueError("Format non accepté. Veuillez choisir un fichier CSV ou JSON.")


# -----------------------------------------------------------------------------
# Détection automatique des colonnes
# -----------------------------------------------------------------------------
def detect_columns(df):
    """Détecte automatiquement les colonnes temps, fréquence et signal."""

    cols = list(df.columns)

    time_col = None
    freq_col = None
    signal_col = None

    for col in cols:
        c = str(col).lower()

        if "time" in c or "temps" in c:
            time_col = col

        if "freq" in c or "frequence" in c or "frequency" in c:
            freq_col = col

        if "sample" in c or "value" in c or "signal" in c or "amplitude" in c:
            signal_col = col

    if signal_col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) >= 2 and (time_col is not None or freq_col is not None):
            signal_col = numeric_cols[1]

        elif len(numeric_cols) >= 1:
            signal_col = numeric_cols[0]

    return time_col, freq_col, signal_col


# -----------------------------------------------------------------------------
# Extraction des caractéristiques
# -----------------------------------------------------------------------------
def extract_features(input_path, output_base, fs=None, export_csv=True, export_json=True):
    """Extrait les caractéristiques du signal et prépare les données d'affichage."""

    df = load_input_file(input_path)

    if df.empty:
        raise ValueError("Le fichier d'entrée est vide.")

    time_col, freq_col, signal_col = detect_columns(df)

    if signal_col is None:
        raise ValueError("Impossible de trouver une colonne numérique pour le signal.")

    df[signal_col] = pd.to_numeric(df[signal_col], errors="coerce")
    df = df.dropna(subset=[signal_col])

    if len(df) < 2:
        raise ValueError("Il faut au moins 2 échantillons pour analyser le signal.")

    fs_source = "non nécessaire"

    # -------------------------------------------------------------------------
    # Cas 1 : le fichier contient déjà un signal spectral
    # -------------------------------------------------------------------------
    if freq_col is not None:
        df[freq_col] = pd.to_numeric(df[freq_col], errors="coerce")
        df = df.dropna(subset=[freq_col, signal_col])

        signal_type = "spectral"

        fft_freqs = df[freq_col].to_numpy()
        fft_vals = df[signal_col].to_numpy()

        signal = None
        time_axis = None
        signal_centered = None

    # -------------------------------------------------------------------------
    # Cas 2 : le fichier contient un signal temporel
    # -------------------------------------------------------------------------
    else:
        signal_type = "temporal"

        signal = df[signal_col].to_numpy()
        signal_centered = signal - np.mean(signal)

        n = len(signal_centered)

        if fs is None and time_col is not None:
            df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
            time_values = df[time_col].dropna().to_numpy()

            if len(time_values) >= 2:
                dt = np.median(np.diff(time_values))

                if dt > 0:
                    fs = 1 / dt
                    fs_source = "calculée automatiquement avec la colonne temps"

        if fs is None:
            fs = DEFAULT_FS
            fs_source = "valeur par défaut 44100 Hz utilisée"

        elif fs_source == "non nécessaire":
            fs_source = "indiquée manuellement"

        fft_vals = np.abs(np.fft.rfft(signal_centered))
        fft_freqs = np.fft.rfftfreq(n, 1 / fs)

        if time_col is not None:
            df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
            time_axis = df[time_col].to_numpy()
        else:
            time_axis = np.arange(len(signal)) / fs

    # -------------------------------------------------------------------------
    # Calcul du centroïde spectral
    # -------------------------------------------------------------------------
    if np.sum(fft_vals) == 0:
        spectral_centroid = 0
    else:
        spectral_centroid = float(np.sum(fft_freqs * fft_vals) / np.sum(fft_vals))

    # -------------------------------------------------------------------------
    # Détection des trois pics principaux
    # -------------------------------------------------------------------------
    peak_indices, _ = find_peaks(fft_vals)
    peak_indices = np.array([i for i in peak_indices if fft_freqs[i] > 0])

    if len(peak_indices) == 0:
        top = np.array([0, 0, 0])
    else:
        top = peak_indices[np.argsort(fft_vals[peak_indices])[-3:]]

    while len(top) < 3:
        top = np.append(top, 0)

    top = top[np.argsort(fft_vals[top])[::-1]]

    # -------------------------------------------------------------------------
    # Indicateurs temporels
    # -------------------------------------------------------------------------
    if signal_type == "temporal":
        mean_val = float(np.mean(signal))
        std_val = float(np.std(signal))
        kurt_val = float(kurtosis(signal))
        skew_val = float(skew(signal))
        rms_val = float(np.sqrt(np.mean(signal ** 2)))
        nb_samples = int(len(signal))

    else:
        mean_val = None
        std_val = None
        kurt_val = None
        skew_val = None
        rms_val = None
        nb_samples = int(len(fft_vals))

    # -------------------------------------------------------------------------
    # Regroupement des caractéristiques
    # -------------------------------------------------------------------------
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

    for i in range(3):
        idx = int(top[i])
        features[f"peak_index_{i}"] = idx
        features[f"peak_amplitude_{i}"] = float(fft_vals[idx])
        features[f"fft_magnitude_{i}"] = float(fft_vals[idx])
        features[f"fft_frequency_{i}"] = float(fft_freqs[idx])

    # -------------------------------------------------------------------------
    # Export des résultats
    # -------------------------------------------------------------------------
    output_files = []

    if export_csv:
        csv_path = output_base + ".csv"
        pd.DataFrame([features]).to_csv(csv_path, index=False)
        output_files.append(csv_path)

    if export_json:
        json_path = output_base + ".json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=4, ensure_ascii=False)
        output_files.append(json_path)

    # -------------------------------------------------------------------------
    # Données utilisées pour les graphiques
    # -------------------------------------------------------------------------
    plot_data = {
        "signal_type": signal_type,
        "signal": signal,
        "signal_centered": signal_centered,
        "time_axis": time_axis,
        "fft_freqs": fft_freqs,
        "fft_vals": fft_vals,
        "peak_indices": top,
        "sampling_frequency_hz": fs,
        "time_col": time_col,
        "signal_col": signal_col,
    }

    return features, output_files, plot_data


# -----------------------------------------------------------------------------
# Interface graphique principale
# -----------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), "interface_extraction_features_qt_v4.ui")
        uic.loadUi(ui_path, self)

        # Figure matplotlib intégrée dans le QWidget nommé plotWidget
        self.figure = Figure(figsize=(10, 7))
        self.canvas = FigureCanvas(self.figure)

        self.plot_layout = QVBoxLayout(self.plotWidget)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.addWidget(self.canvas)

        self.show_empty_plot()

        self.outputFolderLineEdit.setText(os.getcwd())

        self.browseInputButton.clicked.connect(self.choose_input_file)
        self.browseOutputButton.clicked.connect(self.choose_output_folder)
        self.runButton.clicked.connect(self.run_extraction)
        self.manualFsCheckBox.stateChanged.connect(self.update_fs_state)

        self.update_fs_state()

    def show_empty_plot(self):
        """Affiche un graphique vide au lancement."""

        self.figure.clear()

        ax = self.figure.add_subplot(1, 1, 1)
        ax.set_title("Aucun signal affiché")
        ax.set_xlabel("Temps ou fréquence")
        ax.set_ylabel("Amplitude")
        ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()

    def update_fs_state(self):
        """Active ou désactive la zone de fréquence manuelle."""

        self.fsLineEdit.setEnabled(self.manualFsCheckBox.isChecked())

    def choose_input_file(self):
        """Choisit le fichier CSV ou JSON d'entrée."""

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le fichier d'entrée",
            "",
            "Fichiers CSV ou JSON (*.csv *.json);;Fichiers CSV (*.csv);;Fichiers JSON (*.json);;Tous les fichiers (*)"
        )

        if path:
            self.inputPathLineEdit.setText(path)

    def choose_output_folder(self):
        """Choisit le dossier de sortie."""

        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie")

        if folder:
            self.outputFolderLineEdit.setText(folder)

    def display_signal_plot(self, plot_data):
        """Affiche plusieurs signaux dans l'interface."""

        signal_type = plot_data["signal_type"]
        signal = plot_data["signal"]
        signal_centered = plot_data["signal_centered"]
        time_axis = plot_data["time_axis"]
        fft_freqs = plot_data["fft_freqs"]
        fft_vals = plot_data["fft_vals"]
        peak_indices = plot_data["peak_indices"]

        self.figure.clear()

        # ---------------------------------------------------------------------
        # Affichage pour un signal temporel
        # ---------------------------------------------------------------------
        if signal_type == "temporal":
            ax1 = self.figure.add_subplot(4, 1, 1)
            ax1.plot(time_axis, signal)
            ax1.set_title("Signal temporel original")
            ax1.set_xlabel("Temps (s)")
            ax1.set_ylabel("Amplitude")
            ax1.grid(True)

            ax2 = self.figure.add_subplot(4, 1, 2)
            ax2.plot(time_axis, signal_centered)
            ax2.set_title("Signal centré : signal - moyenne")
            ax2.set_xlabel("Temps (s)")
            ax2.set_ylabel("Amplitude centrée")
            ax2.grid(True)

            ax3 = self.figure.add_subplot(4, 1, 3)
            ax3.plot(fft_freqs, fft_vals)
            ax3.set_title("Spectre fréquentiel FFT")
            ax3.set_xlabel("Fréquence (Hz)")
            ax3.set_ylabel("Magnitude")
            ax3.grid(True)

            for idx in peak_indices:
                idx = int(idx)
                if idx < len(fft_freqs):
                    ax3.plot(fft_freqs[idx], fft_vals[idx], "o")
                    ax3.text(
                        fft_freqs[idx],
                        fft_vals[idx],
                        f"{fft_freqs[idx]:.2f} Hz",
                        fontsize=8,
                    )

            ax4 = self.figure.add_subplot(4, 1, 4)
            ax4.hist(signal, bins=30)
            ax4.set_title("Histogramme des amplitudes")
            ax4.set_xlabel("Amplitude")
            ax4.set_ylabel("Nombre")
            ax4.grid(True)

        # ---------------------------------------------------------------------
        # Affichage pour un signal spectral
        # ---------------------------------------------------------------------
        else:
            ax1 = self.figure.add_subplot(2, 1, 1)
            ax1.plot(fft_freqs, fft_vals)
            ax1.set_title("Signal spectral")
            ax1.set_xlabel("Fréquence (Hz)")
            ax1.set_ylabel("Amplitude / Magnitude")
            ax1.grid(True)

            for idx in peak_indices:
                idx = int(idx)
                if idx < len(fft_freqs):
                    ax1.plot(fft_freqs[idx], fft_vals[idx], "o")
                    ax1.text(
                        fft_freqs[idx],
                        fft_vals[idx],
                        f"{fft_freqs[idx]:.2f} Hz",
                        fontsize=8,
                    )

            ax2 = self.figure.add_subplot(2, 1, 2)
            ax2.bar(fft_freqs, fft_vals)
            ax2.set_title("Représentation en barres du spectre")
            ax2.set_xlabel("Fréquence (Hz)")
            ax2.set_ylabel("Amplitude")
            ax2.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()

    def run_extraction(self):
        """Lance l'extraction, affiche les résultats et les graphes."""

        try:
            input_path = self.inputPathLineEdit.text().strip()
            output_folder = self.outputFolderLineEdit.text().strip()

            if not input_path:
                QMessageBox.critical(self, "Erreur", "Veuillez choisir un fichier CSV ou JSON.")
                return

            if not output_folder:
                QMessageBox.critical(self, "Erreur", "Veuillez choisir un dossier de sortie.")
                return

            if not self.exportCsvCheckBox.isChecked() and not self.exportJsonCheckBox.isChecked():
                QMessageBox.critical(self, "Erreur", "Veuillez choisir au moins un format de sortie.")
                return

            fs = None

            if self.manualFsCheckBox.isChecked():
                fs_text = self.fsLineEdit.text().strip()

                if fs_text:
                    fs = float(fs_text)

            output_base = os.path.join(output_folder, "features_output")

            features, output_files, plot_data = extract_features(
                input_path=input_path,
                output_base=output_base,
                fs=fs,
                export_csv=self.exportCsvCheckBox.isChecked(),
                export_json=self.exportJsonCheckBox.isChecked(),
            )

            self.resultTextEdit.clear()
            self.resultTextEdit.append("Extraction terminée avec succès.\n")

            self.resultTextEdit.append("Fichiers créés :")
            for file in output_files:
                self.resultTextEdit.append(f"- {file}")

            self.resultTextEdit.append("\nRésumé des caractéristiques :")
            for key, value in features.items():
                self.resultTextEdit.append(f"{key} : {value}")

            self.display_signal_plot(plot_data)

            QMessageBox.information(self, "Succès", "Extraction terminée avec succès.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

            self.resultTextEdit.clear()
            self.resultTextEdit.append(f"Erreur : {e}")

            self.show_empty_plot()


# -----------------------------------------------------------------------------
# Programme principal
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
