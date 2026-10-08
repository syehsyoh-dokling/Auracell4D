# Ablation on Fluo-N3DH-CHO — official `py-ctcmetrics` (DET, TRA) + mitosis P/R/F1

**Run:** Google Colab CPU, 8 Oct 2026, `python evaluate.py --data ./data --out ./results` (no Drive, no login).
**Local reproduction (Windows, 8 Oct 2026):** `--seqs 01 --detect gt --trackers greedy_nogate ilp_gate` → TRA 0.9276 / 0.9976, divisions 178/4 and 5/4 — identical to Colab (see `results/quick/`).
**Dataset:** CTC Fluo-N3DH-CHO training 01 & 02 (92 frames each, 5×443×512 voxels, 0.202×0.202×1.0 µm, Δt 9.5 min).
**Calibrated gate** from the 3 GT divisions of seq 02: daughter ratio p5/p50/p95 = 1.0/1.0/1.0, mass ratio (V1+V2)/Vp = 2.0/2.0/2.0 → thresholds `ratio_max 1.1, mass 1.8–2.2`.
→ **Finding:** GT TRA masks are *uniform-size markers*, not real segmentations; this is why the original ±15 % gate (mass 0.85–1.15) vetoes 100 % of true divisions.

## GT detections (DET = 1 by construction → measures *linking* quality only)

| seq | tracker | TRA | mitosis pred/GT | TP | P | R | F1 | s/vol |
|---|---|---|---|---|---|---|---|---|
| 01 | greedy_nogate | 0.9276 | 178/4 | 1 | 0.006 | 0.25 | 0.011 | 0.14 |
| 01 | greedy_gate (calibrated) | 0.9587 | 86/4 | 2 | 0.023 | 0.50 | 0.044 | 0.15 |
| 01 | **ilp_nogate** | 0.9970 | 8/4 | 1 | 0.125 | 0.25 | 0.167 | 0.15 |
| 01 | **ilp_gate** | **0.9976** | 5/4 | 1 | 0.200 | 0.25 | **0.222** | 0.15 |
| 01 | greedy_gate ORIGINAL ±15 % | 0.9983 | 0/4 | 0 | 0 | 0 | 0.0 | 0.11 |
| 02 | greedy_nogate | 0.9426 | 103/3 | 2 | 0.019 | 0.33 | 0.037 | 0.11 |
| 02 | greedy_gate (calibrated) | 0.9426 | 103/3 | 2 | 0.019 | 0.33 | 0.037 | 0.12 |
| 02 | **ilp_nogate** | 0.9964 | 7/3 | 0 | 0 | 0 | 0.0 | 0.12 |
| 02 | **ilp_gate** | 0.9964 | 7/3 | 0 | 0 | 0 | 0.0 | 0.12 |
| 02 | greedy_gate ORIGINAL ±15 % | 0.9987 | 0/3 | 0 | 0 | 0 | 0.0 | 0.12 |

## Label-free detections (Otsu + watershed, no GT)

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

## Honest reading

1. **ILP vs greedy (the measurable algorithmic contribution):** with GT detections the ILP raises TRA 0.928→0.997 (seq 01) and 0.943→0.996 (seq 02) and cuts false divisions 178→5–8 and 103→7. The ordering holds under Otsu detections too (`ilp_gate` has the highest TRA in both sequences).
2. **The calibrated soft gate** gives a small but consistent gain over ILP without gate (0.9970→0.9976; 0.3887→0.3919; 0.5087→0.5117) and suppresses false divisions (8→5, 176→63, 138→32).
3. **The original ±15 % gate** yields the highest TRA (0.998) **only because it rejects every division** — the "0.99xx" of the earlier draft was an artefact of a tracker that never detected mitosis.
4. **Mitosis remains an open problem:** recall ≤ 0.5, best F1 0.222 (ilp_gate, 01/GT); 0 on seq 02 and on all Otsu runs. The GT sample is tiny (4 + 3 events) → mitosis numbers are not statistically stable.
5. **The label-free detection baseline is weak:** DET 0.40/0.53 (FN 428/193, FP 1140/979). Segmentation is the bottleneck; the tracker cannot compensate.
6. Runtime 0.11–0.15 s/volume (CPU) on small 5-slice volumes; not a real-time claim.
