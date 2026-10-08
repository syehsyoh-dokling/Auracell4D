# AuraCell 4D — Product Introduction Voice-Over (English, ≈480 words, ≈3:20–3:40)

> Professional product-introduction tone. No timestamps, no on-screen instructions, no research-report language in the narration. Limitations are documented in `docs/TECHNICAL_REPORT.md` §8 and `docs/AUDIT_LOG.md` and are addressed in Q&A.
> Two factual anchors remain in natural wording: the monitoring sequence is a *demonstration scenario*, and the benchmark figures were obtained *with reference detections*.

---

## Narration

**From dishes to chips.** For decades, drugs were tested in two-dimensional dishes and in animals — and nine out of ten candidates that passed there still failed in humans. Organ-on-a-chip changed that: living human cells in micro-channels perfused like blood vessels, now accepted by regulators as an alternative to animal testing. But the chip created a new challenge. It produces thousands of three-dimensional frames that must be interpreted — which cell moved, which divided, which died. Conventional trackers decide frame by frame, and whenever two nuclei touch they invent a division: on a public benchmark with four real divisions, a standard tracker proposed one hundred seventy-eight. AuraCell 4D was built to make that lineage trustworthy — and auditable.

**Where it works.** The laboratory fabricates the cartridge and seeds the cells. AuraCell 4D takes over at docking: geometry and flow rate are recorded, and the physical baseline is computed from them. From the first second of perfusion the acoustic channel listens continuously, while the microscope keeps its periodic cadence. Then the algorithm runs — detection, global linking, biological gate. Every event receives a certificate: continue, flag, or stop. The researcher stays in command, and the cycle repeats at the next dose.

**The algorithm.** For each pair of frames, AuraCell 4D solves one integer linear program: every nucleus takes exactly one fate — link, divide, or disappear — and every nucleus in the next frame has exactly one origin. Biology enters as a cost, not a ban: a division with implausible daughter volumes becomes expensive, so the optimiser avoids it unless the evidence is strong. That cost is calibrated from the data itself.

**Drug or bubble?** In this demonstration scenario, the acoustic channel catches a burst at the resonance frequency of a thirty-micron bubble. The system stamps the moment and requests an extra snapshot. Two cells disappear at the next frame. A plain tracker would count two drug deaths. AuraCell 4D recognises them as mechanical-artefact candidates and keeps them out of the drug-death count — with the reason written down. A pump harmonic outside the bubble band is logged and ignored: the system reacts to evidence, not to noise. Later, a cell ends with no mechanical event nearby — a genuine drug-associated death, and it counts. The result is a number a researcher can defend, with every exclusion explained in the audit trail. When pressure climbs, the system flags it early and recommends a stop; the operator decides. Human in command, evidence from the tool.

**Proven on public data.** Measured with the official Cell Tracking Challenge metrics, with reference detections, AuraCell 4D raises the tracking score from point nine three to point nine nine eight, and cuts false divisions from one hundred seventy-eight to five. The entire evaluation reproduces identically on Colab and on a laptop with a single command — and the interface runs it from one button, then exports the audit trail.

**Who benefits.** The bench scientist reviews a handful of flagged events instead of the whole movie. Regulators receive exactly the traceability they ask for as organ-on-a-chip data replaces animal testing. And every figure in our documentation carries a label — measured or design — so reviewers always know which is which. Next on the roadmap: a learned 3-D segmenter, real chip recordings with a synchronised acoustic channel, then hardware.

AuraCell 4D: trustworthy lineages, every number labelled, every decision explainable.

---

## Editor's screen map (not spoken)

| Narration block | Visual | Source |
|---|---|---|
| From dishes to chips | dish → chip transition; Fig. 5 (false fork vs clean lineage) | `docs/figures/fig5_frame_overlay.png` |
| Where it works | workflow stepper auto-advancing | `gui/demo/index.html?page=1` |
| The algorithm | stage 6 + ILP diagram | `?page=1&step=6` |
| Drug or bubble? | live monitor playing from the burst through the counterfactual counter; brief pressure flag | `?page=2&t=10&play=1`, cut to `?page=2&t=96&play=1`, `?page=2&t=55` |
| Proven on public data | animated TRA bars and 178 → 5 counter; GUI Step 4 | `?page=3`, `docs/figures/gui_step4.png` |
| Who benefits | closing slide | `?page=4` |
