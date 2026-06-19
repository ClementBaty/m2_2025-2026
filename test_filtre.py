import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

'''
 =====================================
 FILTRAGE DU SIGNAL
 =====================================
'''

def filtrer_signal(
        input_signal,
        sampling_rate,
        type_filtre,
        ordre_filtre,
        frequence_coupure=None,
        frequence_basse=None,
        frequence_haute=None):
    """
    Applique un filtre Butterworth sur un signal.

    type_filtre :
        - "passe_bas"
        - "passe_haut"
        - "passe_bande"

    ordre_filtre :
        - 1, 2, 3, ...
    """

    nyquist = sampling_rate / 2

    if type_filtre == "passe_bas":

        if frequence_coupure is None:
            raise ValueError(
                "Il faut renseigner frequence_coupure."
            )

        b, a = signal.butter(
            ordre_filtre,
            frequence_coupure / nyquist,
            btype="low"
        )

    elif type_filtre == "passe_haut":

        if frequence_coupure is None:
            raise ValueError(
                "Il faut renseigner frequence_coupure."
            )

        b, a = signal.butter(
            ordre_filtre,
            frequence_coupure / nyquist,
            btype="high"
        )

    elif type_filtre == "passe_bande":

        if frequence_basse is None or frequence_haute is None:
            raise ValueError(
                "Il faut renseigner frequence_basse et frequence_haute."
            )

        b, a = signal.butter(
            ordre_filtre,
            [
                frequence_basse / nyquist,
                frequence_haute / nyquist
            ],
            btype="band"
        )

    else:
        raise ValueError(
            "Type de filtre inconnu."
        )

    signal_filtre = signal.lfilter(
        b,
        a,
        input_signal
    )

    return signal_filtre

'''
 =====================================
 AFFICHAGE DES RESULTATS
 =====================================
'''

def afficher_resultats(
        input_signal,
        signal_filtre,
        sampling_rate):

    N = len(input_signal)

    temps = np.arange(N) / sampling_rate

    # FFT signal brut
    fft_brut = np.abs(
        np.fft.rfft(input_signal)
    )

    freq_brut = np.fft.rfftfreq(
        N,
        d=1/sampling_rate
    )

    # FFT signal filtré
    fft_filtre = np.abs(
        np.fft.rfft(signal_filtre)
    )

    freq_filtre = np.fft.rfftfreq(
        N,
        d=1/sampling_rate
    )

    plt.figure(figsize=(14, 8))

    # Signal brut
    plt.subplot(2, 2, 1)
    plt.plot(
        temps,
        input_signal
    )
    plt.title("Signal brut")
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.grid()

    # Signal filtré
    plt.subplot(2, 2, 2)
    plt.plot(
        temps,
        signal_filtre
    )
    plt.title("Signal filtre")
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.grid()

    # FFT brute
    plt.subplot(2, 2, 3)
    plt.plot(
        freq_brut,
        fft_brut
    )
    plt.title("FFT signal brut")
    plt.xlabel("Frequence (Hz)")
    plt.ylabel("Amplitude")
    plt.grid()

    # FFT filtrée
    plt.subplot(2, 2, 4)
    plt.plot(
        freq_filtre,
        fft_filtre
    )
    plt.title("FFT signal filtre")
    plt.xlabel("Frequence (Hz)")
    plt.ylabel("Amplitude")
    plt.grid()

    plt.tight_layout()
    plt.show()

'''
 =====================================
 GENERATION D'UN SIGNAL DE TEST
 =====================================
'''
sampling_rate = 1000

temps = np.arange(
    0,
    2,
    1/sampling_rate
)

# Signal composé de plusieurs fréquences
input_signal = (
    np.sin(2*np.pi*10*temps) +
    np.sin(2*np.pi*50*temps) +
    np.sin(2*np.pi*200*temps)
)

# =====================================
# PARAMETRES FILTRE
# =====================================

type_filtre = "passe_bande"
# "passe_bas"
# "passe_haut"
# "passe_bande"

ordre_filtre = 2

frequence_coupure = 60

frequence_basse = 40
frequence_haute = 120
'''
 =====================================
 APPLICATION FILTRE
 =====================================
'''
signal_filtre = filtrer_signal(
    input_signal=input_signal,
    sampling_rate=sampling_rate,
    type_filtre=type_filtre,
    ordre_filtre=ordre_filtre,
    frequence_coupure=frequence_coupure,
    frequence_basse=frequence_basse,
    frequence_haute=frequence_haute
)

# =====================================
# AFFICHAGE
# =====================================

afficher_resultats(
    input_signal,
    signal_filtre,
    sampling_rate
)