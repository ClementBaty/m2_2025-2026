"""
interface.py
============
Squelette de l'interface graphique — Équipe B
Contient UNIQUEMENT la construction visuelle (widgets, layouts, styles).
Aucune logique de traitement ici : tout est branché depuis main.py.

Ne pas modifier ce fichier pour ajouter de la logique métier —
ajouter les fonctions / connexions dans main.py.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSlider, QLineEdit, QLabel, QCheckBox,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QIntValidator

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


# ═════════════════════════════════════════════════════════════════════════
class MainApp(QMainWindow):
# ═════════════════════════════════════════════════════════════════════════
    """
    Fenêtre principale — interface uniquement.

    Widgets exposés (utilisés par main.py) :
        Boutons      : btn_load, btn_generate, btn_apply, btn_reset,
                       btn_save_csv, btn_save_plot
        Filtre       : combo_filter, slider_fc, edit_fc,
                       slider_ordre, edit_ordre
        Affichage    : check_brut, check_filtre
        Graphe       : figure, canvas, ax_haut, ax_bas
        Cartes infos : lbl_fichier, lbl_echant, lbl_fs, lbl_filtre
                       (chacune = dict {"frame":..., "val": QLabel})
        Bornes UI    : lbl_fc_min, lbl_fc_max, lbl_nyq
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filtrage de signal")
        self.resize(1300, 820)
        self._build_ui()
        self._reset_axes()

    # ──────────────────────────────────────────────────────────────────────
    # CONSTRUCTION DE L'INTERFACE
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ╔══════════════ PANNEAU GAUCHE (contrôles) ══════════════╗
        panneau = QWidget()
        panneau.setFixedWidth(370)
        panneau.setStyleSheet("background:#FFFFFF;border-right:1px solid #E2E5EA;")
        pl = QVBoxLayout(panneau)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(10)

        # — Section SIGNAL —
        pl.addWidget(self._titre("SIGNAL"))
        self.btn_load = self._bouton("📁  Charger signal")
        self.btn_generate = self._bouton("〰  Générer signal test")
        pl.addWidget(self.btn_load)
        pl.addWidget(self.btn_generate)

        # — Section TYPE DE FILTRE —
        pl.addSpacing(8)
        pl.addWidget(self._titre("TYPE DE FILTRE"))
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Passe-bas", "Passe-haut", "Passe-bande"])
        self.combo_filter.setStyleSheet(
            "QComboBox{padding:8px 12px;border:1px solid #D5D9DF;border-radius:6px;"
            "font-size:14px;background:#fff;}"
        )
        pl.addWidget(self.combo_filter)

        # — Fréquence de coupure —
        pl.addSpacing(8)
        pl.addWidget(self._titre("FRÉQUENCE DE COUPURE (Hz)"))
        fc_row = QHBoxLayout()
        self.slider_fc = QSlider(Qt.Horizontal)
        self.slider_fc.setMinimum(1)
        self.slider_fc.setMaximum(22050)
        self.slider_fc.setValue(1000)
        self.edit_fc = QLineEdit("1000")
        self.edit_fc.setValidator(QIntValidator(1, 22050))
        self.edit_fc.setFixedWidth(70)
        self.edit_fc.setAlignment(Qt.AlignCenter)
        self.edit_fc.setStyleSheet(self._style_edit())
        fc_row.addWidget(self.slider_fc)
        fc_row.addWidget(self.edit_fc)
        fc_row.addWidget(QLabel("Hz"))
        pl.addLayout(fc_row)

        bornes = QHBoxLayout()
        self.lbl_fc_min = QLabel("1 Hz")
        self.lbl_fc_max = QLabel("22050 Hz")
        self.lbl_nyq    = QLabel("N = 2")
        for l in (self.lbl_fc_min, self.lbl_fc_max, self.lbl_nyq):
            l.setStyleSheet("color:#8A929E;font-size:11px;")
        bornes.addWidget(self.lbl_fc_min)
        bornes.addStretch()
        bornes.addWidget(self.lbl_fc_max)
        bornes.addStretch()
        bornes.addWidget(self.lbl_nyq)
        pl.addLayout(bornes)

        # — Ordre du filtre —
        pl.addSpacing(8)
        pl.addWidget(self._titre("ORDRE DU FILTRE"))
        ord_row = QHBoxLayout()
        self.slider_ordre = QSlider(Qt.Horizontal)
        self.slider_ordre.setMinimum(1)
        self.slider_ordre.setMaximum(10)
        self.slider_ordre.setValue(2)
        self.edit_ordre = QLineEdit("2")
        self.edit_ordre.setValidator(QIntValidator(1, 10))
        self.edit_ordre.setFixedWidth(70)
        self.edit_ordre.setAlignment(Qt.AlignCenter)
        self.edit_ordre.setStyleSheet(self._style_edit())
        ord_row.addWidget(self.slider_ordre)
        ord_row.addWidget(self.edit_ordre)
        pl.addLayout(ord_row)

        ord_bornes = QHBoxLayout()
        lmin, lmax = QLabel("1"), QLabel("10")
        for l in (lmin, lmax):
            l.setStyleSheet("color:#8A929E;font-size:11px;")
        ord_bornes.addWidget(lmin)
        ord_bornes.addStretch()
        ord_bornes.addWidget(lmax)
        pl.addLayout(ord_bornes)

        # — Boutons d'action —
        pl.addSpacing(12)
        self.btn_apply = self._bouton("▶  Appliquer filtre", primary=True)
        self.btn_reset = self._bouton("↻  Réinitialiser")
        self.btn_save_csv = self._bouton("💾  Sauvegarder CSV")
        self.btn_save_plot = self._bouton("🖼  Sauvegarder graphique")
        pl.addWidget(self.btn_apply)
        pl.addWidget(self.btn_reset)
        pl.addWidget(self.btn_save_csv)
        pl.addWidget(self.btn_save_plot)

        # — Affichage —
        pl.addSpacing(10)
        pl.addWidget(self._titre("AFFICHAGE"))
        self.check_brut = QCheckBox("Afficher signal brut")
        self.check_filtre = QCheckBox("Afficher signal filtré")
        self.check_brut.setChecked(True)
        self.check_filtre.setChecked(True)
        for c in (self.check_brut, self.check_filtre):
            c.setStyleSheet("font-size:13px;color:#3A414C;")
        pl.addWidget(self.check_brut)
        pl.addWidget(self.check_filtre)

        pl.addStretch()
        root.addWidget(panneau)

        # ╔══════════════ PANNEAU DROIT (graphes) ══════════════╗
        droite = QWidget()
        droite.setStyleSheet("background:#FFFFFF;")
        dl = QVBoxLayout(droite)
        dl.setContentsMargins(20, 16, 20, 12)
        dl.setSpacing(10)

        # Figure à 2 sous-graphes (signal temporel + filtré seul)
        self.figure = Figure(figsize=(10, 7), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax_haut = self.figure.add_subplot(211)   # brut + filtré superposés
        self.ax_bas  = self.figure.add_subplot(212)   # filtré seul
        dl.addWidget(self.canvas, stretch=1)

        # — Barre d'infos (4 cartes) —
        infos = QHBoxLayout()
        infos.setSpacing(12)
        self.lbl_fichier = self._carte_info("📁", "Fichier", "—")
        self.lbl_echant  = self._carte_info("〰", "Échantillons", "—")
        self.lbl_fs      = self._carte_info("🕐", "fs (Hz)", "—")
        self.lbl_filtre  = self._carte_info("⧩", "Filtre actif", "—")
        for c in (self.lbl_fichier, self.lbl_echant, self.lbl_fs, self.lbl_filtre):
            infos.addWidget(c["frame"])
        dl.addLayout(infos)

        root.addWidget(droite, stretch=1)

        # — Barre de statut —
        self.statusBar().showMessage("Prêt")
        self.statusBar().setStyleSheet("color:#5A6472;font-size:12px;")

    # ──────────────────────────────────────────────────────────────────────
    # GRAPHE — état initial (purement visuel)
    # ──────────────────────────────────────────────────────────────────────

    def _reset_axes(self):
        """Remet les deux graphes dans leur état vide initial."""
        for ax in (self.ax_haut, self.ax_bas):
            ax.clear()
            ax.grid(True, alpha=0.3)
            ax.set_xlabel("Temps (s)")
            ax.set_ylabel("Amplitude")
        self.ax_haut.set_title("Signal temporel")
        self.ax_bas.set_title("Signal filtré seul")
        self.canvas.draw()

    # ──────────────────────────────────────────────────────────────────────
    # HELPERS DE CONSTRUCTION VISUELLE
    # ──────────────────────────────────────────────────────────────────────

    def _titre(self, texte):
        l = QLabel(texte)
        l.setStyleSheet(
            "color:#6B7280;font-size:11px;font-weight:600;letter-spacing:1px;"
        )
        return l

    def _bouton(self, texte, primary=False):
        b = QPushButton(texte)
        b.setMinimumHeight(44)
        b.setCursor(Qt.PointingHandCursor)
        if primary:
            b.setStyleSheet(
                "QPushButton{background:#2563EB;color:#fff;border:none;"
                "border-radius:6px;font-size:14px;font-weight:600;}"
                "QPushButton:hover{background:#1D4ED8;}"
            )
        else:
            b.setStyleSheet(
                "QPushButton{background:#fff;color:#374151;"
                "border:1px solid #D5D9DF;border-radius:6px;font-size:14px;}"
                "QPushButton:hover{background:#F3F4F6;}"
            )
        return b

    def _style_edit(self):
        return ("QLineEdit{border:1px solid #D5D9DF;border-radius:6px;"
                "padding:6px;font-size:14px;background:#fff;}")

    def _carte_info(self, icone, titre, valeur):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;}"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        ttl = QLabel(f"{icone}  {titre}")
        ttl.setStyleSheet("color:#6B7280;font-size:12px;font-weight:600;border:none;")
        val = QLabel(valeur)
        val.setStyleSheet("color:#111827;font-size:13px;border:none;")
        lay.addWidget(ttl)
        lay.addWidget(val)
        return {"frame": frame, "val": val}
