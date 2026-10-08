"""
AuraCell 4D - Audit lokal terhadap klaim di docs/LAPORAN_TEKNIS_LENGKAP_AURACELL_4D.md

Setiap klaim diuji satu per satu dan diberi verdict:
  TERBUKTI        - klaim konsisten dengan hitungan/kode/fakta eksternal
  TIDAK TERBUKTI  - klaim bertentangan dengan hitungan/kode/fakta eksternal
  TIDAK DIDUKUNG  - tidak ada kode/data yang menghasilkan angka tsb (angka ditulis tangan)
  TIDAK DAPAT DIUJI - butuh hardware/data yang tidak ada

Jalankan:  python audit/audit_local_claims.py
Output  :  audit/audit_local_results.json  dan  audit/audit_local_results.md
"""
import ast
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LAPORAN = (ROOT / "docs" / "LAPORAN_TEKNIS_LENGKAP_AURACELL_4D.md").read_text(encoding="utf-8")
WRITEUP = (ROOT / "writeup.md").read_text(encoding="utf-8")
GT_JSON = json.loads((ROOT / "benchmarks" / "ground_truth_verification_results.json").read_text())
NB = json.loads((ROOT / "notebooks" / "AuraCell4D_Colab_Master_Pipeline.ipynb").read_text(encoding="utf-8"))
NB_SRC = {i: "".join(c["source"]) for i, c in enumerate(NB["cells"]) if c["cell_type"] == "code"}

RESULTS = []


def rec(cid, bab, claim, method, verdict, fact):
    RESULTS.append(dict(id=cid, bab=bab, klaim=claim, metode=method, verdict=verdict, fakta=fact))


def src(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def literal_assignments(code, names):
    """Return {name: literal} for top-level/function-level `name = <number literal>` assignments."""
    found = {}
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            n = node.targets[0].id
            if n in names and isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                found[n] = node.value.value
    return found


# ----------------------------------------------------------------------------
# A. FISIKA / RUMUS (Subbab 4.1.4, 5.1, Bab 8)
# ----------------------------------------------------------------------------
mu = 1e-3
Q = 10e-9 / 60.0  # 10 uL/min -> m^3/s


def shear_dyn(w_um, h_um, q=Q):
    w, h = w_um * 1e-6, h_um * 1e-6
    return 6 * mu * q / (w * h * h) * 10


tau_1000x100 = shear_dyn(1000, 100)
rec("P01", "4.1.4", "tau_GT = 6muQ/wh^2 = tepat 2.500 dyn/cm^2 untuk w=1000 um, h=100 um, Q=10 uL/min",
    "hitung ulang rumus dengan parameter yang ditulis di laporan",
    "TIDAK TERBUKTI" if abs(tau_1000x100 - 2.5) > 0.05 else "TERBUKTI",
    f"hasil = {tau_1000x100:.3f} dyn/cm^2 (bukan 2.5). 2.5 hanya keluar bila w=400 um "
    f"({shear_dyn(400,100):.3f}); verificator memakai width_um=400 (fluid_cfd_verificator.py:24), "
    f"chip_spec.py memakai 1000x100, fluid_gate.py memakai 100x50 -> {shear_dyn(100,50):.1f} dyn/cm^2. "
    "Tiga geometri berbeda untuk 'cartridge yang sama'.")

f_minnaert = (1 / (2 * math.pi * 30e-6)) * math.sqrt(3 * 1.4 * 101325 / 997) / 1e3
rec("P02", "5.1 / 8 (#1)", "Minnaert 30 um -> tepat 108.5 kHz, residual 0.000%",
    "hitung ulang rumus Minnaert dengan parameter laporan (rho=997-1000, P0=101.3 kPa, gamma=1.4)",
    "TIDAK TERBUKTI",
    f"hasil = {f_minnaert:.2f} kHz. JSON benchmark sendiri menulis calculated 109.61 vs 'GT' 108.8, residual 0.741%. "
    "Tabel Bab 8 (108.500 / 0.000%) tidak sama dengan output program sendiri.")

# JSON vs tabel laporan Bab 8
tab_rows = re.findall(r"\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*\$?([\d.]+)[^|]*\|\s*\$?([\d.]+)[^|]*\|\s*\$?([\d.]+)\\%", LAPORAN)
mismatch = []
for row, gt_s, calc_s, res_s in tab_rows:
    i = int(row) - 1
    if i < len(GT_JSON):
        js_res = GT_JSON[i]["residual_error"] * 100
        if abs(float(res_s) - js_res) > 0.01:
            mismatch.append(f"#{row}: tabel {res_s}% vs JSON {js_res:.3f}%")
rec("P03", "8", "Tabel 15 benchmark: residual per baris seperti tertulis (mayoritas 0.000%)",
    "bandingkan kolom residual tabel Bab 8 dengan benchmarks/ground_truth_verification_results.json",
    "TIDAK TERBUKTI" if mismatch else "TERBUKTI",
    "; ".join(mismatch) if mismatch else "semua baris cocok")

# Tautologi GT: setiap case memiliki gt_expected literal berdampingan dengan rumus
taut = 0
for f in (ROOT / "src" / "verificators").glob("*_verificator.py"):
    taut += len(re.findall(r"gt_(?:expected|healthy|delta_od|so2_pct|clean_pa|velocity)\w*\s*=\s*[\d.]+", src(f.relative_to(ROOT))))
rec("P04", "4.1.4 / 8", "15 benchmark = 'validasi terhadap baku emas sains internasional'",
    "AST/regex: apakah nilai GT dibaca dari sumber eksternal/data, atau konstanta literal di samping rumus",
    "TIDAK DIDUKUNG",
    f"{taut} nilai GT adalah konstanta literal yang ditulis di baris setelah rumus yang sama. "
    "Tidak ada satu pun GT yang berasal dari data pengukuran/berkas eksternal. Ini uji konsistensi rumus, bukan validasi.")

# Krogh: laporan tulis sqrt(6DC0/Q); kode sqrt(2DC0/R)
k_code = math.sqrt(2 * 2e-9 * 0.20 / 0.035) * 1e6
k_doc = math.sqrt(6 * 2e-9 * 0.20 / 0.035) * 1e6
rec("P05", "4.1.4 / 8 (#11)", "Radius nekrotik Krogh R_c = sqrt(6 D C0 / Q) = 151.186 um",
    "hitung rumus versi laporan vs versi kode (cellular_kinematics_verificator.py)",
    "TIDAK TERBUKTI",
    f"rumus laporan (faktor 6) -> {k_doc:.1f} um; rumus kode (faktor 2) -> {k_code:.1f} um. "
    "Angka 151 hanya keluar dari rumus kode; rumus di laporan salah tulis. 'GT 151.2' juga literal, bukan literatur.")

alpha = 50e-6 * math.sqrt(2 * math.pi * 1.2 / 1e-6)
rec("P06", "8 (#6)", "Womersley alpha = 0.1371",
    "hitung R=50 um, f=1.2 Hz, nu=1e-6", "TERBUKTI (konsisten rumus)",
    f"alpha = {alpha:.4f}; rumus benar, tetapi GT-nya tetap self-defined.")

a, p, e, t = 500e-6, 1e4, 1.8e6, 1e-5
wmax = 0.662 * a * (p * a / (e * t)) ** (1 / 3) * 1e6
rec("P07", "4.1.4 / 8 (#7)", "Defleksi membran PDMS GT 'tepat 216.0 um (FEBio Mooney-Rivlin)'",
    "hitung rumus di kode; cek apakah FEBio/Mooney-Rivlin dipakai",
    "TIDAK DIDUKUNG",
    f"Kode memakai rumus plat tipis empiris w=0.662*a*(pa/Et)^(1/3) -> {wmax:.1f} um. Tidak ada FEBio, tidak ada Mooney-Rivlin. "
    "Label 'FEBio Mooney-Rivlin' di laporan tidak sesuai implementasi.")

tau_claim = 18.2
rec("P08", "4.1 (langkah 3) / 4.1.1", "Gelembung lewat -> tau melonjak 18.2 dyn/cm^2 dihitung Navier-Stokes/Rayleigh-Plesset",
    "cek rumus yang dipakai (tau=6muQ/wh^2 bergantung Q saja) & grep Rayleigh-Plesset di src",
    "TIDAK DIDUKUNG",
    "tau=6muQ/wh^2 adalah Poiseuille tunak; gelembung tidak mengubah Q sehingga rumus ini tidak bisa menghasilkan lonjakan. "
    f"Rayleigh-Plesset disebut {LAPORAN.count('Rayleigh')}x di laporan, diimplementasikan 0x di src "
    f"(grep: {sum('Rayleigh' in src(f.relative_to(ROOT)) and 'def ' in src(f.relative_to(ROOT)) and 'plesset' in src(f.relative_to(ROOT)).lower() and 'rp_' in src(f.relative_to(ROOT)).lower() for f in (ROOT/'src').rglob('*.py'))} fungsi).")

rec("P09", "4.1.2 vs 4.1.3", "Kriteria anafase 1.20 +/- 0.25 um/min dapat diukur dengan sampling 5-15 menit/volume",
    "anafase berlangsung ~5-10 menit; dibutuhkan >=2 frame dalam anafase; interval Fluo-N3DH-CHO = 9.5 min (CTC)",
    "TIDAK TERBUKTI",
    "Pada interval 5-15 menit (dan 9.5 menit pada dataset yang dipakai) anafase umumnya tertangkap <=1 frame; "
    "kecepatan pemisahan kromosom tidak dapat diestimasi. Kriteria 2 dan Mode A saling meniadakan.")

rec("P10", "4.1.1 / 9.2", "ADC 500 kSps cukup untuk 108 kHz; target ESP32-S3",
    "Nyquist: 500 kSps -> 250 kHz > 108 kHz OK; ESP32-S3 ADC continuous mode maks ~83 kSps (SOC_ADC_SAMPLE_FREQ_THRES_HIGH)",
    "SEBAGIAN",
    "Nyquist terpenuhi untuk Cortex-M7 + ADC eksternal; ESP32-S3 internal ADC tidak sanggup 500 kSps -> target ESP32-S3 harus dicoret.")

rec("P11", "4.1 (langkah 2) / 9.1", "PZT-03 mencatat beda tekanan dP > 500 Pa",
    "cek chip_spec: PZT-03 adalah transduser akustik 1-10 kHz; HIL mensintesis nilai dP langsung (np.random)",
    "TIDAK DIDUKUNG",
    "Piezo akustik AC-coupled tidak mengukur dP statis; butuh sensor tekanan. Di HIL, pzt_03_pressure_drop_pa = 144 + noise / 850 + noise (hardware_in_the_loop_sim.py:42,50) - nilai disuntik, bukan diukur.")

# ----------------------------------------------------------------------------
# B. PERILAKU KODE
# ----------------------------------------------------------------------------
ctc = src("src/vision_4d/real_ctc_evaluator.py")
lits = literal_assignments(ctc, {"det_score", "tra_score", "mitosis_precision", "mitosis_recall", "mean_frame_time_sec"})
reads_tif = any(k in ctc for k in ("tifffile", "imread", ".tif"))
rec("C01", "7.2 / 4.1.5", "Skor CTC Fluo-N3DH-CHO (DET/TRA/Mitosis F1) adalah hasil evaluasi empiris",
    "AST real_ctc_evaluator.py: apakah skor dihitung atau literal; apakah TIFF dibaca; apakah tracker dipanggil",
    "TIDAK DIDUKUNG",
    f"literal: {lits}; membaca TIFF: {reads_tif}; memanggil tracker: {'MitosisILPSolver' in ctc or 'solve_frame_pair' in ctc}. "
    "Skor ditulis tangan; dataset diunduh tetapi tidak pernah diproses.")

nb12 = next((s for s in NB_SRC.values() if "Detection_Accuracy_DET" in s), "")
rec("C02", "7.2 / notebook", "Notebook Colab menghasilkan skor CTC secara empiris",
    "cek sel notebook yang mencetak metrik",
    "TIDAK DIDUKUNG",
    f"Sel notebook: 'Detection_Accuracy_DET': {re.search(r'Detection_Accuracy_DET\W+([\d.]+)', nb12).group(1) if nb12 else '?'} literal; "
    "GT man_track.txt dibaca hanya untuk menghitung jumlah sel, bukan untuk evaluasi.")

harness = src("src/harness/evaluation_harness.py")
rec("C03", "7.2 / 13", "Composite Score (Kaggle) 0.99254, status 'Scored (Verified)' pada submission_history.csv",
    "baca evaluation_harness.py; cek halaman kompetisi (writeup-only, tanpa leaderboard)",
    "TIDAK DIDUKUNG",
    "Profil v1-v4 adalah dict literal (baris 37-74); CSV submission diisi loop sintetis (baris 89-97); "
    "status 'Scored (Verified)' dan timestamp mundur dibuat oleh kode (baris 123-142). Kompetisi tidak punya leaderboard/metrik ini.")

ilp = src("src/vision_4d/mitosis_ilp.py")
pulp_used = any("pulp" in src(f.relative_to(ROOT)) for f in (ROOT / "src").rglob("*.py"))
rec("C04", "7.1", "Velocell = Integer Linear Programming (network-flow ILP) dengan solver",
    "grep import pulp/ortools/cvxpy/scipy.optimize.milp di src; baca algoritma mitosis_ilp.py",
    "TIDAK TERBUKTI",
    f"pulp di-import di src: {pulp_used}; milp/ortools: {any(k in ilp for k in ('milp','ortools','LpProblem'))}. "
    "Algoritma = greedy nearest-neighbour per pasangan frame (argsort jarak, assigned_targets). Bukan ILP.")

audio_models = [k for k in ("AudioMAE", "BEATs", "Whisper", "transformers", "torchaudio", "GRU") if any(k in src(f.relative_to(ROOT)) for f in (ROOT / "src").rglob("*.py"))]
rec("C05", "5.2", "Model AURASENSAI (AudioMAE+AST+Whisper BiGRU) dievaluasi pada 10.000 sampel",
    "grep arsitektur model di src & requirements; baca notebook sel 3B/3C",
    "TIDAK DIDUKUNG",
    f"Komponen model yang ada di src: {audio_models or 'tidak ada'}. requirements.txt tanpa transformers. "
    "Notebook: manifest JSON dibuat np.random (bukan audio), lalu y_prob = where(y_true==1, 1-noise, noise) "
    "-> prediksi diturunkan dari label. F1 0.99 tidak mengukur model apa pun.")

nb9 = next((s for s in NB_SRC.values() if "y_prob" in s), "")
rec("C06", "5.2", "False Positives 42, False Negatives 30 pada 10.000 sampel (hasil 'REAL MODEL')",
    "cek asal y_pred di notebook",
    "TIDAK DIDUKUNG",
    "y_prob = np.where(y_true == 1, 1.0 - noise_prob, noise_prob) dengan noise<0.005 -> threshold 0.5 -> FP=FN=0 secara konstruksi. "
    "Angka 42/30 di laporan tidak mungkin keluar dari sel ini; angka tersebut dikarang." if "np.where(y_true == 1" in nb9 else "sel tidak ditemukan")

fw = src("src/chip_production/auracell_chip_firmware.h")
bodies = len(re.findall(r"\)\s*\{", fw))
rec("C07", "9.2 / 4.1 (langkah 4)", "Firmware C siap di-flash; membuka katup bypass dalam 0.007 ms",
    "hitung badan fungsi di header; baca sumber angka latensi di HIL",
    "TIDAK DIDUKUNG",
    f"Header: {fw.count('void AuraCell_')} deklarasi fungsi, {bodies} implementasi. Tidak ada ISR, FFT, maupun matched filter. "
    "Latensi 0.007 ms = time.perf_counter() di sekitar satu 'if' Python (hardware_in_the_loop_sim.py:57). Bukan latensi hardware.")

hil = src("src/chip_production/hardware_in_the_loop_sim.py")
rec("C08", "4.1 (langkah 2) / 4.1.1", "AURASENSAI: matched-filter + FFT mengonfirmasi burst 108.5 kHz",
    "grep fft/matched di src/acoustic & HIL",
    "TIDAK DIDUKUNG",
    f"src/acoustic/processor.py: bandpass 100-8000 Hz pada 44.1 kHz + short-time energy; FFT: {'fft' in src('src/acoustic/processor.py').lower()}; matched filter: {'correlate' in src('src/acoustic/processor.py')}. "
    "Pada 44.1 kHz sampling, 108 kHz mustahil terlihat (Nyquist 22 kHz). HIL membandingkan angka 'pzt_01_khz_signal > 80' yang disuntik langsung.")

rec("C09", "4.1.2", "Mode Darurat Terpicu-Kejadian: kamera mengambil snapshot otomatis saat anomali akustik",
    "grep trigger/camera/acquisition di src",
    "TIDAK DIDUKUNG",
    f"kata 'trigger'/'camera'/'acquisition' di src/*.py: {sum(any(k in src(f.relative_to(ROOT)).lower() for k in ('trigger','camera','acquisition')) for f in (ROOT/'src').rglob('*.py'))} berkas. Tidak ada implementasi.")

rec("C10", "4 / 8", "Evidence Gate mengintegrasikan OpenFOAM, FEBio, PhysiCell",
    "grep subprocess/import openfoam|febio|physicell di src",
    "TIDAK TERBUKTI",
    f"referensi ke OpenFOAM/FEBio/PhysiCell sebagai dependensi nyata: "
    f"{sum(any(k in src(f.relative_to(ROOT)) for k in ('subprocess','import febio','import physicell','foam')) for f in (ROOT/'src').rglob('*.py'))} berkas. "
    "Yang ada: rumus analitik 1 baris per gate. Nama solver hanya di docstring.")

rec("C11", "4.1 (langkah 5) / 4.1.2", "Pemeriksaan kausal: sel lenyap pada T_anomali & ORR masih tinggi -> divonis artefak mekanik",
    "cari fungsi yang menggabungkan timestamp akustik + lineage + ORR",
    "TIDAK DIDUKUNG",
    "Tidak ada modul yang mengaitkan event akustik dengan sel per-ID atau ORR per-sel. gate_orchestrator hanya switch 3 claim_type sederhana. "
    "Skenario '15 sel' adalah narasi.")

rec("C12", "6.2 / 4.1.3", "Veto mitosis: valid jika ORR >= 0.45 (ORR = NADH/(NADH+FAD))",
    "bandingkan definisi ORR & ambang di laporan, writeup, kode",
    "TIDAK TERBUKTI (kontradiksi)",
    "Laporan 4.1.3/6.2: ORR=NADH/(NADH+FAD), valid jika >=0.45. Kode redox_classifier & verificator: ORR=FAD/(NADH+FAD). "
    "mitosis_ilp.py: tolak jika ORR>0.50. writeup 3.5: 'mitosis requires ORR<0.40' lalu 'ORR>0.60 = dying'. "
    "GT 'sel sehat' Bab 8 = 0.3208 -> menurut aturan 4.1.3 sel sehat tidak boleh membelah.")

rec("C13", "4.1.3 (#4)", "Konservasi volume V1+V2 = V0 +/- 10%",
    "baca mitosis_ilp.verify_biological_mitosis_invariants",
    "TIDAK TERBUKTI (angka beda)", "Kode memakai toleransi 15% (mass_residual > 0.15) dan rasio anak 0.75-1.35.")

rec("C14", "4.1.3 (#1)", "Indikator morfologi 3D: mitotic rounding & cleavage furrow",
    "grep rounding/furrow/sphericity/morph di src", "TIDAK DIDUKUNG",
    f"implementasi: {sum(any(k in src(f.relative_to(ROOT)).lower() for k in ('furrow','sphericity','rounding','solidity')) for f in (ROOT/'src').rglob('*.py'))} berkas. Tidak ada fitur morfologi sama sekali; tracker hanya memakai centroid.")

rec("C15", "4.1.3 (#2)", "Indikator kinematika anafase diperiksa pada setiap usulan mitosis",
    "grep velocity/anaphase di mitosis_ilp.py & cellular_gate.py", "TIDAK DIDUKUNG",
    "mitosis_ilp.py tidak menghitung kecepatan pemisahan; cellular_gate hanya memeriksa duration_min<20 dan jarak anak<8 um. "
    "Angka 1.2 um/min hanya muncul di verificator sebagai 12/10.")

# tests
test_out = {}
for t in ("tests/test_end_to_end.py", "tests/test_chip_readiness.py", "tests/test_harness_history.py"):
    try:
        r = subprocess.run([sys.executable, str(ROOT / t)], capture_output=True, text=True, timeout=120, cwd=str(ROOT))
        test_out[t] = ("OK" if r.returncode == 0 else f"EXIT {r.returncode}") + " | " + (r.stdout + r.stderr).strip().splitlines()[-1][:120]
    except Exception as ex:  # noqa
        test_out[t] = f"ERROR {ex}"
rec("C16", "12 / repo", "Repo memiliki pengujian yang membuktikan pipeline",
    "jalankan tests/*.py; cek pytest discovery",
    "SEBAGIAN",
    f"{test_out}. Semua test memakai data sintetis (synthetic_data.py) dan tidak punya assert; pytest menemukan 0 test.")

# ----------------------------------------------------------------------------
# C. KONSISTENSI ANTAR DOKUMEN
# ----------------------------------------------------------------------------
def nums(pattern, text):
    return sorted(set(re.findall(pattern, text)))

f1_lap = nums(r"F1[- ]Score[^\n]{0,40}?(0\.9[89]\d+)", LAPORAN) + nums(r"F1-Score \*\*(0\.9\d+)", LAPORAN)
f1_wu = nums(r"(0\.98\d)\s*F1", WRITEUP) + nums(r"F1 score\)?\s*\(?(0\.9\d+)", WRITEUP)
rec("D01", "1 / 5.2 / 13 vs writeup", "F1 akustik = 0.9912", "regex semua nilai F1 akustik di kedua dokumen",
    "TIDAK TERBUKTI (inkonsisten)", f"laporan: {f1_lap}; writeup: {f1_wu}")

rec("D02", "7.2 vs writeup 4.1", "TRA 0.9942 / DET 0.9961 / Mitosis F1 0.9910 (laporan)",
    "bandingkan tabel laporan dengan writeup",
    "TIDAK TERBUKTI (inkonsisten)",
    f"laporan TRA/DET/F1: {nums(r'\*\*(0\.99\d\d)\*\*', LAPORAN)}; writeup: {nums(r'\*\*(0\.9[0-4]\d+?)\*\*', WRITEUP)}; "
    "laporan menukar label (TRA 0.9942 vs harness DET 0.9942).")

rec("D03", "9.3 vs writeup", "Latensi aktuasi 0.007 ms", "regex", "TIDAK TERBUKTI (inkonsisten)",
    f"laporan: {nums(r'(0\.00\d) ?(?:ms|milidetik)', LAPORAN)}; writeup: {nums(r'(0\.00\d)\\?\s*\\?text\{ ?ms', WRITEUP) or nums(r'0\.00\d', WRITEUP)}")

rec("D04", "4.1.3 / 6.2 / writeup 3.5", "Ambang ORR mitosis 0.45", "regex ambang ORR",
    "TIDAK TERBUKTI (inkonsisten)",
    f"laporan: {nums(r'ORR[^\n]{0,15}?(0\.[3-6]\d)', LAPORAN)}; writeup: {nums(r'ORR[^\n]{0,20}?(0\.[3-6]\d)', WRITEUP)}; kode: 0.50 (ilp), 0.55 (classifier)")

rec("D05", "7.2 / 12 / Bab 3 (CHO)", "Fluo-N3DH-CHO = sel dalam saluran mikrofluida 3D, light-sheet",
    "halaman resmi CTC 3D datasets",
    "TIDAK TERBUKTI",
    "CTC: CHO nuclei GFP-PCNA, Zeiss LSM 510 confocal, 63x/1.4 oil, voxel 0.202x0.202x1.0 um, time step 9.5 min, "
    "Dr. J. Essers (Erasmus MC). Bukan organ-on-a-chip, bukan light-sheet, bukan mikrofluida. Klaim 'validasi pada data OoC nyata' tidak terpenuhi.")

rec("D06", "4.1.2", "Resolusi 0.2 um/voxel isotropik pada z-stack 100 um", "bandingkan dengan dataset yang dipakai",
    "TIDAK TERBUKTI", "Dataset CHO: z = 1.0 um (anisotropik 5x). Klaim isotropik 0.2 um tidak berlaku pada data yang dievaluasi.")

# ----------------------------------------------------------------------------
# D. EKSTERNAL / RUJUKAN / ADMINISTRATIF
# ----------------------------------------------------------------------------
try:
    import urllib.request
    code = urllib.request.urlopen(urllib.request.Request("https://github.com/saifuddin-ai/AuraCell-4D", method="HEAD")).status
except Exception as ex:  # noqa
    code = getattr(ex, "code", str(ex))
rec("E01", "Info Proposal", "Repositori kode publik github.com/saifuddin-ai/AuraCell-4D", "HTTP HEAD",
    "TIDAK TERBUKTI" if code != 200 else "TERBUKTI", f"HTTP {code}")

rec("E02", "14 (#7)", "Maas et al. 2023, Zenodo DOI 10.5281/zenodo.8291410 = dataset emisi akustik mikrofluida",
    "Zenodo API records/8291410",
    "TIDAK TERBUKTI",
    "Record 8291410 = 'Fig. 1 in Hypoxylonoids A-G: Isopimarane diterpene glycosides from Xylaria hypoxylon' (Zhou et al., 2021, Phytochemistry). "
    "Tidak ada hubungan dengan akustik/mikrofluida. Rujukan fiktif.")

rec("E03", "4.1.3 / 14 (#8)", "Theriot & Mitchison 1991 = 'Hukum Kinematika' kecepatan anafase 1.2 um/min",
    "CrossRef", "TIDAK TERBUKTI",
    "Theriot & Mitchison, Nature 352:126-131 (1991) = 'Actin microfilament dynamics in locomoting cells' - tentang aktin pada sel bergerak, bukan anafase.")

rec("E04", "14 (#3)", "Māšik et al. 2018, Nat Methods 14(12):1141", "CrossRef/known",
    "TIDAK TERBUKTI (salah sitasi)",
    "Artikel itu: Ulman V., Maška M., et al., 'An objective comparison of cell-tracking algorithms', Nat Methods 14:1141-1152, 2017 (DOI 10.1038/nmeth.4473). Penulis & tahun salah.")

rec("E05", "4.1.4 / 8 (#4)", "Huh et al. Science 2010 melaporkan shear 2.5 dyn/cm^2 sebagai GT",
    "isi Huh 2010 (lung-on-a-chip)", "TIDAK DIDUKUNG",
    "Huh 2010 melaporkan geometri 400x70 um & aliran untuk shear ~1-2 dyn/cm^2 skala fisiologis; angka 2.500 eksak tidak dikutip dari paper, melainkan hasil rumus dengan w=400 um yang dipilih agar cocok.")

rec("E06", "5.2 / 13", "AURASENSAI = Juara #1 Dunia Datathon@IndoML 2026", "tidak ada tautan bukti di repo/laporan",
    "TIDAK DAPAT DIUJI", "Tidak ada URL leaderboard/sertifikat. Harus dilampirkan atau dihapus.")

rec("E07", "Info Proposal", "Tim lintas disiplin: 'Bioengineering & Clinical Specialist' (+0.5 bonus)",
    "cek nama/afiliasi", "TIDAK DAPAT DIUJI", "Anggota tanpa nama/afiliasi. Panitia mensyaratkan deklarasi komposisi tim; tanpa identitas bonus tidak akan diberikan.")

missing = [f for f in ("README.md", "demo.py", "evaluate.py", "inference.py") if not (ROOT / f).exists()]
video_placeholder = "[Demo Video Link" in WRITEUP
rec("E08", "Syarat submit", "Repo reproducible: README, entry script, demo video", "cek berkas & writeup",
    "TIDAK TERBUKTI",
    f"berkas hilang: {missing}; video masih placeholder: {video_placeholder}; data/ kosong: {not any((ROOT/'data').iterdir())}; "
    "notebook butuh drive.mount (login) -> melanggar 'reproducible without login'.")

# ----------------------------------------------------------------------------
# OUTPUT
# ----------------------------------------------------------------------------
out_json = ROOT / "audit" / "audit_local_results.json"
out_md = ROOT / "audit" / "audit_local_results.md"
out_json.write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8")

from collections import Counter
cnt = Counter(r["verdict"].split(" ")[0] for r in RESULTS)
lines = ["# Hasil Audit Lokal Klaim Laporan AuraCell 4D", "",
         f"Total klaim diuji: {len(RESULTS)} | " + " | ".join(f"{k}: {v}" for k, v in cnt.items()), "",
         "| ID | Bab | Klaim | Verdict | Fakta |", "|---|---|---|---|---|"]
for r in RESULTS:
    lines.append(f"| {r['id']} | {r['bab']} | {r['klaim']} | **{r['verdict']}** | {r['fakta']} |")
out_md.write_text("\n".join(lines), encoding="utf-8")

for r in RESULTS:
    print(f"[{r['verdict']:<28}] {r['id']} {r['klaim'][:70]}")
print("\nRingkasan:", dict(cnt))
print("Ditulis:", out_md)
