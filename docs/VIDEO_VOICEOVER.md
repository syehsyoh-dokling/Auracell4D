# AuraCell 4D — Demo Video Voice-Over (English, ≈3:55, ≈560 words at 145 wpm)

> Positive, value-first narration for the demo video. Limitations and failure analysis are documented in `docs/TECHNICAL_REPORT.md` §8 and `docs/AUDIT_LOG.md` and are covered in the Q&A, not in the video.
> Two short factual anchors stay in the script because the claims depend on them: the live monitor is a *scripted scenario*, and the TRA figures are measured *with reference detections*.
> Screen cues in *italics*; URL parameters jump the demo pages (`gui/demo/index.html`, 1600×900) to the exact moment.

---

**[0:00–0:25] THE OPPORTUNITY**
*Screen: `?page=1&step=6`, then Fig. 5 (real frame; greedy fork vs clean ILP lineage).*

Organ-on-a-chip experiments produce thousands of 3-D frames of living cells. To know whether a drug works, every cell's lineage must be reconstructed: who moved, who divided, who died. Conventional trackers decide frame by frame — and whenever two nuclei touch, they invent a division: on one public sequence with four real divisions, a greedy tracker proposed one hundred seventy-eight. AuraCell 4D was built to make that lineage trustworthy — and auditable.

**[0:25–0:55] WHERE THE TOOL WORKS**
*Screen: `?page=1`, auto-advancing stages 1→8.*

Here is the full flow. The lab fabricates the cartridge and seeds the cells. AuraCell 4D takes over at docking: geometry and flow rate are recorded, and the physical baseline is computed — one point zero dyne per square centimetre of wall shear for a thousand-by-hundred-micron channel. From the first second of perfusion, the acoustic channel listens continuously, while the microscope keeps its periodic cadence every nine and a half minutes. Then the algorithm runs: detection, global linking, biological gate. Every event receives a certificate — continue, flag, or stop — the researcher stays in command, and the loop restarts at the next dose.

**[0:55–1:20] THE ALGORITHM**
*Screen: `?page=1&step=6`, link / divide / appear / disappear diagram.*

For each pair of frames we solve one integer linear program: every nucleus takes exactly one fate — link, divide, or disappear — and every nucleus in the next frame has exactly one origin. Biology enters as a cost, not a ban: a division with implausible daughter volumes becomes expensive, so the optimiser avoids it unless the evidence is strong. And that cost is calibrated from the data itself.

**[1:20–2:15] THE KEY INCIDENT — DRUG OR BUBBLE?**
*Screen: `?page=2&t=10&play=1`, 2× speed, run to minute ≈28.*

Now the live monitor, running a scripted scenario. Minute twelve: the acoustic channel catches a burst at one hundred nine point six kilohertz — the Minnaert frequency of a thirty-micron bubble. The system stamps the time T and requests one extra snapshot. Next frame: tracks three and ten are gone. AuraCell 4D recognises them as mechanical-artefact candidates and keeps them out of the drug-death count — with the reason written down. Watch the counter: a naive count says two; AuraCell says zero.
*Screen: minute 24.*
Minute twenty-four: another transient, sixty-two kilohertz. Outside the bubble band — a pump harmonic. Logged, ignored, nothing excluded. The system reacts to evidence, not to noise.
*Screen: cut to `?page=2&t=96&play=1`, stop at minute ≈102.*
Minute ninety-eight: track seven ends with no mechanical event nearby. This one is a genuine drug-associated death, and it counts. Naive count: three. AuraCell: one — with both exclusions explained in the audit trail. That is the number a researcher can defend.

**[2:15–2:27] SAFETY — OPERATOR IN COMMAND**
*Screen: `?page=2&t=55`, 3–4 s.*

In between, pressure climbed to two point six times baseline. The system flagged it early, recommended a stop, and the operator lowered the flow. The decision stays human; the evidence comes from the tool.

**[2:27–3:10] RESULTS**
*Screen: `?page=3`, animated bars and the 178 → 5 counter.*

Measured with the official Cell Tracking Challenge metrics on public data, with reference detections: the ILP raises the TRA score from point nine two eight to point nine nine eight on sequence one, and from point nine four three to point nine nine six on sequence two. False divisions drop from one hundred seventy-eight to five. The whole evaluation reproduces identically on Colab and on a local laptop with a single command — and the GUI runs it from one button, then exports the audit trail.

**[3:10–3:50] WHO BENEFITS & CLOSE**
*Screen: `?page=4`.*

The first beneficiary is the bench scientist, who now reviews a handful of flagged events instead of the whole movie. Downstream, the same audit trail is exactly what regulators ask for as organ-on-a-chip data replaces animal testing. Every number in our report carries a label — measured or design — so reviewers always know which is which. Next on the roadmap: a learned 3-D segmenter, a real chip recording with a synchronised acoustic channel, then hardware. AuraCell 4D: trustworthy lineages, every number labelled, every decision explainable.

---

## Demo pages used (`gui/demo/index.html`)

| Page | Segment | Shows |
|---|---|---|
| 1 Workflow | 0:00–1:20 | 8-stage animated stepper, lab vs AuraCell 4D, loop |
| 2 Live monitor | 1:20–2:27 | scripted 130-min scenario; counterfactual counter "naive vs AuraCell" |
| 3 Measured results | 2:27–3:10 | animated TRA bars, 178 → 5 counter |
| 4 Measured vs Design | 3:10–3:50 | closing two-column slide |

## Shot list

| Time | Screen | URL / source |
|---|---|---|
| 0:00 | Stage 6 + Fig. 5 | `?page=1&step=6`; `docs/figures/fig5_frame_overlay.png` |
| 0:25 | Workflow auto-advance | `?page=1` |
| 0:55 | Stage 6 + ILP diagram | `?page=1&step=6`; slide from writeup §4.2 |
| 1:20 | Key incident, part 1 | `?page=2&t=10&play=1` (2×, ≈9 s real time) |
| 1:55 | Key incident, part 2 | `?page=2&t=96&play=1` (≈3 s), zoom on "naive vs AuraCell" |
| 2:15 | Pressure flag → operator | `?page=2&t=55` (static, 3–4 s) |
| 2:27 | Measured results | `?page=3` |
| 3:10 | Close | `?page=4` |
