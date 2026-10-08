"""
AuraCell 4D - evaluate.py  (entry script, reproducible without login)

One run produces the full ablation table on Cell Tracking Challenge Fluo-N3DH-CHO:

  Detection : GT (centroids from GT TRA masks)  |  OTSU (Otsu + watershed on raw images, no GT)
  Tracker   : greedy_nogate | greedy_gate | ilp_nogate | ilp_gate
  Gate      : volume/mass thresholds CALIBRATED from the GT distribution of the calibration sequence (not a hand-set +/-15%)
  Metrics   : official DET, TRA (py-ctcmetrics) + mitosis precision/recall/F1 (parent->daughter edges matched to GT)

Usage:
  pip install -r requirements.txt
  python evaluate.py --data ./data --out ./results            # all sequences, all variants
  python evaluate.py --seqs 01 --detect gt --trackers ilp_gate

Outputs: results/ablation.json, results/ablation.md, results/<seq>_<det>_<tracker>_RES/ (masks + res_track.txt)
Every number labelled [Measured] in the writeup comes from this file.
"""
import argparse, json, os, shutil, sys, time, urllib.request, zipfile
from pathlib import Path
import numpy as np
import tifffile
from scipy import ndimage
from skimage.filters import threshold_otsu, gaussian
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.measure import label as cc_label

CTC_URL = "http://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip"
SPACING = (1.0, 0.202, 0.202)  # z, y, x  (um)  - metadata resmi CTC
VOXEL_UM3 = SPACING[0] * SPACING[1] * SPACING[2]
DT_MIN = 9.5


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ data
def ensure_dataset(data_dir: Path) -> Path:
    ds = data_dir / "Fluo-N3DH-CHO"
    if ds.exists():
        return ds
    data_dir.mkdir(parents=True, exist_ok=True)
    zp = data_dir / "Fluo-N3DH-CHO.zip"
    if not zp.exists():
        log(f"[data] downloading {CTC_URL}")
        urllib.request.urlretrieve(CTC_URL, zp)
    with zipfile.ZipFile(zp) as z:
        z.extractall(data_dir)
    return ds


def parse_track(p):
    d = {}
    for line in Path(p).read_text().strip().splitlines():
        a = line.split()
        if len(a) >= 4:
            d[int(a[0])] = (int(a[1]), int(a[2]), int(a[3]))
    return d


# ------------------------------------------------------------------ detection
def cells_from_mask(mask):
    labels = np.unique(mask)
    labels = labels[labels != 0]
    if len(labels) == 0:
        return []
    com = ndimage.center_of_mass(mask > 0, mask, labels)
    vols = ndimage.sum(np.ones_like(mask, dtype=np.uint8), mask, labels)
    return [{"cell_id": int(l), "x": c[2] * SPACING[2], "y": c[1] * SPACING[1], "z": c[0] * SPACING[0],
             "volume_um3": float(v) * VOXEL_UM3} for l, c, v in zip(labels, com, vols)]


def detect_otsu(raw, min_vox=400, min_dist_px=12):
    """Simple label-free detection: gaussian -> Otsu -> watershed on the distance transform."""
    sm = gaussian(raw.astype(np.float32), sigma=(0.5, 2, 2), preserve_range=True)
    thr = threshold_otsu(sm)
    fg = sm > thr
    fg = ndimage.binary_opening(fg, iterations=1)
    dist = ndimage.distance_transform_edt(fg, sampling=SPACING)
    peaks = peak_local_max(dist, min_distance=min_dist_px, labels=cc_label(fg), exclude_border=False)
    markers = np.zeros(fg.shape, dtype=np.int32)
    for i, (z, y, x) in enumerate(peaks, 1):
        markers[z, y, x] = i
    lab = watershed(-dist, markers, mask=fg)
    # buang objek terlalu kecil
    ids, counts = np.unique(lab, return_counts=True)
    for i, c in zip(ids, counts):
        if i != 0 and c < min_vox:
            lab[lab == i] = 0
    return lab.astype(np.uint16)


# ------------------------------------------------------------------ gate calibration
def calibrate_gate(ds: Path, seq: str):
    """Empirical distribution of daughter-volume ratio and mass conservation over GT divisions."""
    tra = ds / f"{seq}_GT" / "TRA"
    tr = parse_track(tra / "man_track.txt")
    frames = sorted(tra.glob("man_track*.tif"))
    vol_cache = {}

    def vols(t):
        if t not in vol_cache:
            m = tifffile.imread(frames[t])
            ids, counts = np.unique(m, return_counts=True)
            vol_cache[t] = {int(i): float(c) * VOXEL_UM3 for i, c in zip(ids, counts) if i != 0}
        return vol_cache[t]

    by_parent = {}
    for cid, (s, e, p) in tr.items():
        if p != 0:
            by_parent.setdefault(p, []).append((cid, s))
    ratios, masses = [], []
    for p, ds_ in by_parent.items():
        if len(ds_) != 2:
            continue
        s_par_end = tr[p][1]
        vp = vols(s_par_end).get(p)
        v1, v2 = vols(ds_[0][1]).get(ds_[0][0]), vols(ds_[1][1]).get(ds_[1][0])
        if vp and v1 and v2:
            ratios.append(max(v1, v2) / min(v1, v2))
            masses.append((v1 + v2) / vp)
    r, m = np.array(ratios), np.array(masses)
    cal = {"n_divisions": int(len(r)),
           "daughter_ratio_p5_p50_p95": [float(np.percentile(r, q)) for q in (5, 50, 95)] if len(r) else None,
           "mass_ratio_p5_p50_p95": [float(np.percentile(m, q)) for q in (5, 50, 95)] if len(m) else None}
    # thresholds = p5-p95 range widened by 10%
    if len(r):
        cal["ratio_max"] = float(np.percentile(r, 95) * 1.1)
        cal["mass_min"] = float(np.percentile(m, 5) * 0.9)
        cal["mass_max"] = float(np.percentile(m, 95) * 1.1)
    else:
        cal.update(ratio_max=1.35, mass_min=0.85, mass_max=1.15)
    return cal


ORIGINAL_GATE = {"ratio_max": 1.35, "ratio_min": 0.75, "mass_min": 0.85, "mass_max": 1.15, "source": "original mitosis_ilp.py (+/-15%)"}


def gate_penalty(vp, v1, v2, cal, hard=False):
    """Return a soft penalty, or None when rejected (hard mode)."""
    ratio = max(v1, v2) / max(min(v1, v2), 1e-6)
    mass = (v1 + v2) / max(vp, 1e-6)
    viol = max(0.0, ratio - cal["ratio_max"]) / cal["ratio_max"] + \
        max(0.0, cal["mass_min"] - mass) / cal["mass_min"] + max(0.0, mass - cal["mass_max"]) / cal["mass_max"]
    if hard:
        return None if viol > 0 else 0.0
    return viol


# ------------------------------------------------------------------ trackers
def greedy_pair(c0, c1, max_dist, div_dist, gate_cal, use_gate):
    """Faithful port of AdvancedMitosisILPSolver.solve_frame_pair (greedy baseline)."""
    if not c0 or not c1:
        return [], []
    P0 = np.array([[c["x"], c["y"], c["z"]] for c in c0]); P1 = np.array([[c["x"], c["y"], c["z"]] for c in c1])
    D = np.sqrt(((P0[:, None] - P1[None]) ** 2).sum(-1))
    assigned, links, divs = set(), [], []
    for i, cc in enumerate(c0):
        valid = [j for j in np.argsort(D[i]) if D[i, j] <= max_dist and j not in assigned]
        if len(valid) >= 2:
            j1, j2 = valid[0], valid[1]
            if np.linalg.norm(P1[j1] - P1[j2]) <= div_dist and D[i, j2] <= div_dist:
                ok = True
                if use_gate:
                    ok = gate_penalty(cc["volume_um3"], c1[j1]["volume_um3"], c1[j2]["volume_um3"], gate_cal, hard=True) is not None
                if ok:
                    divs.append((i, j1, j2)); assigned.update({j1, j2}); continue
        if valid:
            links.append((i, valid[0])); assigned.add(valid[0])
    return links, divs


def ilp_pair(c0, c1, max_dist, div_dist, gate_cal, use_gate, c_app=30.0, c_div=10.0, w_gate=40.0):
    """Frame-pair network-flow ILP (scipy.optimize.milp / HiGHS):
    binary variables link x_ij, division y_i(j1,j2), appear a_j, disappear d_i.
    Constraints: every cell at t0 takes exactly one fate; every cell at t1 has exactly one origin.
    The biological gate enters as a SOFT COST (w_gate * violation), not a hard veto."""
    from scipy.optimize import milp, LinearConstraint, Bounds
    n0, n1 = len(c0), len(c1)
    if n0 == 0 or n1 == 0:
        return [], []
    P0 = np.array([[c["x"], c["y"], c["z"]] for c in c0]); P1 = np.array([[c["x"], c["y"], c["z"]] for c in c1])
    D = np.sqrt(((P0[:, None] - P1[None]) ** 2).sum(-1))
    var, cost = [], []  # var: ("x",i,j) | ("y",i,j1,j2) | ("a",j) | ("d",i)
    for i in range(n0):
        for j in range(n1):
            if D[i, j] <= max_dist:
                var.append(("x", i, j)); cost.append(D[i, j])
        cand = [j for j in range(n1) if D[i, j] <= div_dist]
        for a in range(len(cand)):
            for b in range(a + 1, len(cand)):
                j1, j2 = cand[a], cand[b]
                if np.linalg.norm(P1[j1] - P1[j2]) <= div_dist:
                    pen = gate_penalty(c0[i]["volume_um3"], c1[j1]["volume_um3"], c1[j2]["volume_um3"], gate_cal) if use_gate else 0.0
                    var.append(("y", i, j1, j2)); cost.append(D[i, j1] + D[i, j2] + c_div + w_gate * pen)
    for j in range(n1):
        var.append(("a", j)); cost.append(c_app)
    for i in range(n0):
        var.append(("d", i)); cost.append(c_app)
    nv = len(var)
    A = np.zeros((n0 + n1, nv))
    for k, v in enumerate(var):
        if v[0] == "x":
            A[v[1], k] = 1; A[n0 + v[2], k] = 1
        elif v[0] == "y":
            A[v[1], k] = 1; A[n0 + v[2], k] = 1; A[n0 + v[3], k] = 1
        elif v[0] == "a":
            A[n0 + v[1], k] = 1
        else:
            A[v[1], k] = 1
    res = milp(c=np.array(cost), constraints=LinearConstraint(A, 1, 1), integrality=np.ones(nv), bounds=Bounds(0, 1))
    if res.x is None:
        return [], []
    sol = res.x > 0.5
    links = [(v[1], v[2]) for v, s in zip(var, sol) if s and v[0] == "x"]
    divs = [(v[1], v[2], v[3]) for v, s in zip(var, sol) if s and v[0] == "y"]
    return links, divs


TRACKERS = {
    "greedy_nogate": (greedy_pair, False),
    "greedy_gate": (greedy_pair, True),
    "ilp_nogate": (ilp_pair, False),
    "ilp_gate": (ilp_pair, True),
}


# ------------------------------------------------------------------ run one config
def run_config(ds, seq, detect, tracker, gate_cal, out_root, max_dist=20.0, div_dist=25.0):
    gt_tra = ds / f"{seq}_GT" / "TRA"
    gt_frames = sorted(gt_tra.glob("man_track*.tif"))
    raw_frames = sorted((ds / seq).glob("t*.tif"))
    n = len(gt_frames)
    res_dir = out_root / f"{seq}_{detect}_{tracker}_RES"
    det_dir = out_root / f"{seq}_{detect}_DET"  # raw detection masks kept separate so py-ctcmetrics only sees result masks
    for d in (res_dir,):
        if d.exists():
            shutil.rmtree(d)
    res_dir.mkdir(parents=True); det_dir.mkdir(parents=True, exist_ok=True)
    fn, use_gate = TRACKERS[tracker]

    prev, prev_map, tracks, next_id = None, {}, {}, 1
    pred_divs = []  # (frame t, our d1, our d2)
    t0 = time.time()
    for t in range(n):
        if detect == "gt":
            mask = tifffile.imread(gt_frames[t])
        else:
            det_path = det_dir / f"det{t:03d}.tif"  # cache: detection does not depend on the tracker
            if det_path.exists():
                mask = tifffile.imread(det_path)
            else:
                mask = detect_otsu(tifffile.imread(raw_frames[t])); tifffile.imwrite(det_path, mask)
        cells = cells_from_mask(mask)
        cur = {}
        if prev is None:
            for c in cells:
                cur[c["cell_id"]] = next_id; tracks[next_id] = [t, t, 0]; next_id += 1
        else:
            links, divs = fn(prev, cells, max_dist, div_dist, gate_cal, use_gate)
            used = set()
            for i, j in links:
                nid = prev_map[prev[i]["cell_id"]]; cur[cells[j]["cell_id"]] = nid; tracks[nid][1] = t; used.add(j)
            for i, j1, j2 in divs:
                pid = prev_map[prev[i]["cell_id"]]; ids = []
                for j in (j1, j2):
                    cur[cells[j]["cell_id"]] = next_id; tracks[next_id] = [t, t, pid]; ids.append(next_id); next_id += 1; used.add(j)
                pred_divs.append((t, cells[j1]["cell_id"], cells[j2]["cell_id"]))
            for j, c in enumerate(cells):
                if j not in used:
                    cur[c["cell_id"]] = next_id; tracks[next_id] = [t, t, 0]; next_id += 1
        out = np.zeros(mask.shape, dtype=np.uint16)
        for old, new in cur.items():
            out[mask == old] = new
        tifffile.imwrite(res_dir / f"mask{t:03d}.tif", out)
        prev, prev_map = cells, cur
    sec_per_vol = (time.time() - t0) / n
    with open(res_dir / "res_track.txt", "w") as f:
        for tid, (s, e, p) in tracks.items():
            f.write(f"{tid} {s} {e} {p}\n")

    from ctc_metrics import evaluate_sequence
    m = evaluate_sequence(str(res_dir), str(gt_tra.parent), metrics=["DET", "TRA"])

    # ---- mitosis P/R: match predicted daughters to GT labels (max overlap) at frame t
    gt_tr = parse_track(gt_tra / "man_track.txt")
    # GT event = parent with >=2 daughters; event frame = earliest daughter start frame
    gt_events = {}
    for cid, (s, e, p) in gt_tr.items():
        if p != 0:
            gt_events.setdefault(p, {"daughters": set(), "frame": s})
            gt_events[p]["daughters"].add(cid); gt_events[p]["frame"] = min(gt_events[p]["frame"], s)
    gt_events = {k: v for k, v in gt_events.items() if len(v["daughters"]) >= 2}
    matched_gt, tp = set(), 0
    for t, d1, d2 in pred_divs:
        gtm = tifffile.imread(gt_frames[t])
        detm = gtm if detect == "gt" else tifffile.imread(det_dir / f"det{t:03d}.tif")
        def gt_label_of(det_label):
            vals = gtm[detm == det_label]; vals = vals[vals != 0]
            return int(np.bincount(vals).argmax()) if len(vals) else 0
        g1, g2 = gt_label_of(d1), gt_label_of(d2)
        ok = False
        for p, ev in gt_events.items():
            if abs(ev["frame"] - t) <= 2 and g1 in ev["daughters"] and g2 in ev["daughters"] and g1 != g2:
                ok = True; matched_gt.add(p); break
        tp += ok
    n_pred, n_gt = len(pred_divs), len(gt_events)
    prec = tp / n_pred if n_pred else 0.0
    rec = len(matched_gt) / n_gt if n_gt else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"seq": seq, "detect": detect, "tracker": tracker, "frames": n,
            "DET": round(float(m["DET"]), 4), "TRA": round(float(m["TRA"]), 4),
            "mitosis_pred": n_pred, "mitosis_gt": n_gt, "mitosis_tp": tp,
            "mitosis_precision": round(prec, 3), "mitosis_recall": round(rec, 3), "mitosis_f1": round(f1, 3),
            "sec_per_volume": round(sec_per_vol, 3)}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./data")
    ap.add_argument("--out", default="./results")
    ap.add_argument("--seqs", nargs="+", default=["01", "02"])
    ap.add_argument("--detect", nargs="+", default=["gt", "otsu"])
    ap.add_argument("--trackers", nargs="+", default=list(TRACKERS))
    ap.add_argument("--calib_seq", default="02", help="sequence used to calibrate the gate (also evaluated; in-sample for the gate)")
    args = ap.parse_args()
    ds = ensure_dataset(Path(args.data)); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    cal = calibrate_gate(ds, args.calib_seq)
    log("[gate] calibrated from GT", args.calib_seq, json.dumps(cal))
    rows = []
    for seq in args.seqs:
        for det in args.detect:
            for tr in args.trackers:
                log(f"[run] seq={seq} detect={det} tracker={tr}")
                try:
                    r = run_config(ds, seq, det, tr, cal, out)
                except Exception as ex:  # noqa
                    r = {"seq": seq, "detect": det, "tracker": tr, "error": repr(ex)}
                log("      ", r); rows.append(r)
    # also: the ORIGINAL (+/-15%) gate, to show why mitosis = 0 in the earlier draft
    for seq in args.seqs:
        if "gt" in args.detect and "greedy_gate" in args.trackers:
            r = run_config(ds, seq, "gt", "greedy_gate", ORIGINAL_GATE, out); r["tracker"] = "greedy_gate_ORIGINAL(+/-15%)"; rows.append(r); log("      ", r)

    report = {"dataset": "CTC Fluo-N3DH-CHO (training, 01 & 02)", "spacing_um_zyx": SPACING, "dt_min": DT_MIN,
              "gate_calibration": cal, "gate_original": ORIGINAL_GATE, "rows": rows,
              "note": "detect=gt: perfect detections (DET=1 by construction), measures linking only. detect=otsu: label-free, no GT. "
                         f"Gate calibrated on sequence {args.calib_seq}; rows of that sequence are not an independent test."}
    (out / "ablation.json").write_text(json.dumps(report, indent=2))
    md = ["# Ablation on Fluo-N3DH-CHO (py-ctcmetrics)", "", f"Gate calibration: `{json.dumps(cal)}`", "",
          "| seq | detect | tracker | DET | TRA | mitosis pred/GT | TP | P | R | F1 | s/vol |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "error" in r:
            md.append(f"| {r['seq']} | {r['detect']} | {r['tracker']} | ERROR {r['error'][:60]} |||||||||"); continue
        md.append(f"| {r['seq']} | {r['detect']} | {r['tracker']} | {r['DET']} | {r['TRA']} | {r['mitosis_pred']}/{r['mitosis_gt']} | {r['mitosis_tp']} | {r['mitosis_precision']} | {r['mitosis_recall']} | {r['mitosis_f1']} | {r['sec_per_volume']} |")
    (out / "ablation.md").write_text("\n".join(md))
    log("\n".join(md)); log("\n[done]", out / "ablation.md")


if __name__ == "__main__":
    main()
