# Figures for the technical report / Kaggle writeup

All PNGs are 300 dpi (matplotlib) or 1600-px headless-Chrome captures. Regenerate with:

```bash
python make_figures.py                                    # fig1–fig6 from results/ablation.json + data/
python gui/launch_gui.py --no-open &                      # then, for GUI captures:
chrome --headless=new --window-size=1600,1350 --virtual-time-budget=8000 --screenshot=gui_step4.png "http://127.0.0.1:8765/index.html#step=4"
```

| File | Label | Use in writeup / laporan | What it shows |
|---|---|---|---|
| `fig1_tra_gt_detections.png` | [Measured] | §5.1 / Bab 6.1 (headline figure) | TRA for greedy vs ILP, both sequences, GT detections; dashed red = original ±15 % gate that proposes 0 divisions |
| `fig2_false_divisions.png` | [Measured] | §5.1 / Bab 6.1 | Proposed divisions per tracker on log scale vs true count (4 and 3) |
| `fig3_otsu_robustness.png` | [Measured] | §5.2 / Bab 6.2 | Label-free Otsu detections: DET 0.40/0.53, tracker ordering holds |
| `fig4_gate_calibration.png` | [Measured] | §4.3 / Bab 5.3 | Calibration statistics proving GT TRA masks are uniform markers; why the old gate "worked" |
| `fig5_frame_overlay.png` | [Measured] | §1 problem statement or §5.3 | Same real frame (seq 01, t=40): greedy proposes 126 division events vs ILP 6 |
| `fig6_full_table.png` | [Measured] | Appendix / §5 | All 18 ablation rows as an image |
| `gui_step1.png` | [Design] | §3.1 | Setup screen — reference cartridge, labelled "design" |
| `gui_step2.png` | [Design/Simulation] | §3.2 | Acoustic monitoring panel — labelled simulation |
| `gui_step3.png` | [Design/Simulation] | §3.2 | Spectral/ORR concept panel — labelled simulation |
| `gui_step4.png` | [Measured] | §3.4 / §9 reproduction | Measured-results panel: "local API connected", 18 full + 2 local rows, Run buttons |
| `gui_step5.png` | mixed, labelled | §3.4 | Audit export: measured card, design card, physics unit-test card |

Do not use `gui_step2/3` as evidence of anything; they exist to show the interface of the design concept.
