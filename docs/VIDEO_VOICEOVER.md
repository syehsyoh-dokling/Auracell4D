# AuraCell 4D — Demo Video Voice-Over (English, ≈4 minutes, ~590 words at 145 wpm)

> Every number spoken below is either **[Measured]** (from `results/ablation.json`) or explicitly called a **design**. Do not ad-lib performance figures.
> Screen cues in *italics*. Target total: 3:50–4:00.

---

**[0:00–0:35] THE REAL PROBLEM**
*Screen: a time-lapse of nuclei; two nuclei drift close; a tracker draws a false "division" fork.*

Organ-on-a-chip experiments produce thousands of 3-D frames of living cells. To measure how a drug works, a researcher must reconstruct every cell's lineage: who moved where, who divided, who died. Today that job is done by trackers that decide one frame at a time. When two nuclei merely touch, they invent a division. On a public benchmark sequence with only four real divisions, a standard greedy tracker proposed one hundred and seventy-eight. And no tracker, by itself, can tell a cell that died from a cell that was torn off by a bubble in the channel. Those errors flow straight into dose-response numbers.

**[0:35–1:10] WHY THIS APPROACH FIXES IT**
*Screen: diagram — frame t and t+1, arrows for link / divide / appear / disappear.*

AuraCell 4D replaces frame-by-frame guessing with a global decision. For every pair of consecutive frames we solve a small integer linear program: each nucleus at time t must take exactly one fate — link, divide, or disappear — and each nucleus at the next frame must have exactly one origin. Biology enters not as a hard veto but as a soft cost: implausible volume ratios and broken mass conservation make a division expensive, not forbidden. And those costs are calibrated from data, not typed in by hand.

**[1:10–1:45] WHAT IS DIFFERENT ABOUT IT**
*Screen: the ablation table, rows for greedy vs ILP highlighted.*

Three things make this different. First, it is measured with the official Cell Tracking Challenge metrics, reproducible by anyone with one command and no login. Second, every number in our report carries a label — measured, or design — so a reviewer always knows which is which. Third, we publish our own failure analysis: an earlier version of our gate scored a tracking accuracy of 0.998 — and it got there by rejecting every single real division. We found out, we explain why, and we kept the row in the table.

**[1:45–2:40] HOW IT WORKS — THE FLOW**
*Screen: run `python gui/launch_gui.py`; Step 4; click "Run quick benchmark"; log streams; table refreshes.*

Here is the flow. The researcher points the tool at a folder of 3-D time-lapse stacks. Detection gives a centroid and a volume per nucleus — in this demo we use ground-truth detections to isolate the linking step, and a simple label-free Otsu baseline as a stress test. The ILP links frames, proposes divisions, and attaches a gate penalty to each one. A proposal with zero penalty passes; a proposal that was chosen despite a penalty is flagged for human review, with both daughter volumes shown. Appear-and-disappear spikes are flagged as segmentation or focus problems. In the design version, a continuous acoustic channel and a pressure sensor add timestamps, so cells that vanish right after a flow event are pre-labelled as mechanical-artefact candidates and kept out of the drug-death count — with the reason written next to them. That part is designed and documented; it is not yet built.

**[2:40–3:25] RESULTS — HONESTLY**
*Screen: zoom on seq 01 rows; then the Otsu rows; then the Limitations slide.*

On the public Fluo-N3DH-CHO data, with ground-truth detections, the ILP lifts the official TRA score from 0.928 to 0.998 on sequence one and from 0.943 to 0.996 on sequence two — and cuts false divisions from one hundred seventy-eight to five. The soft gate adds a small but consistent gain. We also show what does not work yet: mitosis recall is low, our label-free detector reaches a DET of only 0.4 to 0.5, and the dataset is conventional culture, not a real chip. We state all of this in the report, because a tool for auditing experiments has to be auditable itself.

**[3:25–3:55] WHO BENEFITS**
*Screen: researcher at a workstation; the audit export JSON; roadmap slide.*

The immediate beneficiary is the bench scientist who today scrolls through hundreds of frames deleting false divisions by hand. With AuraCell 4D, review time goes to a handful of flagged events, and every exclusion is traceable. Downstream, that same traceability is what regulators and journal reviewers ask for when organ-on-a-chip data replaces animal testing. Our next steps are a learned 3-D segmenter, a real chip recording with a synchronised acoustic channel, and only then, hardware. AuraCell 4D: fewer hallucinated divisions, every number labelled, every decision explainable.

---

## Shot list (for recording)
| Time | Screen | Source |
|---|---|---|
| 0:00 | Time-lapse frames + false fork overlay | `data/Fluo-N3DH-CHO/01/t0xx.tif` rendered in any viewer, or GUI Step 4 animation labelled "demo" |
| 0:35 | Link/divide/appear/disappear diagram | writeup §4.2 (draw as 1 slide) |
| 1:10 | Ablation table | `results/ablation.md` or GUI Step 4 table |
| 1:45 | Live run | `python gui/launch_gui.py` → Step 4 → Run quick benchmark (≈2 min; pre-record and speed up) |
| 2:40 | Rows seq 01, Otsu rows, Limitations | GUI table; writeup §7 as slide |
| 3:25 | Step 5 audit export; roadmap | GUI Step 5; writeup §8 as slide |
