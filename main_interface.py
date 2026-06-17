# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 14:46:52 2026

@author: utilisateur
"""



# -*- coding: utf-8 -*-

import sys
import os
import json
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, windows
from scipy.stats import kurtosis, skew
from PyQt5 import QtWidgets
from interface_extraction_features_qt import Ui_MainWindow


# -----------------------------
#  DÉTECTION TYPE SIGNAL
# -----------------------------
def detect_signal_type(df):
    cols = [c.lower() for c in df.columns]

    # Fichier déjà spectral
    if "dominant_frequency_hz" in cols or "frequency" in cols or "freq" in cols:
        return "spectral"

    # Fichier temporel
    if "time_seconds" in cols or "time" in cols or "temps" in cols:
        return "temporal"

    # Heuristique
    first_col = df.iloc[:, 0]
    if first_col.min() < 0:
        return "temporal"

    return "spectral"


# -----------------------------
#  EXTRACTION DE CARACTÉRISTIQUES
# -----------------------------
def extract_features(input_path, fs=None):
    # Lecture CSV ou JSON
    if input_path.lower().endswith(".json"):
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("Le fichier d'entrée est vide.")

    signal_type = detect_signal_type(df)
    sample_id = os.path.basename(input_path)

    # ============================
    # CAS SPECTRAL (ancien comportement)
    # ============================
    if signal_type == "spectral":
        cols_lower = {c.lower(): c for c in df.columns}

        # Fréquence
        if "dominant_frequency_hz" in cols_lower:
            f_col = cols_lower["dominant_frequency_hz"]
        elif "frequency" in cols_lower:
            f_col = cols_lower["frequency"]
        elif "freq" in cols_lower:
            f_col = cols_lower["freq"]
        else:
            f_col = df.columns[0]

        # Amplitude
        if "max_amplitude" in cols_lower:
            a_col = cols_lower["max_amplitude"]
        else:
            # première colonne numérique après la fréquence
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if f_col in num_cols:
                num_cols.remove(f_col)
            a_col = num_cols[0]

        fft_freqs = pd.to_numeric(df[f_col], errors="coerce").to_numpy()
        fft_vals = pd.to_numeric(df[a_col], errors="coerce").to_numpy()

        mask_valid = ~np.isnan(fft_freqs) & ~np.isnan(fft_vals)
        fft_freqs = fft_freqs[mask_valid]
        fft_vals = fft_vals[mask_valid]

        nb_samples = len(fft_vals)
        sampling_frequency = fs  # inconnu, facultatif

        mean_val = std_val = kurt_val = skew_val = rms_val = None

    # ============================
    # CAS TEMPOREL (FFT réelle)
    # ============================
    else:
        # Colonne temps
        time_col = None
        for col in df.columns:
            if "time" in col.lower() or "temps" in col.lower():
                time_col = col
                break

        # Auto-fs
        if fs is None and time_col is not None:
            t = pd.to_numeric(df[time_col], errors="coerce").dropna().to_numpy()
            if len(t) >= 2:
                dt = np.median(np.diff(t))
                if dt > 0:
                    fs = 1.0 / dt

        if fs is None:
            raise ValueError("Impossible de déduire la fréquence d'échantillonnage (fs).")

        # Signal
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if "sample_value" in [c.lower() for c in num_cols]:
            for c in num_cols:
                if c.lower() == "sample_value":
                    sig_col = c
                    break
        else:
            sig_col = num_cols[1] if len(num_cols) > 1 else num_cols[0]

        signal = pd.to_numeric(df[sig_col], errors="coerce").dropna().to_numpy()
        N = len(signal)
        nb_samples = N
        sampling_frequency = fs

        # Fenêtrage Hann
        window = windows.hann(N, sym=False)
        signal_centered = signal - np.mean(signal)
        windowed = signal_centered * window

        # FFT
        fft_vals = np.abs(np.fft.rfft(windowed))
        fft_freqs = np.fft.rfftfreq(N, 1/fs)

        # Statistiques temporelles
        mean_val = float(np.mean(signal))
        std_val = float(np.std(signal))
        kurt_val = float(kurtosis(signal))
        skew_val = float(skew(signal))
        rms_val = float(np.sqrt(np.mean(signal**2)))

    # ============================
    # PICS AMÉLIORÉS
    # ============================
    if len(fft_vals) == 0:
        raise ValueError("Spectre vide après traitement.")

    peak_indices, _ = find_peaks(fft_vals, prominence=np.max(fft_vals) * 0.01)
    peak_indices = peak_indices[fft_freqs[peak_indices] > 0]

    if len(peak_indices) == 0:
        top = np.array([0, 0, 0])
    else:
        top = peak_indices[np.argsort(fft_vals[peak_indices])[-3:]]
        top = top[np.argsort(fft_vals[top])[::-1]]

    while len(top) < 3:
        top = np.append(top, 0)

    # ============================
    # CENTROID LISSÉ
    # ============================
    mag_thresh = 0.001 * np.max(fft_vals)
    mask = fft_vals > mag_thresh
    if np.any(mask):
        spectral_centroid = float(
            np.sum(fft_freqs[mask] * fft_vals[mask]) / np.sum(fft_vals[mask])
        )
    else:
        spectral_centroid = 0.0

    # ============================
    # ÉNERGIE & ENTROPIE
    # ============================
    power_spec = fft_vals**2
    energy = float(np.sum(power_spec))

    if energy > 0:
        p_norm = power_spec / energy
        spectral_entropy = float(-np.sum(p_norm * np.log2(p_norm + 1e-20)))
    else:
        spectral_entropy = 0.0

    # ============================
    # THD & SNR
    # ============================
    def compute_thd_snr(fft_freqs, fft_vals, f0, n_harmonics=5):
        power_total = np.sum(fft_vals[1:]**2)
        idx0 = np.argmin(np.abs(fft_freqs - f0))
        power_fund = fft_vals[idx0]**2

        harm_powers = 0.0
        for k in range(2, n_harmonics + 1):
            fk = k * f0
            if fk > fft_freqs[-1]:
                break
            idxk = np.argmin(np.abs(fft_freqs - fk))
            harm_powers += fft_vals[idxk]**2

        thd = np.sqrt(harm_powers / power_fund) if power_fund > 0 else 0.0

        noise_power = power_total - power_fund - harm_powers
        noise_power = max(noise_power, 1e-20)
        snr = 10 * np.log10(power_fund / noise_power) if power_fund > 0 else 0.0

        return float(thd), float(snr)

    f0_est = float(fft_freqs[top[0]]) if top[0] != 0 else float(fft_freqs[1]) if len(fft_freqs) > 1 else 440.0
    thd, snr = compute_thd_snr(fft_freqs, fft_vals, f0_est)

    # ============================
    # FEATURES FINALES (anciennes + nouvelles)
    # ============================
    features = {
        "sample_id": sample_id,
        "signal_type": signal_type,
        "nb_samples": int(nb_samples),
        "sampling_frequency_hz": float(sampling_frequency) if sampling_frequency is not None else None,

        # FFT principales (comme avant)
        "peak_index_0": int(top[0]),
        "peak_index_1": int(top[1]),
        "peak_index_2": int(top[2]),
        "peak_amplitude_0": float(fft_vals[top[0]]),
        "peak_amplitude_1": float(fft_vals[top[1]]),
        "peak_amplitude_2": float(fft_vals[top[2]]),
        "fft_magnitude_0": float(fft_vals[top[0]]),
        "fft_magnitude_1": float(fft_vals[top[1]]),
        "fft_magnitude_2": float(fft_vals[top[2]]),
        "fft_frequency_0": float(fft_freqs[top[0]]),
        "fft_frequency_1": float(fft_freqs[top[1]]),
        "fft_frequency_2": float(fft_freqs[top[2]]),

        # Spectre avancé
        "spectral_centroid": spectral_centroid,
        "spectral_entropy": spectral_entropy,
        "energy": energy,

        # Temporel
        "mean": float(mean_val) if mean_val is not None else None,
        "std_dev": float(std_val) if std_val is not None else None,
        "kurtosis": float(kurt_val) if kurt_val is not None else None,
        "skewness": float(skew_val) if skew_val is not None else None,
        "rms": float(rms_val) if rms_val is not None else None,

        # Qualité
        "thd": thd,
        "snr_db": snr,
    }

    return features


# -----------------------------
#  INTERFACE GRAPHIQUE
# -----------------------------
class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.browseCsvButton.clicked.connect(self.select_input_file)
        self.ui.browseOutputButton.clicked.connect(self.select_output_folder)
        self.ui.runButton.clicked.connect(self.run_extraction)

    def select_input_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Choisir un fichier d'entrée",
            "",
            "Fichiers CSV/JSON (*.csv *.json)"
        )
        if file:
            self.ui.csvPathLineEdit.setText(file)

    def select_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Choisir un dossier de sortie"
        )
        if folder:
            self.ui.outputFolderLineEdit.setText(folder)

    def run_extraction(self):
        input_path = self.ui.csvPathLineEdit.text().strip()
        output_folder = self.ui.outputFolderLineEdit.text().strip()

        if input_path == "":
            self.ui.resultTextEdit.setText("❌ Aucun fichier d'entrée sélectionné.")
            return

        if output_folder == "":
            self.ui.resultTextEdit.setText("❌ Aucun dossier de sortie sélectionné.")
            return

        # fs manuel ?
        if self.ui.manualFsCheckBox.isChecked():
            try:
                fs = float(self.ui.fsLineEdit.text())
            except Exception:
                self.ui.resultTextEdit.setText("❌ fs invalide.")
                return
        else:
            fs = None  # auto-fs dans extract_features

        try:
            features = extract_features(input_path, fs)
        except Exception as e:
            self.ui.resultTextEdit.setText(f"❌ Erreur pendant l'extraction : {e}")
            return

        # Export CSV
        created_files = []
        if self.ui.exportCsvCheckBox.isChecked():
            csv_out = os.path.join(output_folder, "features_output.csv")
            pd.DataFrame([features]).to_csv(csv_out, sep=";", index=False)
            created_files.append(csv_out)

        # Export JSON
        if self.ui.exportJsonCheckBox.isChecked():
            json_out = os.path.join(output_folder, "features_output.json")
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(features, f, indent=4, ensure_ascii=False)
            created_files.append(json_out)

        # Affichage
        text = "Extraction terminée avec succès.\n\n"
        if created_files:
            text += "Fichiers créés :\n"
            for p in created_files:
                text += f"- {p}\n"
            text += "\n"

        text += "Résumé des caractéristiques :\n"
        for k, v in features.items():
            text += f"{k} : {v}\n"

        self.ui.resultTextEdit.setText(text)


# -----------------------------
#  LANCEMENT
# -----------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
