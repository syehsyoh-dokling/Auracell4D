# ABSTRAK

## AuraCell 4D: Pelacakan Silsilah Sel 3D+t Berbasis *Network-Flow ILP* dengan Gerbang Fisika-Biologi untuk Mikroskopi Time-Lapse Organ-on-a-Chip

**Saifuddin** — AI4S Open Innovation: AI for Life Science (The 5th Pazhou Algorithm Competition), kategori *Model & Algorithm*.
Kode & hasil: https://github.com/syehsyoh-dokling/Auracell4D · entry script `evaluate.py`

---

**Latar belakang.** Eksperimen *organ-on-a-chip* (OoC) menghasilkan ribuan citra 3D+waktu yang harus diubah menjadi silsilah sel: siapa bergerak ke mana, siapa membelah, siapa mati. Tracker standar yang mengambil keputusan per frame secara *greedy* "menghalusinasi" pembelahan setiap kali dua inti sel berdekatan — pada satu sekuens publik dengan hanya 4 pembelahan nyata, tracker greedy mengusulkan 178. Kesalahan semacam ini mengalir langsung ke kurva dosis–respons dan tidak dapat diaudit.

**Metode.** AuraCell 4D memformulasikan *linking* antar-frame sebagai *integer linear program* aliran-jaringan: setiap inti pada frame *t* wajib mengambil tepat satu nasib (tersambung, membelah, hilang) dan setiap inti pada frame *t+1* tepat satu asal (tersambung, anak, muncul). Pengetahuan biologi — rasio volume anak dan konservasi massa — tidak dipakai sebagai veto keras, melainkan sebagai **biaya lunak** yang **dikalibrasi dari distribusi data**, sehingga pembelahan yang tak masuk akal dihambat, bukan dibuang buta. Solver: `scipy.optimize.milp` (HiGHS), ≈0,1 s per pasangan frame di CPU.

**Hasil [Terukur].** Pada dataset publik *Cell Tracking Challenge* Fluo-N3DH-CHO (2 sekuens × 92 frame; metrik resmi `py-ctcmetrics`), dengan deteksi dari *ground truth* untuk mengisolasi kualitas *linking*, ILP menaikkan TRA dari **0,928 → 0,998** (seq 01) dan **0,943 → 0,996** (seq 02) dibanding baseline greedy, serta memangkas pembelahan palsu **178 → 5**. Gerbang lunak menambah perbaikan kecil yang konsisten. Hasil direproduksi identik hingga empat desimal pada Colab dan Windows lokal dengan satu perintah, tanpa login.

**Temuan & limitasi (dinyatakan terbuka).** Versi awal gerbang dengan ambang massa ±15 % tampak mencapai TRA 0,998 — ternyata karena **menolak seluruh pembelahan nyata**: mask *ground truth* CTC adalah penanda berukuran seragam, bukan segmentasi. Kami melaporkan artefak ini sebagai analisis kegagalan. Recall mitosis masih rendah (F1 terbaik 0,22, hanya 7 peristiwa GT), baseline deteksi *label-free* lemah (DET 0,40–0,53), dan Fluo-N3DH-CHO adalah kultur konvensional, bukan chip nyata.

**Desain operasional [Desain].** Mesin yang sama dirancang menerima kanal akustik **kontinu** (piezo ≥250 kS/s, pita Minnaert 80–180 kHz; gelembung 30 µm ≈ 109,6 kHz) di samping pencitraan **berkala** (5–15 menit), dengan tabel keputusan LANJUT / TANDAI / HENTIKAN yang terikat pada geometri cartridge acuan (1000 × 100 µm, 10 µL/min → τ = 1,0 dyn/cm²). Sel yang lenyap tepat setelah peristiwa aliran diberi label "kandidat artefak mekanik" dan dikeluarkan dari hitungan kematian-obat **dengan alasan tertulis**. Bagian ini terdokumentasi dan belum divalidasi pada perangkat keras.

**Kontribusi & manfaat.** (1) Tracker ILP bergerbang yang terukur unggul atas greedy pada metrik resmi; (2) disiplin pelabelan — setiap angka berlabel *[Terukur]* atau *[Desain]*; (3) analisis kegagalan yang dipublikasikan; (4) antarmuka lokal yang menjalankan evaluasi dari tombol dan mengekspor jejak audit. Penerima manfaat langsung adalah peneliti bangku yang kini cukup meninjau segelintir peristiwa ter-*flag* alih-alih seluruh film; di hilir, keterlacakan yang sama adalah yang diminta regulator dan reviewer saat data OoC menggantikan uji hewan.

**Kata kunci:** organ-on-a-chip, pelacakan sel 3D+t, integer linear programming, network flow, Cell Tracking Challenge, gerbang biofisika, reproduksibilitas, auditabilitas.
