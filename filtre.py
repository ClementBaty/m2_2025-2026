import numpy as np
from scipy import signal


# =====================================
# VARIABLES EXTERNES
# =====================================

input_signal = None           # Signal chargé depuis un CSV
frequence_coupure = None      # Valeur provenant de l'IHM
frequence_basse = None        # Passe-bande
frequence_haute = None        # Passe-bande


# =====================================
# FILTRES
# =====================================

def passe_bas_ordre_1(input_signal, sampling_rate):
    b, a = signal.butter(
        1,
        frequence_coupure / (sampling_rate / 2),
        btype='low'
    )
    return signal.lfilter(b, a, input_signal)


def passe_bas_ordre_2(input_signal, sampling_rate):
    b, a = signal.butter(
        2,
        frequence_coupure / (sampling_rate / 2),
        btype='low'
    )
    return signal.lfilter(b, a, input_signal)


def passe_haut_ordre_1(input_signal, sampling_rate):
    b, a = signal.butter(
        1,
        frequence_coupure / (sampling_rate / 2),
        btype='high'
    )
    return signal.lfilter(b, a, input_signal)


def passe_haut_ordre_2(input_signal, sampling_rate):
    b, a = signal.butter(
        2,
        frequence_coupure / (sampling_rate / 2),
        btype='high'
    )
    return signal.lfilter(b, a, input_signal)


def passe_bande(input_signal, sampling_rate):
    b, a = signal.butter(
        2,
        [
            frequence_basse / (sampling_rate / 2),
            frequence_haute / (sampling_rate / 2)
        ],
        btype='band'
    )
    return signal.lfilter(b, a, input_signal)


# =====================================
# APPLICATION DU FILTRE
# =====================================

def appliquer_filtre(
        input_signal,
        sampling_rate,
        type_filtre):

    if type_filtre == "PB1":
        return passe_bas_ordre_1(
            input_signal,
            sampling_rate
        )

    elif type_filtre == "PB2":
        return passe_bas_ordre_2(
            input_signal,
            sampling_rate
        )

    elif type_filtre == "PH1":
        return passe_haut_ordre_1(
            input_signal,
            sampling_rate
        )

    elif type_filtre == "PH2":
        return passe_haut_ordre_2(
            input_signal,
            sampling_rate
        )

    elif type_filtre == "PASSE_BANDE":
        return passe_bande(
            input_signal,
            sampling_rate
        )

    else:
        raise ValueError("Filtre inconnu")