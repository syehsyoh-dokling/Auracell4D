# ABSTRACT

## AuraCell 4D: Physics-Gated Network-Flow ILP Lineage Tracking for Organ-on-a-Chip Time-Lapse Microscopy

**Saifuddin** — AI4S Open Innovation: AI for Life Science (The 5th Pazhou Algorithm Competition), category *Model & Algorithm*.
Code & results: https://github.com/syehsyoh-dokling/Auracell4D · entry script `evaluate.py`

---

**Background.** Organ-on-a-chip (OoC) experiments produce thousands of 3D+time images that must be turned into cell lineages: who moved where, who divided, who died. Standard trackers that decide frame by frame in a *greedy* manner "hallucinate" a division whenever two nuclei come close — on one public sequence with only 4 true divisions, a greedy tracker proposed 178. Such errors flow directly into dose–response curves and cannot be audited.

**Method.** AuraCell 4D formulates inter-frame linking as a network-flow *integer linear program*: every nucleus at frame *t* must take exactly one fate (link, divide, disappear) and every nucleus at frame *t+1* exactly one origin (link, daughter, appear). Biological knowledge — daughter-volume ratio and mass conservation — is not used as a hard veto but as a **soft cost calibrated from the data distribution**, so implausible divisions are discouraged rather than blindly discarded. Solver: `scipy.optimize.milp` (HiGHS), ≈0.1 s per frame pair on CPU.

**Results [Measured].** On the public *Cell Tracking Challenge* dataset Fluo-N3DH-CHO (2 sequences × 92 frames; official `py-ctcmetrics`), with detections taken from ground truth to isolate linking quality, the ILP raises TRA from **0.928 → 0.998** (seq 01) and **0.943 → 0.996** (seq 02) over the greedy baseline and cuts false divisions from **178 → 5**. The soft gate adds a small, consistent gain. The results were reproduced identically to four decimals on Colab and on a local Windows machine with a single command and no login.

**Findings & limitations (stated openly).** Across an ablation of 18 configurations (4 trackers × 2 detection modes × 2 sequences, including the earlier gate), we found that the previous draft's gate with a ±15 % mass threshold appeared to reach TRA 0.998 — because it **rejected every true division** (0 of 7): CTC ground-truth TRA masks are uniform-size markers, not segmentations, so the daughter/parent mass ratio is always 2.0, never 1.0. We keep that row in the results table and report it as a failure analysis. Mitosis recall remains low (best F1 0.22, only 7 GT events), the label-free detection baseline is weak (DET 0.40–0.53), and Fluo-N3DH-CHO is conventional culture, not a real chip.

**Operational design [Design].** The same engine is designed to ingest a **continuous** acoustic channel (piezo ≥250 kS/s, Minnaert band 80–180 kHz; a 30 µm bubble rings at ≈109.6 kHz) alongside **periodic** imaging (5–15 min), with a CONTINUE / FLAG / STOP decision table tied to the reference cartridge geometry (1000 × 100 µm, 10 µL/min → τ = 1.0 dyn/cm²). Cells that vanish right after a flow event are labelled "mechanical-artefact candidates" and excluded from drug-death counts **with the reason written next to them**. This part is documented and not yet validated on hardware.

**Contributions & impact.** (1) A gated ILP tracker that measurably outperforms greedy linking on official metrics; (2) a labelling discipline — every number is tagged *[Measured]* or *[Design]*; (3) a published failure analysis; (4) a local interface that runs the evaluation from a button and exports an audit trail. The immediate beneficiary is the bench scientist, who now reviews a handful of flagged events instead of the whole movie; downstream, the same traceability is what regulators and reviewers ask for when OoC data replaces animal testing.

**Keywords:** organ-on-a-chip, 3D+t cell tracking, integer linear programming, network flow, Cell Tracking Challenge, biophysical gate, reproducibility, auditability.
