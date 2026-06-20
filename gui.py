"""
Interface graphique — Groupe D.

Szymon, Mame, Sokhna, Ouail — M2 T3I ALTERNANCE 2026

Interface PyQt5 à trois onglets construite au-dessus de
:mod:`classification_backend` :

* **Test** : teste un fichier de nature inconnue, soit par comparaison à la
  base de données (KNN), soit par l'algorithme à seuils.
* **Base de données** : crée des catégories et y importe des fichiers de
  référence.
* **Journal** : affiche toutes les informations pertinentes de traitement.

Les calculs longs sont exécutés dans un fil dédié pendant qu'un spinner
(``loading.png``) tourne à 360°, afin de garder l'interface réactive.
"""

import os
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QTransform
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QLineEdit, QGroupBox,
    QTextEdit, QProgressBar,
)

import classification_backend as backend


# Palette de couleurs réutilisée pour les barres de score par classe.
CLASS_COLORS = [
    "#0d6efd", "#198754", "#ffc107", "#dc3545",
    "#6f42c1", "#fd7e14", "#20c997",
]

# Feuille de style globale pour une interface moderne et claire.
STYLE_SHEET = """
QMainWindow, QWidget { background-color: #f5f7fa; color: #212529; }
QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 8px;
                   background: #ffffff; }
QTabBar::tab { background: #e9ecef; padding: 10px 22px; min-width: 95px;
               border-top-left-radius: 8px; border-top-right-radius: 8px;
               margin-right: 2px; color: #495057; }
QTabBar::tab:selected { background: #ffffff; color: #0d6efd; font-weight: bold; }
QGroupBox { border: 1px solid #dee2e6; border-radius: 8px; margin-top: 12px;
            font-weight: bold; background: #ffffff; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px;
                   color: #0d6efd; }
QPushButton { background-color: #0d6efd; color: white; border: none;
              border-radius: 6px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #0b5ed7; }
QPushButton:disabled { background-color: #adb5bd; }
QLineEdit, QComboBox { border: 1px solid #ced4da; border-radius: 6px;
                       padding: 6px; background: #ffffff; }
QTextEdit { border: 1px solid #dee2e6; border-radius: 6px; background: #ffffff; }
"""


class Worker(QThread):
    """
    Fil d'exécution générique pour déporter un calcul long hors de l'interface.

    Émet ``finished_ok`` avec le résultat en cas de succès, ou ``failed`` avec
    le message d'erreur sinon.
    """

    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, function, *args, **kwargs):
        """
        Prépare le fil avec la fonction à exécuter et ses arguments.

        :param function: fonction à exécuter dans le fil.
        :param args: arguments positionnels transmis à la fonction.
        :param kwargs: arguments nommés transmis à la fonction.
        """
        super().__init__()
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def run(self):
        """
        Exécute la fonction et émet le signal correspondant au résultat.

        :returns: ``None``.
        """
        try:
            result = self._function(*self._args, **self._kwargs)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class SpinnerOverlay(QWidget):
    """
    Voile semi-transparent affichant ``loading.png`` en rotation à 360°.

    Recouvre la fenêtre pendant les calculs longs. Si l'image est absente,
    un simple texte d'attente est affiché à la place.
    """

    def __init__(self, parent=None):
        """
        Construit le voile et son minuteur de rotation.

        :param parent: widget parent recouvert par le voile.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 180);")
        self._angle = 0

        self._pixmap = None
        if backend.LOADING_FILE.exists():
            pix = QPixmap(str(backend.LOADING_FILE))
            if not pix.isNull():
                self._pixmap = pix.scaled(32, 32, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        if self._pixmap is None:
            self._label.setText("Traitement en cours…")
            self._label.setStyleSheet("font-size: 16px; color: #0d6efd;")
        else:
            self._label.setPixmap(self._pixmap)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.hide()

    def _rotate(self):
        """
        Fait pivoter l'image de 30° à chaque tic du minuteur.

        :returns: ``None``.
        """
        if self._pixmap is None:
            return
        self._angle = (self._angle + 30) % 360
        rotated = self._pixmap.transformed(
            QTransform().rotate(self._angle), Qt.SmoothTransformation
        )
        self._label.setPixmap(rotated)

    def resizeEvent(self, event):
        """
        Maintient le label centré lorsque le voile est redimensionné.

        :param event: évènement de redimensionnement Qt.
        :returns: ``None``.
        """
        self._label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def start(self):
        """
        Affiche le voile et démarre la rotation.

        :returns: ``None``.
        """
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()
        self._timer.start(60)

    def stop(self):
        """
        Arrête la rotation et masque le voile.

        :returns: ``None``.
        """
        self._timer.stop()
        self.hide()


class ResultPanel(QGroupBox):
    """
    Panneau de résultat : type détecté, confiance et barres de score par classe.

    Les barres sont générées dynamiquement selon les classes fournies ; seules
    celles dont la confiance est strictement supérieure à 0 % sont affichées.
    """

    def __init__(self, parent=None):
        """
        Construit le panneau de résultat (cartes + zone de barres).

        :param parent: widget parent.
        """
        super().__init__("Résultat", parent)
        layout = QVBoxLayout(self)
        cards = QHBoxLayout()

        self._type_value = self._make_card(cards, "Type détecté", "#cfe2ff", "#084298")
        self._conf_value = self._make_card(cards, "Confiance", "#d1e7dd", "#0f5132")

        self._bars_box = QVBoxLayout()
        bars_title = QLabel("Score par classe (> 0 %)")
        bars_title.setStyleSheet("font-size: 12px; color: #6c757d; font-weight: normal;")
        self._bars_box.addWidget(bars_title)
        bars_container = QWidget()
        bars_container.setLayout(self._bars_box)

        cards.addWidget(bars_container, stretch=2)
        layout.addLayout(cards)

    def _make_card(self, parent_layout, title, bg_color, fg_color):
        """
        Crée une carte d'affichage (titre + grande valeur) et la place dans le layout.

        :param parent_layout: layout horizontal recevant la carte.
        :param title: intitulé affiché en petit.
        :param bg_color: couleur de fond de la carte.
        :param fg_color: couleur du texte.
        :returns: le QLabel de la valeur, pour mise à jour ultérieure.
        """
        card = QWidget()
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 10px;")
        card.setMinimumSize(130, 90)
        box = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(f"color: {fg_color}; font-size: 12px; background: transparent;")
        lbl_value = QLabel("—")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet(
            f"color: {fg_color}; font-size: 24px; font-weight: bold; background: transparent;"
        )
        box.addWidget(lbl_title)
        box.addWidget(lbl_value)
        parent_layout.addWidget(card)
        return lbl_value

    def _clear_bars(self):
        """
        Supprime les barres de score précédemment affichées.

        :returns: ``None``.
        """
        while self._bars_box.count() > 1:  # on garde le titre en position 0
            item = self._bars_box.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def update_result(self, label: str, confidence: float, scores: dict):
        """
        Met à jour les cartes et (re)génère les barres de score par classe.

        :param label: type détecté.
        :param confidence: confiance dans [0, 1].
        :param scores: dictionnaire ``{classe: pourcentage}``.
        :returns: ``None``.
        """
        self._type_value.setText(str(label).capitalize())
        self._conf_value.setText(f"{int(round(confidence * 100))} %")
        self._clear_bars()

        visible = {c: p for c, p in scores.items() if p > 0}
        ordered = sorted(visible.items(), key=lambda kv: kv[1], reverse=True)
        for index, (cls, pct) in enumerate(ordered):
            color = CLASS_COLORS[index % len(CLASS_COLORS)]
            row = QWidget()
            line = QHBoxLayout(row)
            line.setContentsMargins(0, 0, 0, 0)
            name = QLabel(cls.capitalize())
            name.setFixedWidth(80)
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(int(pct))
            bar.setTextVisible(False)
            bar.setFixedHeight(12)
            bar.setStyleSheet(
                f"QProgressBar {{ background:#e9ecef; border-radius:6px; }}"
                f"QProgressBar::chunk {{ background-color:{color}; border-radius:6px; }}"
            )
            pct_label = QLabel(f"{int(pct)} %")
            pct_label.setFixedWidth(45)
            line.addWidget(name)
            line.addWidget(bar)
            line.addWidget(pct_label)
            self._bars_box.addWidget(row)


class InfoBadge(QLabel):
    """
    Petit badge informatif circulaire « i » affichant un message au survol.
    """

    def __init__(self, message: str, parent=None):
        """
        Construit le badge et installe son infobulle.

        :param message: texte affiché au survol de la souris.
        :param parent: widget parent.
        """
        super().__init__("i", parent)
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "background-color: #0dcaf0; color: white; border-radius: 10px;"
            "font-weight: bold; font-style: italic;"
        )
        self.setToolTip(message)


class TestTab(QWidget):
    """
    Onglet de test d'un fichier de nature inconnue (KNN ou algorithmique).
    """

    def __init__(self, spinner: SpinnerOverlay, parent=None):
        """
        Construit l'onglet de test.

        :param spinner: voile de chargement partagé avec la fenêtre principale.
        :param parent: widget parent.
        """
        super().__init__(parent)
        self._spinner = spinner
        self._worker = None
        self._last_result = None
        self._setup_ui()

    def _setup_ui(self):
        """
        Met en place les widgets de l'onglet Test.

        :returns: ``None``.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        file_group = QGroupBox("Échantillon à tester")
        file_row = QHBoxLayout(file_group)
        self._path_label = QLineEdit(str(backend.DEFAULT_SAMPLE))
        self._path_label.setReadOnly(True)
        browse_btn = QPushButton("Parcourir")
        browse_btn.clicked.connect(self._browse_clicked)
        file_row.addWidget(self._path_label, stretch=1)
        file_row.addWidget(browse_btn)
        layout.addWidget(file_group)

        method_group = QGroupBox("Choisir la méthode de classification des données")
        method_layout = QVBoxLayout(method_group)
        buttons_row = QHBoxLayout()

        db_row = QHBoxLayout()
        self._db_btn = QPushButton("Comparer à la base de données")
        self._db_btn.clicked.connect(self._database_clicked)
        badge = InfoBadge("Méthode efficace seulement si la base de données a été complétée.")
        db_row.addWidget(self._db_btn)
        db_row.addWidget(badge)
        db_row.addStretch()

        self._rules_btn = QPushButton("Algorithmique")
        self._rules_btn.setStyleSheet(
            "background-color: #198754; color: white; border: none;"
            "border-radius: 6px; padding: 8px 16px; font-weight: bold;"
        )
        self._rules_btn.clicked.connect(self._rules_clicked)

        buttons_row.addLayout(db_row, stretch=1)
        buttons_row.addWidget(self._rules_btn)
        method_layout.addLayout(buttons_row)
        layout.addWidget(method_group)

        self._result_panel = ResultPanel()
        layout.addWidget(self._result_panel)

        layout.addStretch()

        self._export_btn = QPushButton("Exporter processed_data.csv")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_clicked)
        layout.addWidget(self._export_btn)

    def _browse_clicked(self):
        """
        Ouvre un sélecteur de fichier pour choisir l'échantillon à tester.

        :returns: ``None``.
        """
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier features.csv",
            str(backend.ROOT_DIR), "Fichiers CSV (*.csv)"
        )
        if path:
            self._path_label.setText(path)

    def _database_clicked(self):
        """
        Lance la classification par base de données après contrôle de complétude.

        :returns: ``None``.
        """
        status = backend.database_status()
        if not status["complete"]:
            choice = QMessageBox.question(
                self, "Base incomplète",
                "La base de données semble incomplète, êtes-vous sûr de vouloir continuer ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if choice == QMessageBox.No:
                self._open_path(status["deficient_path"])
                return
        self._run_classification(backend.classify_with_database)

    def _rules_clicked(self):
        """
        Lance la classification algorithmique par seuils.

        :returns: ``None``.
        """
        self._run_classification(backend.classify_by_rules)

    def _open_path(self, path):
        """
        Ouvre l'explorateur de fichiers à l'emplacement indiqué.

        :param path: dossier à ouvrir.
        :returns: ``None``.
        """
        try:
            os.startfile(str(path))
        except Exception as exc:
            QMessageBox.warning(self, "Explorateur", f"Ouverture impossible : {exc}")

    def _run_classification(self, function):
        """
        Exécute une fonction de classification dans un fil, avec spinner.

        :param function: fonction de backend prenant le chemin du fichier.
        :returns: ``None``.
        """
        filepath = self._path_label.text()
        self._set_buttons_enabled(False)
        self._spinner.start()
        self._worker = Worker(function, filepath)
        self._worker.finished_ok.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.start()

    def _on_success(self, result):
        """
        Affiche le résultat de la classification et réactive l'interface.

        :param result: dictionnaire renvoyé par la fonction de classification.
        :returns: ``None``.
        """
        self._spinner.stop()
        self._set_buttons_enabled(True)
        self._last_result = result
        self._result_panel.update_result(
            result["label"], result["confidence"], result["scores"]
        )
        self._export_btn.setEnabled(True)

    def _on_failure(self, message):
        """
        Signale une erreur survenue pendant la classification.

        :param message: message d'erreur à afficher.
        :returns: ``None``.
        """
        self._spinner.stop()
        self._set_buttons_enabled(True)
        QMessageBox.critical(self, "Erreur", message)

    def _set_buttons_enabled(self, enabled):
        """
        Active ou désactive les boutons de méthode pendant un calcul.

        :param enabled: ``True`` pour réactiver les boutons.
        :returns: ``None``.
        """
        self._db_btn.setEnabled(enabled)
        self._rules_btn.setEnabled(enabled)

    def _export_clicked(self):
        """
        Exporte le dernier résultat de classification.

        :returns: ``None``.
        """
        if not self._last_result:
            return
        try:
            backend.export_results(
                self._last_result["row"],
                self._last_result["label"],
                self._last_result["confidence"],
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Export impossible : {exc}")
            return
        QMessageBox.information(self, "Succès", "Export réussi !")


class DatabaseTab(QWidget):
    """
    Onglet de gestion de la base : création de catégories et import de fichiers.
    """

    def __init__(self, spinner: SpinnerOverlay, parent=None):
        """
        Construit l'onglet Base de données.

        :param spinner: voile de chargement partagé.
        :param parent: widget parent.
        """
        super().__init__(parent)
        self._spinner = spinner
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        """
        Met en place les widgets de l'onglet Base de données.

        :returns: ``None``.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        select_group = QGroupBox("Catégorie")
        select_layout = QVBoxLayout(select_group)
        combo_row = QHBoxLayout()
        combo_row.addWidget(QLabel("Type de fichier :"))
        self._combo = QComboBox()
        combo_row.addWidget(self._combo, stretch=1)
        select_layout.addLayout(combo_row)

        add_row = QHBoxLayout()
        self._type_input = QLineEdit()
        self._type_input.setPlaceholderText("Nouveau type (max 10 caractères)")
        self._type_input.setMaxLength(20)
        self._add_btn = QPushButton("Ajouter le type")
        self._add_btn.clicked.connect(self._add_type_clicked)
        add_row.addWidget(self._type_input, stretch=1)
        add_row.addWidget(self._add_btn)
        select_layout.addLayout(add_row)

        self._limit_label = QLabel(f"Limite de {backend.MAX_CATEGORIES} types atteinte.")
        self._limit_label.setStyleSheet("color: #dc3545; font-weight: normal;")
        self._limit_label.setVisible(False)
        select_layout.addWidget(self._limit_label)
        layout.addWidget(select_group)

        info = QLabel("Choisissez un ou plusieurs fichiers de référence "
                      "correspondant au type sélectionné.")
        info.setStyleSheet("color: #6c757d;")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

        load_btn = QPushButton("Charger un fichier de référence")
        load_btn.clicked.connect(self._load_clicked)
        layout.addWidget(load_btn)

    def showEvent(self, event):
        """
        Rafraîchit la liste déroulante à chaque affichage de l'onglet.

        :param event: évènement d'affichage Qt.
        :returns: ``None``.
        """
        super().showEvent(event)
        self.refresh_dropdown()

    def refresh_dropdown(self):
        """
        Recharge la liste des catégories et gère la limite maximale.

        :returns: ``None``.
        """
        categories = backend.get_category_folders()
        self._combo.clear()
        self._combo.addItems(categories)
        at_limit = len(categories) >= backend.MAX_CATEGORIES
        self._add_btn.setEnabled(not at_limit)
        self._limit_label.setVisible(at_limit)

    def _add_type_clicked(self):
        """
        Crée une nouvelle catégorie à partir du champ de saisie.

        :returns: ``None``.
        """
        try:
            backend.add_category(self._type_input.text())
        except ValueError as exc:
            QMessageBox.critical(self, "Erreur", str(exc))
            return
        self._type_input.clear()
        QMessageBox.information(self, "Succès", "Type de fichier ajouté !")
        self.refresh_dropdown()

    def _load_clicked(self):
        """
        Importe un fichier de référence dans la catégorie sélectionnée.

        :returns: ``None``.
        """
        if self._combo.count() == 0:
            QMessageBox.critical(self, "Erreur", "Créez d'abord un type de fichier.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier features.csv",
            str(backend.ROOT_DIR), "Fichiers CSV (*.csv)"
        )
        if not path:
            return
        category = self._combo.currentText()
        self._spinner.start()
        self._worker = Worker(backend.add_reference_file, path, category)
        self._worker.finished_ok.connect(self._on_loaded)
        self._worker.failed.connect(self._on_failure)
        self._worker.start()

    def _on_loaded(self, _result):
        """
        Confirme l'import et la mise à jour de la référence.

        :param _result: chemin du fichier importé (non utilisé ici).
        :returns: ``None``.
        """
        self._spinner.stop()
        QMessageBox.information(self, "Succès", "Fichier chargé et référence mise à jour !")

    def _on_failure(self, message):
        """
        Signale une erreur survenue pendant l'import.

        :param message: message d'erreur.
        :returns: ``None``.
        """
        self._spinner.stop()
        QMessageBox.critical(self, "Erreur", message)


class JournalTab(QWidget):
    """
    Onglet Journal : affiche en temps réel tous les messages de traitement.
    """

    def __init__(self, parent=None):
        """
        Construit l'onglet Journal et s'abonne au journal du backend.

        :param parent: widget parent.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("Journal des traitements")
        title.setStyleSheet("font-weight: bold; color: #0d6efd;")
        layout.addWidget(title)
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        layout.addWidget(self._text)
        clear_btn = QPushButton("Effacer le journal")
        clear_btn.clicked.connect(self._text.clear)
        layout.addWidget(clear_btn)
        backend.register_journal(self.append_message)

    def append_message(self, message: str):
        """
        Ajoute une ligne au journal.

        :param message: message à afficher.
        :returns: ``None``.
        """
        self._text.append(message)


class MainWindow(QMainWindow):
    """
    Fenêtre principale regroupant les trois onglets et le voile de chargement.
    """

    def __init__(self):
        """
        Construit la fenêtre, ses onglets et applique le style.
        """
        super().__init__()
        self.setWindowTitle("Classificateur de type de fichier — Groupe D")
        self.setMinimumSize(720, 640)
        if backend.ICON_FILE.exists():
            self.setWindowIcon(QIcon(str(backend.ICON_FILE)))

        self._spinner = SpinnerOverlay(self)

        tabs = QTabWidget()
        tabs.addTab(TestTab(self._spinner), "Test")
        tabs.addTab(DatabaseTab(self._spinner), "Base de données")
        tabs.addTab(JournalTab(), "Journal")
        self.setCentralWidget(tabs)

    def resizeEvent(self, event):
        """
        Maintient le voile de chargement à la taille de la fenêtre.

        :param event: évènement de redimensionnement Qt.
        :returns: ``None``.
        """
        self._spinner.setGeometry(self.rect())
        super().resizeEvent(event)


def launch() -> None:
    """
    Point d'entrée de l'interface : initialise et lance l'application Qt.

    :returns: ne retourne pas (sort via ``sys.exit``).
    """
    backend.ensure_directories()
    backend.build_reference()
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
