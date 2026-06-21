# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 13:57:20 2026

@author: utilisateur
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

def detect_signal_type(df):
    cols = df.columns

    # Cas 1 : présence d'une colonne temps → signal temporel
    if any("time" in c.lower() for c in cols):
        return "temporal"

    # Cas 2 : présence d'une colonne fréquence → spectre
    if any("freq" in c.lower() for c in cols):
        return "spectral"

    # Cas 3 : valeurs négatives → signal temporel
    if df.iloc[:, 0].min() < 0:
        return "temporal"

    # Cas 4 : valeurs strictement positives → spectre possible
    return "spectral"


def extract_features(csv_input, csv_output, fs=None):
    df = pd.read_csv(csv_input)
    signal_type = detect_signal_type(df)

    print(f"Type détecté : {signal_type}")

    #  CAS 1 : SIGNAL TEMPOREL
    if signal_type == "temporal":
        if fs is None:
            raise ValueError("Vous devez fournir fs (fréquence d'échantillonnage) pour un signal temporel.")

        # On prend la colonne amplitude brute
        signal = df.iloc[:, 1].values if "sample_value" in df.columns else df.iloc[:, 0].values
        N = len(signal)

        # FFT
        fft_vals = np.abs(np.fft.rfft(signal))
        fft_freqs = np.fft.rfftfreq(N, 1/fs)

    #  CAS 2 : SPECTRE DE FREQUENCE
    else:
        # Si spectre déjà présent : colonne 0 = fréquence, colonne 1 = amplitude
        fft_freqs = df.iloc[:, 0].values
        fft_vals = df.iloc[:, 1].values
        N = len(fft_vals)

    # EXTRACTION DES 3 PLUS GRANDS PICS 
    peak_indices, _ = find_peaks(fft_vals)
    if len(peak_indices) == 0:
        peak_indices = np.array([0, 0, 0])

    top = np.argsort(fft_vals[peak_indices])[-3:]
    top = peak_indices[top]

    # Sécurisation
    while len(top) < 3:
        top = np.append(top, 0)

    # Indices et amplitudes
    peak_index_0, peak_index_1, peak_index_2 = top
    peak_amplitude_0 = fft_vals[peak_index_0]
    peak_amplitude_1 = fft_vals[peak_index_1]
    peak_amplitude_2 = fft_vals[peak_index_2]

    # Magnitudes FFT
    fft_magnitude_0 = peak_amplitude_0
    fft_magnitude_1 = peak_amplitude_1
    fft_magnitude_2 = peak_amplitude_2

    # Fréquences correspondantes
    fft_frequency_0 = fft_freqs[peak_index_0]
    fft_frequency_1 = fft_freqs[peak_index_1]
    fft_frequency_2 = fft_freqs[peak_index_2]

    # Centroid spectral
    spectral_centroid = np.sum(fft_freqs * fft_vals) / np.sum(fft_vals)

    # Statistiques temporelles (si signal temporel)
    if signal_type == "temporal":
        mean_val = np.mean(signal)
        std_val = np.std(signal)
        kurt_val = kurtosis(signal)
        skew_val = skew(signal)
        rms_val = np.sqrt(np.mean(signal**2))
    else:
        mean_val = std_val = kurt_val = skew_val = rms_val = None

    # Construction du dictionnaire final
    features = {
        "sample_id": csv_input,
        "fft_magnitude_0": fft_magnitude_0,
        "fft_magnitude_1": fft_magnitude_1,
        "fft_magnitude_2": fft_magnitude_2,
        "fft_frequency_0": fft_frequency_0,
        "fft_frequency_1": fft_frequency_1,
        "fft_frequency_2": fft_frequency_2,
        "spectral_centroid": spectral_centroid,
        "mean": mean_val,
        "std_dev": std_val,
        "kurtosis": kurt_val,
        "skewness": skew_val,
        "rms": rms_val,
        "peak_index_0": peak_index_0,
        "peak_index_1": peak_index_1,
        "peak_index_2": peak_index_2,
        "peak_amplitude_0": peak_amplitude_0,
        "peak_amplitude_1": peak_amplitude_1,
        "peak_amplitude_2": peak_amplitude_2
    }

    # Export CSV
    pd.DataFrame([features]).to_csv(csv_output, index=False)
    print(f"Extraction terminée → {csv_output}")


# Exemple d'utilisation :
extract_features("signal_filtered.csv", "features_output.csv", fs=44100)

