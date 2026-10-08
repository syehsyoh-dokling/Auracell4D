# AuraCell 4D — Physics-Gated, Audit-Ready Lineage Tracking for Organ-on-a-Chip Time-Lapse Microscopy

**Kaggle AI4S Open Innovation: AI for Life Science (5th Pazhou Algorithm Competition)**
Submission category: *see writeup.md (declared at top)*

> Every number in the writeup carries one of two labels:
> **[Measured]** — produced by `evaluate.py` on public Cell Tracking Challenge data, reproducible without login;
> **[Simulated/Concept]** — physics-based simulation or design concept; no performance claim is made.

## What this repository actually contains

| Component | Status | Where |
|---|---|---|
| Frame-pair **network-flow ILP tracker** (link / divide / appear / disappear) with biological gate as *soft cost* | [Measured] | `evaluate.py::ilp_pair` |
| Greedy nearest-neighbour tracker (baseline, port of the original `mitosis_ilp.py`) | [Measured] | `evaluate.py::greedy_pair` |
| Label-free detection baseline (Gaussian → Otsu → watershed) | [Measured] | `evaluate.py::detect_otsu` |
| Gate calibration from GT division statistics (no hand-picked ±15 %) | [Measured] | `evaluate.py::calibrate_gate` |
| Official CTC metrics DET / TRA via `py-ctcmetrics` + mitosis P/R/F1 | [Measured] | `evaluate.py::run_config` |
| Analytic physics consistency checks (Poiseuille, Minnaert, Womersley, Krogh, Hertz, thin-plate) | [Simulated] | `src/verificators/` |
| Synthetic acoustic / hyperspectral signal generators and detectors | [Simulated] | `src/utils/synthetic_data.py`, `src/acoustic/`, `src/spectral/` |
| Scientist GUI (5-step workflow, static/simulated data) | [Concept] | `gui/` |
| Cartridge spec, firmware header, HIL simulator | [Concept / roadmap] | `src/chip_production/` |

Not included (honestly): a trained cell segmentation model, real organ-on-a-chip recordings, real acoustic data, firmware implementation, any hardware measurement.

## Reproduce the measured results (≈15–30 min on CPU, no login)

```bash
pip install -r requirements.txt
python evaluate.py --data ./data --out ./results
```

`evaluate.py` downloads the public **Fluo-N3DH-CHO** training set from the Cell Tracking Challenge (CHO nuclei GFP-PCNA, Zeiss LSM 510 confocal, 0.202×0.202×1.0 µm, Δt = 9.5 min, 2 sequences × 92 frames), then runs the full ablation:

- detection: `gt` (centroids from GT masks → DET = 1 by construction, isolates linking quality) and `otsu` (label-free, no GT)
- trackers: `greedy_nogate`, `greedy_gate`, `ilp_nogate`, `ilp_gate`, plus the original ±15 % gate for reference
- outputs: `results/ablation.md`, `results/ablation.json`, and CTC-format result folders

Quick subset: `python evaluate.py --seqs 01 --detect gt --trackers ilp_gate`

## Test it from the UI (local, no login)

```bash
python gui/launch_gui.py          # or double-click Launch_AuraCell_Workstation.bat
```
Opens `http://127.0.0.1:8765/index.html` and starts a tiny local API (`/api/results`, `/api/run`, `/api/status`).

1. **Step 4 → "4D Cell Tracking & Mitosis".** The badge must read **"local API connected"**; the table auto-loads `results/ablation.json` (18 rows). If the file is missing, the panel says so.
2. Click **"Run quick benchmark"** → downloads Fluo-N3DH-CHO on first use (~108 MB), runs `greedy_nogate` and `ilp_gate` on sequence 01 with GT detections, streams the log, then refreshes the table (written to `results/quick/`, never overwriting the full ablation). Expected: TRA 0.9276 (greedy) vs 0.9976 (ILP), false divisions 178 vs 5 — the local Windows run on 8 Oct 2026 reproduced the Colab numbers to all four decimals.
3. **"Run full ablation"** reproduces every row (15–30 min CPU).
4. **Step 5 → "Download audit export (JSON)"** saves the loaded measured rows with explicit labels for simulated panels.
5. Steps 2–3 (acoustic, spectral) are **animated simulations** and are labelled as such in the UI; nothing there is a measurement.

Opening `gui/index.html` directly as a file still works for the simulations, but the measured panel then shows "file:// mode" and cannot load data (browsers block `fetch` on `file://`).

## Known limitations (see writeup §Limitations)

- Mitosis recall is low; the volume-based gate is calibrated on CTC TRA *markers* (uniform size), not true segmentations.
- Fluo-N3DH-CHO is a conventional culture dataset, **not** organ-on-a-chip data.
- Anaphase kinematics cannot be measured at 9.5 min/frame.
- Acoustic and spectral modules are simulations demonstrating the gate interface only.

## Audit trail

`docs/AUDIT_KLAIM.md` records the claim-by-claim audit of the earlier draft (46 claims; what was removed and why), with raw results in `audit/`.

## Data & licenses

- Cell Tracking Challenge, Fluo-N3DH-CHO (Dr. J. Essers, Erasmus MC) — CTC terms of use; cite Ulman, Maška et al., *Nat Methods* 14:1141–1152 (2017), doi:10.1038/nmeth.4473.
- No personal, clinical or restricted data are used.
