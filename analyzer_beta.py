"""Backend module for the signal analysis dashboard.

This file contains only the analysis/data logic:
- input validation
- anomaly detection
- synthetic time-domain signal generation
- FFT computation
- FFT PNG export
- CSV/JSON loading
- CSV export
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
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
    """Threshold values used to classify a sample."""

    confidence_min: float = 0.90
    frequency_max_hz: float = 900.0
    rms_max: float = 0.50
    kurtosis_max: float = 6.0
    energy_min: float = 0.001


class SignalAnalyzer:
    """Backend class for signal analysis."""

    def __init__(self) -> None:
        self.thresholds = AnomalyThresholds()

    def load_dataframe(self, file_path: str | Path) -> pd.DataFrame:
        """Load a CSV or JSON file and validate its columns."""

        path = Path(file_path)

        if path.suffix.lower() == ".csv":
            dataframe = pd.read_csv(path)
        elif path.suffix.lower() == ".json":
            dataframe = pd.read_json(path)
        else:
            raise ValueError("Please select a CSV or JSON file.")

        self.validate_dataframe(dataframe)
        return dataframe

    def apply_thresholds(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Apply anomaly rules to all samples."""

        self.validate_dataframe(df_raw)
        results = []

        for _, row in df_raw.iterrows():
            reasons = []

            if row["confidence"] < self.thresholds.confidence_min:
                reasons.append("Confidence below threshold")

            if row["dominant_frequency_hz"] > self.thresholds.frequency_max_hz:
                reasons.append("Dominant frequency above threshold")

            if row["rms"] > self.thresholds.rms_max:
                reasons.append("RMS amplitude too high")

            if row["kurtosis"] > self.thresholds.kurtosis_max:
                reasons.append("Abnormal kurtosis")

            if row["energy"] < self.thresholds.energy_min:
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
    def validate_dataframe(dataframe: pd.DataFrame) -> None:
        """Check that the dataframe contains all required columns."""

        missing = [
            column for column in REQUIRED_COLUMNS if column not in dataframe.columns
        ]

        if missing:
            raise ValueError("Missing columns: " + ", ".join(missing))

    @staticmethod
    def make_time_series(row: pd.Series) -> tuple[np.ndarray, np.ndarray]:
        """Generate a synthetic time-domain signal from sample features."""

        t = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
        amplitude = float(row["rms"]) * np.sqrt(2)
        frequency = float(row["dominant_frequency_hz"])

        signal = float(row["mean"]) + amplitude * np.sin(
            2 * np.pi * frequency * t
        )

        return t, signal

    @classmethod
    def make_fft(cls, row: pd.Series) -> tuple[np.ndarray, np.ndarray]:
        """Compute the FFT amplitude spectrum of one sample."""

        _, signal = cls.make_time_series(row)

        n_points = len(signal)
        yf = np.abs(fft(signal))[: n_points // 2] * 2 / n_points
        xf = fftfreq(n_points, 1 / FS)[: n_points // 2]

        return xf, yf

    def save_fft_plot_files(self, results_df: pd.DataFrame) -> None:
        """Save one FFT PNG file for every sample."""

        if results_df.empty:
            return

        plots_path = Path(PLOTS_DIR)
        plots_path.mkdir(parents=True, exist_ok=True)

        for _, row in results_df.iterrows():
            sample_id = int(row["sample_id"])
            fft_path = plots_path / f"fft_{sample_id}.png"
            self.save_fft_png(row, fft_path)

    def save_fft_png(self, row: pd.Series, file_path: Path) -> None:
        """Save one FFT spectrum as a PNG file."""

        xf, yf = self.make_fft(row)

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

    @staticmethod
    def export_results(results_df: pd.DataFrame, file_path: str | Path) -> None:
        """Export only the required result columns to CSV."""

        if results_df.empty:
            raise ValueError("No results to export.")

        results_df[EXPORT_COLUMNS].to_csv(file_path, index=False)