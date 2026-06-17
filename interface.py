from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox,
    QFileDialog, QTextEdit, QProgressBar
)
from PyQt5.QtCore import Qt
import sys

app = QApplication(sys.argv)

fenetre = QMainWindow()
fenetre.setWindowTitle("Groupe D — Traitement et Classification")
fenetre.setMinimumSize(850, 700)

central = QWidget()
fenetre.setCentralWidget(central)
layout_principal = QVBoxLayout(central)
layout_principal.setSpacing(10)

# ── ETAPE 1 ──────────────────────────────────
groupe1 = QGroupBox("1. Charger le fichier features.csv du Groupe C")
layout1 = QHBoxLayout(groupe1)
label_fichier = QLabel("Aucun fichier sélectionné")
label_fichier.setStyleSheet("color: gray;")
btn_charger = QPushButton("Charger features.csv")
label_format = QLabel("format : .csv")
label_format.setStyleSheet("color: gray; font-size: 11px;")
layout1.addWidget(label_fichier, stretch=3)
layout1.addWidget(btn_charger)
layout1.addWidget(label_format)

# ── ETAPE 2 ──────────────────────────────────
groupe2 = QGroupBox("2. Traitement des données")
layout2 = QHBoxLayout(groupe2)
btn_traiter = QPushButton("Lancer le traitement")
btn_traiter.setStyleSheet("background-color: #fff3cd; color: #856404; border: 1px solid #ffc107;")
label_traitement = QLabel("Lecture et analyse du signal")
label_traitement.setStyleSheet("color: gray;")
layout2.addWidget(btn_traiter)
layout2.addWidget(label_traitement, stretch=2)

# ── ETAPE 3 ──────────────────────────────────
groupe3 = QGroupBox("3. Classification")
layout3 = QHBoxLayout(groupe3)
btn_classifier = QPushButton("Lancer la classification")
btn_classifier.setStyleSheet("background-color: #d1e7dd; color: #0f5132; border: 1px solid #0f5132;")
label_classif = QLabel("Identifie le type du signal : audio / vidéo / image / bruit")
label_classif.setStyleSheet("color: gray;")
layout3.addWidget(btn_classifier)
layout3.addWidget(label_classif, stretch=2)

# ── JOURNAL ───────────────────────────────────
groupe_journal = QGroupBox("Journal")
layout_journal = QVBoxLayout(groupe_journal)
journal = QTextEdit()
journal.setReadOnly(True)
journal.setMaximumHeight(90)
journal.setStyleSheet("font-family: Courier; font-size: 12px;")
layout_journal.addWidget(journal)

# ── RESULTAT ──────────────────────────────────
groupe_res = QGroupBox("Résultat")
layout_res = QVBoxLayout(groupe_res)
ligne_res = QHBoxLayout()

# Carte type détecté
carte_type = QWidget()
carte_type.setStyleSheet("background-color: #cfe2ff; border-radius: 10px;")
carte_type.setMinimumSize(120, 90)
layout_carte_type = QVBoxLayout(carte_type)
label_titre_type = QLabel("Type détecté")
label_titre_type.setAlignment(Qt.AlignCenter)
label_titre_type.setStyleSheet("color: #084298; font-size: 12px; background: transparent;")
label_type = QLabel("—")
label_type.setAlignment(Qt.AlignCenter)
label_type.setStyleSheet("color: #084298; font-size: 24px; font-weight: bold; background: transparent;")
layout_carte_type.addWidget(label_titre_type)
layout_carte_type.addWidget(label_type)

# Carte confiance
carte_conf = QWidget()
carte_conf.setStyleSheet("background-color: #d1e7dd; border-radius: 10px;")
carte_conf.setMinimumSize(120, 90)
layout_carte_conf = QVBoxLayout(carte_conf)
label_titre_conf = QLabel("Confiance")
label_titre_conf.setAlignment(Qt.AlignCenter)
label_titre_conf.setStyleSheet("color: #0f5132; font-size: 12px; background: transparent;")
label_conf = QLabel("—")
label_conf.setAlignment(Qt.AlignCenter)
label_conf.setStyleSheet("color: #0f5132; font-size: 24px; font-weight: bold; background: transparent;")
layout_carte_conf.addWidget(label_titre_conf)
layout_carte_conf.addWidget(label_conf)

# Barres de score par classe
widget_barres = QWidget()
layout_barres = QVBoxLayout(widget_barres)
label_detail = QLabel("Score par classe")
label_detail.setStyleSheet("font-size: 12px; color: gray;")

def creer_barre(nom, couleur, couleur_pct):
    ligne = QHBoxLayout()
    lbl = QLabel(nom)
    lbl.setFixedWidth(45)
    barre = QProgressBar()
    barre.setMaximum(100)
    barre.setValue(0)
    barre.setStyleSheet(f"QProgressBar::chunk {{ background-color: {couleur}; }}")
    barre.setTextVisible(False)
    barre.setFixedHeight(10)
    lbl_pct = QLabel("0%")
    lbl_pct.setFixedWidth(35)
    lbl_pct.setStyleSheet(f"color: {couleur_pct};")
    ligne.addWidget(lbl)
    ligne.addWidget(barre)
    ligne.addWidget(lbl_pct)
    return ligne, barre, lbl_pct

ligne_audio, barre_audio, lbl_audio_pct = creer_barre("Audio", "#0d6efd", "#084298")
ligne_video, barre_video, lbl_video_pct = creer_barre("Vidéo", "#198754", "#0f5132")
ligne_image, barre_image, lbl_image_pct = creer_barre("Image", "#ffc107", "#856404")
ligne_bruit, barre_bruit, lbl_bruit_pct = creer_barre("Bruit", "#dc3545", "#842029")

layout_barres.addWidget(label_detail)
layout_barres.addLayout(ligne_audio)
layout_barres.addLayout(ligne_video)
layout_barres.addLayout(ligne_image)
layout_barres.addLayout(ligne_bruit)

ligne_res.addWidget(carte_type)
ligne_res.addWidget(carte_conf)
ligne_res.addWidget(widget_barres, stretch=2)

btn_exporter = QPushButton("Exporter processed_data.csv")
layout_res.addLayout(ligne_res)
layout_res.addWidget(btn_exporter)

layout_principal.addWidget(groupe1)
layout_principal.addWidget(groupe2)
layout_principal.addWidget(groupe3)
layout_principal.addWidget(groupe_journal)
layout_principal.addWidget(groupe_res)

# ═════════════════════════════════════════════
# VARIABLES GLOBALES
# ═════════════════════════════════════════════

fichier_csv = None
donnees     = None
resultat    = None  # label et confiance du signal unique

# ═════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═════════════════════════════════════════════

def get_val(row, *noms):
    """Cherche une valeur dans la ligne en essayant plusieurs noms de colonnes."""
    for nom in noms:
        if nom in row.index:
            try:
                return float(row[nom])
            except:
                pass
    return 0.0

def calculer_scores(row):
    """
    Calcule un score entre 0 et 1 pour chaque classe.
    Basé sur l'arbre de décision du prof.
    Retourne un dictionnaire {classe: score}.
    """
    std      = get_val(row, "std_dev", "std")
    kurtosis = get_val(row, "kurtosis")
    centroid = get_val(row, "spectral_centroid", "dominant_frequency_hz", "dominant_frequency")
    rms      = get_val(row, "rms", "rms_energy")
    skewness = get_val(row, "skewness")
    mag2     = get_val(row, "fft_magnitude_2")

    scores = {"audio": 0.0, "video": 0.0, "image": 0.0, "bruit": 0.0}

    # ── Score AUDIO ──────────────────────────
    # centroïde dans zone audible + magnitude FFT forte
    if centroid > 800:
        scores["audio"] += 0.5
    if centroid > 1500:
        scores["audio"] += 0.2
    if mag2 > 0.5:
        scores["audio"] += 0.2
    if 0.05 < std < 0.25:
        scores["audio"] += 0.1

    # ── Score VIDÉO ──────────────────────────
    # forte variation temporelle + énergie élevée
    if std > 0.20:
        scores["video"] += 0.4
    if rms > 0.40:
        scores["video"] += 0.3
    if std > 0.25:
        scores["video"] += 0.2
    if skewness < 0.5:
        scores["video"] += 0.1

    # ── Score IMAGE ──────────────────────────
    # signal quasi-plat ou centroïde très bas
    if std < 0.05:
        scores["image"] += 0.5
    if centroid < 500:
        scores["image"] += 0.3
    if kurtosis > 4:
        scores["image"] += 0.1
    if rms < 0.10:
        scores["image"] += 0.1

    # ── Score BRUIT ──────────────────────────
    # kurtosis élevé = pics impulsifs
    if kurtosis > 6:
        scores["bruit"] += 0.6
    if skewness > 1:
        scores["bruit"] += 0.2
    if std > 0.30 and centroid > 3000:
        scores["bruit"] += 0.2

    # Normaliser entre 0 et 100
    total = sum(scores.values())
    if total == 0:
        total = 1
    for k in scores:
        scores[k] = round(scores[k] / total * 100)

    return scores

# ═════════════════════════════════════════════
# FONCTIONS DES BOUTONS
# ═════════════════════════════════════════════

def charger_fichier():
    global fichier_csv
    fichier, _ = QFileDialog.getOpenFileName(
        fenetre, "Charger features.csv", "", "CSV (*.csv)"
    )
    if fichier:
        fichier_csv = fichier
        nom = fichier.split("/")[-1]
        label_fichier.setText(nom)
        label_fichier.setStyleSheet("color: black;")
        journal.append("→ Fichier chargé : " + nom)

def traiter():
    global donnees
    if fichier_csv is None:
        journal.append("⚠ Chargez d'abord un fichier CSV !")
        return
    import pandas as pd
    donnees = pd.read_csv(fichier_csv)
    journal.append("✓ Signal chargé — " + str(len(donnees)) + " ligne(s) détectée(s)")
    journal.append("✓ Colonnes : " + ", ".join(donnees.columns.tolist()))
    journal.append("✓ Normalisation terminée")

def classifier():
    global donnees, resultat
    if donnees is None:
        journal.append("⚠ Lancez d'abord le traitement !")
        return

    journal.append("→ Classification en cours...")

    # Prendre la première ligne = le signal unique
    row = donnees.iloc[0]

    # Calculer les scores pour chaque classe
    scores = calculer_scores(row)

    # Trouver le meilleur
    meilleur = max(scores, key=scores.get)
    conf     = scores[meilleur]

    # Sauvegarder pour export
    resultat = {
        "sample_id": row.get("sample_id", 0) if "sample_id" in row.index else 0,
        "label":     meilleur,
        "confidence": round(conf / 100, 2),
        "mean":      get_val(row, "mean"),
        "std_dev":   get_val(row, "std_dev", "std"),
        "kurtosis":  get_val(row, "kurtosis"),
        "skewness":  get_val(row, "skewness"),
        "rms":       get_val(row, "rms", "rms_energy"),
        "dominant_frequency_hz": get_val(row, "spectral_centroid",
                                         "dominant_frequency_hz",
                                         "dominant_frequency"),
        "energy":    round(get_val(row, "rms", "rms_energy") ** 2, 6),
    }

    # Mettre à jour l'interface
    label_type.setText(meilleur.capitalize())
    label_conf.setText(str(conf) + "%")

    barre_audio.setValue(scores["audio"])
    barre_video.setValue(scores["video"])
    barre_image.setValue(scores["image"])
    barre_bruit.setValue(scores["bruit"])
    lbl_audio_pct.setText(str(scores["audio"]) + "%")
    lbl_video_pct.setText(str(scores["video"]) + "%")
    lbl_image_pct.setText(str(scores["image"]) + "%")
    lbl_bruit_pct.setText(str(scores["bruit"]) + "%")

    journal.append("✓ Classification terminée !")
    journal.append("→ Type détecté : " + meilleur.upper() +
                   " avec " + str(conf) + "% de confiance")

def exporter():
    global resultat
    if resultat is None:
        journal.append("⚠ Classifiez d'abord le signal !")
        return
    import pandas as pd
    df_out = pd.DataFrame([resultat])
    df_out.to_csv("C:/Users/E068531/processed_data.csv", index=False)
    journal.append("✓ processed_data.csv exporté dans C:/Users/E068531/")

# ── Connexion des boutons ─────────────────────
btn_charger.clicked.connect(charger_fichier)
btn_traiter.clicked.connect(traiter)
btn_classifier.clicked.connect(classifier)
btn_exporter.clicked.connect(exporter)

fenetre.show()
app.exec_()