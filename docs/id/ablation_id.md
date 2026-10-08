# Ablasi Fluo-N3DH-CHO — metrik resmi `py-ctcmetrics` (DET, TRA) + mitosis P/R/F1

**Dijalankan:** Google Colab CPU, 8 Okt 2026, `python evaluate.py --data ./data --out ./results` (tanpa Drive/login).
**Reproduksi lokal (Windows, 8 Okt 2026):** `--seqs 01 --detect gt --trackers greedy_nogate ilp_gate` → TRA 0.9276 / 0.9976, divisi 178/4 dan 5/4 — identik dengan Colab (lihat `results/quick/`).
**Dataset:** CTC Fluo-N3DH-CHO training 01 & 02 (92 frame masing-masing, 5×443×512 voxel, 0.202×0.202×1.0 µm, Δt 9.5 min).
**Gate terkalibrasi** dari 3 divisi GT seq 02: rasio anak p5/p50/p95 = 1.0/1.0/1.0, rasio massa (V1+V2)/Vp = 2.0/2.0/2.0 → ambang `ratio_max 1.1, mass 1.8–2.2`.
→ **Temuan:** mask GT TRA adalah *penanda berukuran seragam*, bukan segmentasi nyata; itulah sebabnya gate asli ±15 % (mass 0.85–1.15) memveto 100 % divisi sejati.

## Deteksi GT (DET = 1 by construction → mengukur kualitas *linking* saja)

| seq | tracker | TRA | mitosis pred/GT | TP | P | R | F1 | s/vol |
|---|---|---|---|---|---|---|---|---|
| 01 | greedy_nogate | 0.9276 | 178/4 | 1 | 0.006 | 0.25 | 0.011 | 0.14 |
| 01 | greedy_gate (kalibrasi) | 0.9587 | 86/4 | 2 | 0.023 | 0.50 | 0.044 | 0.15 |
| 01 | **ilp_nogate** | 0.9970 | 8/4 | 1 | 0.125 | 0.25 | 0.167 | 0.15 |
| 01 | **ilp_gate** | **0.9976** | 5/4 | 1 | 0.200 | 0.25 | **0.222** | 0.15 |
| 01 | greedy_gate ORIGINAL ±15 % | 0.9983 | 0/4 | 0 | 0 | 0 | 0.0 | 0.11 |
| 02 | greedy_nogate | 0.9426 | 103/3 | 2 | 0.019 | 0.33 | 0.037 | 0.11 |
| 02 | greedy_gate (kalibrasi) | 0.9426 | 103/3 | 2 | 0.019 | 0.33 | 0.037 | 0.12 |
| 02 | **ilp_nogate** | 0.9964 | 7/3 | 0 | 0 | 0 | 0.0 | 0.12 |
| 02 | **ilp_gate** | 0.9964 | 7/3 | 0 | 0 | 0 | 0.0 | 0.12 |
| 02 | greedy_gate ORIGINAL ±15 % | 0.9987 | 0/3 | 0 | 0 | 0 | 0.0 | 0.12 |

## Deteksi label-free (Otsu + watershed, tanpa GT)

| seq | tracker | DET | TRA | mitosis pred/GT | TP | P | R | F1 | s/vol |
|---|---|---|---|---|---|---|---|---|---|
| 01 | greedy_nogate | 0.4011 | 0.3652 | 578/4 | 4 | 0.007 | 0.50 | 0.014 | 0.64 |
| 01 | greedy_gate | 0.4011 | 0.3914 | 19/4 | 0 | 0 | 0 | 0.0 | 0.12 |
| 01 | ilp_nogate | 0.4011 | 0.3887 | 176/4 | 0 | 0 | 0 | 0.0 | 0.14 |
| 01 | **ilp_gate** | 0.4011 | **0.3919** | 63/4 | 0 | 0 | 0 | 0.0 | 0.14 |
| 02 | greedy_nogate | 0.5262 | 0.4761 | 495/3 | 2 | 0.004 | 0.33 | 0.008 | 0.70 |
| 02 | greedy_gate | 0.5262 | 0.5091 | 13/3 | 1 | 0.077 | 0.33 | 0.125 | 0.11 |
| 02 | ilp_nogate | 0.5262 | 0.5087 | 138/3 | 0 | 0 | 0 | 0.0 | 0.13 |
| 02 | **ilp_gate** | 0.5262 | **0.5117** | 32/3 | 0 | 0 | 0 | 0.0 | 0.13 |

## Bacaan jujur

1. **ILP vs greedy (kontribusi algoritmik yang terukur):** pada deteksi GT, ILP menaikkan TRA 0.928→0.997 (seq 01) dan 0.943→0.996 (seq 02), dan memangkas divisi palsu 178→5–8 dan 103→7. Konsisten pada deteksi Otsu (TRA tertinggi di kedua sekuens untuk `ilp_gate`).
2. **Gate lunak terkalibrasi** memberi perbaikan kecil tapi konsisten atas ILP tanpa gate (0.9970→0.9976; 0.3887→0.3919; 0.5087→0.5117), dan menekan divisi palsu (8→5, 176→63, 138→32).
3. **Gate asli ±15 %** menghasilkan TRA tertinggi (0.998) **hanya karena menolak semua divisi** — angka "0.99xx" di draf lama adalah artefak dari tracker yang tidak pernah mendeteksi mitosis.
4. **Mitosis tetap masalah terbuka:** recall ≤ 0.5, F1 terbaik 0.222 (ilp_gate, 01/GT); 0 pada seq 02 dan pada semua Otsu. Sampel GT sangat kecil (4 + 3 event) → angka mitosis tidak stabil secara statistik.
5. **Deteksi label-free baseline lemah:** DET 0.40/0.53 (FN 428/193, FP 1140/979). Segmentasi adalah hambatan utama; tracker tidak bisa menutupinya.
6. Latensi 0.11–0.15 s/volume (CPU) pada volume kecil 5 slice; bukan klaim real-time.
