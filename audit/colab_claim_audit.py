"""
AuraCell 4D - Audit klaim yang membutuhkan data nyata (dijalankan di Google Colab).

Menguji:
  K1  Isi Google Drive AuraCell4D_Datasets: apakah ada audio nyata untuk '10.000 sampel suara mikro'?
  K2  Fluo-N3DH-CHO: unduh/ekstrak, statistik GT (sel, mitosis, frame), metadata dataset
  K3  Jalankan tracker Velocell (greedy, salinan persis dari src/vision_4d/mitosis_ilp.py) pada
      centroid GT (deteksi sempurna) lalu hitung TRA/DET resmi dengan py-ctcmetrics.
      Ini adalah BATAS ATAS kinerja linking; angka di laporan (0.918 / 0.9942) harus dibandingkan dengannya.
  K4  Keterukuran anafase: interval frame dataset vs durasi anafase
  K5  Apakah ada bobot model AURASENSAI (.pt/.ckpt/.safetensors) di Drive?

Pakai di Colab:
  !pip -q install py-ctcmetrics tifffile
  %run colab_claim_audit.py
Hasil ditulis ke Drive: AuraCell4D_Datasets/AUDIT_claim_results.json
"""
import json, os, sys, time, zipfile, urllib.request, subprocess
from pathlib import Path
import numpy as np

subprocess.run([sys.executable, "-m", "pip", "-q", "install", "py-ctcmetrics", "tifffile", "scikit-image"], check=False)
import tifffile
from scipy import ndimage

try:
    from google.colab import drive  # type: ignore
    drive.mount("/content/drive", force_remount=False)
    DRIVE = Path("/content/drive/MyDrive/AuraCell4D_Datasets")
except Exception:
    DRIVE = Path(os.environ.get("AURACELL_DATA", "./AuraCell4D_Datasets"))
DRIVE.mkdir(parents=True, exist_ok=True)
RESULTS = {}


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- K1
log("=" * 70, "\nK1  Inventaris Drive:", DRIVE)
inv = {}
for p in DRIVE.rglob("*"):
    if p.is_file():
        inv[p.suffix.lower()] = inv.get(p.suffix.lower(), 0) + 1
log("   ekstensi berkas:", inv)
audio_exts = {".wav", ".flac", ".mp3", ".h5", ".hdf5", ".npy", ".npz"}
n_audio = sum(v for k, v in inv.items() if k in audio_exts)
manifest = DRIVE / "benchmark_raw" / "micro_acoustics_10k" / "dataset_10k_manifest.json"
man_info = None
if manifest.exists():
    m = json.loads(manifest.read_text())
    man_info = {"n_items": len(m), "keys": sorted(m[0].keys()), "contoh": m[0]}
RESULTS["K1_audio_10k"] = {
    "berkas_audio_di_drive": n_audio,
    "manifest_ada": manifest.exists(),
    "manifest": man_info,
    "verdict": "TIDAK DIDUKUNG" if n_audio == 0 else "PERLU CEK",
    "fakta": "Tidak ada satu pun berkas audio/waveform; hanya manifest JSON berisi center_freq & snr acak (np.random)."
    if n_audio == 0 else f"{n_audio} berkas mirip audio ditemukan - periksa asalnya.",
}
log("  ", RESULTS["K1_audio_10k"]["verdict"], "-", RESULTS["K1_audio_10k"]["fakta"])

# --------------------------------------------------------------------------- K5
weights = [str(p.relative_to(DRIVE)) for p in DRIVE.rglob("*") if p.suffix.lower() in {".pt", ".pth", ".ckpt", ".safetensors", ".onnx", ".bin"}]
RESULTS["K5_model_weights"] = {"ditemukan": weights, "verdict": "TIDAK DIDUKUNG" if not weights else "PERLU CEK"}
log("K5  Bobot model AURASENSAI di Drive:", weights or "tidak ada")

# --------------------------------------------------------------------------- K2
log("=" * 70, "\nK2  Fluo-N3DH-CHO")
raw = DRIVE / "benchmark_raw"
raw.mkdir(exist_ok=True)
zip_path = raw / "Fluo-N3DH-CHO.zip"
ds = raw / "Fluo-N3DH-CHO"
if not ds.exists():
    if not zip_path.exists():
        url = "http://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip"
        log("   mengunduh", url)
        urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(raw)
log("   dataset di", ds, "ada:", ds.exists())


def parse_track(p):
    d = {}
    for line in Path(p).read_text().strip().splitlines():
        a = line.split()
        if len(a) >= 4:
            d[int(a[0])] = (int(a[1]), int(a[2]), int(a[3]))
    return d


k2 = {}
for seq in ("01", "02"):
    gt_tra = ds / f"{seq}_GT" / "TRA"
    if not gt_tra.exists():
        continue
    tr = parse_track(gt_tra / "man_track.txt")
    frames = sorted(gt_tra.glob("man_track*.tif"))
    k2[seq] = {"n_tracks": len(tr), "n_divisions_daughters": sum(1 for v in tr.values() if v[2] != 0),
               "n_frames": len(frames)}
    if frames:
        vol = tifffile.imread(frames[0])
        k2[seq]["shape_ZYX"] = list(vol.shape)
k2["metadata_resmi_CTC"] = {"sel": "CHO nuclei GFP-PCNA", "mikroskop": "Zeiss LSM 510 confocal 63x/1.4 oil",
                             "voxel_um": [0.202, 0.202, 1.0], "time_step_min": 9.5,
                             "sumber": "Dr. J. Essers, Erasmus MC Rotterdam", "organ_on_chip": False}
RESULTS["K2_ctc_dataset"] = k2
log("  ", json.dumps(k2, indent=1))

# --------------------------------------------------------------------------- K3
log("=" * 70, "\nK3  Jalankan tracker Velocell pada centroid GT -> TRA/DET resmi")


class AdvancedMitosisILPSolver:  # salinan persis dari src/vision_4d/mitosis_ilp.py (tanpa perubahan logika)
    def __init__(self, max_migration_distance=15.0, division_distance=20.0, max_gap_frames=2, max_distance=None):
        self.max_dist = max_distance if max_distance is not None else max_migration_distance
        self.div_dist = division_distance
        self.max_gap = max_gap_frames

    def verify_biological_mitosis_invariants(self, parent, d1, d2, parent_volume=100.0, d1_volume=48.0, d2_volume=51.0, metabolic_orr=0.30):
        vol_ratio = d1_volume / (d2_volume + 1e-6)
        if not (0.75 <= vol_ratio <= 1.35):
            return False, "asym"
        mass_residual = abs(parent_volume - (d1_volume + d2_volume)) / parent_volume
        if mass_residual > 0.15:
            return False, "mass"
        if metabolic_orr > 0.50:
            return False, "orr"
        return True, "ok"

    def solve_frame_pair(self, cells_t0, cells_t1, spectral_orr_map=None):
        n0, n1 = len(cells_t0), len(cells_t1)
        if n0 == 0 or n1 == 0:
            return {"links": [], "divisions": []}
        c0 = np.array([[c["x"], c["y"], c["z"]] for c in cells_t0])
        c1 = np.array([[c["x"], c["y"], c["z"]] for c in cells_t1])
        dist = np.sqrt(((c0[:, None, :] - c1[None, :, :]) ** 2).sum(-1))
        assigned, links, divisions = set(), [], []
        for i, cc in enumerate(cells_t0):
            order = np.argsort(dist[i])
            valid = [j for j in order if dist[i, j] <= self.max_dist and j not in assigned]
            if len(valid) >= 2:
                j1, j2 = valid[0], valid[1]
                d_between = np.linalg.norm(c1[j1] - c1[j2])
                if d_between <= self.div_dist and dist[i, j2] <= self.div_dist:
                    ok, _ = self.verify_biological_mitosis_invariants(
                        cc, cells_t1[j1], cells_t1[j2], cc.get("volume_um3", 100.0),
                        cells_t1[j1].get("volume_um3", 49.0), cells_t1[j2].get("volume_um3", 50.0), cc.get("metabolic_orr", 0.32))
                    if ok:
                        divisions.append((cc["cell_id"], cells_t1[j1]["cell_id"], cells_t1[j2]["cell_id"]))
                        assigned.update({j1, j2})
                        continue
            if valid:
                j = valid[0]
                links.append((cc["cell_id"], cells_t1[j]["cell_id"]))
                assigned.add(j)
        return {"links": links, "divisions": divisions}


def centroids_um(vol, spacing=(1.0, 0.202, 0.202)):
    labels = np.unique(vol)
    labels = labels[labels != 0]
    cz, cy, cx = [], [], []
    com = ndimage.center_of_mass(vol > 0, vol, labels)
    cells = []
    for lab, (z, y, x) in zip(labels, com):
        vox = int((vol == lab).sum())
        cells.append({"cell_id": int(lab), "x": x * spacing[2], "y": y * spacing[1], "z": z * spacing[0],
                      "volume_um3": vox * spacing[0] * spacing[1] * spacing[2]})
    return cells


def run_tracker_on_sequence(seq, n_frames=None, max_dist=15.0):
    gt_tra = ds / f"{seq}_GT" / "TRA"
    frames = sorted(gt_tra.glob("man_track*.tif"))
    if n_frames:
        frames = frames[:n_frames]
    res_dir = DRIVE / "AUDIT_RES" / f"{seq}_RES"
    res_dir.mkdir(parents=True, exist_ok=True)
    solver = AdvancedMitosisILPSolver(max_distance=max_dist)

    # Volume sebelumnya diperlukan untuk relabel; gunakan actual volumes (bukan default 100/49/50)
    prev_cells, prev_map = None, {}
    next_id = 1
    tracks = {}  # new_id -> [start, end, parent]
    t0 = time.time()
    for t, fp in enumerate(frames):
        vol = tifffile.imread(fp)
        cells = centroids_um(vol)
        cur_map = {}
        if prev_cells is None:
            for c in cells:
                cur_map[c["cell_id"]] = next_id
                tracks[next_id] = [t, t, 0]
                next_id += 1
        else:
            res = solver.solve_frame_pair(prev_cells, cells)
            linked = set()
            for a, b in res["links"]:
                nid = prev_map[a]
                cur_map[b] = nid
                tracks[nid][1] = t
                linked.add(b)
            for p, d1, d2 in res["divisions"]:
                pid = prev_map[p]
                for d in (d1, d2):
                    cur_map[d] = next_id
                    tracks[next_id] = [t, t, pid]
                    next_id += 1
                    linked.add(d)
            for c in cells:
                if c["cell_id"] not in linked:
                    cur_map[c["cell_id"]] = next_id
                    tracks[next_id] = [t, t, 0]
                    next_id += 1
        # relabel mask with our track ids
        out = np.zeros_like(vol, dtype=np.uint16)
        for old, new in cur_map.items():
            out[vol == old] = new
        tifffile.imwrite(res_dir / f"mask{t:03d}.tif", out)
        prev_cells, prev_map = cells, cur_map
    with open(res_dir / "res_track.txt", "w") as f:
        for tid, (s, e, p) in tracks.items():
            f.write(f"{tid} {s} {e} {p}\n")
    latency = (time.time() - t0) / len(frames)
    # py-ctcmetrics membutuhkan GT dir yang hanya berisi frame yang dievaluasi; buat salinan subset bila n_frames
    gt_eval = gt_tra
    if n_frames:
        gt_eval = DRIVE / "AUDIT_RES" / f"{seq}_GT_sub" / "TRA"
        gt_eval.mkdir(parents=True, exist_ok=True)
        import shutil
        for fp in frames:
            shutil.copy(fp, gt_eval / fp.name)
        tr = parse_track(gt_tra / "man_track.txt")
        with open(gt_eval / "man_track.txt", "w") as f:
            for cid, (s, e, p) in tr.items():
                if s < len(frames):
                    f.write(f"{cid} {s} {min(e, len(frames)-1)} {p}\n")
    from ctc_metrics import evaluate_sequence
    metrics = evaluate_sequence(str(res_dir), str(gt_eval.parent), metrics=["DET", "TRA", "BIO(0)"] if False else ["DET", "TRA"])
    n_div_pred = sum(1 for v in tracks.values() if v[2] != 0)
    tr_gt = parse_track(gt_tra / "man_track.txt")
    n_div_gt = sum(1 for v in tr_gt.values() if v[2] != 0 and (not n_frames or v[0] < len(frames)))
    return {"frames": len(frames), "metrics": metrics, "pred_daughters": n_div_pred, "gt_daughters": n_div_gt,
            "sec_per_volume": round(latency, 3), "max_dist_um": max_dist}


k3 = {}
for seq in ("01", "02"):
    if (ds / f"{seq}_GT" / "TRA").exists():
        try:
            k3[seq] = run_tracker_on_sequence(seq, n_frames=None)
            log(f"   seq {seq}:", k3[seq])
        except Exception as ex:
            k3[seq] = {"error": repr(ex)}
            log("   gagal", seq, ex)
k3["catatan"] = ("Deteksi = GT sempurna, jadi DET~1.0 by construction; TRA mengukur kualitas LINKING tracker Velocell saja. "
                 "Angka laporan TRA 0.918/0.9942 harus >= angka ini agar masuk akal; bila tracker asli menghasilkan TRA lebih rendah, "
                 "klaim laporan tidak dapat direproduksi.")
RESULTS["K3_velocell_real_ctc"] = k3

# --------------------------------------------------------------------------- K4
dt = 9.5
anaphase_min = (5, 10)
RESULTS["K4_anaphase_measurable"] = {
    "time_step_min": dt, "anaphase_duration_min": anaphase_min,
    "frames_in_anaphase": [round(a / dt, 2) for a in anaphase_min],
    "verdict": "TIDAK TERBUKTI",
    "fakta": "Dengan interval 9.5 menit, anafase tertangkap 0.5-1 frame; kecepatan 1.20+/-0.25 um/min tidak dapat diukur dari dataset ini.",
}
log("K4 ", RESULTS["K4_anaphase_measurable"])

out = DRIVE / "AUDIT_claim_results.json"
out.write_text(json.dumps(RESULTS, indent=2, default=str))
log("\nSelesai. Hasil:", out)
print(json.dumps(RESULTS, indent=1, default=str))
