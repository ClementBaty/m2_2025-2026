import numpy as np
from scipy import signal


# =====================================
# PROGRAMME DE FILTRAGE UNIQUEMENT
# =====================================

def filtrer_signal(
        input_signal,
        sampling_rate,
        type_filtre,
        ordre_filtre,
        frequence_coupure=None,
        frequence_basse=None,
        frequence_haute=None):
    """
    Fonction qui applique un filtre sur un signal.

    input_signal       : signal à filtrer
    sampling_rate      : fréquence d'échantillonnage en Hz
    type_filtre        : "passe_bas", "passe_haut" ou "passe_bande"
    ordre_filtre       : ordre du filtre, par exemple 1, 2, 3, 4...
    frequence_coupure  : fréquence de coupure pour passe-bas ou passe-haut
    frequence_basse    : fréquence basse pour passe-bande
    frequence_haute    : fréquence haute pour passe-bande
    """

    nyquist = sampling_rate / 2

    if type_filtre == "passe_bas":

        if frequence_coupure is None:
            raise ValueError("Il faut donner une fréquence de coupure.")

        frequence_normalisee = frequence_coupure / nyquist

        b, a = signal.butter(
            ordre_filtre,
            frequence_normalisee,
            btype="low"
        )

    elif type_filtre == "passe_haut":

        if frequence_coupure is None:
            raise ValueError("Il faut donner une fréquence de coupure.")

        frequence_normalisee = frequence_coupure / nyquist

        b, a = signal.butter(
            ordre_filtre,
            frequence_normalisee,
            btype="high"
        )

    elif type_filtre == "passe_bande":

        if frequence_basse is None or frequence_haute is None:
            raise ValueError("Il faut donner une fréquence basse et une fréquence haute.")

        frequences_normalisees = [
            frequence_basse / nyquist,
            frequence_haute / nyquist
        ]

        b, a = signal.butter(
            ordre_filtre,
            frequences_normalisees,
            btype="band"
        )

    else:
        raise ValueError("Type de filtre inconnu.")

    signal_filtre = signal.lfilter(b, a, input_signal)

    return signal_filtre