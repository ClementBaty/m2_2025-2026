"""
Signal Analysis Dashboard with three real PyQt5 tabs.

Run:
    python way.py

Integrated:
- Existing anomaly dashboard
- Existing FFT/time-series logic
- SBS feature selection
- 3D plot using the best 3 separating axes
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from scipy.fft import fft, fftfreq


FS = 8_000
DURATION = 0.02
PLOTS_DIR = "plots"

REQUIRED_COLUMNS = [
    "sample_id",
    "label",
    "confidence",
    "mean",
    "std_dev",
    "kurtosis",
    "skewness",
    "rms",
    "dominant_frequency_hz",
    "energy",
]

EXPORT_COLUMNS = [
    "sample_id",
    "label",
    "confidence",
    "fft_plot_path",
    "time_series_plot_path",
    "is_anomaly",
    "anomaly_reason",
]

FEATURE_COLUMNS = [
    "confidence",
    "mean",
    "std_dev",
    "kurtosis",
    "skewness",
    "rms",
    "dominant_frequency_hz",
    "energy",
]

DEMO_DF = pd.DataFrame(
    [
        {
            "sample_id": 0,
            "label": "audio",
            "confidence": 0.95,
            "mean": 0.0001,
            "std_dev": 0.12,
            "kurtosis": 3.2,
            "skewness": 0.05,
            "rms": 0.08,
            "dominant_frequency_hz": 440.0,
            "energy": 0.08,
        },
        {
            "sample_id": 1,
            "label": "audio",
            "confidence": 0.92,
            "mean": 0.0002,
            "std_dev": 0.11,
            "kurtosis": 3.1,
            "skewness": 0.04,
            "rms": 0.07,
            "dominant_frequency_hz": 440.0,
            "energy": 0.07,
        },
        {
            "sample_id": 2,
            "label": "noise",
            "confidence": 0.88,
            "mean": 0.0003,
            "std_dev": 0.13,
            "kurtosis": 3.3,
            "skewness": 0.06,
            "rms": 0.09,
            "dominant_frequency_hz": 1000.0,
            "energy": 0.01,
        },
        {
            "sample_id": 3,
            "label": "audio",
            "confidence": 0.97,
            "mean": 0.0001,
            "std_dev": 0.10,
            "kurtosis": 3.0,
            "skewness": 0.03,
            "rms": 0.10,
            "dominant_frequency_hz": 880.0,
            "energy": 0.10,
        },
    ]
)


@dataclass
class AnomalyThresholds:
    """Thresholds used to classify a sample as clean or anomaly."""

    confidence_min: float = 0.90
    frequency_max_hz: float = 900.0
    rms_max: float = 0.50
    kurtosis_max: float = 6.0


class SignalAnalyzer:
    """Signal analysis logic."""

    def __init__(self) -> None:
        self.thresholds = AnomalyThresholds()

    def apply_thresholds(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Apply anomaly thresholds to a dataframe."""
        self.validate_dataframe(df_raw)
        results = []

        for _, row in df_raw.iterrows():
            reasons = []

            if (
                row["confidence"] < self.thresholds.confidence_min
                and row["dominant_frequency_hz"]
                > self.thresholds.frequency_max_hz
            ):
                reasons.append("Low confidence and high frequency noise")

            if row["rms"] > self.thresholds.rms_max:
                reasons.append("RMS amplitude too high")

            if row["kurtosis"] > self.thresholds.kurtosis_max:
                reasons.append("Abnormal kurtosis")

            if row["energy"] < 0.001:
                reasons.append("Suspiciously low energy")

            sample_id = int(row["sample_id"])
            result = row.to_dict()
            result.update(
                {
                    "fft_plot_path": f"{PLOTS_DIR}/fft_{sample_id}.png",
                    "time_series_plot_path": (
                        f"{PLOTS_DIR}/time_series_{sample_id}.png"
                    ),
                    "is_anomaly": bool(reasons),
                    "anomaly_reason": "; ".join(reasons),
                }
            )
            results.append(result)

        return pd.DataFrame(results)

    @staticmethod
    def make_time_series(row: pd.Series) -> tuple[np.ndarray, np.ndarray]:
        """Generate a synthetic time-domain signal."""
        t = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
        amplitude = float(row["rms"]) * np.sqrt(2)
        frequency = float(row["dominant_frequency_hz"])
        signal = float(row["mean"]) + amplitude * np.sin(
            2 * np.pi * frequency * t
        )
        return t, signal

    @classmethod
    def make_fft(cls, row: pd.Series) -> tuple[np.ndarray, np.ndarray]:
        """Compute FFT amplitude spectrum."""
        _, signal = cls.make_time_series(row)
        n_points = len(signal)
        yf = np.abs(fft(signal))[: n_points // 2] * 2 / n_points
        xf = fftfreq(n_points, 1 / FS)[: n_points // 2]
        return xf, yf

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """Check required input columns."""
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError("Missing columns: " + ", ".join(missing))

    @staticmethod
    def standardize_features(X: np.ndarray) -> np.ndarray:
        """
        Standardize features without sklearn.

        This is important because features such as energy and frequency
        can have bigger numerical values than RMS or mean.
        """

        mean = X.mean(axis=0)
        std = X.std(axis=0)

        std[std == 0] = 1.0

        return (X - mean) / std

    @staticmethod
    def j_score(X_list: list[np.ndarray]) -> float:
        """
        Compute a Fisher-like separability score.

        High J means:
        - class centers are far from each other
        - points inside each class are compact
        """

        class_means = np.array([Xi.mean(axis=0) for Xi in X_list])
        global_mean = class_means.mean(axis=0)

        inter = np.sum((class_means - global_mean) ** 2)

        intra = 0.0
        for Xi, class_mean in zip(X_list, class_means):
            intra += np.sum((Xi - class_mean) ** 2)

        if intra == 0:
            return 0.0

        return inter / intra

    def choose_best_3_features_sbs(self, df: pd.DataFrame) -> list[str]:
        """
        Choose the best 3 existing columns for 3D class separation using SBS.

        Important:
        - It does not calculate new signal features.
        - It only uses the columns already available in the loaded CSV.
        """

        available_features = [
            col
            for col in FEATURE_COLUMNS
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
        ]

        if len(available_features) < 3:
            raise ValueError(
                "At least 3 numeric features are required for the 3D SBS plot."
            )

        if "label" not in df.columns:
            raise ValueError("Column 'label' is required for SBS separation.")

        clean_df = df.dropna(subset=available_features + ["label"]).copy()

        labels = sorted(clean_df["label"].astype(str).unique())

        if len(labels) < 2:
            raise ValueError("At least 2 different labels are required for SBS.")

        X_raw = clean_df[available_features].to_numpy(float)
        X_scaled = self.standardize_features(X_raw)

        scaled_df = pd.DataFrame(X_scaled, columns=available_features)
        scaled_df["label"] = clean_df["label"].astype(str).to_numpy()

        X_classes = [
            scaled_df[scaled_df["label"] == label][available_features]
            .to_numpy(float)
            for label in labels
        ]

        selected = list(range(len(available_features)))

        while len(selected) > 3:
            best_score = -1.0
            best_remove = None

            for feature_index in selected:
                keep = [idx for idx in selected if idx != feature_index]

                score = self.j_score([Xi[:, keep] for Xi in X_classes])

                if score > best_score:
                    best_score = score
                    best_remove = feature_index

            selected.remove(best_remove)

        return [available_features[idx] for idx in selected]


class PlotCanvas(FigureCanvas):
    """Matplotlib canvas without tight_layout warning."""

    def __init__(self, width: float = 4.5, height: float = 3.0) -> None:
        self.figure = Figure(figsize=(width, height), dpi=100)
        super().__init__(self.figure)
        self.setMinimumHeight(250)

    def get_axis(self, title: str, projection: Optional[str] = None):
        """Clear figure and return an axis."""
        self.figure.clear()

        axis = self.figure.add_subplot(111, projection=projection)
        axis.set_title(title, fontsize=10, fontweight="bold")
        axis.grid(True, alpha=0.25)

        if projection == "3d":
            self.figure.subplots_adjust(
                left=0.02,
                right=0.98,
                bottom=0.05,
                top=0.88,
            )
        else:
            self.figure.subplots_adjust(
                left=0.14,
                right=0.96,
                bottom=0.20,
                top=0.86,
            )

        return axis

    def draw_empty(self, title: str = "") -> None:
        """Draw empty chart."""
        axis = self.get_axis(title)
        axis.text(0.5, 0.5, "No data loaded", ha="center", va="center")
        axis.set_xticks([])
        axis.set_yticks([])
        self.draw_idle()


class MetricCard(QFrame):
    """Simple metric card."""

    def __init__(self, title: str) -> None:
        super().__init__()

        self.title_label = QLabel(title)
        self.value_label = QLabel("--")
        self.sub_label = QLabel("")

        self.title_label.setObjectName("metricTitle")
        self.value_label.setObjectName("metricValue")
        self.sub_label.setObjectName("metricSub")
        self.setObjectName("metricCard")

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.sub_label)
        layout.addStretch()

    def set_value(self, value: str, sub: str = "") -> None:
        """Update card value."""
        self.value_label.setText(value)
        self.sub_label.setText(sub)


class MainWindow(QMainWindow):
    """Main window with three real tabs."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Signal Analysis Dashboard")
        self.resize(1320, 820)

        self.analyzer = SignalAnalyzer()
        self.raw_df: Optional[pd.DataFrame] = None
        self.results_df: Optional[pd.DataFrame] = None

        self.build_ui()
        self.connect_signals()
        self.apply_style()
        self.draw_empty_plots()

    def build_ui(self) -> None:
        """Build the main interface."""

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(14, 12, 14, 14)
        root_layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Signal Analysis Dashboard")
        title.setObjectName("appTitle")

        subtitle = QLabel("Upload processed_data.csv/json → analyze → export results")
        subtitle.setObjectName("appSubtitle")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.status_label = QLabel("● Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        root_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        root_layout.addWidget(self.tabs, stretch=1)

        self.tab_data = QWidget()
        self.tab_charts = QWidget()
        self.tab_samples = QWidget()

        self.tabs.addTab(self.tab_data, "1  Data / Settings")
        self.tabs.addTab(self.tab_charts, "2  Dashboard Charts")
        self.tabs.addTab(self.tab_samples, "3  Samples / Details")

        self.build_data_tab()
        self.build_charts_tab()
        self.build_samples_tab()

    def build_data_tab(self) -> None:
        """Build first tab: data and settings only."""

        layout = QVBoxLayout(self.tab_data)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        io_group = QGroupBox("Input / Output")
        io_layout = QHBoxLayout(io_group)

        self.btn_load = QPushButton("Load CSV / JSON")
        self.btn_demo = QPushButton("Load demo data")
        self.btn_export = QPushButton("Export analysis_results.csv")
        self.btn_export.setEnabled(False)

        expected = QLabel(
            "Expected columns: sample_id · label · confidence · mean · std_dev · "
            "kurtosis · skewness · rms · dominant_frequency_hz · energy"
        )
        expected.setObjectName("hintLabel")

        io_layout.addWidget(self.btn_load)
        io_layout.addWidget(self.btn_demo)
        io_layout.addWidget(self.btn_export)
        io_layout.addStretch()
        io_layout.addWidget(expected)

        layout.addWidget(io_group)

        threshold_group = QGroupBox("Anomaly thresholds")
        threshold_grid = QGridLayout(threshold_group)

        self.slider_conf = self.make_slider(50, 100, 90)
        self.slider_freq = self.make_slider(200, 4000, 900)
        self.slider_rms = self.make_slider(10, 200, 50)
        self.slider_kurt = self.make_slider(20, 120, 60)

        self.label_conf_value = QLabel("0.90")
        self.label_freq_value = QLabel("900 Hz")
        self.label_rms_value = QLabel("0.50")
        self.label_kurt_value = QLabel("6.0")

        self.add_slider_row(
            threshold_grid,
            0,
            "Confidence min",
            self.label_conf_value,
            self.slider_conf,
        )
        self.add_slider_row(
            threshold_grid,
            1,
            "Frequency max",
            self.label_freq_value,
            self.slider_freq,
        )
        self.add_slider_row(
            threshold_grid,
            2,
            "RMS max",
            self.label_rms_value,
            self.slider_rms,
        )
        self.add_slider_row(
            threshold_grid,
            3,
            "Kurtosis max",
            self.label_kurt_value,
            self.slider_kurt,
        )

        layout.addWidget(threshold_group)

        metrics_group = QGroupBox("Summary metrics")
        metrics_layout = QGridLayout(metrics_group)

        self.metric_total = MetricCard("Total samples")
        self.metric_anomalies = MetricCard("Anomalies")
        self.metric_confidence = MetricCard("Avg confidence")
        self.metric_labels = MetricCard("Label split")

        metrics_layout.addWidget(self.metric_total, 0, 0)
        metrics_layout.addWidget(self.metric_anomalies, 0, 1)
        metrics_layout.addWidget(self.metric_confidence, 0, 2)
        metrics_layout.addWidget(self.metric_labels, 0, 3)

        layout.addWidget(metrics_group)
        layout.addStretch()

    def build_charts_tab(self) -> None:
        """Build second tab: dashboard charts only."""

        layout = QGridLayout(self.tab_charts)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.plot_conf = PlotCanvas()
        self.plot_freq = PlotCanvas()
        self.plot_sbs_3d = PlotCanvas()
        self.plot_labels = PlotCanvas()

        layout.addWidget(
            self.chart_group("Confidence per sample", self.plot_conf),
            0,
            0,
        )
        layout.addWidget(
            self.chart_group("Dominant frequency", self.plot_freq),
            0,
            1,
        )
        layout.addWidget(
            self.chart_group("Best 3D separation using SBS", self.plot_sbs_3d),
            1,
            0,
        )
        layout.addWidget(
            self.chart_group("Label breakdown", self.plot_labels),
            1,
            1,
        )

    def build_samples_tab(self) -> None:
        """Build third tab: table and details only."""

        layout = QVBoxLayout(self.tab_samples)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        table_group = QGroupBox("Sample table")
        table_layout = QVBoxLayout(table_group)

        filter_layout = QHBoxLayout()

        self.combo_label = QComboBox()
        self.combo_label.addItem("All labels", "all")

        self.combo_status = QComboBox()
        self.combo_status.addItem("All samples", "all")
        self.combo_status.addItem("Anomalies only", "true")
        self.combo_status.addItem("Clean only", "false")

        filter_layout.addWidget(QLabel("Label:"))
        filter_layout.addWidget(self.combo_label)
        filter_layout.addSpacing(18)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.combo_status)
        filter_layout.addStretch()

        table_layout.addLayout(filter_layout)

        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(
            [
                "#",
                "Label",
                "Confidence",
                "Freq (Hz)",
                "RMS",
                "Energy",
                "Kurtosis",
                "Status",
                "Reason",
                "Detail",
            ]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        table_layout.addWidget(self.table)
        layout.addWidget(table_group, stretch=2)

        detail_group = QGroupBox("Sample detail")
        detail_layout = QVBoxLayout(detail_group)

        self.detail_title = QLabel("Select a row to show signal details.")
        self.detail_title.setObjectName("detailTitle")

        self.detail_stats = QLabel("")
        self.detail_stats.setWordWrap(True)

        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_stats)

        detail_plots_layout = QGridLayout()

        self.plot_time = PlotCanvas(height=2.4)
        self.plot_fft = PlotCanvas(height=2.4)

        detail_plots_layout.addWidget(
            self.chart_group("Time-domain signal", self.plot_time),
            0,
            0,
        )
        detail_plots_layout.addWidget(
            self.chart_group("FFT spectrum", self.plot_fft),
            0,
            1,
        )

        detail_layout.addLayout(detail_plots_layout)
        layout.addWidget(detail_group, stretch=2)

    @staticmethod
    def make_slider(minimum: int, maximum: int, value: int) -> QSlider:
        """Create horizontal slider."""
        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        return slider

    @staticmethod
    def add_slider_row(
        grid: QGridLayout,
        row: int,
        title: str,
        value_label: QLabel,
        slider: QSlider,
    ) -> None:
        """Add one slider row."""
        name_label = QLabel(title)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        grid.addWidget(name_label, row, 0)
        grid.addWidget(value_label, row, 1)
        grid.addWidget(slider, row, 2)
        grid.setColumnStretch(2, 1)

    @staticmethod
    def chart_group(title: str, canvas: PlotCanvas) -> QGroupBox:
        """Put plot canvas inside group box."""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(canvas)
        return group

    def connect_signals(self) -> None:
        """Connect widgets to methods."""

        self.btn_load.clicked.connect(self.load_file)
        self.btn_demo.clicked.connect(self.load_demo_data)
        self.btn_export.clicked.connect(self.export_results)

        self.slider_conf.valueChanged.connect(self.update_thresholds)
        self.slider_freq.valueChanged.connect(self.update_thresholds)
        self.slider_rms.valueChanged.connect(self.update_thresholds)
        self.slider_kurt.valueChanged.connect(self.update_thresholds)

        self.combo_label.currentIndexChanged.connect(self.update_table)
        self.combo_status.currentIndexChanged.connect(self.update_table)

        self.table.itemSelectionChanged.connect(self.show_selected_sample)

    def apply_style(self) -> None:
        """Apply stylesheet."""

        self.setStyleSheet(
            """
            QMainWindow {
                background: #f8f9fa;
            }

            QLabel#appTitle {
                font-size: 25px;
                font-weight: 700;
                color: #111827;
            }

            QLabel#appSubtitle,
            QLabel#hintLabel {
                color: #6b7280;
                font-size: 12px;
            }

            QLabel#statusLabel {
                color: #166534;
                font-size: 13px;
            }

            QTabWidget#mainTabs::pane {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                top: -1px;
            }

            QTabBar::tab {
                background: #e5e7eb;
                color: #111827;
                padding: 12px 28px;
                margin-right: 4px;
                border: 1px solid #d1d5db;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                min-width: 170px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                color: #0f766e;
                border-top: 3px solid #0f766e;
            }

            QGroupBox {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                margin-top: 10px;
                padding: 12px;
                background: #ffffff;
                font-weight: 600;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QPushButton {
                padding: 8px 13px;
                border: 1px solid #d1d5db;
                border-radius: 7px;
                background: #ffffff;
            }

            QPushButton:hover {
                background: #f3f4f6;
            }

            QPushButton:disabled {
                color: #9ca3af;
                background: #f9fafb;
            }

            QFrame#metricCard {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                min-height: 90px;
            }

            QLabel#metricTitle {
                color: #6b7280;
                font-size: 12px;
            }

            QLabel#metricValue {
                color: #111827;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#metricSub {
                color: #6b7280;
                font-size: 11px;
            }

            QLabel#detailTitle {
                font-size: 16px;
                font-weight: 700;
            }

            QTableWidget {
                background: #ffffff;
                alternate-background-color: #f9fafb;
                gridline-color: #e5e7eb;
            }

            QHeaderView::section {
                background: #f3f4f6;
                padding: 7px;
                border: 1px solid #d1d5db;
                font-weight: 600;
            }
            """
        )

    def draw_empty_plots(self) -> None:
        """Initialize plots."""

        self.plot_conf.draw_empty("Confidence per sample")
        self.plot_freq.draw_empty("Dominant frequency")
        self.plot_sbs_3d.draw_empty("Best 3D separation using SBS")
        self.plot_labels.draw_empty("Label breakdown")
        self.plot_time.draw_empty("Time-domain signal")
        self.plot_fft.draw_empty("FFT spectrum")

    def load_file(self) -> None:
        """Load CSV or JSON file."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load processed data",
            "",
            "Data files (*.csv *.json);;CSV files (*.csv);;JSON files (*.json)",
        )

        if not file_path:
            return

        try:
            path = Path(file_path)

            if path.suffix.lower() == ".csv":
                df_raw = pd.read_csv(path)
            elif path.suffix.lower() == ".json":
                df_raw = pd.read_json(path)
            else:
                raise ValueError("Please select a CSV or JSON file.")

            SignalAnalyzer.validate_dataframe(df_raw)

            self.raw_df = df_raw
            self.status_label.setText(f"● Loaded: {path.name}")

            self.reprocess_all()

        except Exception as exc:
            QMessageBox.critical(self, "Load error", str(exc))

    def load_demo_data(self) -> None:
        """Load demo dataframe."""

        self.raw_df = DEMO_DF.copy()
        self.status_label.setText("● Demo data loaded")
        self.reprocess_all()

    def export_results(self) -> None:
        """Export results CSV."""

        if self.results_df is None or self.results_df.empty:
            QMessageBox.warning(self, "No data", "Load data before exporting.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export analysis results",
            "analysis_results.csv",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            self.results_df[EXPORT_COLUMNS].to_csv(file_path, index=False)
            self.status_label.setText("● Results exported")
        except Exception as exc:
            QMessageBox.critical(self, "Export error", str(exc))

    def update_thresholds(self) -> None:
        """Update thresholds from sliders."""

        conf = self.slider_conf.value() / 100
        freq = float(self.slider_freq.value())
        rms = self.slider_rms.value() / 100
        kurt = self.slider_kurt.value() / 10

        self.label_conf_value.setText(f"{conf:.2f}")
        self.label_freq_value.setText(f"{freq:.0f} Hz")
        self.label_rms_value.setText(f"{rms:.2f}")
        self.label_kurt_value.setText(f"{kurt:.1f}")

        self.analyzer.thresholds = AnomalyThresholds(
            confidence_min=conf,
            frequency_max_hz=freq,
            rms_max=rms,
            kurtosis_max=kurt,
        )

        if self.raw_df is not None:
            self.reprocess_all()

    def reprocess_all(self) -> None:
        """Reprocess data, save FFT PNG plots, and update all tabs."""

        if self.raw_df is None:
            return

        try:
            self.results_df = self.analyzer.apply_thresholds(self.raw_df)
            self.btn_export.setEnabled(True)

            self.save_fft_plot_files()

            self.update_label_filter_values()
            self.update_metrics()
            self.update_charts()
            self.update_table()

        except Exception as exc:
            QMessageBox.critical(self, "Processing error", str(exc))

    def save_fft_plot_files(self) -> None:
        """Save one FFT PNG file for every sample in the results dataframe."""

        if self.results_df is None or self.results_df.empty:
            return

        plots_path = Path(PLOTS_DIR)
        plots_path.mkdir(parents=True, exist_ok=True)

        for _, row in self.results_df.iterrows():
            sample_id = int(row["sample_id"])
            fft_path = plots_path / f"fft_{sample_id}.png"
            self.save_fft_png(row, fft_path)

    def save_fft_png(self, row: pd.Series, file_path: Path) -> None:
        """Save one FFT spectrum as a PNG file."""

        xf, yf = self.analyzer.make_fft(row)

        figure = Figure(figsize=(7.0, 4.0), dpi=120)
        axis = figure.add_subplot(111)

        axis.plot(xf, yf, linewidth=1.4)
        axis.fill_between(xf, yf, alpha=0.15)
        axis.axvline(
            float(row["dominant_frequency_hz"]),
            linestyle="--",
            linewidth=1,
        )

        axis.set_title(f"FFT spectrum - Sample {int(row['sample_id'])}")
        axis.set_xlabel("Frequency (Hz)")
        axis.set_ylabel("Amplitude")
        axis.grid(True, alpha=0.25)

        figure.subplots_adjust(
            left=0.12,
            right=0.96,
            bottom=0.16,
            top=0.88,
        )

        figure.savefig(file_path)
        figure.clear()

    def update_label_filter_values(self) -> None:
        """Refresh label combo box."""

        if self.results_df is None:
            return

        current_value = self.combo_label.currentData()
        labels = sorted(str(label) for label in self.results_df["label"].unique())

        self.combo_label.blockSignals(True)
        self.combo_label.clear()
        self.combo_label.addItem("All labels", "all")

        for label in labels:
            self.combo_label.addItem(label, label)

        index = self.combo_label.findData(current_value)
        self.combo_label.setCurrentIndex(index if index >= 0 else 0)
        self.combo_label.blockSignals(False)

    def update_metrics(self) -> None:
        """Update metric cards."""

        if self.results_df is None or self.results_df.empty:
            return

        df = self.results_df
        total = len(df)
        anomalies = int(df["is_anomaly"].sum())
        avg_conf = df["confidence"].mean() * 100
        label_counts = df["label"].value_counts()
        label_text = " / ".join(f"{k}: {v}" for k, v in label_counts.items())

        self.metric_total.set_value(str(total), "in dataset")
        self.metric_anomalies.set_value(
            str(anomalies),
            f"{(anomalies / total) * 100:.0f}% of samples",
        )
        self.metric_confidence.set_value(f"{avg_conf:.1f}%", "across all samples")
        self.metric_labels.set_value(label_text, "label split")

    def update_charts(self) -> None:
        """Update dashboard charts."""

        if self.results_df is None or self.results_df.empty:
            self.draw_empty_plots()
            return

        df = self.results_df
        samples = [f"S{int(i)}" for i in df["sample_id"]]
        colors_status = [
            "#ef4444" if value else "#3b82f6" for value in df["is_anomaly"]
        ]

        axis = self.plot_conf.get_axis("Confidence per sample")
        axis.bar(samples, df["confidence"] * 100, color=colors_status)
        axis.set_ylim(0, 100)
        axis.set_ylabel("Confidence (%)")
        self.plot_conf.draw_idle()

        axis = self.plot_freq.get_axis("Dominant frequency")
        colors_freq = [
            "#f59e0b"
            if freq > self.analyzer.thresholds.frequency_max_hz
            else "#10b981"
            for freq in df["dominant_frequency_hz"]
        ]
        axis.bar(samples, df["dominant_frequency_hz"], color=colors_freq)
        axis.axhline(
            self.analyzer.thresholds.frequency_max_hz,
            color="#ef4444",
            linestyle="--",
            linewidth=1,
        )
        axis.set_ylabel("Frequency (Hz)")
        self.plot_freq.draw_idle()

        self.update_sbs_3d_plot(df)

        axis = self.plot_labels.get_axis("Label breakdown")
        counts = df["label"].value_counts()

        if not counts.empty:
            axis.pie(
                counts.values,
                labels=counts.index,
                autopct="%1.0f%%",
                startangle=90,
                wedgeprops={"width": 0.45},
            )
            axis.axis("equal")

        self.plot_labels.draw_idle()

    def update_sbs_3d_plot(self, df: pd.DataFrame) -> None:
        """Draw 3D SBS feature separation plot."""

        try:
            selected_features = self.analyzer.choose_best_3_features_sbs(df)

            x_feature = selected_features[0]
            y_feature = selected_features[1]
            z_feature = selected_features[2]

            axis = self.plot_sbs_3d.get_axis(
                f"Best 3D separation: {x_feature}, {y_feature}, {z_feature}",
                projection="3d",
            )

            labels = sorted(df["label"].astype(str).unique())
            markers = ["o", "^", "s", "D", "*", "P", "X", "v"]

            for index, label in enumerate(labels):
                class_df = df[df["label"].astype(str) == label]

                axis.scatter(
                    class_df[x_feature],
                    class_df[y_feature],
                    class_df[z_feature],
                    marker=markers[index % len(markers)],
                    s=45,
                    alpha=0.85,
                    label=label,
                )

            axis.set_xlabel(x_feature)
            axis.set_ylabel(y_feature)
            axis.set_zlabel(z_feature)
            axis.view_init(elev=22, azim=35)
            axis.legend(fontsize=8)

            self.plot_sbs_3d.draw_idle()

        except Exception as exc:
            axis = self.plot_sbs_3d.get_axis("Best 3D separation using SBS")
            axis.text(
                0.5,
                0.5,
                f"SBS 3D plot unavailable:\n{exc}",
                ha="center",
                va="center",
                wrap=True,
            )
            axis.set_xticks([])
            axis.set_yticks([])
            self.plot_sbs_3d.draw_idle()

    def get_filtered_results(self) -> pd.DataFrame:
        """Return table-filtered dataframe."""

        if self.results_df is None:
            return pd.DataFrame()

        df = self.results_df.copy()
        label_value = self.combo_label.currentData()
        status_value = self.combo_status.currentData()

        if label_value and label_value != "all":
            df = df[df["label"].astype(str) == str(label_value)]

        if status_value == "true":
            df = df[df["is_anomaly"]]
        elif status_value == "false":
            df = df[~df["is_anomaly"]]

        return df

    def update_table(self) -> None:
        """Update sample table."""

        df = self.get_filtered_results()
        self.table.setRowCount(0)

        if df.empty:
            return

        self.table.setRowCount(len(df))

        for row_index, (_, row) in enumerate(df.iterrows()):
            is_anomaly = bool(row["is_anomaly"])

            values = [
                int(row["sample_id"]),
                str(row["label"]),
                f"{row['confidence'] * 100:.1f}%",
                f"{row['dominant_frequency_hz']:.0f}",
                f"{row['rms']:.4f}",
                f"{row['energy']:.4f}",
                f"{row['kurtosis']:.2f}",
                "Anomaly" if is_anomaly else "Clean",
                row["anomaly_reason"] if is_anomaly else "—",
                "Select row",
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                if column_index == 0:
                    item.setData(Qt.UserRole, int(row["sample_id"]))

                if column_index == 7:
                    item.setForeground(Qt.red if is_anomaly else Qt.darkGreen)

                self.table.setItem(row_index, column_index, item)

        self.table.resizeColumnsToContents()

    def show_selected_sample(self) -> None:
        """Show selected row details."""

        if self.results_df is None or self.table.currentRow() < 0:
            return

        sample_item = self.table.item(self.table.currentRow(), 0)

        if sample_item is None:
            return

        sample_id = sample_item.data(Qt.UserRole)
        row_df = self.results_df[self.results_df["sample_id"] == sample_id]

        if row_df.empty:
            return

        row = row_df.iloc[0]

        self.detail_title.setText(f"Sample {sample_id} — {row['label']}")

        self.detail_stats.setText(
            f"Confidence: {row['confidence'] * 100:.1f}%   |   "
            f"Frequency: {row['dominant_frequency_hz']:.0f} Hz   |   "
            f"RMS: {row['rms']:.4f}   |   "
            f"Energy: {row['energy']:.4f}   |   "
            f"Kurtosis: {row['kurtosis']:.2f}   |   "
            f"Status: {'Anomaly' if row['is_anomaly'] else 'Clean'}   |   "
            f"Reason: {row['anomaly_reason'] if row['is_anomaly'] else '—'}"
        )

        color = "#ef4444" if bool(row["is_anomaly"]) else "#3b82f6"

        t, signal = self.analyzer.make_time_series(row)
        axis = self.plot_time.get_axis("Time-domain signal")
        axis.plot(t, signal, color=color, linewidth=1.4)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Amplitude")
        self.plot_time.draw_idle()

        xf, yf = self.analyzer.make_fft(row)
        axis = self.plot_fft.get_axis("FFT spectrum")
        axis.plot(xf, yf, color=color, linewidth=1.4)
        axis.fill_between(xf, yf, color=color, alpha=0.15)
        axis.axvline(
            row["dominant_frequency_hz"],
            color="#ef4444",
            linestyle="--",
            linewidth=1,
        )
        axis.set_xlabel("Frequency (Hz)")
        axis.set_ylabel("Amplitude")
        self.plot_fft.draw_idle()


def main() -> None:
    """Run application."""

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()