import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = "processed_data.csv"
OUTPUT_FILE = "analysis_results.csv"
PLOTS_DIR = "plots"

FS = 8000
DURATION = 0.02


def load_data():
    # Read the input file
    return pd.read_csv(INPUT_FILE)


def prepare_folder():
    # Create plots folder
    os.makedirs(PLOTS_DIR, exist_ok=True)


def detect_anomaly(row):
    confidence = row["confidence"]
    frequency = row["dominant_frequency_hz"]

    if confidence < 0.90 and frequency > 900:
        return True, "Low confidence and high frequency noise"

    return False, ""


def create_fft_plot(row):
    sample_id = int(row["sample_id"])
    frequency = row["dominant_frequency_hz"]

    path = f"{PLOTS_DIR}/fft_{sample_id}.png"

    plt.figure()
    plt.vlines(frequency, 0, 1)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title(f"Dominant Frequency - Sample {sample_id}")
    plt.grid(True)
    plt.savefig(path)
    plt.close()

    return path


def create_time_series_plot(row):
    sample_id = int(row["sample_id"])
    mean = row["mean"]
    rms = row["rms"]
    frequency = row["dominant_frequency_hz"]

    amplitude = rms * np.sqrt(2)

    t = np.linspace(0, DURATION, int(FS * DURATION))
    x = mean + amplitude * np.sin(2 * np.pi * frequency * t)

    path = f"{PLOTS_DIR}/time_series_{sample_id}.png"

    plt.figure()
    plt.plot(t, x)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title(f"Synthetic Signal - Sample {sample_id}")
    plt.grid(True)
    plt.savefig(path)
    plt.close()

    return path


def create_result_row(row, fft_path, time_path, is_anomaly, reason):
    # Build one line of the final CSV
    return {
        "sample_id": row["sample_id"],
        "label": row["label"],
        "confidence": row["confidence"],
        "fft_plot_path": fft_path,
        "time_series_plot_path": time_path,
        "is_anomaly": is_anomaly,
        "anomaly_reason": reason
    }


def analyze_one_sample(row):
    # Analyze one row from the input file
    fft_path = create_fft_plot(row)
    time_path = create_time_series_plot(row)
    is_anomaly, reason = detect_anomaly(row)

    return create_result_row(row, fft_path, time_path, is_anomaly, reason)


def analyze_all_samples(data):
    # Analyze all samples
    results = []

    for _, row in data.iterrows():
        result = analyze_one_sample(row)
        results.append(result)

    return pd.DataFrame(results)


def save_results(results):
    # Save final CSV
    results.to_csv(OUTPUT_FILE, index=False)


def main():
    prepare_folder()

    data = load_data()

    results = analyze_all_samples(data)

    save_results(results)

    print("Analysis finished")
    print(f"Result saved in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()