"""
AuraCell 4D - Acoustic Processing Engine (AURASENSAI Core)
Sub-20ms microfluidic event detection, background incubator noise rejection,
and transient acoustic pulse isolation.
"""

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

class AcousticProcessor:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def bandpass_filter(self, signal, lowcut=100.0, highcut=8000.0, order=4):
        """Removes low-frequency incubator hum and high-frequency sensor hiss."""
        nyq = 0.5 * self.sample_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, signal)

    def extract_energy_envelope(self, signal, frame_len_ms=20.0, hop_ms=10.0):
        """Computes Short-Time Energy (STE) on a rolling 20ms timeline."""
        frame_len = int((frame_len_ms / 1000.0) * self.sample_rate)
        hop = int((hop_ms / 1000.0) * self.sample_rate)
        
        num_frames = max(1, (len(signal) - frame_len) // hop + 1)
        envelope = np.zeros(num_frames)
        timestamps = np.zeros(num_frames)
        
        for i in range(num_frames):
            start = i * hop
            end = start + frame_len
            frame = signal[start:end]
            envelope[i] = np.sum(frame ** 2)
            timestamps[i] = (start + frame_len / 2.0) / self.sample_rate
            
        return timestamps, envelope

    def detect_transient_events(self, signal, threshold_std=3.5):
        """
        Isolates microfluidic transients (cavitation, clogging spikes, cell membrane rupture)
        using peak-relative matched energy boundaries.
        """
        filtered = self.bandpass_filter(signal)
        timestamps, envelope = self.extract_energy_envelope(filtered)
        
        mean_env = np.mean(envelope)
        std_env = np.std(envelope)
        dynamic_threshold = mean_env + threshold_std * std_env
        
        peaks, properties = find_peaks(envelope, height=dynamic_threshold, distance=5)
        
        detected_events = []
        for p in peaks:
            peak_time = timestamps[p]
            peak_energy = envelope[p]
            detected_events.append({
                "type": "acoustic_transient_burst",
                "timestamp_sec": float(np.round(peak_time, 4)),
                "window_start_sec": float(np.round(max(0, peak_time - 0.010), 4)),
                "window_end_sec": float(np.round(peak_time + 0.010, 4)),
                "energy": float(np.round(peak_energy, 4)),
                "snr_db": float(np.round(10 * np.log10(peak_energy / (mean_env + 1e-9)), 2))
            })
            
        return detected_events
