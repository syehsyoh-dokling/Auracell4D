"""
AuraCell 4D - render publication figures (300 dpi PNG) from measured results.
    python make_figures.py            -> docs/figures/fig*.png
Reads results/ablation.json (and, if present, data/Fluo-N3DH-CHO + results/quick/*_RES for the frame overlay).
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((ROOT / "results" / "ablation.json").read_text())
rows = [r for r in R["rows"] if "error" not in r]
DPI = 300
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
C_GREEDY, C_ILP, C_ORIG, C_GATE = "#9aa4b2", "#0f8b8d", "#c0392b", "#f39c12"


def get(seq, det, tr):
    for r in rows:
        if r["seq"] == seq and r["detect"] == det and r["tracker"] == tr:
            return r
    return None


trackers = ["greedy_nogate", "greedy_gate", "ilp_nogate", "ilp_gate"]
labels = ["greedy\nno gate", "greedy\n+ gate", "ILP\nno gate", "ILP\n+ soft gate"]
colors = [C_GREEDY, C_GATE, C_ILP, "#065f60"]

# ---------------------------------------------------------------- Fig 1: TRA, GT detections
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
for ax, seq in zip(axes, ["01", "02"]):
    vals = [get(seq, "gt", t)["TRA"] for t in trackers]
    bars = ax.bar(labels, vals, color=colors)
    orig = get(seq, "gt", "greedy_gate_ORIGINAL(+/-15%)")
    if orig:
        ax.axhline(orig["TRA"], ls="--", lw=1, color=C_ORIG)
        ax.text(-0.4, orig["TRA"] - 0.004, f"original ±15% gate: {orig['TRA']:.4f}\n(0 divisions proposed — artefact)", ha="left", va="top", fontsize=7, color=C_ORIG)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.001, f"{v:.4f}", ha="center", va="bottom", fontsize=7.5)
    ax.set_ylim(0.90, 1.003)
    ax.set_title(f"Fluo-N3DH-CHO seq {seq} — GT detections (DET = 1)", fontsize=9)
    ax.set_ylabel("TRA (official CTC metric)" if seq == "01" else "")
fig.suptitle("[Measured] Linking quality: ILP vs greedy", fontsize=10, y=1.02)
fig.tight_layout(); fig.savefig(OUT / "fig1_tra_gt_detections.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig 2: false divisions (log)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
for ax, seq in zip(axes, ["01", "02"]):
    pred = [get(seq, "gt", t)["mitosis_pred"] for t in trackers]
    gt_n = get(seq, "gt", "ilp_gate")["mitosis_gt"]
    bars = ax.bar(labels, [max(p, 0.5) for p in pred], color=colors)
    ax.axhline(gt_n, ls=":", lw=1.2, color="k"); ax.text(3.45, gt_n * 1.15, f"true divisions in GT: {gt_n}", ha="right", fontsize=7.5)
    for b, v in zip(bars, pred):
        ax.text(b.get_x() + b.get_width() / 2, max(v, 0.5) * 1.12, str(v), ha="center", va="bottom", fontsize=8)
    ax.set_yscale("log"); ax.set_ylim(0.4, 400)
    ax.set_title(f"seq {seq} — divisions proposed (log scale)", fontsize=9)
    ax.set_ylabel("proposed divisions" if seq == "01" else "")
fig.suptitle("[Measured] False divisions collapse under the ILP; the soft gate trims further", fontsize=10, y=1.02)
fig.tight_layout(); fig.savefig(OUT / "fig2_false_divisions.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig 3: label-free (Otsu) robustness
fig, ax = plt.subplots(figsize=(7.2, 3.0))
x = np.arange(len(trackers)); w = 0.38
for i, (seq, hatch) in enumerate([("01", ""), ("02", "//")]):
    tra = [get(seq, "otsu", t)["TRA"] for t in trackers]
    det = get(seq, "otsu", "ilp_gate")["DET"]
    bars = ax.bar(x + (i - 0.5) * w, tra, w, color=colors, hatch=hatch, edgecolor="white", label=f"seq {seq}  (DET = {det:.3f})")
    for b, v in zip(bars, tra):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.3f}", ha="center", va="bottom", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 0.65); ax.set_ylabel("TRA")
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_title("[Measured] Label-free Otsu+watershed detections — detection is the bottleneck, ordering of trackers holds", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "fig3_otsu_robustness.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig 4: gate calibration finding
cal = R["gate_calibration"]
fig, ax = plt.subplots(figsize=(7.2, 2.6))
ax.axis("off")
txt = (
    "Gate calibration from GT divisions (seq 02, n = %d)\n"
    "  daughter volume ratio  V_big / V_small       p5 / p50 / p95 = %s\n"
    "  mass ratio  (V_d1 + V_d2) / V_parent          p5 / p50 / p95 = %s\n\n"
    "Finding: CTC TRA ground-truth masks are uniform-size markers, not segmentations.\n"
    "A hand-set gate 'mass ≈ 1 ± 15%%' (0.85–1.15) therefore rejects EVERY true division →\n"
    "TRA 0.998 with zero divisions (the '0.99xx' of the earlier draft was this artefact).\n"
    "Calibrated soft gate used here: ratio ≤ %.2f, mass ∈ [%.2f, %.2f]; applied as cost, not veto."
) % (cal["n_divisions"], cal["daughter_ratio_p5_p50_p95"], cal["mass_ratio_p5_p50_p95"], cal["ratio_max"], cal["mass_min"], cal["mass_max"])
ax.text(0.01, 0.98, txt, va="top", ha="left", family="monospace", fontsize=8.2)
ax.set_title("[Measured] Why the old hard gate looked perfect", fontsize=10, loc="left")
fig.savefig(OUT / "fig4_gate_calibration.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig 5: real frame overlay (if data present)
try:
    import tifffile
    seq = "01"; t = 40
    raw = tifffile.imread(ROOT / "data" / "Fluo-N3DH-CHO" / seq / f"t{t:03d}.tif")
    gt = tifffile.imread(ROOT / "data" / "Fluo-N3DH-CHO" / f"{seq}_GT" / "TRA" / f"man_track{t:03d}.tif")
    mip = raw.max(axis=0).astype(float); mip = (mip - np.percentile(mip, 1)) / (np.percentile(mip, 99.8) - np.percentile(mip, 1) + 1e-9)
    from scipy import ndimage
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    axes[0].imshow(np.clip(mip, 0, 1), cmap="gray"); axes[0].set_title(f"Raw GFP-PCNA\nmax-projection, frame {t}", fontsize=9)
    for ax, (name, folder, col) in zip(axes[1:], [("greedy, no gate", "01_gt_greedy_nogate_RES", C_GREEDY), ("ILP + soft gate", "01_gt_ilp_gate_RES", C_ILP)]):
        ax.imshow(np.clip(mip, 0, 1), cmap="gray")
        for rdir in (ROOT / "results" / "quick" / folder, ROOT / "results" / folder):
            if rdir.exists():
                break
        tr = {}
        for line in (rdir / "res_track.txt").read_text().splitlines():
            a = line.split(); tr[int(a[0])] = (int(a[1]), int(a[2]), int(a[3]))
        m = tifffile.imread(rdir / f"mask{t:03d}.tif").max(axis=0)
        ids = np.unique(m); ids = ids[ids != 0]
        com = ndimage.center_of_mass(m > 0, m, ids)
        n_div_sofar = sum(1 for v in tr.values() if v[2] != 0 and v[0] <= t)
        for i, (y, x) in zip(ids, com):
            is_daughter = tr.get(int(i), (0, 0, 0))[2] != 0
            ax.plot(x, y, "o", ms=9, mfc="none", mec=("#f1c40f" if is_daughter else col), mew=1.4)
            ax.text(x + 6, y - 6, str(i), color="w", fontsize=6)
        ax.set_title(f"{name}\n{len(ids)} tracks · {n_div_sofar} division events up to frame {t}", fontsize=9)
    for ax in axes: ax.axis("off")
    fig.suptitle("[Measured] Same frame, same GT detections — yellow = daughter of a proposed division", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "fig5_frame_overlay.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)
except Exception as ex:  # noqa
    print("fig5 skipped:", ex)

# ---------------------------------------------------------------- Fig 6: full table as image
fig, ax = plt.subplots(figsize=(9.5, 0.28 * len(rows) + 0.9)); ax.axis("off")
cols = ["seq", "detect", "tracker", "DET", "TRA", "div pred/GT", "mitosis P", "R", "F1"]
cell = [[r["seq"], r["detect"], r["tracker"].replace("greedy_gate_ORIGINAL(+/-15%)", "greedy_gate ORIGINAL ±15%"), f"{r['DET']:.3f}", f"{r['TRA']:.4f}", f"{r['mitosis_pred']}/{r['mitosis_gt']}", f"{r['P']:.3f}", f"{r['R']:.2f}", f"{r['F1']:.3f}"] for r in rows]
tab = ax.table(cellText=cell, colLabels=cols, loc="center", cellLoc="center", colWidths=[0.05, 0.07, 0.27, 0.07, 0.08, 0.11, 0.09, 0.06, 0.06])
tab.auto_set_font_size(False); tab.set_fontsize(7.5); tab.scale(1, 1.25)
for (i, j), c in tab.get_celld().items():
    if i == 0: c.set_facecolor("#e8eef2"); c.set_text_props(weight="bold")
    elif rows[i - 1]["tracker"] == "ilp_gate": c.set_facecolor("#e3f4f4")
    elif "ORIGINAL" in rows[i - 1]["tracker"]: c.set_facecolor("#fbe9e7")
ax.set_title("[Measured] Full ablation — CTC Fluo-N3DH-CHO, py-ctcmetrics (results/ablation.json)", fontsize=10)
fig.savefig(OUT / "fig6_full_table.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)

print("written:", sorted(p.name for p in OUT.glob("*.png")))
