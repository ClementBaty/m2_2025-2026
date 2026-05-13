# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:08:49 2026

@author: ga08007z
"""

"""
Console script for raw signal acquisition simulation.

This script asks the user for signal metadata, generates fake samples,
and saves everything into a CSV file using pandas.

Author: 

- Alex Grapin
- Groupe A
"""

from datetime import datetime
import random
import pandas as pd


class SignalAcquisition:
    """
    Class used to simulate the acquisition of a raw signal.

    This class collects signal information from the user, generates fake
    samples, and exports the result into a CSV file.
    """

    def __init__(self):
        """
        Initialize the SignalAcquisition object with default values.
        """
        self.signal_type = None
        self.source = None
        self.sample_rate = None
        self.duration = None
        self.timestamp = None
        self.samples = []

    def ask_user_inputs(self):
        """
        Ask the user for the signal metadata through the console.

        The method retrieves:
        - signal type
        - source
        - sample rate (Hz)
        - duration (seconds)
        """
        self.signal_type = input("Enter signal type (ex: ECG, EEG, Audio): ")
        self.source = input("Enter signal source (ex: Sensor1, File, Device): ")

        self.sample_rate = float(input("Enter sample rate in Hz (ex: 1000): "))
        self.duration = float(input("Enter duration in seconds (ex: 5): "))

    def generate_timestamp(self):
        """
        Generate a timestamp corresponding to the current date and time.

        The timestamp format is ISO style: YYYY-MM-DD HH:MM:SS
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_fake_samples(self):
        """
        Generate fake samples for the signal.

        The number of samples is computed from:
        sample_rate * duration

        Fake values are random floats between -1 and 1.
        """
        number_of_samples = int(self.sample_rate * self.duration)

        self.samples = []
        for _ in range(number_of_samples):
            self.samples.append(random.uniform(-1.0, 1.0))

    def export_to_csv(self, filename="signal_raw.csv"):
        """
        Export the signal data into a CSV file using pandas.

        The CSV file contains:
        - timestamp
        - signal_type
        - source
        - sample_rate
        - duration
        - sample_index
        - sample_value

        Parameters
        ----------
        filename : str
            Name of the output CSV file.
        """
        data = []

        for index, value in enumerate(self.samples):
            data.append(
                {
                    "timestamp": self.timestamp,
                    "signal_type": self.signal_type,
                    "source": self.source,
                    "sample_rate": self.sample_rate,
                    "duration": self.duration,
                    "sample_index": index,
                    "sample_value": value,
                }
            )

        dataframe = pd.DataFrame(data)
        dataframe.to_csv(filename, index=False)

        print(f"\nFile saved successfully: {filename}")

    def run(self):
        """
        Run the complete acquisition simulation process.
        """
        print("=== RAW SIGNAL ACQUISITION TEST ===\n")

        self.ask_user_inputs()
        self.generate_timestamp()
        self.generate_fake_samples()
        self.export_to_csv()


if __name__ == "__main__":
    acquisition = SignalAcquisition()
    acquisition.run()