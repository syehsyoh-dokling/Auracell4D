# AuraCell 4D — Demo Video Voice-Over (English, target 3:50–4:00, ≈570 words at 145 wpm)

> Condensed section-by-section from the Indonesian script (`docs/id/VIDEO_VOICEOVER_ID.md`, 5:20) without dropping any substantive point.
> Every spoken number is **[Measured]** (`results/ablation.json`) or explicitly called design/simulation. Do not ad-lib figures.
> Screen cues in *italics*; URL parameters jump the demo pages (`gui/demo/index.html`, 1600×900) to the exact moment.

---

**[0:00–0:25] THE REAL PROBLEM** — 62 words
*Screen: `?page=1&step=6`, then Fig. 5 (real frame with a false division fork).*

Organ-on-a-chip experiments produce thousands of 3-D frames of living cells. To know whether a drug works, every cell's lineage must be reconstructed: who moved, who divided, who died. Today's trackers decide frame by frame — and whenever two nuclei touch, they invent a division. On one public sequence with four real divisions, a greedy tracker proposed one hundred seventy-eight. And no tracker can tell a drug death from a cell torn off by a bubble. Those errors go straight into dose–response numbers.

**[0:25–0:55] WHERE THE TOOL WORKS** — 78 words
*Screen: `?page=1`, auto-advancing stages 1→8.*

The full flow. Cartridge fabrication and cell seeding belong to the lab, not to us. AuraCell 4D starts at docking: geometry and flow rate are recorded, and the physical baseline is computed — one point zero dyne per square centimetre of wall shear for a thousand-by-hundred-micron channel. From the first second of perfusion the acoustic channel listens continuously, while the microscope keeps its periodic cadence, every nine and a half minutes. Then our algorithm runs: detection, global linking, biological gate. Every event receives a certificate — continue, flag, or stop — and the researcher decides, before the loop restarts at the next dose.

**[0:55–1:20] THE ALGORITHM** — 60 words
*Screen: `?page=1&step=6`, link / divide / appear / disappear diagram.*

For each pair of frames we solve one integer linear program: every nucleus must take exactly one fate — link, divide, or disappear — and every nucleus in the next frame exactly one origin. Biology enters not as a ban but as a cost: a division with implausible daughter volumes becomes expensive, not forbidden. And that cost is calibrated from data, not typed in by hand.

**[1:20–2:15] THE KEY INCIDENT — DRUG OR BUBBLE?** — 150 words
*Screen: `?page=2&t=10&play=1`, 2× speed, run to minute ≈28.*

Now the live monitor — a scripted simulation, not a hardware recording. Minute twelve: the acoustic channel catches a burst at one hundred nine point six kilohertz — the Minnaert frequency of a thirty-micron bubble. The system stamps the time T and requests one extra snapshot. Next frame: tracks three and ten are gone. A plain tracker would count two drug deaths. AuraCell 4D marks them as mechanical-artefact candidates and excludes them — with the reason written down. Watch the counter: naive two, AuraCell zero.
*Screen: minute 24.*
Minute twenty-four: another transient, sixty-two kilohertz. Outside the bubble band — a pump harmonic. Logged, ignored, nothing excluded. The tool does not panic at every sound.
*Screen: cut to `?page=2&t=96&play=1`, stop at minute ≈102.*
Minute ninety-eight: track seven ends with no mechanical event nearby. This one counts as a drug-associated death. The naive count now reads three; ours reads one — and both exclusions carry their own reason in the audit trail.

**[2:15–2:27] SAFETY — AS A RECOMMENDATION** — 34 words
*Screen: `?page=2&t=55`, 3–4 s.*

In between, pressure rose to two point six times baseline. The system recommended a stop; the operator lowered the flow. The software does not control the pump — that part is design, not yet validated.

**[2:27–3:15] RESULTS — HONESTLY** — 128 words
*Screen: `?page=3`, animated bars; then the limitations box.*

What we actually measured, with the official Cell Tracking Challenge metrics: on public data with ground-truth detections, the ILP raises the TRA score from zero point nine two eight to zero point nine nine eight on sequence one, and from zero point nine four three to zero point nine nine six on sequence two. False divisions drop from one hundred seventy-eight to five. The result reproduces identically on Colab and on a local laptop with one command. We also report what does not work yet: mitosis recall is low, our label-free detector reaches a DET of only zero point four to zero point five, and the data is conventional culture, not a real chip. One more thing: our earlier gate scored a TRA of zero point nine nine eight — by rejecting every real division. We kept that row in the table.

**[3:15–3:50] WHO BENEFITS & CLOSE** — 72 words
*Screen: `?page=4`.*

The first beneficiary is the bench scientist, who now reviews a handful of flagged events instead of the whole movie. Downstream, that same audit trail is what regulators ask for when organ-on-a-chip data replaces animal testing. Next steps: a learned 3-D segmenter, a real chip recording with a synchronised acoustic channel, and only then hardware. AuraCell 4D: fewer hallucinated divisions, every number labelled, every decision explainable.

---

## Condensation map (Indonesian 5:20 → English ≈3:50)

| Section | ID words | EN words | What was compressed (substance kept) |
|---|---|---|---|
| Problem | 108 | 62 | merged the two "tracker" sentences; kept 178 vs 4 and drug-vs-bubble |
| Where it works | 118 | 78 | one sentence per stage; kept docking baseline 1.0 dyn/cm², continuous vs 9.5-min periodic, certificates, researcher decides, loop |
| Algorithm | 73 | 60 | kept one-fate/one-origin, soft cost, calibrated from data |
| Key incident | 190 | 150 | kept all three beats: 109.6 kHz/30 µm/T/snapshot → tracks 3 & 10 → naive 2 vs 0; 62 kHz ignored; track 7 → 3 vs 1 with reasons |
| Safety | 44 | 34 | kept 2.6×, recommendation, operator, not validated |
| Results | 150 | 128 | kept all four numbers, 178→5, reproduction, three limitations, old-gate failure row |
| Close | 86 | 72 | kept scientist, regulators/animal testing, roadmap, tagline |

## Demo pages used (`gui/demo/index.html`)

| Page | Segment | Shows | On-screen label |
|---|---|---|---|
| 1 Workflow | 0:00–1:20 | 8-stage animated stepper, ecosystem vs AuraCell 4D, loop | DESIGN · animated explainer |
| 2 Live monitor | 1:20–2:27 | scripted 130-min scenario; counterfactual counter "naive vs AuraCell" | SIMULATION · no hardware |
| 3 Measured results | 2:27–3:15 | animated TRA bars, 178 → 5 counter, limitations | [MEASURED] |
| 4 Measured vs Design | 3:15–3:50 | closing two-column slide | closing |

## Shot list

| Time | Screen | URL / source |
|---|---|---|
| 0:00 | Stage 6 + Fig. 5 | `?page=1&step=6`; `docs/figures/fig5_frame_overlay.png` |
| 0:25 | Workflow auto-advance | `?page=1` |
| 0:55 | Stage 6 + ILP diagram | `?page=1&step=6`; slide from writeup §4.2 |
| 1:20 | Key incident, part 1 | `?page=2&t=10&play=1` (2×, ≈9 s real time) |
| 1:55 | Key incident, part 2 | `?page=2&t=96&play=1` (≈3 s), zoom on "naive vs AuraCell" |
| 2:15 | Clog STOP | `?page=2&t=55` (static, 3–4 s) |
| 2:27 | Measured results | `?page=3` |
| 3:15 | Close | `?page=4` |
