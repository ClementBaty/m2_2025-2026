"""
File Type Classifier — Group D
Szymon, Mame, Sokhna — M2 T3I ALTERNANCE 2026

Receives features.csv from Group C, classifies the file type using KNN
against a local reference database, displays the result in a PyQt5 GUI,
and exports processed_data.csv for Group 5.
"""

import ctypes
import os
import sys
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QLineEdit,
)
from PyQt5.QtGui import QIcon


# ---------------------------------------------------------------------------
# User-configurable constants
# ---------------------------------------------------------------------------

MAX_CATEGORIES = 7

FEATURE_COLUMNS = [
    "fft_magnitude_0", "fft_magnitude_1", "fft_magnitude_2",
    "fft_frequency_0", "fft_frequency_1", "fft_frequency_2",
    "spectral_centroid", "mean", "std_dev", "kurtosis",
    "skewness", "rms",
    "peak_index_0", "peak_index_1", "peak_index_2",
    "peak_amplitude_0", "peak_amplitude_1", "peak_amplitude_2",
]

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent
SAMPLE_DIR = ROOT_DIR / "SAMPLE"
DATABASE_DIR = ROOT_DIR / "DATABASE"
REFERENCE_FILE = DATABASE_DIR / "reference.csv"
DEFAULT_SAMPLE = SAMPLE_DIR / "features.csv"
EXPORT_FILE = ROOT_DIR / "processed_data.csv"

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def get_category_folders() -> list:
    """Return sorted list of category subfolder names inside DATABASE_DIR."""
    if not DATABASE_DIR.exists():
        return []
    return sorted(
        entry.name
        for entry in DATABASE_DIR.iterdir()
        if entry.is_dir()
    )


def build_reference() -> None:
    """Scan all category subfolders and rebuild DATABASE/reference.csv."""
    frames = []
    for category in get_category_folders():
        cat_dir = DATABASE_DIR / category
        for csv_file in sorted(cat_dir.glob("*features.csv")):
            try:
                df = pd.read_csv(csv_file)
                df["label"] = category.upper()
                frames.append(df)
            except Exception as exc:
                print(f"Warning: could not read {csv_file}: {exc}")

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = pd.DataFrame(columns=["label"] + FEATURE_COLUMNS)

    combined.to_csv(REFERENCE_FILE, index=False)


def _count_all_db_files() -> int:
    """Count total indexed features.csv files across all category subfolders."""
    total = 0
    for category in get_category_folders():
        total += len(list((DATABASE_DIR / category).glob("*features.csv")))
    return total


def classify_sample(filepath: str) -> tuple:
    """
    Classify the first row of filepath using KNN against the reference database.

    Returns (label, confidence) where confidence is the fraction of K neighbors
    belonging to the winning label.

    Raises ValueError if the reference database is empty or missing.
    """
    sample_df = pd.read_csv(filepath)
    if len(sample_df) > 1:
        print(f"Warning: {filepath} has {len(sample_df)} rows; only the first row is used.")
    sample_row = sample_df.iloc[[0]]

    if not REFERENCE_FILE.exists():
        raise ValueError("Database is empty. Please load reference files first.")

    ref_df = pd.read_csv(REFERENCE_FILE)
    if ref_df.empty or "label" not in ref_df.columns:
        raise ValueError("Database is empty. Please load reference files first.")

    ref_labels = ref_df["label"].values

    # Determine which feature columns are actually available in both DataFrames
    available_in_ref = [c for c in FEATURE_COLUMNS if c in ref_df.columns]
    available_in_sample = [c for c in FEATURE_COLUMNS if c in sample_row.columns]
    common_cols = [c for c in available_in_ref if c in available_in_sample]

    missing_from_ref = set(FEATURE_COLUMNS) - set(available_in_ref)
    missing_from_sample = set(FEATURE_COLUMNS) - set(available_in_sample)
    if missing_from_ref:
        print(f"Warning: columns missing from reference: {missing_from_ref}")
    if missing_from_sample:
        print(f"Warning: columns missing from sample: {missing_from_sample}")
        # Fill missing columns with 0
        for col in set(available_in_ref) - set(available_in_sample):
            sample_row = sample_row.copy()
            sample_row[col] = 0.0
        common_cols = available_in_ref  # now all ref cols are present in sample

    ref_features = ref_df[common_cols].fillna(0).values
    sample_features = sample_row[common_cols].fillna(0).values

    scaler = StandardScaler()
    ref_scaled = scaler.fit_transform(ref_features)
    sample_scaled = scaler.transform(sample_features)

    total_files = _count_all_db_files()
    k = max(1, 5 + total_files // 10)
    k = min(k, len(ref_scaled))  # cannot exceed available rows

    knn = KNeighborsClassifier(n_neighbors=k, metric="euclidean")
    knn.fit(ref_scaled, ref_labels)

    neighbors_indices = knn.kneighbors(sample_scaled, return_distance=False)[0]
    neighbor_labels = ref_labels[neighbors_indices]

    predicted_label = knn.predict(sample_scaled)[0]
    confidence = float(np.sum(neighbor_labels == predicted_label)) / k

    return predicted_label, round(confidence, 2)


def export_results(filepath: str, label: str, confidence: float) -> None:
    """Write classification results to processed_data.csv in the root folder."""
    df = pd.read_csv(filepath)
    row = df.iloc[0]

    if "sample_id" in df.columns:
        sample_id = row["sample_id"]
    else:
        sample_id = Path(filepath).name

    def get_col(col):
        return row[col] if col in df.columns else float("nan")

    # dominant_frequency_hz: fft_frequency_X where X = argmax(fft_magnitude_X)
    mag_cols = [c for c in ["fft_magnitude_0", "fft_magnitude_1", "fft_magnitude_2"] if c in df.columns]
    freq_cols = [c for c in ["fft_frequency_0", "fft_frequency_1", "fft_frequency_2"] if c in df.columns]
    if mag_cols and freq_cols and len(mag_cols) == len(freq_cols):
        mags = [float(row[c]) for c in mag_cols]
        best_idx = int(np.argmax(mags))
        dominant_frequency_hz = float(row[freq_cols[best_idx]])
    else:
        dominant_frequency_hz = float("nan")

    # energy: sum of fft_magnitude_i^2
    if mag_cols:
        energy = sum(float(row[c]) ** 2 for c in mag_cols)
    else:
        energy = float("nan")

    result_df = pd.DataFrame([{
        "sample_id": sample_id,
        "label": label,
        "confidence": confidence,
        "mean": get_col("mean"),
        "std_dev": get_col("std_dev"),
        "kurtosis": get_col("kurtosis"),
        "skewness": get_col("skewness"),
        "rms": get_col("rms"),
        "dominant_frequency_hz": dominant_frequency_hz,
        "energy": energy,
    }])

    result_df.to_csv(EXPORT_FILE, index=False)


# ---------------------------------------------------------------------------
# GUI — Home tab
# ---------------------------------------------------------------------------


class HomeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_label = None
        self._last_confidence = None
        self._last_filepath = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # --- File selection row ---
        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Sample to test:"))
        self._path_label = QLabel(str(DEFAULT_SAMPLE))
        self._path_label.setWordWrap(True)
        file_row.addWidget(self._path_label, stretch=1)
        browse_btn = QPushButton("BROWSE")
        browse_btn.clicked.connect(self._browse_clicked)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        # --- TEST button ---
        test_btn = QPushButton("TEST")
        test_btn.setFixedHeight(40)
        test_btn.clicked.connect(self._test_clicked)
        layout.addWidget(test_btn)

        # --- Results area ---
        results_group = QVBoxLayout()
        self._type_label = QLabel("File type: ——")
        self._type_label.setEnabled(False)
        self._confidence_label = QLabel("Confidence: ——")
        self._confidence_label.setEnabled(False)
        results_group.addWidget(self._type_label)
        results_group.addWidget(self._confidence_label)
        layout.addLayout(results_group)

        layout.addStretch()

        # --- Export button ---
        self._export_btn = QPushButton("EXPORT RESULTS")
        self._export_btn.setFixedHeight(40)
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_clicked)
        layout.addWidget(self._export_btn)

    def _browse_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select features CSV", str(ROOT_DIR), "CSV files (*.csv)"
        )
        if path:
            self._path_label.setText(path)

    def _test_clicked(self):
        filepath = self._path_label.text()
        try:
            label, confidence = classify_sample(filepath)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File not found:\n{filepath}")
            return
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Classification failed:\n{exc}")
            return

        self._last_label = label
        self._last_confidence = confidence
        self._last_filepath = filepath

        self._type_label.setText(f"File type: {label}")
        self._type_label.setEnabled(True)
        self._confidence_label.setText(f"Confidence: {confidence:.2f}")
        self._confidence_label.setEnabled(True)
        self._export_btn.setEnabled(True)

        QMessageBox.information(self, "Success", "Classification successful!")

    def _export_clicked(self):
        try:
            export_results(self._last_filepath, self._last_label, self._last_confidence)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Export failed: {exc}")
            return
        QMessageBox.information(self, "Success", "Export successful!")


# ---------------------------------------------------------------------------
# GUI — Database tab
# ---------------------------------------------------------------------------


class DatabaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # --- Dropdown row ---
        dropdown_row = QHBoxLayout()
        dropdown_row.addWidget(QLabel("File type:"))
        self._combo = QComboBox()
        dropdown_row.addWidget(self._combo, stretch=1)
        layout.addLayout(dropdown_row)

        # --- Add type row ---
        add_row = QHBoxLayout()
        self._type_input = QLineEdit()
        self._type_input.setPlaceholderText("New file type name (max 10 chars)")
        self._type_input.setMaxLength(20)
        add_row.addWidget(self._type_input, stretch=1)
        self._add_btn = QPushButton("ADD FILE TYPE")
        self._add_btn.clicked.connect(self._add_type_clicked)
        add_row.addWidget(self._add_btn)
        layout.addLayout(add_row)

        # --- Limit label ---
        self._limit_label = QLabel(f"Maximum limit of {MAX_CATEGORIES} file types reached.")
        self._limit_label.setStyleSheet("color: red;")
        self._limit_label.setVisible(False)
        layout.addWidget(self._limit_label)

        layout.addStretch()

        # --- Info label ---
        self._info_label = QLabel(f"Choose one or multiple reference files corresponding to the selected file type.")
        self._info_label.setStyleSheet("color: black;")
        self._info_label.setVisible(True)
        layout.addWidget(self._info_label)

        layout.addStretch()

        # --- Load button ---
        load_btn = QPushButton("LOAD")
        load_btn.setFixedHeight(40)
        load_btn.clicked.connect(self._load_clicked)
        layout.addWidget(load_btn)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_dropdown()

    def refresh_dropdown(self):
        categories = get_category_folders()
        self._combo.clear()
        self._combo.addItems(categories)

        at_limit = len(categories) >= MAX_CATEGORIES
        self._add_btn.setEnabled(not at_limit)
        self._limit_label.setVisible(at_limit)

    def _add_type_clicked(self):
        name = self._type_input.text().strip().upper()
        if not name:
            return
        if len(name) > 10:
            QMessageBox.critical(self, "Error", "The name is limited to 10 characters.")
            return
        os.makedirs(DATABASE_DIR / name, exist_ok=True)
        self._type_input.clear()
        QMessageBox.information(self, "Success", "File type added successfully!")
        self.refresh_dropdown()

    def _load_clicked(self):
        if self._combo.count() == 0:
            QMessageBox.critical(self, "Error", "Please select or create a file type first.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select features CSV", str(ROOT_DIR), "CSV files (*.csv)"
        )
        if not path:
            return

        category = self._combo.currentText()
        cat_dir = DATABASE_DIR / category
        existing = list(cat_dir.glob("*features.csv"))
        index = len(existing) + 1
        dest = cat_dir / f"{index}features.csv"
        shutil.copy2(path, dest)

        build_reference()

        QMessageBox.information(self, "Success", "File loaded and reference updated!")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Type Classifier — Group D")
        self.setMinimumSize(600, 500)
        icon_path = ROOT_DIR / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        tabs = QTabWidget()
        tabs.addTab(HomeTab(), "Home")
        tabs.addTab(DatabaseTab(), "Database")
        self.setCentralWidget(tabs)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("group4.filetypeclassifier")

    for d in [SAMPLE_DIR, DATABASE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    build_reference()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
