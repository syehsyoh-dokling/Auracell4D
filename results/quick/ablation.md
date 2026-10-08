# Ablasi Fluo-N3DH-CHO (py-ctcmetrics)

Gate kalibrasi: `{"n_divisions": 3, "daughter_ratio_p5_p50_p95": [1.0, 1.0, 1.0], "mass_ratio_p5_p50_p95": [2.0, 2.0, 2.0], "ratio_max": 1.1, "mass_min": 1.8, "mass_max": 2.2}`

| seq | deteksi | tracker | DET | TRA | mitosis pred/GT | TP | P | R | F1 | s/vol |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | gt | greedy_nogate | 1.0 | 0.9276 | 178/4 | 1 | 0.006 | 0.25 | 0.011 | 0.16 |
| 01 | gt | ilp_gate | 1.0 | 0.9976 | 5/4 | 1 | 0.2 | 0.25 | 0.222 | 0.108 |