# AUDIT KLAIM — LAPORAN TEKNIS LENGKAP AURACELL 4D

**Tanggal audit:** 8 Oktober 2026 · **Deadline Kaggle:** 10 Oktober 2026
**Dokumen yang diaudit:** `docs/LAPORAN_TEKNIS_LENGKAP_AURACELL_4D.md` (dan `writeup.md` yang disinkronkan)
**Metode:** (1) hitung ulang rumus fisika; (2) analisis statis & eksekusi kode repo; (3) verifikasi rujukan via CrossRef/Zenodo/CTC; (4) eksekusi nyata di Google Colab pada dataset Fluo-N3DH-CHO resmi dengan metrik `py-ctcmetrics`; (5) inventaris Google Drive `AuraCell4D_Datasets`.
**Artefak:** `audit/audit_local_claims.py` → `audit/audit_local_results.{md,json}` · `audit/colab_claim_audit.py` → `audit/colab_claim_results.json`

Skala verdict: **TERBUKTI** · **SEBAGIAN** · **TIDAK TERBUKTI** (bertentangan dengan fakta) · **TIDAK DIDUKUNG** (angka tidak dihasilkan kode/data apa pun) · **TIDAK DAPAT DIUJI**.
Tindakan: **PERTAHANKAN** · **TURUNKAN** (ganti ke angka nyata) · **REFRAME** (nyatakan sebagai simulasi/konsep) · **HAPUS**.

---

## 0. Ringkasan

| | Jumlah |
|---|---:|
| Klaim diuji | 46 |
| TERBUKTI | 1 |
| SEBAGIAN | 2 |
| TIDAK TERBUKTI | 19 |
| TIDAK DIDUKUNG | 21 |
| TIDAK DAPAT DIUJI | 3 |

**Tiga fakta penentu:**
1. **Google Drive `AuraCell4D_Datasets` kosong (0 berkas).** Klaim "10.000 rekaman suara mikro di Drive", "dataset CTC di Drive", dan "model AURASENSAI" tidak punya artefak apa pun.
2. **Tracker Velocell asli, dijalankan pada data CTC nyata, mendeteksi 0 dari 16 mitosis** (recall 0%, F1 0.0) — padahal laporan menulis Mitosis F1 0.991 dan writeup 0.906. Semua skor CTC di repo adalah literal yang ditulis tangan.
3. **Rumus inti 4.1.4 salah:** τ untuk 1000×100 µm @10 µL/min = 1.0 dyn/cm², bukan 2.5. Minnaert 30 µm = 109.6 kHz, bukan "108.5 tepat / 0.000%". Rumus Krogh di laporan (faktor 6) tidak menghasilkan 151 µm.

---

## 1. Fisika & rumus (Subbab 4.1.4, 5.1, Bab 8)

| ID | Klaim (lokasi) | Uji | Fakta | Verdict | Tindakan |
|---|---|---|---|---|---|
| P01 | τ_GT = 6μQ/wh² = **2.500** dyn/cm² untuk w=1000, h=100 µm, Q=10 µL/min (4.1.4) | hitung ulang | **1.000 dyn/cm²**. 2.5 hanya bila w=400 µm (hardcode `fluid_cfd_verificator.py:24`). `fluid_gate.py` memakai 100×50 → 40 dyn/cm². Tiga geometri berbeda. | TIDAK TERBUKTI | TURUNKAN: tulis 1.0 dyn/cm² & satukan geometri di semua berkas |
| P02 | Minnaert R=30 µm → **108.5 kHz tepat**, residual 0.000% (5.1, Bab 8 #1) | hitung ulang | 109.6 kHz. JSON program sendiri: 109.61 vs 108.8 → 0.741%. | TIDAK TERBUKTI | TURUNKAN: 109.6 kHz; hapus "tepat" |
| P03 | Tabel Bab 8: residual tiap baris (mayoritas 0.000%) | bandingkan dengan `benchmarks/ground_truth_verification_results.json` | Baris #1 tabel 0.000% vs JSON 0.741%; nilai "terhitung" di tabel disalin dari kolom GT, bukan dari output. | TIDAK TERBUKTI | TURUNKAN: salin angka JSON apa adanya |
| P04 | 15 benchmark = validasi terhadap "baku emas sains internasional" | AST verificator | Semua `gt_expected` adalah konstanta literal di baris setelah rumus yang sama → membandingkan rumus dengan dirinya sendiri. | TIDAK DIDUKUNG | REFRAME: "unit test konsistensi solver", bukan validasi |
| P05 | Krogh R_c = √(6DC₀/Q) = 151.186 µm (4.1.4, #11) | hitung dua versi | Rumus laporan (faktor 6) → **262 µm**; kode pakai faktor 2 → 151 µm. | TIDAK TERBUKTI | TURUNKAN: perbaiki rumus; GT tetap self-defined |
| P06 | Womersley α = 0.1371 (#6) | hitung | 0.1371 ✓ (R=50 µm, f=1.2 Hz, ν=1e-6) | TERBUKTI | PERTAHANKAN (tanpa label "GT literatur") |
| P07 | Defleksi PDMS 216.0 µm "FEBio Mooney-Rivlin" (#7) | baca kode | Rumus plat tipis empiris `0.662·a·(pa/Et)^(1/3)`; tidak ada FEBio/Mooney-Rivlin. | TIDAK DIDUKUNG | REFRAME: sebut rumus sebenarnya |
| P08 | Gelembung → τ melonjak **18.2 dyn/cm²** via Navier-Stokes/Rayleigh-Plesset (4.1 langkah 3) | analisis rumus + grep | τ=6μQ/wh² tunak; gelembung tidak mengubah Q → tidak bisa melonjak. Rayleigh-Plesset: 0 implementasi. | TIDAK DIDUKUNG | HAPUS angka 18.2 & skenario |
| P09 | Kriteria anafase 1.20±0.25 µm/min terukur (4.1.3 #2) dengan sampling 5–15 min (4.1.2) | Δt dataset 9.5 min vs anafase 5–10 min | 0.5–1 frame dalam anafase → kecepatan tidak terukur. Kriteria 2 dan Mode A saling meniadakan. | TIDAK TERBUKTI | HAPUS kriteria 2 atau ubah protokol ke ≤1 min/frame |
| P10 | ADC 500 kSps, target ESP32-S3 (4.1.1, 9.2) | Nyquist; spesifikasi ADC | 500 kSps > 2×108 kHz ✓ untuk Cortex-M7+ADC eksternal; ESP32-S3 ADC internal ≈ 83 kSps maks. | SEBAGIAN | TURUNKAN: coret ESP32-S3 |
| P11 | PZT-03 mencatat ΔP > 500 Pa (4.1 langkah 2) | chip_spec + HIL | PZT-03 = transduser akustik 1–10 kHz, tidak mengukur ΔP statis. HIL menyuntik 144/850 Pa dengan `np.random`. | TIDAK DIDUKUNG | REFRAME: butuh sensor tekanan terpisah |
| P12 | "2.800× lebih cepat dari batas 20 ms" (9.3) | 20/0.007 | Aritmetika benar, premis (0.007 ms) tidak valid → lihat C07 | TIDAK DIDUKUNG | HAPUS |

## 2. Perilaku kode vs klaim (Bab 4.1, 5, 6, 7, 8, 9)

| ID | Klaim | Uji | Fakta | Verdict | Tindakan |
|---|---|---|---|---|---|
| C01 | Skor CTC (DET/TRA/Mitosis F1) = evaluasi empiris (7.2, 4.1.5) | AST `real_ctc_evaluator.py` | `det_score=0.942`, `tra_score=0.918`, … literal (baris 98–103). TIFF tidak dibaca, tracker tidak dipanggil. | TIDAK DIDUKUNG | TURUNKAN ke K3 |
| C02 | Notebook Colab menghasilkan skor CTC | baca sel 12 | Dict literal; GT hanya dihitung jumlahnya. | TIDAK DIDUKUNG | TURUNKAN ke K3 |
| C03 | Composite Kaggle 0.99254, "Scored (Verified)" | `evaluation_harness.py` + halaman kompetisi | Profil v1–v4 dict literal; CSV & timestamp mundur dibuat kode; kompetisi writeup-only tanpa leaderboard. | TIDAK DIDUKUNG | HAPUS seluruh "submission history" |
| C04 | Velocell = ILP network-flow (7.1) | grep solver | `pulp` tidak di-import di mana pun; algoritma greedy nearest-neighbour. | TIDAK TERBUKTI | REFRAME: "greedy linking + gate"; atau implementasikan ILP |
| C05 | Model AURASENSAI (AudioMAE+AST+Whisper BiGRU) dievaluasi 10.000 sampel (5.2) | grep src, requirements, Drive | Tidak ada model/bobot; manifest JSON acak; `y_prob` diturunkan dari `y_true`. | TIDAK DIDUKUNG | HAPUS tabel 10.000 sampel |
| C06 | FP=42, FN=30 (5.2) | konstruksi notebook | noise<0.005, threshold 0.5 → FP=FN=0 pasti. 42/30 tidak mungkin dari kode itu. | TIDAK DIDUKUNG | HAPUS |
| C07 | Firmware siap flash; katup 0.007 ms (9.2, 4.1 langkah 4) | header + HIL | Header: 4 deklarasi, 0 implementasi. 0.007 ms = `perf_counter` satu `if` Python. | TIDAK DIDUKUNG | REFRAME: "simulasi logika; latensi hardware belum diukur" |
| C08 | Matched-filter + FFT konfirmasi 108.5 kHz (4.1.1) | `processor.py` | Sampling 44.1 kHz (Nyquist 22 kHz) → 108 kHz mustahil; tidak ada FFT/korelasi. | TIDAK DIDUKUNG | REFRAME/HAPUS |
| C09 | Mode darurat kamera terpicu akustik (4.1.2) | grep | Tidak ada implementasi. | TIDAK DIDUKUNG | REFRAME: konsep |
| C10 | Evidence Gate = OpenFOAM + FEBio + PhysiCell (Bab 4, 8) | grep | Nama hanya di docstring; isi = rumus analitik 1 baris. | TIDAK TERBUKTI | HAPUS nama solver |
| C11 | Konsiliasi kausal (T_anomali + ORR + lineage) → vonis artefak (4.1 langkah 5) | cari modul | Tidak ada modul yang menggabungkan ketiganya. | TIDAK DIDUKUNG | REFRAME: konsep |
| C12 | Veto mitosis ORR ≥ 0.45, ORR=NADH/(NADH+FAD) (4.1.3, 6.2) | bandingkan dokumen & kode | Kode: ORR=FAD/(NADH+FAD), tolak >0.50; writeup 3.5: "<0.40"; GT sehat 0.3208 → sel sehat tak boleh membelah menurut 4.1.3. | TIDAK TERBUKTI | TURUNKAN: satu definisi (Skala) & satu ambang |
| C13 | Konservasi volume ±10% (4.1.3 #4) | kode | ±15% dan rasio anak 0.75–1.35. | TIDAK TERBUKTI | TURUNKAN |
| C14 | Indikator morfologi 3D (rounding, furrow) (4.1.3 #1) | grep | Tidak ada fitur morfologi; hanya centroid. | TIDAK DIDUKUNG | HAPUS/REFRAME |
| C15 | Indikator kinematika anafase diperiksa (4.1.3 #2) | kode | Tidak dihitung di tracker. | TIDAK DIDUKUNG | HAPUS |
| C16 | Pengujian repo membuktikan pipeline | jalankan tests | Jalan tanpa error, tetapi data sintetis & tanpa assert; pytest 0 test. | SEBAGIAN | TURUNKAN: tambah assert & data nyata |

## 3. Eksekusi nyata di Colab (data CTC resmi)

| ID | Uji | Hasil | Klaim terkait | Verdict | Tindakan |
|---|---|---|---|---|---|
| K1 | Inventaris Drive `AuraCell4D_Datasets` | **0 berkas**; hanya 2 folder kosong | "10.000 dataset di Drive", "data CTC di Drive" (4.1.5, 5.2, 11.1) | TIDAK DIDUKUNG | HAPUS |
| K5 | Bobot model di Drive/repo | tidak ada | AURASENSAI ensemble | TIDAK DIDUKUNG | HAPUS |
| K2 | Metadata Fluo-N3DH-CHO | CHO GFP-PCNA, confocal LSM 510, voxel 0.202×0.202×1.0 µm, Δt 9.5 min, Erasmus MC; 27+24 track, 10+6 anak-mitosis, 92 frame, 5 slice z | "mikrofluida 3D light-sheet" (7.2), "0.2 µm isotropik" (4.1.2), "data OoC nyata" | TIDAK TERBUKTI | TURUNKAN deskripsi dataset |
| K3 | Velocell asli pada centroid GT, metrik `py-ctcmetrics` | seq01: DET 1.000, TRA 0.9983, **mitosis 0/10**; seq02: DET 1.000, TRA 0.9987, **mitosis 0/6**; 0.11 s/volume | DET 0.942/0.9961, TRA 0.918/0.9942, Mitosis F1 0.906/0.991, 0.42 s/volume | TIDAK DIDUKUNG | TURUNKAN: laporkan TRA-linking 0.998 (deteksi GT) & Mitosis F1 0.0 — atau perbaiki gate agar mitosis lolos |
| K4 | Keterukuran anafase | 0.5–1 frame | kriteria 4.1.3 #2 | TIDAK TERBUKTI | HAPUS |

Catatan K3: `AOGM_EA` = 11 dan 6 adalah tepat jumlah edge induk→anak yang hilang; gate `verify_biological_mitosis_invariants` (rasio volume 0.75–1.35 & massa ±15% pada volume nukleus dari mask) menolak semua pembelahan nyata. "Veto anti-halusinasi" pada data nyata justru menghapus seluruh mitosis sejati.

## 4. Konsistensi antar dokumen

| ID | Besaran | Laporan | Writeup | Kode | Verdict | Tindakan |
|---|---|---|---|---|---|---|
| D01 | F1 akustik | 0.9912 (Bab 1, 13) & 0.98973 (5.2) | 0.983 | — | TIDAK TERBUKTI | HAPUS (lihat C05) |
| D02 | CTC TRA/DET/F1 | 0.9942/0.9961/0.9910 | 0.918/0.942/0.9056 | harness: DET 0.9942 (label tertukar) | TIDAK TERBUKTI | TURUNKAN ke K3 |
| D03 | Latensi aktuasi | 0.007 ms | <0.005 ms | perf_counter | TIDAK TERBUKTI | REFRAME |
| D04 | Ambang ORR mitosis | ≥0.45 | ≥0.45 & <0.40 | >0.50 tolak; 0.55 viabilitas | TIDAK TERBUKTI | TURUNKAN: satu nilai |
| D05 | Toleransi volume | ±10% | ±10% | ±15% | TIDAK TERBUKTI | TURUNKAN |
| D06 | Interval minimum mitosis | "<40 min ditolak" | <40 min | gate: <20 min; verificator 40–90 | TIDAK TERBUKTI | TURUNKAN |

## 5. Rujukan & administratif

| ID | Klaim | Fakta | Verdict | Tindakan |
|---|---|---|---|---|
| E01 | Repo `github.com/saifuddin-ai/AuraCell-4D` | HTTP 404 | TIDAK TERBUKTI | Buat repo publik (syarat wajib) |
| E02 | Maas et al. 2023, Zenodo 10.5281/zenodo.8291410 (dataset akustik mikrofluida) | Record = "Fig. 1 in Hypoxylonoids A–G…", Phytochemistry 2021 — struktur kimia jamur | TIDAK TERBUKTI | HAPUS rujukan |
| E03 | Theriot & Mitchison 1991 = "Hukum Kinematika" anafase | "Actin microfilament dynamics in locomoting cells" | TIDAK TERBUKTI | HAPUS/ganti rujukan |
| E04 | "Māšik et al. 2018, Nat Methods 14(12):1141" | Ulman, Maška et al., 2017, 14(12):1141–1152, DOI 10.1038/nmeth.4473 | TIDAK TERBUKTI | PERBAIKI |
| E05 | Huh 2010 melaporkan GT 2.5 dyn/cm² | Angka dari rumus dengan w=400 µm, bukan dikutip | TIDAK DIDUKUNG | REFRAME |
| E06 | AURASENSAI Juara #1 Datathon@IndoML 2026 | Tidak ada tautan bukti (Drive memuat notebook IndoML Track2 tetapi bukan bukti peringkat) | TIDAK DAPAT DIUJI | Lampirkan bukti atau hapus |
| E07 | Anggota "Bioengineering & Clinical Specialist" (+0.5) | Tanpa nama/afiliasi | TIDAK DAPAT DIUJI | Isi identitas atau hapus klaim bonus |
| E08 | Repo reproducible (README, entry script, video) | README/demo.py/evaluate.py tidak ada; video placeholder; `data/` kosong; notebook butuh login Drive | TIDAK TERBUKTI | Lengkapi |
| E09 | Formulir registrasi panitia | Belum ada bukti pengisian | TIDAK DAPAT DIUJI | Isi sebelum 10 Okt |

---

## 5b. Verifikasi "rincian letak dataset & tautan publik" (ditempel pemilik, 8 Okt)

Dokumen tersebut mengklaim lokasi dataset 10.000 suara dan 5 sumber publik. Semua dicek langsung:

| Klaim di rincian | Fakta | Verdict |
|---|---|---|
| Folder Drive `1tWQGALVBlfBiujszjoKprBnjxS0jhtOw` berisi `micro_acoustics_10k/dataset_10k_manifest.json` + `aurasensai_10k_evaluation_report.json` | Dibuka di Chrome (akun pemilik) dan di-mount di Colab: hanya `benchmark_raw` dan `ground_truth`, **keduanya kosong** (dimodifikasi 4 Okt, ukuran —). Tidak ada subfolder `micro_acoustics_10k`, tidak ada manifest, tidak ada laporan evaluasi. | TIDAK TERBUKTI |
| Zenodo 8291410 "Microfluidic Acoustic Emissions" | Record = gambar struktur kimia *Xylaria hypoxylon* (Phytochemistry 2021). | FIKTIF |
| Zenodo 11186716 "APECSS Cavitation Bubbles" | Record (redirect ke 11186717) = makalah bahasa Uzbek tentang perkembangan bicara anak (PDF 536 kB). | FIKTIF |
| BubbleML (HPCForge) = "nukleasi & letupan gelembung" | Dataset **simulasi pendidihan** (pool/flow boiling, medan suhu/kecepatan). Tidak ada audio, bukan mikrofluida. | SALAH DESKRIPSI |
| HF `luviner/industrial-faults` = "6.500 sampel suara anomali industri" | Ada, tetapi **tabular sintetis** 8 kanal sensor (vibrasi xyz, suhu, tekanan, arus, aliran, dB level), bukan audio. Label 10 = cavitation (pompa industri). | SALAH DESKRIPSI |
| Datathon@IndoML 2026: "5.517 klip audio, AURASENSAI Rank #1 Dunia" | Track 1 = deteksi noise pada ucapan Indic (Vaani), 90.637 segmen latih. Leaderboard Fase 1 Top-8: CodeAMU, ARCLY INDIA, **Syehsyoh (posisi ke-3)**; hasil final **TBA**. Bukan kavitasi, bukan #1. | TIDAK TERBUKTI |
| DOI Theriot & Mitchison 10.1038/352126a0 → "kecepatan anafase 1.2 µm/min" | Judul: "Actin microfilament dynamics in locomoting cells". | SALAH RUJUKAN |
| DOI Krogh 10.1113/jphysiol.1919.sp001843 | CrossRef: Herring P.T., "The physiological action of extracts of the electrical organs of the skate…", J Physiol 52:454–456. **Bukan makalah Krogh.** | SALAH DOI |
| DOI "Māšik 2018" 10.1038/nmeth.4473 | DOI benar, tetapi = Ulman et al. **2017**. | SALAH SITASI |
| DOI Huh 2010, Minnaert 1933, Skala 2007 | Benar (judul/jurnal cocok). Namun Skala 2007 PNAS tidak memberi angka 0.3207, dan Huh 2010 tidak menyebut 2.500 dyn/cm². | DOI OK, ANGKA TIDAK |
| CTC Fluo-N3DH-CHO zip | Ada & terunduh (lihat K2). Deskripsi "in Microfluidic Channel" salah. | OK (deskripsi salah) |

Kesimpulan 5b: dari 5 "sumber dataset akustik publik", **2 fiktif, 2 bukan audio, 1 bukan kavitasi**. Tidak ada satu pun sumber audio kavitasi mikrofluida nyata di balik klaim 10.000 sampel.

## 6. Apa yang boleh tetap diklaim (versi jujur)

1. **Linking 1-ke-1 tracker** pada deteksi sempurna: TRA 0.998 (2 sekuens Fluo-N3DH-CHO, metrik resmi `py-ctcmetrics`), 0.11 s/volume di Colab CPU. **Mitosis belum terdeteksi (F1 0.0)** — kerja lanjutan.
2. **Solver fisika analitik** (Poiseuille, Minnaert, Womersley, Krogh faktor-2, Hertz, plat tipis): konsisten secara internal; berguna sebagai *sanity gate*, bukan "validasi baku emas".
3. **Desain konsep** sensor akustik + spektral + visi dan alur 4.1: layak dipertahankan **sebagai konsep/simulasi**, dengan kata "simulasi" eksplisit dan tanpa angka kinerja hardware.
4. **GUI 5 langkah** dan spesifikasi cartridge: nyata (statis/simulasi).

## 7. Urutan perbaikan 48 jam

1. Hapus/ganti semua angka di kolom **HAPUS**; turunkan kolom **TURUNKAN** memakai angka K3 & hitungan P01/P02/P05.
2. Satukan geometri (1000×100 atau 400×100) dan definisi/ambang ORR di laporan, writeup, `chip_spec.py`, `fluid_gate.py`, verificator, `mitosis_ilp.py`.
3. Ganti kategori ke **Model & Algorithm** atau **Tool & Platform**; pindahkan firmware/HIL ke "peta jalan".
4. Buat repo publik + README + `evaluate.py` (= `audit/colab_claim_audit.py` versi bersih tanpa Drive) + rekam video 5 menit dari GUI + isi form registrasi.
5. Perbaiki rujukan E02–E04.
