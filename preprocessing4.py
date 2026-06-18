"""
preprocessing.py

Groupe B - Prétraitement du signal

Fonctionnalités :
- Lecture automatique CSV / JSON
- Détection automatique du signal
- Filtrage Butterworth (passe-bas ou passe-haut)
- Normalisation
- Extraction de caractéristiques
- Export CSV standardisé
- Visualisation optionnelle

Auteur : Groupe B
"""

import os
import ast
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq


# ==========================================================
# PARAMÈTRES MODIFIABLES
# ==========================================================

SAMPLING_RATE = 1000  # Hz
FILTER_TYPE = "lowpass"  # "lowpass" ou "highpass"
CUTOFF_FREQ = 50       # Hz
FILTER_ORDER = 4

INPUT_FILE = "signal_raw_bruite.csv"
OUTPUT_FILE = "signal_filtered.csv"

SHOW_PLOTS = True


# ==========================================================
# LECTURE DES DONNÉES
# ==========================================================

def Conversion_chaine_liste(value):# Convertit une chaîne contenant un signal en liste numérique.

    if isinstance(value, list):
        return np.asarray(value, dtype=float)

    if isinstance(value, np.ndarray):
        return value.astype(float)

    if not isinstance(value, str):
        return None

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, (list, tuple)):
            return np.asarray(parsed, dtype=float)

    except Exception:
        pass

    try:
        values = [float(x.strip()) for x in value.split(",")]
        return np.asarray(values)
    except Exception:
        return None


def recherche_colonne(df): # Recherche automatique de la colonne contenant le signal.

    priority_names = [
        "samples",
        "signal",
        "data",
        "values",
        "audio",
        "waveform"
    ]

    columns_lower = {
        col.lower(): col for col in df.columns
    }

    # Recherche par nom connu
    for name in priority_names:
        if name in columns_lower:
            return columns_lower[name]

    # Recherche par contenu
    for col in df.columns:

        first_valid = df[col].dropna()

        if len(first_valid) == 0:
            continue

        candidate = Conversion_chaine_liste(str(first_valid.iloc[0]))

        if candidate is not None and len(candidate) > 3:
            return col

    return None


def Charger_signal(file_path):# Charge un signal depuis CSV ou JSON.

    ext = os.path.splitext(file_path)[1].lower()

    # ======================================================
    # CSV
    # ======================================================

    if ext == ".csv":

        df = pd.read_csv(file_path)

        signal_col = recherche_colonne(df)

        # Cas 1 : colonne contenant une liste
        if signal_col is not None:

            signals = []

            for value in df[signal_col].dropna():
                parsed = Conversion_chaine_liste(str(value))

                if parsed is not None:
                    signals.extend(parsed)

            return np.asarray(signals, dtype=float)

        # Cas 2 : toutes les colonnes sont numériques
        numeric_df = df.select_dtypes(include=np.number)

        if not numeric_df.empty:
            return numeric_df.to_numpy().flatten()

    # ======================================================
    # JSON
    # ======================================================

    elif ext == ".json":

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):

            for key in [
                "samples",
                "signal",
                "data",
                "values"
            ]:
                if key in data:
                    return np.asarray(data[key], dtype=float)

        elif isinstance(data, list):
            return np.asarray(data, dtype=float)

    raise ValueError(
        "Impossible de détecter automatiquement le signal."
    )


# ==========================================================
# FILTRAGE
# ==========================================================

def butter_filter(
    signal,
    fs,
    cutoff,
    filter_type="lowpass",
    order=4
):# Filtre Butterworth.
    

    nyquist = fs / 2

    normalized_cutoff = cutoff / nyquist

    b, a = butter(
        order,
        normalized_cutoff,
        btype="low" if filter_type == "lowpass" else "high"
    )

    return filtfilt(b, a, signal)


# ==========================================================
# NORMALISATION
# ==========================================================

def Normalisation_signal(signal):  #Normalisation entre -1 et 1.

    max_abs = np.max(np.abs(signal))

    if max_abs == 0:
        return signal

    return signal / max_abs


# ==========================================================
# EXTRACTION DE CARACTÉRISTIQUES
# ==========================================================

def extraction_amp_freq(signal, fs):
    # Calcule :
    # - amplitude maximale
    # - fréquence dominante
   

    max_amplitude = float(np.max(np.abs(signal)))

    N = len(signal)

    yf = np.abs(fft(signal))

    xf = fftfreq(N, 1 / fs)

    positive_mask = xf > 0

    xf = xf[positive_mask]
    yf = yf[positive_mask]

    dominant_frequency = float(
        xf[np.argmax(yf)]
    )

    return {
        "max_amplitude": max_amplitude,
        "dominant_frequency": dominant_frequency
    }


# ==========================================================
# EXPORT
# ==========================================================

def sauvegarde_resultat(signal_filtered, features, output_file):
    # Sauvegarde :
    # sample_index | filtered_signal

    # et ajoute les caractéristiques à chaque ligne.
   

    df = pd.DataFrame({
        "sample_index": np.arange(len(signal_filtered)),
        "filtered_signal": signal_filtered,
        "max_amplitude": features["max_amplitude"],
        "dominant_frequency": features["dominant_frequency"]
    })

    df.to_csv(output_file, index=False)

    print(f"Résultats sauvegardés dans : {output_file}")


# ==========================================================
# VISUALISATION
# ==========================================================

def Affichage(raw_signal):

    plt.figure(figsize=(12, 5))

    plt.plot(raw_signal, label="Signal brut")

    plt.title("Signal avant filtrage")
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()



def Affichage_Signal_Filtre(filtered_signal):

    plt.figure(figsize=(12, 5))

    plt.plot(
        filtered_signal,
        label="Signal filtré",
        linewidth=2
    )

    plt.title("Signal après filtrage")
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
    
    
def Affichage_Combinée(raw_signal,filtered_signal):

    plt.figure(figsize=(12, 5))

    plt.plot(raw_signal, label="Signal brut")

    plt.plot(
        filtered_signal,
        label="Signal filtré",
        linewidth=2
    )

    plt.title("Combinaison avant/après filtrage")
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================

def main():

    print("Chargement du signal...")

    raw_signal = Charger_signal(INPUT_FILE)

    print(
        f"Nombre d'échantillons détectés : {len(raw_signal)}"
    )

    filtered_signal = butter_filter(
        raw_signal,
        fs=SAMPLING_RATE,
        cutoff=CUTOFF_FREQ,
        filter_type=FILTER_TYPE,
        order=FILTER_ORDER
    )

    filtered_signal = Normalisation_signal(
        filtered_signal
    )

    features = extraction_amp_freq(
        filtered_signal,
        SAMPLING_RATE
    )

    print("\nCaractéristiques :")
    for key, value in features.items():
        print(f"{key}: {value:.4f}")

    sauvegarde_resultat(
        filtered_signal,
        features,
        OUTPUT_FILE
    )

    if SHOW_PLOTS:
       Affichage(
            raw_signal)
       Affichage_Signal_Filtre(filtered_signal)  
       Affichage_Combinée(raw_signal,filtered_signal)
        


if __name__ == "__main__":
    main()