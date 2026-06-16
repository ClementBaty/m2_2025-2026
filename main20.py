"""
main.py
=======
Point d'entrée et logique applicative — Équipe B
Importe l'interface depuis interface.py, définit toutes les fonctions
de traitement (chargement, filtrage, export) et connecte les boutons
aux fonctions correspondantes.

Lancement :
    python main.py

Dépendances :
    pip install pyqt5 matplotlib scipy numpy pandas
"""

import sys
import json
import numpy as np
import pandas as pd
from scipy import signal as sp_signal
from scipy.io import wavfile

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from interface import MainApp


# ═════════════════════════════════════════════════════════════════════════
# ÉTAT GLOBAL DE L'APPLICATION
# ═════════════════════════════════════════════════════════════════════════
# On regroupe l'état dans un dictionnaire pour éviter les variables
# globales éparpillées. Toutes les fonctions ci-dessous le lisent/modifient.

etat = {
    "signal_brut":   None,   # np.ndarray
    "signal_filtre": None,   # np.ndarray
    "temps":         None,   # np.ndarray (s)
    "fs":            1000.0, # fréquence d'échantillonnage (Hz)
    "fichier":       None,   # str — chemin du fichier chargé
    "meta": {                # métadonnées du dernier filtre appliqué
        "type": None, "fc": None, "fc2": None, "ordre": None
    },
}


# ═════════════════════════════════════════════════════════════════════════
# FONCTIONS DE LECTURE DE FICHIERS
# ═════════════════════════════════════════════════════════════════════════

def lire_csv(chemin):
    """Lit un CSV avec détection automatique du séparateur (, ou ;)."""
    try:
        df = pd.read_csv(chemin, comment="#", sep=",")
        if df.shape[1] < 2:
            df = pd.read_csv(chemin, comment="#", sep=";")
    except Exception:
        df = pd.read_csv(chemin, comment="#", sep=";")
    if df.empty:
        raise ValueError("Fichier CSV vide.")
    return df


def lire_json(chemin):
    """Lit un JSON (liste d'objets ou dictionnaire de listes)."""
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("Fichier JSON vide.")
    return df


def detecter_colonne_signal(df):
    """Retourne le nom de la colonne contenant les valeurs du signal."""
    for nom in ["valeur", "signal", "amplitude", "value", "data", "y"]:
        low = {c.lower(): c for c in df.columns}
        if nom in low:
            return low[nom]
    num = df.select_dtypes(include=[np.number]).columns.tolist()
    return num[1] if len(num) >= 2 else (num[0] if num else None)


def construire_axe_temps(df, n):
    """
    Retourne l'axe temporel en secondes.
    Met à jour etat['fs'] si une colonne temps est trouvée.
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
    return np.arange(n) / etat["fs"]


def charger_depuis_dataframe(df):
    """Extrait signal_brut et temps depuis un DataFrame, met à jour l'état."""
    col = detecter_colonne_signal(df)
    if col is None:
        raise ValueError(f"Colonne signal introuvable. Colonnes : {list(df.columns)}")
    etat["signal_brut"] = df[col].to_numpy(dtype=float)
    etat["temps"] = construire_axe_temps(df, len(etat["signal_brut"]))


def lire_wav(chemin):
    """Lit un fichier WAV et met à jour l'état (mono, normalisé)."""
    fs, data = wavfile.read(chemin)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(float)
    m = np.max(np.abs(data))
    if m > 0:
        data = data / m
    etat["fs"] = float(fs)
    etat["signal_brut"] = data
    etat["temps"] = np.arange(len(data)) / etat["fs"]


# ═════════════════════════════════════════════════════════════════════════
# FONCTIONS DE FILTRAGE (Butterworth)
# ═════════════════════════════════════════════════════════════════════════

def valider_frequences(type_filtre, fc, fc2, nyq):
    """Lève ValueError si les fréquences violent le critère de Nyquist."""
    if fc <= 0:
        raise ValueError("fc doit être > 0 Hz.")
    if fc >= nyq:
        raise ValueError(f"fc ({fc} Hz) doit être < fs/2 ({nyq:.0f} Hz).")
    if type_filtre == "passe_bande":
        if fc2 <= fc:
            raise ValueError("Passe-bande : fc2 doit être > fc.")
        if fc2 >= nyq:
            raise ValueError(f"fc2 ({fc2} Hz) doit être < fs/2 ({nyq:.0f} Hz).")


def appliquer_butterworth(data, type_filtre, fc, fc2, ordre, nyq):
    """
    Construit et applique un filtre Butterworth avec filtfilt
    (zéro déphasage).

    type_filtre : "passe_bas" | "passe_haut" | "passe_bande"
    """
    if type_filtre == "passe_bas":
        b, a = sp_signal.butter(ordre, fc / nyq, btype="low")
    elif type_filtre == "passe_haut":
        b, a = sp_signal.butter(ordre, fc / nyq, btype="high")
    elif type_filtre == "passe_bande":
        b, a = sp_signal.butter(ordre, [fc / nyq, fc2 / nyq], btype="band")
    else:
        raise ValueError(f"Type de filtre inconnu : {type_filtre}")
    return sp_signal.filtfilt(b, a, data)


def generer_signal_test(fs=1000.0, duree=2.0):
    """Génère un signal de test : 5 Hz + 50 Hz + bruit."""
    t = np.arange(0, duree, 1 / fs)
    sig = (np.sin(2 * np.pi * 5 * t)
           + 0.5 * np.sin(2 * np.pi * 50 * t)
           + 0.3 * np.random.randn(len(t)))
    return t, sig


# ═════════════════════════════════════════════════════════════════════════
# FONCTIONS D'AFFICHAGE (mise à jour des graphes / infos)
# ═════════════════════════════════════════════════════════════════════════

def update_graph(win):
    """Redessine les deux graphes selon l'état et les cases cochées."""
    win.ax_haut.clear()
    win.ax_bas.clear()

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

    if etat["signal_filtre"] is not None:
        win.ax_bas.plot(etat["temps"], etat["signal_filtre"],
                        color="#DC2626", linewidth=1.3)
    win.ax_bas.set_title("Signal filtré seul")
    win.ax_bas.set_xlabel("Temps (s)")
    win.ax_bas.set_ylabel("Amplitude")
    win.ax_bas.grid(True, alpha=0.3)

    win.canvas.draw()


def description_filtre():
    """Retourne une description lisible du filtre actif."""
    m = etat["meta"]
    if m["type"] is None:
        return "—"
    if m["type"] == "passe_bande":
        return f"Passe-bande • N={m['ordre']} • {m['fc']}–{m['fc2']} Hz"
    labels = {"passe_bas": "Passe-bas", "passe_haut": "Passe-haut"}
    return f"{labels.get(m['type'], '—')} • N={m['ordre']} • Fc={m['fc']} Hz"


def maj_infos(win):
    """Met à jour les 4 cartes d'information (Fichier, Échantillons, fs, Filtre)."""
    nom = etat["fichier"].split("/")[-1] if etat["fichier"] else "—"
    win.lbl_fichier["val"].setText(nom)
    win.lbl_echant["val"].setText(
        str(len(etat["signal_brut"])) if etat["signal_brut"] is not None else "—")
    win.lbl_fs["val"].setText(f"{etat['fs']:.0f}")
    win.lbl_filtre["val"].setText(description_filtre())


def entete_csv():
    """Génère les lignes de commentaires (#) pour l'export CSV."""
    m = etat["meta"]
    lignes = [
        "# signal_filtered.csv — équipe B",
        f"# Source        : {etat['fichier']}",
        f"# Echantillons  : {len(etat['signal_brut'])}",
        f"# fs            : {etat['fs']} Hz",
        f"# Filtre        : {m['type']}",
        f"# Fc            : {m['fc']} Hz",
    ]
    if m["fc2"]:
        lignes.append(f"# Fc2           : {m['fc2']} Hz")
    lignes += [f"# Ordre         : {m['ordre']}",
               "# Methode       : Butterworth + filtfilt (zero-phase)", "#"]
    return "\n".join(lignes) + "\n"


# ═════════════════════════════════════════════════════════════════════════
# SLOTS — connectés aux boutons de l'interface
# ═════════════════════════════════════════════════════════════════════════

def on_load_signal(win):
    """Bouton 'Charger signal' → ouvre .csv / .json / .wav."""
    chemin, _ = QFileDialog.getOpenFileName(
        win, "Ouvrir un signal", "",
        "Signaux (*.csv *.json *.wav);;CSV (*.csv);;JSON (*.json);;WAV (*.wav)"
    )
    if not chemin:
        return

    try:
        if chemin.endswith(".csv"):
            charger_depuis_dataframe(lire_csv(chemin))
        elif chemin.endswith(".json"):
            charger_depuis_dataframe(lire_json(chemin))
        elif chemin.endswith(".wav"):
            lire_wav(chemin)
            win.slider_fc.setMaximum(int(etat["fs"] / 2))
            win.lbl_fc_max.setText(f"{int(etat['fs']/2)} Hz")
        else:
            raise ValueError("Format non supporté.")
    except Exception as e:
        QMessageBox.critical(win, "Erreur de lecture", str(e))
        return

    etat["signal_filtre"] = None
    etat["fichier"] = chemin
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}

    maj_infos(win)
    update_graph(win)
    win.statusBar().showMessage("Signal chargé avec succès")


def on_generate_test(win):
    """Bouton 'Générer signal test' → signal 5 Hz + 50 Hz + bruit."""
    etat["fs"] = 1000.0
    t, sig = generer_signal_test(fs=etat["fs"], duree=2.0)

    etat["signal_brut"] = sig
    etat["temps"] = t
    etat["signal_filtre"] = None
    etat["fichier"] = "signal_test (généré)"
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}

    win.slider_fc.setMaximum(int(etat["fs"] / 2))
    win.lbl_fc_max.setText(f"{int(etat['fs']/2)} Hz")

    maj_infos(win)
    update_graph(win)
    win.statusBar().showMessage("Signal test généré (5 Hz + 50 Hz + bruit)")


def on_apply_filter(win):
    """Bouton 'Appliquer filtre' → Butterworth selon combo_filter / sliders."""
    if etat["signal_brut"] is None:
        QMessageBox.warning(win, "Aucun signal",
                            "Chargez ou générez d'abord un signal.")
        return

    type_index = win.combo_filter.currentIndex()
    type_filtre = ["passe_bas", "passe_haut", "passe_bande"][type_index]
    fc    = int(win.edit_fc.text() or win.slider_fc.value())
    ordre = int(win.edit_ordre.text() or win.slider_ordre.value())
    fc2   = min(fc * 3, int(etat["fs"] / 2) - 1)  # 2e coupure auto (passe-bande)
    nyq   = etat["fs"] / 2.0

    try:
        valider_frequences(type_filtre, fc, fc2, nyq)
    except ValueError as e:
        QMessageBox.warning(win, "Paramètre invalide", str(e))
        return

    try:
        etat["signal_filtre"] = appliquer_butterworth(
            etat["signal_brut"], type_filtre, fc, fc2, ordre, nyq)
    except Exception as e:
        QMessageBox.critical(win, "Erreur de filtrage", str(e))
        return

    etat["meta"] = {
        "type": type_filtre, "fc": fc,
        "fc2": fc2 if type_filtre == "passe_bande" else None,
        "ordre": ordre,
    }

    maj_infos(win)
    update_graph(win)
    win.statusBar().showMessage(f"Filtre appliqué : {description_filtre()}")


def on_reset(win):
    """Bouton 'Réinitialiser' → efface le signal filtré."""
    etat["signal_filtre"] = None
    etat["meta"] = {"type": None, "fc": None, "fc2": None, "ordre": None}
    maj_infos(win)
    update_graph(win)
    win.statusBar().showMessage("Filtre réinitialisé")


def on_save_csv(win):
    """Bouton 'Sauvegarder CSV' → exporte signal_filtered.csv avec métadonnées."""
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


def on_save_plot(win):
    """Bouton 'Sauvegarder graphique' → export PNG / PDF."""
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


# ═════════════════════════════════════════════════════════════════════════
# CONNEXIONS — relie les boutons/widgets de l'interface aux fonctions
# ═════════════════════════════════════════════════════════════════════════

def connecter_signaux(win):
    """Connecte chaque widget de l'interface à sa fonction de traitement."""

    # Boutons → fonctions (via lambda pour passer win)
    win.btn_load.clicked.connect(lambda: on_load_signal(win))
    win.btn_generate.clicked.connect(lambda: on_generate_test(win))
    win.btn_apply.clicked.connect(lambda: on_apply_filter(win))
    win.btn_reset.clicked.connect(lambda: on_reset(win))
    win.btn_save_csv.clicked.connect(lambda: on_save_csv(win))
    win.btn_save_plot.clicked.connect(lambda: on_save_plot(win))

    # Synchronisation sliders ↔ champs texte (fréquence de coupure)
    win.slider_fc.valueChanged.connect(
        lambda v: win.edit_fc.setText(str(v)))
    win.edit_fc.editingFinished.connect(
        lambda: win.slider_fc.setValue(int(win.edit_fc.text() or 1)))

    # Synchronisation sliders ↔ champs texte (ordre du filtre)
    win.slider_ordre.valueChanged.connect(
        lambda v: (win.edit_ordre.setText(str(v)), win.lbl_nyq.setText(f"N = {v}")))
    win.edit_ordre.editingFinished.connect(
        lambda: win.slider_ordre.setValue(int(win.edit_ordre.text() or 1)))

    # Cases d'affichage → redessiner le graphe
    win.check_brut.stateChanged.connect(lambda _: update_graph(win))
    win.check_filtre.stateChanged.connect(lambda _: update_graph(win))


# ═════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    connecter_signaux(win)
    win.show()
    sys.exit(app.exec_())
