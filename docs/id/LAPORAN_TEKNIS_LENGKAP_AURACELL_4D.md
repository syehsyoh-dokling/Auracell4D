# LAPORAN TEKNIS: AURACELL 4D
## Pelacakan Silsilah Sel 3D+t Berbasis Network-Flow ILP dengan Gerbang Fisika-Biologi untuk Mikroskopi Time-Lapse Organ-on-a-Chip

---

### INFORMASI SUBMISI
* **Kompetisi:** The 5th Pazhou Algorithm Competition · AI4S Open Innovation: AI for Life Science (AI + Organ-on-a-Chip)
* **Kategori yang dideklarasikan:** **Model & Algorithm** — ILP network-flow bergerbang fisika untuk pelacakan silsilah sel, dengan ablasi pada data publik Cell Tracking Challenge. Fusi sensor dan aktuasi chip disajikan sebagai **desain konsep & peta jalan**, bukan hasil.
* **Tim:** Saifuddin — AI & sistem (visi komputer, pemrosesan sinyal, optimasi). *Tidak ada anggota biologi/bioteknik yang dideklarasikan; kami tidak mengklaim bonus lintas disiplin.*
* **Repositori kode:** https://github.com/syehsyoh-dokling/Auracell4D · entry script `evaluate.py`
* **Video demo:** `[tautan publik — diisi saat submit]`
* **Dokumen resmi (Inggris):** `writeup.md`. Dokumen ini adalah padanan Bahasa Indonesia dan dijaga sinkron.

> **Konvensi label.** Setiap angka dalam laporan ini berlabel:
> **[Terukur]** — dihasilkan `evaluate.py` pada data publik (`results/ablation.json`), dapat direproduksi reviewer tanpa login.
> **[Desain]** — parameter desain berbasis fisika atau simulasi; **tidak ada klaim kinerja**.
> Draf sebelumnya memuat angka kinerja yang tidak dapat direproduksi; seluruhnya diaudit (`docs/AUDIT_KLAIM.md`, 46 klaim) dan dihapus. Tidak ada angka lama yang dipertahankan kecuali diukur ulang.

---

## DAFTAR ISI
1. Ringkasan
2. Definisi Masalah
3. Data
4. **Di Mana Alat Ini Dipakai dan Apa Arti Setiap Angkanya** (desain operasional)
5. Metode
6. Hasil [Terukur]
7. Uji Konsistensi Fisika [Desain]
8. Limitasi
9. Peta Jalan
10. Reproduksi
11. Kepatuhan Data & Lisensi
12. Daftar Pustaka (DOI terverifikasi)

---

## 1. RINGKASAN

Eksperimen time-lapse organ-on-a-chip (OoC) menghasilkan citra 3D+t yang harus diubah menjadi silsilah sel, hitungan pembelahan, dan pemisahan antara efek obat dengan artefak mekanik (misalnya sel yang lepas akibat gelembung). Tracker greedy standar "menghalusinasi" pembelahan setiap kali dua inti sel berdekatan, dan tidak ada tracker yang sendirian dapat membedakan sel yang mati dari sel yang terlepas oleh lonjakan aliran.

Kontribusi AuraCell 4D: **(i)** *integer linear program* network-flow per pasangan frame — setiap inti pada *t* harus mengambil tepat satu nasib (tersambung, membelah, hilang) dan setiap inti pada *t+1* tepat satu asal (tersambung, anak, muncul); **(ii)** **gerbang biologis sebagai biaya lunak** — penalti rasio volume dan konservasi massa yang **dikalibrasi dari data**, bukan ditetapkan tangan — sehingga pembelahan yang tidak masuk akal secara fisik dihambat, bukan diveto membabi buta.

Pada data publik Cell Tracking Challenge **Fluo-N3DH-CHO** (2 × 92 frame), dengan deteksi dari ground truth untuk mengisolasi kualitas *linking*, ILP menaikkan skor TRA resmi dari **0.928/0.943 (greedy) menjadi 0.997/0.996 [Terukur]** dan memangkas pembelahan palsu dari 178 menjadi 5 pada sekuens 01. Gerbang lunak menambah perbaikan kecil yang konsisten. Recall mitosis masih rendah (F1 terbaik 0.22) dan baseline deteksi label-free kami lemah (DET 0.40–0.53); keduanya dilaporkan sebagai limitasi terbuka. Kami juga menunjukkan *mengapa* versi lama gerbang tampak mencapai TRA 0.998: ia menolak semua pembelahan nyata, karena penanda TRA CTC berukuran seragam.

Mesin yang sama dirancang untuk menerima kanal akustik kontinu dan citra berkala, melekatkan sertifikat LANJUT / TANDAI / TOLAK yang dapat ditelusuri pada setiap peristiwa silsilah, dan memberi peneliti hitungan dosis–respons dengan setiap pengecualian beralasan. Bagian itu hari ini berstatus **[Desain]** terdokumentasi.

---

## 2. DEFINISI MASALAH

Tiga mode kegagalan dominan pada analisis citra OoC:

1. **Pembelahan palsu.** Dua inti bersentuhan → tracker nearest-neighbour membuat induk dengan dua anak. Pada sekuens 92 frame dengan hanya 4 pembelahan nyata, tracker greedy mengusulkan **178** [Terukur].
2. **Tertukarnya identitas dan drift.** Keputusan lokal per frame mengakumulasi kesalahan; metrik TRA resmi menghukum setiap edge yang salah.
3. **Kontaminasi hitungan dosis–respons oleh artefak.** Sel yang terlepas karena gelembung atau lonjakan tekanan dihitung "mati karena obat" bila tidak ada yang mengaitkan peristiwa mekanik dengan garis waktu citra.

Dua yang pertama bersifat algoritmik — ditangani dan **diukur** di sini. Yang ketiga memerlukan kanal sensor yang sudah kami rancang tetapi belum dibangun; Bab 4 menjelaskan persis cara kerjanya dan arti setiap angka, agar reviewer dapat menilai desainnya apa adanya.

---

## 3. DATA

| Butir | Nilai |
|---|---|
| Dataset | Cell Tracking Challenge, **Fluo-N3DH-CHO**, sekuens latih 01 & 02 |
| Biologi / pencitraan | Inti sel CHO dengan GFP-PCNA; Zeiss LSM 510 confocal, 63×/1.4 oil; **kultur konvensional — bukan organ-on-a-chip** |
| Geometri | 92 frame × 5 × 443 × 512 voxel; 0.202 × 0.202 × 1.0 µm; Δt = 9.5 menit |
| Ground truth | Penanda TRA (`man_track*.tif`, `man_track.txt`): 27 / 24 track; 4 / 3 peristiwa pembelahan dengan ≥ 2 anak |
| Penyedia / lisensi | Dr. J. Essers, Erasmus MC Rotterdam; ketentuan CTC; sitasi Ulman, Maška et al., *Nat Methods* 14:1141–1152 (2017) |
| Unduhan | otomatis oleh `evaluate.py` dari `data.celltrackingchallenge.net` |

Tidak ada data pribadi, klinis, atau terbatas. **Tidak ada rekaman OoC nyata dan tidak ada rekaman akustik nyata** yang digunakan; sinyal sintetis diberi label [Desain].

---

## 4. DI MANA ALAT INI DIPAKAI DAN APA ARTI SETIAP ANGKANYA (DESAIN OPERASIONAL)

Bab ini menjawab empat pertanyaan praktis: **di mana** perangkat lunak ini berada, **bagaimana** ia mendengar, **apa arti setiap angka** pada cartridge sungguhan, dan **bagaimana** ia mengubah hari kerja peneliti. Yang berlabel [Terukur] sudah ada dan dievaluasi; yang berlabel [Desain] sudah dispesifikasikan tetapi belum divalidasi pada perangkat keras.

### 4.1 Di mana ia berjalan

| Mode | Lokasi | Masukan | Keluaran | Status |
|---|---|---|---|---|
| **A. Analisis batch** | Workstation lab yang sudah menerima ekspor time-lapse mikroskop | Folder tumpukan TIFF 3D (tata letak CTC atau OME-TIFF), CSV sensor opsional | Graf silsilah, sertifikat per peristiwa, metrik ablasi bila ada GT, log audit JSON | **[Terukur]** (`evaluate.py`) |
| **B. Pemantauan langsung** | Workstation yang sama, terhubung ke reader OoC (ADC piezo + sensor tekanan) dan API akuisisi mikroskop | Aliran akustik kontinu, aliran tekanan, z-stack berkala | Rekomendasi TANDAI/HENTIKAN ke operator secara real-time, snapshot tambahan terpicu-kejadian, log audit yang sama | **[Desain]** |

Mesinnya sama di kedua mode; mode B hanya menambah ingesti sensor dan kanal peringatan operator. **Tidak ada klaim aktuasi katup otonom**: pada mode B perangkat lunak *merekomendasikan*, operator *memutuskan*. Firmware loop tertutup adalah butir peta jalan (Bab 9).

### 4.2 Bagaimana ia mendengar: akustik kontinu, citra berkala, snapshot terpicu-kejadian

* **Kanal akustik bersifat kontinu, bukan berkala [Desain].** Transduser piezo kontak di inlet saluran disampel kontinu ≥ 250 kS/s (Nyquist untuk pita ~110 kHz di bawah). Sinyal di-bandpass dan direduksi menjadi **envelope energi jangka pendek pada jendela 20 ms, hop 10 ms**; peristiwa dinyatakan bila envelope melampaui baseline bergulir sebesar **3.5 σ** (detektor di `src/acoustic/processor.py`, saat ini hanya diuji pada sinyal sintetis).
* **Seperti apa suara gelembung [Desain].** Gelembung gas bebas berjari-jari *R* beresonansi pada frekuensi Minnaert *f* = (1/2π*R*)·√(3γP₀/ρ). Dengan γ = 1.4, P₀ = 101.3 kPa, ρ = 997 kg/m³: *R* = 20 µm → 164 kHz; **30 µm → 109.6 kHz**; 50 µm → 66 kHz. Detektor karena itu memantau **pita 80–180 kHz**; frekuensi pusat burst memberi estimasi ukuran gelembung; viskositas/suhu medium menggesernya beberapa persen sehingga pita sengaja dibuat lebar. *Nilai-nilai ini dihitung, bukan diukur pada chip.*
* **Pencitraan bersifat berkala [Terukur untuk analisis, Desain untuk kontrol].** Z-stack diambil tiap 5–15 menit (data CTC di sini Δt = 9.5 menit). Kadens ini cukup untuk linking dan deteksi pembelahan, tetapi **tidak** untuk kinematika anafase (anafase 5–10 menit → ≤ 1 frame); karena itu kami tidak membuat klaim kinematik apa pun.
* **Snapshot terpicu-kejadian [Desain].** Peristiwa akustik atau tekanan menetapkan stempel waktu *T* dan meminta satu z-stack tambahan dalam 60 detik, sehingga frame "tepat sesudah" peristiwa tersedia meski kadens berkala melewatkannya.

### 4.3 Apa arti setiap angka pada cartridge sungguhan — tabel keputusan

Geometri acuan (satu cartridge, satu tabel, dipakai konsisten di kode dan naskah): saluran **1000 × 100 µm**, panjang 25 mm, perfusi **10 µL/min**, viskositas medium 1 mPa·s.

| Besaran | Cara diperoleh | Nilai baseline yang diharapkan | **LANJUT** | **TANDAI** (log + snapshot tambahan + notifikasi operator) | **HENTIKAN perfusi (rekomendasi)** | Status |
|---|---|---|---|---|---|---|
| Tegangan geser dinding τ = 6µQ/(w h²) | dari laju pompa & geometri cartridge | **1.0 dyn/cm²** | 0.5 – 15 dyn/cm² (rentang fisiologis endotel) | 15 – 30 dyn/cm² | > 30 dyn/cm² | [Desain] dihitung; ambang dari rentang literatur, belum divalidasi di sini |
| Beda tekanan ΔP sepanjang saluran | sensor tekanan (piezo **tidak** mengukur ΔP statis) | baseline Hagen–Poiseuille cartridge (dihitung saat setup) | < 1.5 × baseline | 1.5 – 2.5 × baseline (oklusi 50 % ≈ 2.3 ×) | > 2.5 × baseline atau naik > 20 %/menit (risiko membran) | [Desain] |
| Burst akustik (80–180 kHz, > 3.5 σ) | aliran piezo kontinu | tidak ada | 0 burst | 1 burst → stempel *T*, snapshot; ≥ 3 burst / 10 menit → notifikasi operator | ≥ 10 burst / 10 menit atau burst apa pun bersamaan dengan TANDAI ΔP | [Desain] |
| Sel lenyap dalam ±1 frame dari *T* | tracker: track berakhir pada *T* ± 1 tanpa pembelahan | 0 | 0 | ≥ 1 → setiap sel ditandai **"kandidat artefak mekanik"**, dikeluarkan dari hitungan kematian-obat sambil menunggu tinjauan | — | [Desain] (logika pengecualian memakai tracker yang terukur) |
| Usulan pembelahan dengan penalti gerbang | biaya lunak ILP (rasio volume, konservasi massa) | penalti 0 | penalti 0 → **LANJUT** | penalti > 0 tetapi dipilih ILP → **TANDAI untuk tinjauan** (ditampilkan dengan volume kedua anak) | — | [Terukur] mekanisme; ambang dikalibrasi per sumber deteksi |
| Laju muncul/hilang per frame | variabel ILP a_j / d_i | rendah, stabil | ≤ 2 × median bergulir | > 2 × → **TANDAI** (masalah segmentasi/fokus) | > 5 × berkelanjutan → periksa fokus/aliran sebelum melanjutkan | [Desain] aturan atas besaran terukur |
| DET / TRA | hanya bila ada GT (mode benchmark) | — | — | — | — | [Terukur] pada CTC: TRA 0.997 / 0.996 dengan deteksi GT |

Cara membaca tabel: **angka di kolom LANJUT berarti eksperimen dapat ditafsirkan**; TANDAI tidak pernah menghapus data — ia melekatkan alasan pada suatu peristiwa dan meminta manusia melihat; HENTIKAN adalah rekomendasi kepada operator, karena perangkat lunak hari ini tidak mengendalikan pompa.

### 4.4 Bagaimana ini mengubah pekerjaan peneliti

*Sebelumnya:* ekspor time-lapse → jalankan tracker → gulir frame secara manual untuk menghapus pembelahan palsu yang kentara → hitung sel mati → berharap tidak ada yang terlepas oleh gelembung yang tidak pernah terlihat.

*Dengan AuraCell 4D (mode A, hari ini):* jalankan batch gaya `evaluate.py` → terima graf silsilah yang **pembelahan palsunya sudah jarang (5, bukan 178, pada benchmark [Terukur])**, setiap pembelahan tersisa membawa penalti gerbangnya, dan setiap edge dapat ditelusuri ke biaya ILP. Waktu tinjauan dipakai untuk segelintir peristiwa TANDAI, bukan seluruh film.

*Dengan mode B (desain):* graf yang sama membawa stempel waktu akustik/tekanan; sel yang lenyap tepat setelah peristiwa aliran sudah diberi label kandidat artefak dan dikeluarkan dari hitungan dosis–respons **dengan alasan tertulis di sampingnya** — jejak audit yang dapat diikuti regulator atau reviewer.

---

## 5. METODE

### 5.1 Deteksi
* **Deteksi GT** — centroid dan volume voxel dari penanda TRA CTC. DET = 1 secara konstruksi; mengisolasi kualitas linking.
* **Baseline label-free** — Gaussian (σ = 0.5, 2, 2) → ambang Otsu → distance transform → watershed dari maksimum lokal (jarak min. 12 px), objek < 400 voxel dibuang. Sengaja sederhana; ini komponen terlemah (Bab 6).

### 5.2 ILP network-flow per pasangan frame
Untuk frame berurutan dengan deteksi *i* ∈ *t*, *j* ∈ *t*+1 dan jarak Euklidean terkoreksi anisotropi *D*ᵢⱼ (µm):

* variabel biner: link *x*ᵢⱼ (bila *D*ᵢⱼ ≤ 20 µm), pembelahan *y*ᵢ,(ⱼ₁,ⱼ₂) (kedua anak dalam 25 µm dari induk dan satu sama lain), muncul *a*ⱼ, hilang *d*ᵢ;
* kendala: Σⱼ *x*ᵢⱼ + Σ *y*ᵢ,· + *d*ᵢ = 1 untuk setiap *i*;  Σᵢ *x*ᵢⱼ + Σ *y*·,(ⱼ∈pasangan) + *a*ⱼ = 1 untuk setiap *j*;
* tujuan: Σ *D*ᵢⱼ *x*ᵢⱼ + Σ (*D*ᵢⱼ₁ + *D*ᵢⱼ₂ + *c*_div + *w*_gate · pen) *y* + *c*_app Σ(*a* + *d*), dengan *c*_div = 10, *c*_app = 30, *w*_gate = 40;
* solver: `scipy.optimize.milp` (HiGHS); ≈ 0.1 s per pasangan frame di CPU.

### 5.3 Gerbang biologis sebagai biaya lunak, dikalibrasi dari data
pen = max(0, rasio − rasio_maks)/rasio_maks + max(0, massa_min − massa)/massa_min + max(0, massa − massa_maks)/massa_maks, dengan rasio = V_besar/V_kecil dan massa = (V₁ + V₂)/V_induk. Batas = persentil 5–95 (±10 %) statistik yang sama pada pembelahan GT sekuens *kalibrasi* (02). **Temuan:** pada penanda TRA CTC rasio ≡ 1.0 dan massa ≡ 2.0 — penanda adalah bola seragam, bukan segmentasi. Gerbang tetapan tangan "massa ≈ 1 ± 15 %" karena itu menolak *semua* pembelahan nyata (Bab 6, baris "gerbang asli").

### 5.4 Baseline
`greedy_nogate` / `greedy_gate`: port setia tracker nearest-neighbour terdahulu, dengan dan tanpa gerbang keras.

---

## 6. HASIL [TERUKUR]

Semua angka dari `results/ablation.json`; DET/TRA resmi via `py-ctcmetrics`; P/R/F1 mitosis dengan mencocokkan edge induk→anak prediksi ke anak GT (±2 frame). Gerbang dikalibrasi pada seq 02 → **seq 01 adalah uji independen**; baris seq 02 bersifat in-sample untuk gerbang.

### 6.1 Kualitas linking dengan deteksi GT (DET = 1)

| seq | tracker | TRA | pembelahan palsu/nyata | P mitosis | R | F1 |
|---|---|---|---|---|---|---|
| 01 | greedy, tanpa gerbang | 0.9276 | 178 / 4 | 0.006 | 0.25 | 0.011 |
| 01 | greedy + gerbang kalibrasi | 0.9587 | 86 / 4 | 0.023 | 0.50 | 0.044 |
| 01 | **ILP, tanpa gerbang** | 0.9970 | 8 / 4 | 0.125 | 0.25 | 0.167 |
| 01 | **ILP + gerbang lunak** | **0.9976** | **5 / 4** | 0.200 | 0.25 | **0.222** |
| 01 | greedy + gerbang asli ±15 % | 0.9983 | **0 / 4** | — | 0 | 0 |
| 02 | greedy (± gerbang identik) | 0.9426 | 103 / 3 | 0.019 | 0.33 | 0.037 |
| 02 | ILP (± gerbang identik) | 0.9964 | 7 / 3 | 0 | 0 | 0 |
| 02 | greedy + gerbang asli ±15 % | 0.9987 | **0 / 3** | — | 0 | 0 |

### 6.2 Ketahanan dengan deteksi label-free (Otsu + watershed)

| seq | DET | tracker | TRA | pembelahan diprediksi |
|---|---|---|---|---|
| 01 | 0.401 | greedy / greedy+gerbang / ILP / **ILP+gerbang** | 0.365 / 0.391 / 0.389 / **0.392** | 578 / 19 / 176 / 63 |
| 02 | 0.526 | greedy / greedy+gerbang / ILP / **ILP+gerbang** | 0.476 / 0.509 / 0.509 / **0.512** | 495 / 13 / 138 / 32 |

### 6.3 Bacaan hasil
1. **ILP vs greedy adalah kontribusi yang terukur:** TRA +0.05–0.07 dan pembelahan palsu 20–35 × lebih sedikit pada deteksi yang sama; urutannya bertahan pada deteksi buruk.
2. **Gerbang lunak membantu sedikit tetapi konsisten** (TRA +0.0006 s.d. +0.003; pembelahan palsu 8→5, 176→63, 138→32).
3. **TRA 0.998 gerbang keras lama adalah artefak**: nol pembelahan diusulkan, 7 pembelahan nyata terlewat semua. Kami melaporkannya untuk mendokumentasikan mode kegagalan.
4. **Mitosis belum terpecahkan di sini**: F1 terbaik 0.22; 0 pada seq 02; total hanya 7 peristiwa GT, sehingga angka ini tidak stabil secara statistik.
5. **Deteksi adalah hambatan untuk pemakaian label-free**: DET 0.40/0.53. Segmenter terlatih adalah langkah berikut yang jelas; tracker tidak dapat menutupinya.
6. Waktu proses 0.11–0.15 s/volume (CPU) pada volume kecil 5 irisan; bukan klaim real-time.

---

## 7. UJI KONSISTENSI FISIKA [DESAIN]

`src/verificators/` mengimplementasikan pemeriksaan bentuk-tertutup (geser Poiseuille, resonansi Minnaert, bilangan Womersley, panjang difusi Krogh *L* = √(2DC₀/R), indentasi Hertz, defleksi plat tipis). Ini adalah **unit test konsistensi internal** — masing-masing membandingkan rumus dengan konstanta acuan yang ditulis di sampingnya — dan berguna sebagai gerbang kewarasan pada Bab 4.3. Ini **bukan** validasi terhadap data literatur, dan kami tidak melaporkan "residual error" sebagai hasil. Geometri acuan dan konvensi ORR (Skala: FAD/(NADH+FAD)) disatukan di seluruh kode dan naskah.

---

## 8. LIMITASI (dinyatakan apa adanya)

* Fluo-N3DH-CHO adalah kultur konvensional, bukan OoC; kami tidak memiliki rekaman OoC atau akustik nyata.
* Deteksi mitosis lemah dan sampel GT sangat kecil; kesimpulan tentang pembelahan bersifat awal.
* Gerbang yang dikalibrasi pada penanda TRA tidak transfer ke segmentasi nyata; harus dikalibrasi ulang per sumber deteksi.
* Baseline deteksi label-free buruk; hasil 6.2 adalah uji ketahanan, bukan pipeline siap pakai.
* Kinematika anafase tidak dapat diukur pada 9.5 menit/frame.
* Setiap baris [Desain] di Bab 4.3 — deteksi akustik pada perangkat keras, ambang tekanan, aturan HENTIKAN — belum divalidasi. Header firmware di repo hanyalah deklarasi antarmuka; skrip HIL adalah simulasi Python yang angka latensinya tidak bermakna bagi perangkat keras.
* Gerbang hiperspektral/redoks adalah konsep; tidak ada data spektral yang dipakai.

---

## 9. PETA JALAN
1. Segmenter inti 3D terlatih (mis. Cellpose-3D / StarDist-3D) untuk mengangkat DET > 0.9 pada data label-free.
2. ILP multi-frame (gap-closing); kalibrasi gerbang pada segmentasi nyata.
3. Akuisisi time-lapse OoC nyata dengan piezo inlet + log tekanan tersinkron; validasi ambang Bab 4.3; publikasikan rekamannya.
4. Mode langsung dengan operator-in-the-loop; baru kemudian firmware.

---

## 10. REPRODUKSI
```bash
pip install -r requirements.txt
python evaluate.py --data ./data --out ./results               # ablasi penuh (≈15–30 menit CPU)
python evaluate.py --seqs 01 --detect gt --trackers ilp_gate   # cek cepat
```
Keluaran: `results/ablation.md`, `results/ablation.json`, folder hasil format CTC. Pustaka eksternal: numpy, scipy (HiGHS MILP), scikit-image, tifffile, py-ctcmetrics.

---

## 11. KEPATUHAN DATA & LISENSI
* Cell Tracking Challenge Fluo-N3DH-CHO — ketentuan penggunaan CTC; sitasi Ulman et al. 2017.
* Tidak ada data pribadi, klinis, atau terbatas. Tidak ada rekaman akustik pihak ketiga yang digunakan.
* Pustaka: numpy, scipy, scikit-image, tifffile (BSD); py-ctcmetrics (lihat lisensi paket).

---

## 12. DAFTAR PUSTAKA (DOI terverifikasi)
1. Ulman V., Maška M., et al. *An objective comparison of cell-tracking algorithms.* Nat Methods 14(12):1141–1152 (2017). doi:10.1038/nmeth.4473
2. Huh D., et al. *Reconstituting organ-level lung functions on a chip.* Science 328:1662–1668 (2010). doi:10.1126/science.1188302
3. Minnaert M. *On musical air-bubbles and the sounds of running water.* Phil. Mag. 16(104):235–248 (1933). doi:10.1080/14786443309462277
4. Skala M.C., et al. *In vivo multiphoton microscopy of NADH and FAD redox states… in precancerous epithelia.* PNAS 104(49):19494–19499 (2007). doi:10.1073/pnas.0708425104
5. Cell Tracking Challenge, laman dataset 3D: https://celltrackingchallenge.net/3d-datasets/
6. FDA Modernization Act 2.0, Public Law 117-328 (2022).
