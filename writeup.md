# AuraCell 4D: Physics-Gated Network-Flow Lineage Tracking for Organ-on-a-Chip Time-Lapse Microscopy

---

### SUBMISSION METADATA & DECLARATIONS
* **Track:** The 5th Pazhou Algorithm Competition · AI4S Open Innovation: AI for Life Science (AI + Organ-on-a-Chip)
* **Category Declaration:** **Model & Algorithm** — a physics-gated network-flow ILP for 3D+t cell lineage tracking, with an ablation on public Cell Tracking Challenge data. (Sensor fusion and chip actuation are presented as *design concept and roadmap*, not as results.)
* **Team:** Saifuddin — AI & systems (computer vision, signal processing, optimisation). *No biology/bioengineering member is declared; we do not claim the cross-disciplinary bonus.*
* **Code repository:** https://github.com/syehsyoh-dokling/Auracell4D — entry script `evaluate.py`, `README.md`, `requirements.txt`
* **Demo video:** https://youtu.be/5ts7kyqQb_k
* **Reproducibility:** `pip install -r requirements.txt && python evaluate.py` downloads the public dataset and regenerates every **[Measured]** number in this document in ≈15–30 min on CPU, without login.

> **Labelling convention used throughout.** Every quantitative statement carries one of two tags:
> **[Measured]** — produced by `evaluate.py` on public data (`results/ablation.json`).
> **[Design]** — a physics-based design parameter or simulation; **no performance is claimed**.
> A previous draft of this project contained performance figures that could not be reproduced. They were audited claim-by-claim (`docs/AUDIT_LOG.md`) and removed. Nothing below is carried over from that draft unless it was re-measured.
> Full technical report with embedded figures: `docs/TECHNICAL_REPORT.md` · one-page abstract: `docs/ABSTRACT.md` · figures: `docs/figures/`.

---

## Project Summary (≈250 words)

Organ-on-a-chip (OoC) time-lapse experiments produce 3D+t image series from which researchers must reconstruct cell lineages, count divisions, and separate drug effects from mechanical artefacts such as bubble-induced detachment. Off-the-shelf greedy trackers hallucinate divisions whenever two nuclei pass close to each other, and no tracker by itself can tell a cell that died from a cell that was torn off by a transient flow event.

AuraCell 4D contributes (i) a **frame-pair network-flow integer linear program** in which every nucleus at time *t* must take exactly one fate (link, divide, disappear) and every nucleus at *t+1* exactly one origin (link, daughter, appear), and (ii) a **biological gate expressed as a soft cost** — volume-ratio and mass-conservation penalties calibrated from data rather than hand-set — so that physically implausible divisions are discouraged, not vetoed blindly.

On the public Cell Tracking Challenge **Fluo-N3DH-CHO** set (2 × 92 frames), with detections taken from ground truth to isolate linking quality, the ILP raises the official TRA score from **0.928/0.943 (greedy) to 0.997/0.996 [Measured]** and cuts false divisions from 178 to 5 on sequence 01. The soft gate adds a small, consistent gain. Mitosis recall remains low (best F1 0.22) and our label-free detection baseline is weak (DET 0.40–0.53); both are reported as open limitations. We also show *why* a previous version of the gate appeared to reach TRA 0.998: it rejected every real division, because CTC tracking markers are uniform in size.

The same engine is designed to ingest a continuous acoustic channel and periodic imaging, attach a traceable PASS / FLAG / REJECT certificate to every lineage event, and give researchers dose–response counts with every exclusion explained. That part is a documented **[Design]** today.

---

## 1. Problem Definition and Why It Matters

Three failure modes dominate OoC image analysis:

1. **False divisions.** When two nuclei touch, nearest-neighbour trackers create a parent with two daughters. On a 92-frame sequence with only 4 true divisions, a greedy tracker proposed **178** [Measured].
2. **Identity swaps and drift.** Greedy, frame-local decisions accumulate errors; the official TRA metric penalises each wrong edge.
3. **Artefact contamination of drug-response counts.** Cells detached by a bubble or a pressure surge are counted as "dead by drug" if nothing links the mechanical event to the image timeline.

The first two are algorithmic and are addressed and measured here. The third requires a sensor channel that we have designed but not yet built; Section 3 specifies exactly how it would operate and what each number would mean, so that reviewers can judge the design on its own terms.

---

## 2. Data

| Item | Value |
|---|---|
| Dataset | Cell Tracking Challenge, **Fluo-N3DH-CHO**, training sequences 01 and 02 |
| Biology / imaging | CHO nuclei expressing GFP-PCNA; Zeiss LSM 510 confocal, 63×/1.4 oil; **conventional culture — not organ-on-a-chip** |
| Geometry | 92 frames × 5 × 443 × 512 voxels; 0.202 × 0.202 × 1.0 µm; Δt = 9.5 min |
| Ground truth | TRA markers (`man_track*.tif`, `man_track.txt`): 27 / 24 tracks; 4 / 3 division events with ≥2 daughters |
| Provider / licence | Dr. J. Essers, Erasmus MC Rotterdam; CTC terms of use; cite Ulman, Maška et al., *Nat Methods* 14:1141–1152 (2017), doi:10.1038/nmeth.4473 |
| Download | performed by `evaluate.py` from `data.celltrackingchallenge.net` |

**Data sources used for all measured results (complete list — nothing else is used):**

| Resource | URL | Role |
|---|---|---|
| Fluo-N3DH-CHO training set (zip, ≈108 MB) | http://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip | the only dataset; downloaded automatically by `evaluate.py` |
| Dataset description page (imaging metadata, provider) | https://celltrackingchallenge.net/3d-datasets/ | voxel size, Δt, microscope, provenance |
| CTC terms of use & citation policy | https://celltrackingchallenge.net/ | licence |
| Official metrics implementation `py-ctcmetrics` | https://pypi.org/project/py-ctcmetrics/ (source: https://github.com/CellTrackingChallenge/py-ctcmetrics) | DET / TRA computation |
| Reference paper for the metrics and dataset | https://doi.org/10.1038/nmeth.4473 | citation |

No private, clinical or personal data are used. No real OoC recordings and no real acoustic recordings are used; synthetic signals are labelled **[Design]** and are generated in-code (`src/utils/synthetic_data.py`), not downloaded.

---

## 3. Where It Runs and What the Numbers Mean (Operational Design)

This section answers four practical questions: *where* the software sits, *how* it listens, *what each number means* on a real cartridge, and *how* it changes a researcher's day. Items marked **[Measured]** exist and are evaluated; items marked **[Design]** are specified but not yet validated on hardware.

### 3.1 Where it runs

| Mode | Where | Input | Output | Status |
|---|---|---|---|---|
| **A. Batch analysis** | The lab workstation that already receives the microscope's time-lapse export | Folder of 3D TIFF stacks (CTC layout or OME-TIFF), optional sensor CSV | Lineage graph, per-event certificate, `ablation`-style metrics when GT exists, JSON audit log | **[Measured]** (`evaluate.py`) |
| **B. Live monitoring** | Same workstation, connected to the OoC reader (piezo ADC + pressure sensor) and to the microscope's acquisition API | Continuous acoustic stream, pressure stream, periodic z-stacks | Real-time FLAG/STOP recommendations to the operator, event-triggered extra snapshot, same audit log | **[Design]** |

The engine is the same in both modes; mode B only adds sensor ingestion and an operator alert channel. No autonomous valve actuation is claimed: in mode B the software *recommends* and the operator *decides*. Firmware for closed-loop actuation is a roadmap item (Section 8).

### 3.2 How it listens: continuous acoustics, periodic imaging, event-triggered snapshots

* **Acoustic channel is continuous, not periodic [Design].** A contact piezo transducer at the channel inlet is sampled continuously at ≥ 250 kS/s (Nyquist for the ~110 kHz band below). The signal is band-passed and reduced to a **short-time energy envelope on 20 ms windows with 10 ms hop**; an event is declared when the envelope exceeds the rolling baseline by **3.5 σ** (the detector in `src/acoustic/processor.py`, currently exercised only on synthetic signals).
* **What a bubble sounds like [Design].** A free gas bubble of radius *R* rings at the Minnaert frequency *f* = (1/2π*R*)·√(3γP₀/ρ). With γ = 1.4, P₀ = 101.3 kPa, ρ = 997 kg/m³: *R* = 20 µm → 164 kHz; **30 µm → 109.6 kHz**; 50 µm → 66 kHz. The detector therefore watches an **80–180 kHz band**; a burst's centre frequency gives a bubble-size estimate, and medium viscosity/temperature shift it by a few percent, so the band is deliberately wide. *These values are computed, not measured on a chip.*
* **Imaging is periodic [Measured for analysis, Design for control].** Z-stacks are acquired every 5–15 min (the CTC data used here has Δt = 9.5 min). This cadence is enough for linking and division detection but **not** for anaphase kinematics (anaphase lasts 5–10 min → ≤ 1 frame); we therefore make no kinematic claim.
* **Event-triggered snapshot [Design].** An acoustic or pressure event sets a timestamp *T* and requests one additional z-stack within 60 s, so the frame "just after" the event exists even when the periodic cadence would miss it.

### 3.3 What each number means on a real cartridge — decision table

Reference geometry (one cartridge, one table, used consistently in code and text): channel **1000 × 100 µm**, length 25 mm, perfusion **10 µL/min**, medium viscosity 1 mPa·s.

| Quantity | How it is obtained | Expected value at baseline | **Continue** | **FLAG** (log + extra snapshot + operator notice) | **STOP perfusion recommended** | Status |
|---|---|---|---|---|---|---|
| Wall shear stress τ = 6µQ/(w h²) | from pump flow rate and cartridge geometry | **1.0 dyn/cm²** | 0.5 – 15 dyn/cm² (endothelial physiological range) | 15 – 30 dyn/cm² | > 30 dyn/cm² | [Design] computed; thresholds from literature ranges, not validated here |
| Pressure drop ΔP across channel | pressure sensor (a piezo cannot measure static ΔP) | Hagen–Poiseuille baseline for the cartridge (computed at setup) | < 1.5 × baseline | 1.5 – 2.5 × baseline (50 % occlusion ≈ 2.3 ×) | > 2.5 × baseline or rising > 20 %/min (membrane risk) | [Design] |
| Acoustic burst (80–180 kHz, > 3.5 σ) | continuous piezo stream | none | 0 bursts | 1 burst → timestamp *T*, snapshot; ≥ 3 bursts / 10 min → operator notice | ≥ 10 bursts / 10 min or any burst with ΔP flag | [Design] |
| Cells vanishing within ±1 frame of *T* | tracker: tracks ending at *T* ± 1 without a division | 0 | 0 | ≥ 1 → each cell marked **"mechanical-artefact candidate"**, excluded from drug-death counts pending review | — | [Design] (the exclusion logic uses the measured tracker) |
| Division proposal with gate penalty | ILP soft cost (volume ratio, mass conservation) | penalty 0 | penalty 0 → **PASS** | penalty > 0 but chosen by ILP → **FLAG for review** (shown with both daughters' volumes) | — | [Measured] mechanism; thresholds calibrated per detection source |
| Appear/disappear rate per frame | ILP a_j / d_i variables | low, stable | ≤ 2 × running median | > 2 × → **FLAG** (segmentation or focus problem) | sustained > 5 × → check focus/flow before continuing | [Design] rule on a measured quantity |
| DET / TRA | only when GT exists (benchmark mode) | — | — | — | — | [Measured] on CTC: TRA 0.997 / 0.996 with GT detections |

Reading the table: **green numbers mean the experiment is interpretable**; a FLAG never deletes data — it attaches a reason to an event and asks a human to look; a STOP is a recommendation to the operator, because the software does not control the pump today.

### 3.4 How this changes a researcher's work

*Before:* export time-lapse → run a tracker → manually scroll frames to delete obvious false divisions → count dead cells → hope none were torn off by a bubble you never saw.

*With AuraCell 4D (mode A today):* run `evaluate.py`-style batch → receive a lineage graph in which **false divisions are already rare (5 instead of 178 on the benchmark [Measured])**, each remaining division carries its gate penalty, and every edge is traceable to an ILP cost. Review time goes to the few FLAGGED events instead of the whole movie.

*With mode B (design):* the same graph additionally carries acoustic/pressure timestamps; cells that vanished right after a flow event are pre-labelled as artefact candidates and kept out of the dose–response count **with the reason written next to them** — the audit trail a regulator or a reviewer can follow.

---

## 4. Method

### 4.1 Detection
* **GT detections** — centroids and voxel volumes from the CTC TRA markers. DET = 1 by construction; isolates linking quality.
* **Label-free baseline** — Gaussian smoothing (σ = 0.5, 2, 2) → Otsu threshold → distance transform → watershed from local maxima (min. distance 12 px), objects < 400 voxels removed. Deliberately simple; it is the weakest component (Section 5).

### 4.2 Frame-pair network-flow ILP
For consecutive frames with detections *i* ∈ *t*, *j* ∈ *t*+1 and anisotropy-corrected Euclidean distances *D*ᵢⱼ (µm):

* variables: link *x*ᵢⱼ (if *D*ᵢⱼ ≤ 20 µm), division *y*ᵢ,(ⱼ₁,ⱼ₂) (both daughters within 25 µm of the parent and of each other), appear *a*ⱼ, disappear *d*ᵢ — all binary;
* constraints: Σⱼ *x*ᵢⱼ + Σ *y*ᵢ,· + *d*ᵢ = 1 for every *i*;  Σᵢ *x*ᵢⱼ + Σ *y*·,(ⱼ∈pair) + *a*ⱼ = 1 for every *j*;
* objective: Σ *D*ᵢⱼ *x*ᵢⱼ + Σ (*D*ᵢⱼ₁ + *D*ᵢⱼ₂ + *c*_div + *w*_gate · pen) *y* + *c*_app Σ(*a* + *d*), with *c*_div = 10, *c*_app = 30, *w*_gate = 40;
* solver: `scipy.optimize.milp` (HiGHS); ≈ 0.1 s per frame pair on CPU.

### 4.3 Biological gate as soft cost, calibrated from data
pen = max(0, ratio − ratio_max)/ratio_max + max(0, mass_min − mass)/mass_min + max(0, mass − mass_max)/mass_max, with ratio = V_big/V_small and mass = (V₁ + V₂)/V_parent. The bounds are the 5th–95th percentiles (±10 %) of the same statistics over GT divisions of the *calibration* sequence (02). **Finding:** on CTC TRA markers ratio ≡ 1.0 and mass ≡ 2.0 — the markers are uniform spheres, not segmentations. A hand-set "mass ≈ 1 ± 15 %" gate therefore rejects *every* true division (Section 5, row "original gate").

### 4.4 Baselines
`greedy_nogate` / `greedy_gate`: faithful port of the earlier nearest-neighbour tracker with and without the hard gate.

---

## 5. Results [Measured]

All numbers from `results/ablation.json`; official DET/TRA via `py-ctcmetrics`; mitosis P/R/F1 by matching predicted parent→daughter edges to GT daughters (±2 frames). Gate calibrated on seq 02 → **seq 01 is the independent test**; seq 02 rows are in-sample for the gate.

### 5.1 Linking quality with GT detections (DET = 1)

| seq | tracker | TRA | false/true divisions | mitosis P | R | F1 |
|---|---|---|---|---|---|---|
| 01 | greedy, no gate | 0.9276 | 178 / 4 | 0.006 | 0.25 | 0.011 |
| 01 | greedy + calibrated gate | 0.9587 | 86 / 4 | 0.023 | 0.50 | 0.044 |
| 01 | **ILP, no gate** | 0.9970 | 8 / 4 | 0.125 | 0.25 | 0.167 |
| 01 | **ILP + soft gate** | **0.9976** | **5 / 4** | 0.200 | 0.25 | **0.222** |
| 01 | greedy + original ±15 % gate | 0.9983 | **0 / 4** | — | 0 | 0 |
| 02 | greedy (± gate identical) | 0.9426 | 103 / 3 | 0.019 | 0.33 | 0.037 |
| 02 | ILP (± gate identical) | 0.9964 | 7 / 3 | 0 | 0 | 0 |
| 02 | greedy + original ±15 % gate | 0.9987 | **0 / 3** | — | 0 | 0 |

![Fig. 1 — TRA, GT detections](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/fig1_tra_gt_detections.png)
![Fig. 2 — divisions proposed](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/fig2_false_divisions.png)
![Fig. 5 — same real frame, greedy vs ILP](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/fig5_frame_overlay.png)

### 5.2 Robustness with label-free detection (Otsu + watershed)

| seq | DET | tracker | TRA | predicted divisions |
|---|---|---|---|---|
| 01 | 0.401 | greedy no gate / greedy gate / ILP no gate / **ILP + gate** | 0.365 / 0.391 / 0.389 / **0.392** | 578 / 19 / 176 / 63 |
| 02 | 0.526 | greedy no gate / greedy gate / ILP no gate / **ILP + gate** | 0.476 / 0.509 / 0.509 / **0.512** | 495 / 13 / 138 / 32 |

![Fig. 3 — Otsu robustness](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/fig3_otsu_robustness.png)
![Fig. 4 — gate calibration finding](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/fig4_gate_calibration.png)

### 5.3 What the results say
1. **ILP vs greedy is the measurable contribution:** +0.05–0.07 TRA and 20–35 × fewer false divisions at equal detections; the ordering holds under poor detections too.
2. **The soft gate helps a little, consistently** (TRA +0.0006 to +0.003; false divisions 8→5, 176→63, 138→32).
3. **Failure analysis.** Across the 18-configuration ablation (4 trackers × 2 detection modes × 2 sequences, including the earlier gate), the previous draft's ±15 % mass gate appeared to reach TRA 0.998 — because it rejected every true division (0 of 7): CTC TRA masks are uniform-size markers, so the daughter/parent mass ratio is always 2.0, never 1.0. We keep the row in the table and report it as a failure mode.
4. **Mitosis is unsolved here**: best F1 0.22; 0 on seq 02; only 7 GT events in total, so these numbers are not statistically stable.
5. **Detection is the bottleneck for label-free use**: DET 0.40/0.53. A learned segmenter is the obvious next step; the tracker cannot compensate.
6. Runtime 0.11–0.15 s/volume (CPU) on small 5-slice volumes; not a real-time claim.

---

## 6. Physics Consistency Checks [Design]

`src/verificators/` implements closed-form checks (Poiseuille shear, Minnaert resonance, Womersley number, Krogh diffusion length *L* = √(2DC₀/R), Hertz indentation, thin-plate deflection). They are **internal consistency unit tests** — each compares a formula with a reference constant written next to it — and are useful as sanity gates in Section 3.3. They are *not* validations against literature data, and we do not report "residual errors" as results. Reference geometry and ORR convention (Skala: FAD/(NADH+FAD)) are unified across code and text.

---

## 7. Limitations (stated plainly)

* Fluo-N3DH-CHO is conventional culture, not OoC; no real OoC or acoustic recordings were available to us.
* Mitosis detection is weak and the GT sample is tiny; conclusions about divisions are preliminary.
* The gate calibrated on TRA markers does not transfer to real segmentations; it must be recalibrated per detection source.
* Label-free detection baseline is poor; results in 5.2 are a robustness check, not a deployable pipeline.
* Anaphase kinematics cannot be measured at 9.5 min/frame.
* Every row in Section 3.3 marked [Design] — acoustic detection on hardware, pressure thresholds, STOP rules — is unvalidated. The firmware header in the repo is an interface declaration only; the HIL script is a Python simulation whose latency numbers mean nothing about hardware.
* Hyperspectral/redox gating is a concept; no spectral data were used.

---

## 8. Roadmap
1. Learned 3D nuclear segmenter (e.g., Cellpose-3D / StarDist-3D) to lift DET above 0.9 on label-free data.
2. Multi-frame (gap-closing) ILP; calibrate the gate on true segmentations.
3. Acquire a real OoC time-lapse with a synchronised inlet piezo + pressure log; validate Section 3.3 thresholds; publish the recordings.
4. Operator-in-the-loop live mode; only then firmware.

---

![GUI Step 4 — measured-results panel](https://raw.githubusercontent.com/syehsyoh-dokling/Auracell4D/main/docs/figures/gui_step4.png)

## 9. Reproduction
```bash
pip install -r requirements.txt
python evaluate.py --data ./data --out ./results          # full ablation (≈15–30 min CPU)
python evaluate.py --seqs 01 --detect gt --trackers ilp_gate   # quick check
```
Outputs: `results/ablation.md`, `results/ablation.json`, CTC-format result folders. External libraries: numpy, scipy (HiGHS MILP), scikit-image, tifffile, py-ctcmetrics.

---

## 10. References (verified DOIs)
1. Ulman V., Maška M., et al. *An objective comparison of cell-tracking algorithms.* Nat Methods 14(12):1141–1152 (2017). doi:10.1038/nmeth.4473
2. Huh D., et al. *Reconstituting organ-level lung functions on a chip.* Science 328:1662–1668 (2010). doi:10.1126/science.1188302
3. Minnaert M. *On musical air-bubbles and the sounds of running water.* Phil. Mag. 16(104):235–248 (1933). doi:10.1080/14786443309462277
4. Skala M.C., et al. *In vivo multiphoton microscopy of NADH and FAD redox states… in precancerous epithelia.* PNAS 104(49):19494–19499 (2007). doi:10.1073/pnas.0708425104
5. Cell Tracking Challenge, Fluo-N3DH-CHO dataset page: https://celltrackingchallenge.net/3d-datasets/
6. FDA Modernization Act 2.0, Public Law 117-328 (2022).
