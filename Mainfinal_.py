"""
Main final du Groupe B 

OUATTARA NADIEN 
DEOGRACIAS KASABELE
BACAR NADJILAT
ALI ELIAN

"""

import sys
import os
import ast
import json
import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from interface import MainApp


etat = {
    "signal_brut":   None,    # np.ndarray — signal original chargé
    "signal_filtre": None,    # np.ndarray — signal après filtrage
    "temps":         None,    # np.ndarray — axe temporel en secondes
    "fs":            1000.0,  # float      — fréquence d'échantillonnage (Hz)
    "fichier":       None,    # str        — chemin du fichier source
    "meta": {                 # dict       — paramètres du dernier filtre appliqué
        "type":  None,        # "passe_bas" | "passe_haut" | "passe_bande"
        "fc":    None,        # fréquence de coupure basse (Hz)
        "fc2":   None,        # fréquence de coupure haute (Hz), passe-bande seulement
        "ordre": None,        # ordre du filtre Butterworth
    },
}

# Declaration des fonction  

def Conversion_chaine_liste(value):
    """Convertit une chaîne contenant un signal en tableau numpy.

    Supporte les formats : liste Python, tuple, valeurs séparées par virgules.
    """
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

def recherche_colonne(df):
    """Recherche automatiquement la colonne contenant le signal dans un DataFrame.

    Cherche d'abord par nom connu, puis par analyse du contenu des cellules.

    Returns:
        str: Nom de la colonne détectée, ou None si aucune trouvée.
    """
    # Noms prioritaires 
    noms_prioritaires = [
        "valeur", "signal", "amplitude", "value",
        "data", "samples", "audio", "waveform", "y"
    ]

    colonnes_lower = {col.lower(): col for col in df.columns}

    # Recherche par nom connu
    for nom in noms_prioritaires:
        if nom in colonnes_lower:
            return colonnes_lower[nom]

    # Recherche par contenu des cellules
    for col in df.columns:
        premier_valide = df[col].dropna()
        if len(premier_valide) == 0:
            continue
        candidat = Conversion_chaine_liste(str(premier_valide.iloc[0]))
        if candidat is not None and len(candidat) > 3:
            return col

    # Fallback : deuxième colonne numérique
    num = df.select_dtypes(include=[np.number]).columns.tolist()
    return num[1] if len(num) >= 2 else (num[0] if num else None)

def construire_axe_temps(df, n):
    """Construit l'axe temporel en secondes depuis un DataFrame.

    Si une colonne temporelle est trouvée, calcule fs automatiquement.
    Sinon, génère un axe synthétique basé sur etat['fs'].

    Returns:
        np.ndarray: Axe temporel en secondes.
    """
    low = {c.lower(): c for c in df.columns}
    for nom in ["temps", "time", "t", "timestamp", "x"]:
        if nom in low:
            t = df[low[nom]].to_numpy(dtype=float)
            if len(t) > 1:
                dt = np.mean(np.diff(t))
                if dt > 0:
                    etat["fs"] = round(1.0 / dt, 2)
            return t

    # Aucune colonne temps trouvée : axe synthétique
    return np.arange(n) / etat["fs"]

# FONCTIONS DE LECTURE DES FICHIERS

def Charger_signal(file_path):
    """Charge un signal depuis un fichier CSV ou JSON.

    Détecte automatiquement la colonne signal et construit l'axe temporel.
    Met à jour etat['signal_brut'], etat['temps'] et etat['fs'].
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        # Détection automatique du séparateur (, ou ;)
        try:
            df = pd.read_csv(file_path, comment="#", sep=",")
            if df.shape[1] < 2:
                df = pd.read_csv(file_path, comment="#", sep=";")
        except Exception:
            df = pd.read_csv(file_path, comment="#", sep=";")

        if df.empty:
            raise ValueError("Fichier CSV vide.")

        col_signal = recherche_colonne(df)

        if col_signal is not None:
            # Cas : colonne contenant des listes encodées
            signaux = []
            for valeur in df[col_signal].dropna():
                parsed = Conversion_chaine_liste(str(valeur))
                if parsed is not None and len(parsed) > 1:
                    signaux.extend(parsed)

            if signaux:
                etat["signal_brut"] = np.asarray(signaux, dtype=float)
                etat["temps"] = np.arange(len(etat["signal_brut"])) / etat["fs"]
                return

            # Cas standard : une valeur par ligne
            etat["signal_brut"] = df[col_signal].to_numpy(dtype=float)
            etat["temps"] = construire_axe_temps(df, len(etat["signal_brut"]))
            return

        # Fallback : toutes colonnes numériques aplaties
        numeric_df = df.select_dtypes(include=np.number)
        if not numeric_df.empty:
            etat["signal_brut"] = numeric_df.to_numpy().flatten()
            etat["temps"] = np.arange(len(etat["signal_brut"])) / etat["fs"]
            return

    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            for cle in ["samples", "signal", "data", "values", "valeur"]:
                if cle in data:
                    etat["signal_brut"] = np.asarray(data[cle], dtype=float)
                    etat["temps"] = np.arange(len(etat["signal_brut"])) / etat["fs"]
                    return

        elif isinstance(data, list):
            etat["signal_brut"] = np.asarray(data, dtype=float)
            etat["temps"] = np.arange(len(etat["signal_brut"])) / etat["fs"]
            return

    raise ValueError("Impossible de détecter automatiquement le signal.")


def generer_signal_test(fs=1000.0, duree=2.0):
    """Génère un signal de test composé de deux sinusoïdes et d'un bruit.

    Composition : 5 Hz + 50 Hz + bruit gaussien (amplitude 0.3).
    Utilisé pour tester l'interface sans fichier externe.
    """
    t = np.arange(0, duree, 1 / fs)
    sig = (np.sin(2 * np.pi * 5 * t)
           + 0.5 * np.sin(2 * np.pi * 50 * t)
           + 0.3 * np.random.randn(len(t)))
    return t, sig

# FONCTIONS DE FILTRAGE 

def filtrer_signal(input_signal, sampling_rate, type_filtre, ordre_filtre,
                   frequence_coupure=None, frequence_basse=None, frequence_haute=None):
    """Applique un filtre Butterworth sur un signal.

    Args:
        input_signal (np.ndarray): Signal à filtrer.
        sampling_rate (float): Fréquence d'échantillonnage en Hz.
        type_filtre (str): "passe_bas", "passe_haut" ou "passe_bande".
        ordre_filtre (int): Ordre du filtre.
        frequence_coupure (float, optional): Fréquence de coupure (passe-bas/haut).
        frequence_basse (float, optional): Fréquence basse (passe-bande).
        frequence_haute (float, optional): Fréquence haute (passe-bande).
    """
    nyquist = sampling_rate / 2

    if type_filtre == "passe_bas":
        if frequence_coupure is None:
            raise ValueError("Il faut donner une fréquence de coupure.")
        frequence_normalisee = frequence_coupure / nyquist
        b, a = butter(ordre_filtre, frequence_normalisee, btype="low")

    elif type_filtre == "passe_haut":
        if frequence_coupure is None:
            raise ValueError("Il faut donner une fréquence de coupure.")
        frequence_normalisee = frequence_coupure / nyquist
        b, a = butter(ordre_filtre, frequence_normalisee, btype="high")

    elif type_filtre == "passe_bande":
        if frequence_basse is None or frequence_haute is None:
            raise ValueError("Il faut donner une fréquence basse et une fréquence haute.")
        frequences_normalisees = [frequence_basse / nyquist, frequence_haute / nyquist]
        b, a = butter(ordre_filtre, frequences_normalisees, btype="band")

    else:
        raise ValueError("Type de filtre inconnu.")

    # lfilter : filtrage causal (un seul passage, introduit un déphasage)
    return lfilter(b, a, input_signal)

def valider_frequences(type_filtre, fc, fc2, nyq):
    """Vérifie que les fréquences respectent le critère de Nyquist.

    Args:
        type_filtre (str): "passe_bas", "passe_haut" ou "passe_bande".
        fc (float): Fréquence de coupure basse (Hz).
        fc2 (float): Fréquence de coupure haute (Hz), pour passe-bande.
        nyq (float): Fréquence de Nyquist = fs / 2 (Hz).
    """
    if fc <= 0:
        raise ValueError("fc doit être > 0 Hz.")
    if fc >= nyq:
        raise ValueError(f"fc ({fc} Hz) doit être < fs/2 ({nyq:.0f} Hz).")
    if type_filtre == "passe_bande":
        if fc2 <= fc:
            raise ValueError("Passe-bande : fc2 doit être > fc.")
        if fc2 >= nyq:
            raise ValueError(f"fc2 ({fc2} Hz) doit être < fs/2 ({nyq:.0f} Hz).")

# FONCTIONS D'ANALYSE 

def Normalisation_signal(signal):
    """Normalise le signal dans l'intervalle [-1 ; 1]."""
    max_abs = np.max(np.abs(signal))
    if max_abs == 0:
        return signal
    return signal / max_abs

def extraction_amp_freq(signal, fs):
    """Calcule l'amplitude maximale et la fréquence dominante d'un signal.

    Utilise la transformée de Fourier rapide (FFT) pour identifier
    la composante fréquentielle la plus puissante.

    Returns:
        dict: {"max_amplitude": float, "dominant_frequency": float}
    """
    max_amplitude = float(np.max(np.abs(signal)))

    N = len(signal)
    yf = np.abs(fft(signal))
    xf = fftfreq(N, 1 / fs)

    # Conserver uniquement les fréquences positives
    masque_positif = xf > 0
    xf = xf[masque_positif]
    yf = yf[masque_positif]

    frequence_dominante = float(xf[np.argmax(yf)])

    return {
        "max_amplitude": max_amplitude,
        "dominant_frequency": frequence_dominante  # clé correcte
    }

# FONCTIONS D'AFFICHAGE 

def mise_a_jour_graph(win):
    """Redessine les deux graphes matplotlib intégrés dans l'interface.

    Graphe haut : signal brut (bleu) et signal filtré (rouge) superposés.
    Graphe bas  : signal filtré seul (rouge).
    Respecte l'état des cases 'Afficher signal brut' et 'Afficher signal filtré'.
    """
    win.ax_haut.clear()
    win.ax_bas.clear()

    # Graphe haut : Signal temporel + signal filtré
    if etat["signal_brut"] is not None and win.check_brut.isChecked():
        win.ax_haut.plot(etat["temps"], etat["signal_brut"],
                         color="#2563EB", linewidth=0.7,
                         label="Signal brut", alpha=0.8)

    if etat["signal_filtre"] is not None and win.check_filtre.isChecked():
        win.ax_haut.plot(etat["temps"], etat["signal_filtre"],
                         color="#DC2626", linewidth=1.3,
                         label="Signal filtré")

    win.ax_haut.set_title("Signal temporel")
    win.ax_haut.set_xlabel("Temps (s)")
    win.ax_haut.set_ylabel("Amplitude")
    win.ax_haut.grid(True, alpha=0.3)

    if etat["signal_brut"] is not None or etat["signal_filtre"] is not None:
        win.ax_haut.legend(loc="upper right", fontsize=9)

    # Graphe bas : signal filtré seul
    if etat["signal_filtre"] is not None:
        win.ax_bas.plot(etat["temps"], etat["signal_filtre"],
                        color="#DC2626", linewidth=1.3)

    win.ax_bas.set_title("Signal filtré seul")
    win.ax_bas.set_xlabel("Temps (s)")
    win.ax_bas.set_ylabel("Amplitude")
    win.ax_bas.grid(True, alpha=0.3)

    win.canvas.draw()


def description_filtre():
    """Retourne une description lisible du filtre actif pour la carte info."""
    m = etat["meta"]
    if m["type"] is None:
        return "—"
    if m["type"] == "passe_bande":
        return f"Passe-bande • N={m['ordre']} • {m['fc']}–{m['fc2']} Hz"
    labels = {"passe_bas": "Passe-bas", "passe_haut": "Passe-haut"}
    return f"{labels.get(m['type'], '—')} • N={m['ordre']} • Fc={m['fc']} Hz"

def Affichage_données(win):
    """Met à jour les quatre blocs d'informations.

    Cartes d'affichage : Fichier, Échantillons, fs (Hz), Filtre actif.
    Si un signal filtré est disponible, affiche aussi la fréquence dominante.
    """
    nom = etat["fichier"].split("/")[-1] if etat["fichier"] else "—"
    win.lbl_fichier["val"].setText(nom)
    win.lbl_echant["val"].setText(
        str(len(etat["signal_brut"])) if etat["signal_brut"] is not None else "—")
    win.lbl_fs["val"].setText(f"{etat['fs']:.0f}")

    # Afficher fréquence dominante si signal filtré disponible
    if etat["signal_filtre"] is not None:
        try:
            stats = extraction_amp_freq(etat["signal_filtre"], etat["fs"])
            fd = stats["dominant_frequency"]  # ← clé corrigée
            win.lbl_filtre["val"].setText(
                f"{description_filtre()}\n fd={fd:.1f} Hz")
        except Exception:
            win.lbl_filtre["val"].setText(description_filtre())
    else:
        win.lbl_filtre["val"].setText(description_filtre())


# FONCTIONS D'EXPORT CSV

def entete_csv():
    """Génère l'en-tête commenté pour le fichier CSV exporté.

    Inclut les métadonnées : source, échantillons, fs, paramètres du filtre.
    """
    m = etat["meta"]
    lignes = [
        "# signal.csv ",
        f"# Source        : {etat['fichier']}",
        f"# Echantillons  : {len(etat['signal_brut'])}",
        f"# fs            : {etat['fs']} Hz",
        f"# Filtre        : {m['type']}",
        f"# Fc            : {m['fc']} Hz",
    ]
    if m["fc2"]:
        lignes.append(f"# Fc2           : {m['fc2']} Hz")
    lignes += [
        f"# Ordre         : {m['ordre']}",
        "# Methode       : Butter + lfilter",
        "#"
    ]
    return "\n".join(lignes) + "\n"


# SLOTS — Connection des boutons de l'interface

def Selection_signal(win):
    """Chargement d'un signal depuis un fichier CSV sélectionné par l'utilisateur.

    Args:
        win (MainApp): Fenêtre principale de l'application.
    """
    chemin, _ = QFileDialog.getOpenFileName(
        win, "Ouvrir un signal", "",
        "Signaux (*.csv *.json);;CSV (*.csv);;JSON (*.json)"
    )
    if not chemin:
        return

    try:
        Charger_signal(chemin)  # ← corrigé : appelle Charger_signal, pas Selection_signal
        # Mettre à jour le slider fc selon la fréquence de Nyquist
        win.slider_fc.setMaximum(int(etat["fs"] / 2))
        win.lbl_fc_max.setText(f"{int(etat['fs']/2)} Hz")
    except Exception as e:
        QMessageBox.critical(win, "Erreur de lecture", str(e))
        return

    etat["signal_filtre"] = None
    etat["fichier"] = chemin
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}

    Affichage_données(win)
    mise_a_jour_graph(win)
    win.statusBar().showMessage("Signal chargé avec succès")


def Générer_signal_test(win):
    """Génère un signal de test et l'affiche dans l'interface.

    Signal composé de : 5 Hz + 50 Hz + bruit gaussien, durée 2s, fs=1000Hz.
    """
    etat["fs"] = 1000.0
    t, sig = generer_signal_test(fs=etat["fs"], duree=2.0)

    etat["signal_brut"] = sig
    etat["temps"] = t
    etat["signal_filtre"] = None
    etat["fichier"] = "signal_test (généré)"
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}

    win.slider_fc.setMaximum(int(etat["fs"] / 2))
    win.lbl_fc_max.setText(f"{int(etat['fs']/2)} Hz")

    Affichage_données(win)
    mise_a_jour_graph(win)
    win.statusBar().showMessage("Signal test généré (5 Hz + 50 Hz + bruit)")


def Appliquer_filtre(win):
    """Applique le filtre sélectionné sur le signal brut chargé.

    Lit les paramètres depuis les widgets (combo_filter, edit_fc, edit_ordre),
    appelle filtrer_signal() du groupe, puis rafraîchit graphe et cartes infos.
    """
    if etat["signal_brut"] is None:
        QMessageBox.warning(win, "Aucun signal",
                            "Chargez ou générez d'abord un signal.")
        return

    # Lecture des paramètres depuis les widgets de l'interface
    type_index = win.combo_filter.currentIndex()
    type_filtre = ["passe_bas", "passe_haut", "passe_bande"][type_index]
    fc    = int(win.edit_fc.text() or win.slider_fc.value())
    ordre = int(win.edit_ordre.text() or win.slider_ordre.value())
    fc2   = min(fc * 3, int(etat["fs"] / 2) - 1)  # fréquence haute auto (passe-bande)
    nyq   = etat["fs"] / 2.0

    # Validation des fréquences avant filtrage
    try:
        valider_frequences(type_filtre, fc, fc2, nyq)
    except ValueError as e:
        QMessageBox.warning(win, "Paramètre invalide", str(e))
        return

    # Application du filtre via la fonction du groupe (filtre_2.py)
    try:
        if type_filtre == "passe_bande":
            etat["signal_filtre"] = filtrer_signal(
                etat["signal_brut"], etat["fs"], type_filtre, ordre,
                frequence_basse=fc, frequence_haute=fc2)
        else:
            etat["signal_filtre"] = filtrer_signal(
                etat["signal_brut"], etat["fs"], type_filtre, ordre,
                frequence_coupure=fc)
    except Exception as e:
        QMessageBox.critical(win, "Erreur de filtrage", str(e))
        return

    etat["meta"] = {
        "type": type_filtre, "fc": fc,
        "fc2": fc2 if type_filtre == "passe_bande" else None,
        "ordre": ordre,
    }

    Affichage_données(win)
    mise_a_jour_graph(win)
    win.statusBar().showMessage(f"Filtre appliqué : {description_filtre()}")


def Reinitialiser(win):
    """Efface le signal filtré et remet les cartes infos à leur état initial."""
    etat["signal_filtre"] = None
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}
    Affichage_données(win)
    mise_a_jour_graph(win)
    win.statusBar().showMessage("Filtre réinitialisé")


def save_csv(win):
    """Exporte le signal filtré dans un fichier CSV avec métadonnées.

    Colonnes exportées : temps, valeur_brute, valeur_filtree.
    Un en-tête commenté contenant les paramètres du filtre est ajouté.
    """
    if etat["signal_filtre"] is None:
        QMessageBox.warning(win, "Aucun signal filtré",
                            "Appliquez d'abord un filtre.")
        return

    chemin, _ = QFileDialog.getSaveFileName(
        win, "Sauvegarder le signal filtré", "signal_filtered.csv", "CSV (*.csv)")
    if not chemin:
        return
    if not chemin.endswith(".csv"):
        chemin += ".csv"

    df = pd.DataFrame({
        "temps":          np.round(etat["temps"], 6),
        "valeur_brute":   np.round(etat["signal_brut"], 6),
        "valeur_filtree": np.round(etat["signal_filtre"], 6),
    })

    try:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(entete_csv())
            df.to_csv(f, index=False)
    except Exception as e:
        QMessageBox.critical(win, "Erreur d'export", str(e))
        return

    QMessageBox.information(win, "Export réussi",
                            f"{len(df)} lignes exportées vers :\n{chemin}")
    win.statusBar().showMessage(f"Exporté : {chemin}")


def Save_graphique(win):
    """Exporte le graphe affiché sous forme d'image PNG ou PDF."""
    if etat["signal_brut"] is None:
        QMessageBox.warning(win, "Rien à sauvegarder", "Aucun graphe affiché.")
        return

    chemin, _ = QFileDialog.getSaveFileName(
        win, "Sauvegarder le graphique", "graphique.png",
        "Image PNG (*.png);;PDF (*.pdf)")
    if not chemin:
        return

    try:
        win.figure.savefig(chemin, dpi=150, bbox_inches="tight")
    except Exception as e:
        QMessageBox.critical(win, "Erreur", str(e))
        return

    win.statusBar().showMessage(f"Graphique sauvegardé : {chemin}")


# Liaison — relie les boutons de l'interface aux fonctions

def connecter_signaux(win):
    """Connexion de chaque widget de l'interface à sa fonction de traitement."""

    # Boutons → fonctions (lambda pour transmettre la référence win)
    win.btn_load.clicked.connect(lambda: Selection_signal(win))
    win.btn_generate.clicked.connect(lambda: Générer_signal_test(win))
    win.btn_apply.clicked.connect(lambda: Appliquer_filtre(win))
    win.btn_reset.clicked.connect(lambda: Reinitialiser(win))
    win.btn_save_csv.clicked.connect(lambda: save_csv(win))
    win.btn_save_plot.clicked.connect(lambda: Save_graphique(win))

    # Synchronisation bidirectionnelle slider ↔ champ texte (fréquence de coupure)
    win.slider_fc.valueChanged.connect(lambda v: win.edit_fc.setText(str(v)))
    win.edit_fc.editingFinished.connect(
        lambda: win.slider_fc.setValue(int(win.edit_fc.text() or 1)))

    # Synchronisation bidirectionnelle slider ↔ champ texte (ordre du filtre)
    win.slider_ordre.valueChanged.connect(
        lambda v: (win.edit_ordre.setText(str(v)), win.lbl_nyq.setText(f"N = {v}")))
    win.edit_ordre.editingFinished.connect(
        lambda: win.slider_ordre.setValue(int(win.edit_ordre.text() or 1)))

    # Cases d'affichage → mise à jour immédiate du graphe
    win.check_brut.stateChanged.connect(lambda _: mise_a_jour_graph(win))
    win.check_filtre.stateChanged.connect(lambda _: mise_a_jour_graph(win))


# POINT D'ENTRÉE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    connecter_signaux(win)
    win.show()
    sys.exit(app.exec_())
