"""
AuraCell 4D - Synthetic In-Vitro Multimodal Generator
Generates lightweight in-memory synthetic streams for local tests and pipeline validation:
1. Microfluidic acoustic waveforms (AURASENSAI test stream)
2. 4D Volumetric cell spatiotemporal positions & division events (Velocell test stream)
3. 16-band snapshot hyperspectral cubes (SpectrumaX test stream)
"""

import numpy as np

def generate_synthetic_acoustic_stream(duration_sec=2.0, sample_rate=44100, num_events=3):
    """
    Generates a realistic microfluidic acoustic signal:
    - High-frequency ambient pump hum and pink noise
    - Injected transient microbubble cavitation pulses (80-150 kHz harmonics)
    - Low-frequency cardiomyocyte contractions (1.5 Hz MCG pulses)
    """
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)

    # 1. Background incubator pump noise (50 Hz hum + harmonics + pink noise)
    noise = 0.05 * np.sin(2 * np.pi * 50 * t) + 0.02 * np.sin(2 * np.pi * 150 * t)
    noise += 0.03 * np.random.normal(0, 1, num_samples)

    # 2. Infrasound Cardiomyocyte contraction pulse (1.2 Hz)
    mcg_pulse = 0.15 * np.sin(2 * np.pi * 1.2 * t) * (np.sin(2 * np.pi * 1.2 * t) > 0.8)

    signal = noise + mcg_pulse
    ground_truth_events = []

    # 3. Inject transient microbubble cavitation bursts
    event_times = np.linspace(0.4, duration_sec - 0.4, num_events)
    for et in event_times:
        idx = int(et * sample_rate)
        width = int(0.015 * sample_rate)  # 15 ms duration
        burst_t = np.linspace(0, 0.015, width)
        burst = 0.4 * np.sin(2 * np.pi * 3200 * burst_t) * np.hanning(width)
        signal[idx : idx + width] += burst
        ground_truth_events.append({
            "type": "cavitation_bubble_burst",
            "start_sec": float(et),
            "end_sec": float(et + 0.015),
            "peak_amplitude": 0.4
        })

    return {
        "time": t,
        "signal": signal,
        "sample_rate": sample_rate,
        "events": ground_truth_events
    }

def generate_synthetic_4d_cells(num_initial_cells=6, num_timepoints=5, box_size=100.0):
    """
    Generates a 3D+time lineage tracking ground-truth:
    Cells move Brownian-like with drift, and at t=2, cell_0 undergoes mitosis into two daughters.
    """
    timepoints = []
    current_cells = []
    
    # Initialize cells at t=0
    for cid in range(num_initial_cells):
        current_cells.append({
            "cell_id": cid,
            "x": float(np.random.uniform(20, box_size - 20)),
            "y": float(np.random.uniform(20, box_size - 20)),
            "z": float(np.random.uniform(10, box_size - 10)),
            "parent_id": None
        })

    next_id = num_initial_cells

    for t in range(num_timepoints):
        frame_cells = []
        new_generation = []
        
        for c in current_cells:
            # Check for programmed mitosis event at t=2 for cell_0
            if t == 2 and c["cell_id"] == 0:
                # Divide into two daughter cells
                d1 = {
                    "cell_id": next_id,
                    "x": c["x"] + 2.5,
                    "y": c["y"] + 1.0,
                    "z": c["z"],
                    "parent_id": 0,
                    "event": "mitosis_daughter_1"
                }
                d2 = {
                    "cell_id": next_id + 1,
                    "x": c["x"] - 2.5,
                    "y": c["y"] - 1.0,
                    "z": c["z"],
                    "parent_id": 0,
                    "event": "mitosis_daughter_2"
                }
                new_generation.extend([d1, d2])
                next_id += 2
            else:
                # Normal migration with Brownian displacement
                dx = np.random.normal(0, 1.2)
                dy = np.random.normal(0, 1.2)
                dz = np.random.normal(0, 0.4)
                updated = {
                    "cell_id": c["cell_id"],
                    "x": float(c["x"] + dx),
                    "y": float(c["y"] + dy),
                    "z": float(c["z"] + dz),
                    "parent_id": c.get("parent_id")
                }
                new_generation.append(updated)

        current_cells = new_generation
        timepoints.append({
            "t": t,
            "cells": [dict(c) for c in current_cells]
        })

    return timepoints

def generate_synthetic_hyperspectral_cube(height=32, width=32, num_bands=16):
    """
    Generates a 16-band snapshot hyperspectral cube representing NADH (band 2)
    and FAD (band 6) autofluorescence profiles across viable vs stressed cells.
    """
    cube = np.random.normal(0.1, 0.02, (height, width, num_bands)).clip(0, 1)
    
    # Insert viable cell cluster in top-left
    cube[5:15, 5:15, 2] += 0.6  # High NADH
    cube[5:15, 5:15, 6] += 0.2  # Normal FAD
    
    # Insert apoptotic cell cluster in bottom-right
    cube[20:28, 20:28, 2] += 0.1  # Depleted NADH
    cube[20:28, 20:28, 6] += 0.7  # High oxidized FAD
    
    return cube
