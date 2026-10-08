# CLAIM AUDIT LOG — the earlier AuraCell 4D draft

**Audit date:** 8 October 2026 · **Competition deadline:** 10 October 2026
**Audited documents:** the previous `LAPORAN_TEKNIS_LENGKAP_AURACELL_4D.md` (Indonesian technical report) and the `writeup.md` synchronised with it — both now archived under `docs/id/` and `_deprecated/`.
**Method:** (1) recomputation of physics formulas; (2) static analysis and execution of the repository code; (3) reference verification via CrossRef / Zenodo / the Cell Tracking Challenge site; (4) real execution on Google Colab against the official Fluo-N3DH-CHO data with `py-ctcmetrics`; (5) inventory of the Google Drive folder `AuraCell4D_Datasets`.
**Artefacts:** `audit/audit_local_claims.py` → `audit/audit_local_results.{md,json}` · `audit/colab_claim_audit.py` → `audit/colab_claim_results.json` (raw outputs are in Indonesian; this document is the English record).

Verdict scale: **PROVEN** · **PARTIAL** · **DISPROVEN** (contradicted by facts) · **UNSUPPORTED** (number produced by no code or data) · **UNTESTABLE**.
Action taken: **KEEP** · **DOWNGRADE** (replace with the measured value) · **REFRAME** (state as simulation/concept) · **REMOVE**.

---

## 0. Summary

| | Count |
|---|---:|
| Claims audited | 46 |
| PROVEN | 1 |
| PARTIAL | 2 |
| DISPROVEN | 19 |
| UNSUPPORTED | 21 |
| UNTESTABLE | 3 |

**Three decisive facts**
1. **Google Drive `AuraCell4D_Datasets` was empty (0 files).** The claims "10,000 micro-acoustic recordings on Drive", "CTC dataset on Drive" and "AURASENSAI model" had no artefact at all.
2. **The original tracker, run on real CTC data, detected 0 of 16 mitoses** (recall 0 %, F1 0.0) while the report stated Mitosis F1 0.991 and the writeup 0.906. All CTC scores in the repository were hand-written literals.
3. **The core formula of §4.1.4 was wrong:** τ for 1000×100 µm @ 10 µL/min = 1.0 dyn/cm², not 2.5. Minnaert for 30 µm = 109.6 kHz, not "exactly 108.5 / 0.000 %". The Krogh formula as written (factor 6) does not give 151 µm.

---

## 1. Physics & formulas (§4.1.4, §5.1, Ch. 8 of the old report)

| ID | Claim (location) | Test | Fact | Verdict | Action |
|---|---|---|---|---|---|
| P01 | τ_GT = 6μQ/wh² = **2.500** dyn/cm² for w=1000, h=100 µm, Q=10 µL/min | recomputation | **1.000 dyn/cm²**. 2.5 only if w=400 µm (hard-coded in `fluid_cfd_verificator.py:24`); `fluid_gate.py` used 100×50 → 40 dyn/cm². Three geometries for "the same cartridge". | DISPROVEN | DOWNGRADE: 1.0 dyn/cm²; unify geometry everywhere |
| P02 | Minnaert R=30 µm → **108.5 kHz exactly**, residual 0.000 % | recomputation | 109.6 kHz. The program's own JSON: 109.61 vs 108.8 → 0.741 %. | DISPROVEN | DOWNGRADE: 109.6 kHz; drop "exactly" |
| P03 | Table Ch. 8: per-row residuals (mostly 0.000 %) | compare with `benchmarks/ground_truth_verification_results.json` | Row 1: table 0.000 % vs JSON 0.741 %; "computed" values copied from the GT column. | DISPROVEN | DOWNGRADE: copy JSON values verbatim |
| P04 | 15 benchmarks = "validation against international gold standards" | AST of verificators | Every `gt_expected` is a literal constant written on the line after the same formula → formula compared with itself. | UNSUPPORTED | REFRAME: "internal solver consistency unit tests" |
| P05 | Krogh R_c = √(6DC₀/Q) = 151.186 µm | compute both versions | Report formula (factor 6) → **262 µm**; code uses factor 2 → 151 µm. | DISPROVEN | DOWNGRADE: fix the formula |
| P06 | Womersley α = 0.1371 | compute | 0.1371 ✓ | PROVEN | KEEP (without a "literature GT" label) |
| P07 | PDMS deflection 216.0 µm "FEBio Mooney-Rivlin" | read code | Empirical thin-plate formula `0.662·a·(pa/Et)^(1/3)`; no FEBio, no Mooney-Rivlin. | UNSUPPORTED | REFRAME |
| P08 | Bubble → τ spikes to **18.2 dyn/cm²** via Navier-Stokes/Rayleigh-Plesset | formula analysis + grep | τ=6μQ/wh² is steady Poiseuille; a bubble does not change Q. Rayleigh-Plesset: 0 implementations. | UNSUPPORTED | REMOVE |
| P09 | Anaphase criterion 1.20±0.25 µm/min measurable at 5–15 min sampling | dataset Δt 9.5 min vs anaphase 5–10 min | 0.5–1 frame in anaphase → velocity not measurable. | DISPROVEN | REMOVE |
| P10 | ADC 500 kS/s, target ESP32-S3 | Nyquist; ADC specs | 500 kS/s > 2×108 kHz ✓ for Cortex-M7 + external ADC; ESP32-S3 internal ADC ≈ 83 kS/s max. | PARTIAL | DOWNGRADE: drop ESP32-S3 |
| P11 | PZT-03 records ΔP > 500 Pa | chip_spec + HIL | PZT-03 is a 1–10 kHz acoustic transducer; cannot measure static ΔP. HIL injects 144/850 Pa with `np.random`. | UNSUPPORTED | REFRAME: separate pressure sensor |
| P12 | "2,800× faster than the 20 ms limit" | 20/0.007 | Arithmetic fine; premise (0.007 ms) invalid → see C07 | UNSUPPORTED | REMOVE |

## 2. Code behaviour vs claims

| ID | Claim | Test | Fact | Verdict | Action |
|---|---|---|---|---|---|
| C01 | CTC scores (DET/TRA/Mitosis F1) are an empirical evaluation | AST `real_ctc_evaluator.py` | `det_score=0.942`, `tra_score=0.918`, … literals (lines 98–103). TIFFs never read, tracker never called. | UNSUPPORTED | DOWNGRADE to measured |
| C02 | Colab notebook produces the CTC scores | notebook cell 12 | Dict literal; GT only counted. | UNSUPPORTED | DOWNGRADE |
| C03 | "Kaggle composite 0.99254", status "Scored (Verified)" | `evaluation_harness.py` + competition page | Profiles v1–v4 are a dict literal; CSV and back-dated timestamps generated by code; the competition is writeup-only and has no leaderboard. | UNSUPPORTED | REMOVE |
| C04 | Velocell = network-flow ILP | grep solvers | `pulp` never imported; greedy nearest-neighbour. | DISPROVEN | implemented a real ILP (`evaluate.py`) |
| C05 | AURASENSAI (AudioMAE+AST+Whisper BiGRU) evaluated on 10,000 samples | grep src, requirements, Drive | No model, no weights; manifest JSON random; `y_prob` derived from `y_true`. | UNSUPPORTED | REMOVE |
| C06 | FP=42, FN=30 | notebook construction | noise<0.005, threshold 0.5 → FP=FN=0 by construction. 42/30 cannot come from that cell. | UNSUPPORTED | REMOVE |
| C07 | Firmware ready to flash; valve in 0.007 ms | header + HIL | Header: 4 declarations, 0 implementations. 0.007 ms = `perf_counter` around one Python `if`. | UNSUPPORTED | REFRAME |
| C08 | Matched filter + FFT confirms 108.5 kHz | `processor.py` | 44.1 kHz sampling (Nyquist 22 kHz) → 108 kHz impossible; no FFT/correlation. | UNSUPPORTED | REFRAME/REMOVE |
| C09 | Event-triggered camera mode | grep | Not implemented. | UNSUPPORTED | REFRAME: concept |
| C10 | Evidence Gate = OpenFOAM + FEBio + PhysiCell | grep | Names only in docstrings; one-line analytic formulas. | DISPROVEN | REMOVE solver names |
| C11 | Causal reconciliation (T_anomaly + ORR + lineage) → artefact verdict | search | No module combines the three. | UNSUPPORTED | REFRAME: concept |
| C12 | Mitosis veto ORR ≥ 0.45, ORR=NADH/(NADH+FAD) | compare docs & code | Code: ORR=FAD/(NADH+FAD), reject >0.50; writeup §3.5: "<0.40"; healthy GT 0.3208 → healthy cells could never divide. | DISPROVEN | one definition (Skala), one threshold |
| C13 | Volume conservation ±10 % | code | ±15 % and daughter ratio 0.75–1.35. | DISPROVEN | DOWNGRADE |
| C14 | 3D morphology indicators (rounding, furrow) | grep | No morphology features; centroids only. | UNSUPPORTED | REMOVE |
| C15 | Anaphase kinematics checked per mitosis proposal | code | Not computed. | UNSUPPORTED | REMOVE |
| C16 | Repository tests prove the pipeline | run tests | Run without errors, but synthetic data and no asserts; pytest finds 0 tests. | PARTIAL | DOWNGRADE |

## 3. Real execution on Colab (official CTC data)

| ID | Test | Result | Related claim | Verdict |
|---|---|---|---|---|
| K1 | Drive `AuraCell4D_Datasets` inventory | **0 files**; only 2 empty folders | "10,000 dataset on Drive" | UNSUPPORTED |
| K5 | Model weights in Drive/repo | none | AURASENSAI ensemble | UNSUPPORTED |
| K2 | Fluo-N3DH-CHO metadata | CHO GFP-PCNA, confocal LSM 510, voxel 0.202×0.202×1.0 µm, Δt 9.5 min, Erasmus MC; 27+24 tracks, 10+6 daughter tracks, 92 frames, 5 z-slices | "microfluidic 3D light-sheet", "0.2 µm isotropic", "real OoC data" | DISPROVEN |
| K3 | Original tracker on GT centroids, `py-ctcmetrics` | seq01: DET 1.000, TRA 0.9983, **mitoses 0/10**; seq02: DET 1.000, TRA 0.9987, **mitoses 0/6** | DET 0.942/0.9961, TRA 0.918/0.9942, Mitosis F1 0.906/0.991 | UNSUPPORTED |
| K4 | Anaphase measurability | 0.5–1 frame | criterion §4.1.3 #2 | DISPROVEN |

Note on K3: `AOGM_EA` = 11 and 6 is exactly the number of parent→daughter edges missed; the hard gate rejected every real division. The "anti-hallucination veto" on real data deleted all true mitoses.

## 4. Cross-document consistency

| ID | Quantity | Report | Writeup | Code | Verdict |
|---|---|---|---|---|---|
| D01 | Acoustic F1 | 0.9912 & 0.98973 | 0.983 | — | DISPROVEN |
| D02 | CTC TRA/DET/F1 | 0.9942/0.9961/0.9910 | 0.918/0.942/0.9056 | harness: DET 0.9942 (labels swapped) | DISPROVEN |
| D03 | Actuation latency | 0.007 ms | <0.005 ms | perf_counter | DISPROVEN |
| D04 | ORR mitosis threshold | ≥0.45 | ≥0.45 & <0.40 | >0.50 reject; 0.55 viability | DISPROVEN |
| D05 | Volume tolerance | ±10 % | ±10 % | ±15 % | DISPROVEN |
| D06 | Minimum mitosis interval | "<40 min rejected" | <40 min | gate: <20 min; verificator 40–90 | DISPROVEN |

## 5. References & administrative

| ID | Claim | Fact | Verdict |
|---|---|---|---|
| E01 | Repo `github.com/saifuddin-ai/AuraCell-4D` | HTTP 404 (replaced by `github.com/syehsyoh-dokling/Auracell4D`) | DISPROVEN → fixed |
| E02 | Maas et al. 2023, Zenodo 10.5281/zenodo.8291410 (microfluidic acoustic dataset) | Record = "Fig. 1 in Hypoxylonoids A–G…", *Phytochemistry* 2021 — fungal chemical structures | FICTITIOUS → removed |
| E02b | Zenodo 11186716 "APECSS Cavitation Bubbles" | Uzbek-language paper on child speech development (1 PDF) | FICTITIOUS → removed |
| E02c | BubbleML (HPCForge) "bubble nucleation/burst" | Boiling **simulation** fields; no audio, not microfluidic | MISDESCRIBED → removed |
| E02d | HF `luviner/industrial-faults` "6,500 industrial anomaly sounds" | Synthetic **tabular** sensor data, not audio | MISDESCRIBED → removed |
| E02e | Datathon@IndoML 2026 "5,517 clips, AURASENSAI rank #1" | Track 1 = noise events in Indic speech (90,637 segments); phase-1 top-8 lists "Syehsyoh" 3rd; final TBA | DISPROVEN → removed |
| E03 | Theriot & Mitchison 1991 = anaphase kinematics | "Actin microfilament dynamics in locomoting cells" | DISPROVEN → removed |
| E03b | "Krogh" DOI 10.1113/jphysiol.1919.sp001843 | CrossRef: Herring P.T., electric organs of skate — not Krogh | WRONG DOI → removed |
| E04 | "Māšik et al. 2018, Nat Methods 14(12):1141" | Ulman, Maška et al., 2017, doi:10.1038/nmeth.4473 | WRONG CITATION → fixed |
| E05 | Huh 2010 reports 2.5 dyn/cm² as GT | Value came from the formula with w=400 µm, not from the paper | UNSUPPORTED → reframed |
| E06 | "AURASENSAI world #1 at Datathon@IndoML 2026" | No evidence link | UNTESTABLE → removed |
| E07 | "Bioengineering & Clinical Specialist" team member (+0.5 bonus) | No name/affiliation | UNTESTABLE → bonus not claimed |
| E08 | Reproducible repo (README, entry script, demo video) | README/`evaluate.py` missing; video placeholder; `data/` empty; notebook needed Drive login | DISPROVEN → fixed (video pending) |
| E09 | Organiser registration form | No evidence of submission | UNTESTABLE → owner's task |

---

## 6. What the current submission keeps (honest version)

1. **ILP linking** measured on CTC with official metrics (TRA 0.998/0.996 with GT detections; 178→5 false divisions), reproduced on two machines.
2. **Analytic physics checks** as internal unit tests, not literature validation.
3. **Sensor-fusion design** (continuous acoustics + periodic imaging + decision table) stated as design, with no performance claim.
4. **The GUI**, with every simulated panel labelled as such and a measured-results panel wired to `evaluate.py`.

All removed material remains in `_deprecated/` and `docs/id/` as evidence of what was changed and why.
