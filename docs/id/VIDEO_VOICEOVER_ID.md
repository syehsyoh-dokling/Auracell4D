# AuraCell 4D — Naskah Voice-Over Video Demo (Bahasa Indonesia, ≈4 menit, ≈560 kata)

> Setiap angka yang diucapkan berlabel **[Terukur]** (dari `results/ablation.json`) atau disebut eksplisit sebagai **desain/simulasi**. Jangan improvisasi angka.
> Layar: halaman demo `gui/demo/index.html` (1600×900). Cue layar dalam *miring*; parameter URL untuk melompat ke momen.

---

**[0:00–0:30] MASALAH NYATA**
*Layar: `?page=1&step=5` → `?page=1&step=6` (stepper), lalu Fig. 5 (frame nyata, garpu pembelahan palsu).*

Eksperimen organ-on-a-chip menghasilkan ribuan frame tiga dimensi berisi sel hidup. Untuk tahu apakah obat bekerja, peneliti harus merekonstruksi silsilah setiap sel: siapa bergerak, siapa membelah, siapa mati. Hari ini pekerjaan itu dilakukan tracker yang memutuskan frame demi frame. Begitu dua inti sel bersentuhan, ia mengarang pembelahan. Pada satu sekuens publik dengan hanya empat pembelahan nyata, tracker greedy mengusulkan seratus tujuh puluh delapan. Dan tidak ada tracker yang bisa membedakan sel yang mati karena obat dari sel yang terlepas oleh gelembung. Kesalahan itu masuk langsung ke angka dosis–respons.

**[0:30–1:05] DI MANA ALAT INI BEKERJA**
*Layar: `?page=1` auto-advance dari tahap 1 ke 8.*

Inilah alur lengkapnya. Fabrikasi cartridge dan penanaman sel adalah urusan laboratorium — bukan kami. Peran AuraCell 4D dimulai saat cartridge di-dock: geometri dan laju aliran dicatat, dan baseline fisikanya dihitung — tegangan geser satu koma nol dyn per sentimeter persegi untuk kanal seribu kali seratus mikrometer. Sejak perfusi dimulai, kanal akustik mendengar terus-menerus, sementara mikroskop tetap memotret berkala tiap sembilan setengah menit. Lalu algoritma kami bekerja: deteksi, penautan global, gerbang biologi. Setiap peristiwa mendapat sertifikat — lanjut, tandai, atau hentikan — dan peneliti yang memutuskan, sebelum siklus kembali ke dosis berikutnya.

**[1:05–1:35] ALGORITMANYA**
*Layar: `?page=1&step=6`, lalu diagram link / divide / appear / disappear.*

Untuk setiap pasangan frame kami menyelesaikan satu program linear integer: setiap inti harus mengambil tepat satu nasib — tersambung, membelah, atau hilang — dan setiap inti di frame berikutnya tepat satu asal. Biologi tidak masuk sebagai larangan, tetapi sebagai biaya: pembelahan dengan volume anak yang janggal menjadi mahal, bukan dilarang. Dan biaya itu dikalibrasi dari data, bukan diketik tangan.

**[1:35–2:35] INSIDEN UTAMA — OBAT ATAU GELEMBUNG?**
*Layar: `?page=2&t=10&play=1`, biarkan berjalan 2× sampai menit ±28.*

Sekarang monitor langsung — ini simulasi berskenario, bukan rekaman perangkat keras. Menit dua belas: kanal akustik menangkap letupan di seratus sembilan koma enam kilohertz. Itu frekuensi Minnaert gelembung tiga puluh mikrometer. Sistem menandai waktu T dan meminta satu snapshot tambahan. Frame berikutnya: track tiga dan sepuluh lenyap. Tracker biasa akan menghitung dua kematian karena obat. AuraCell 4D menandainya sebagai kandidat artefak mekanik dan mengeluarkannya dari hitungan — dengan alasannya tertulis. Lihat penghitungnya: naif dua, AuraCell nol.
*Layar: menit 24.*
Menit dua puluh empat: transien lain, enam puluh dua kilohertz. Di luar pita gelembung — harmonik pompa. Dicatat, diabaikan, tidak ada yang dikeluarkan. Alat ini tidak panik pada setiap suara.
*Layar: potong ke `?page=2&t=96&play=1`, berhenti di menit ±102.*
Menit sembilan puluh delapan: track tujuh berakhir, tanpa peristiwa mekanik di sekitarnya. Yang ini dihitung sebagai kematian terkait obat. Hitungan naif sekarang tiga; hitungan kami satu — dan dua pengecualian membawa alasannya sendiri di jejak audit.

**[2:35–2:50] KESELAMATAN — SEBAGAI REKOMENDASI**
*Layar: `?page=2&t=55`, 3–4 detik.*

Di antara keduanya, tekanan naik dua koma enam kali baseline. Sistem merekomendasikan berhenti; operator yang menurunkan aliran. Perangkat lunak ini tidak mengendalikan pompa — itu bagian desain, belum divalidasi.

**[2:50–3:30] HASIL — APA ADANYA**
*Layar: `?page=3`, batang animasi; lalu kotak limitasi.*

Yang benar-benar kami ukur, dengan metrik resmi Cell Tracking Challenge: pada data publik dengan deteksi ground truth, ILP menaikkan skor TRA dari nol koma sembilan dua delapan menjadi nol koma sembilan sembilan delapan pada sekuens satu, dan dari nol koma sembilan empat tiga menjadi nol koma sembilan sembilan enam pada sekuens dua. Pembelahan palsu turun dari seratus tujuh puluh delapan menjadi lima. Hasil ini direproduksi identik di Colab dan di laptop lokal dengan satu perintah. Dan kami juga melaporkan yang belum berhasil: recall mitosis masih rendah, detektor label-free kami hanya mencapai DET nol koma empat sampai nol koma lima, dan datanya kultur konvensional, bukan chip sungguhan. Satu lagi: gerbang versi awal kami mencetak TRA nol koma sembilan sembilan delapan — dengan menolak setiap pembelahan nyata. Barisnya kami pertahankan di tabel.

**[3:30–3:55] PENERIMA MANFAAT & PENUTUP**
*Layar: `?page=4`.*

Penerima manfaat pertama adalah peneliti bangku yang kini cukup meninjau segelintir peristiwa bertanda, bukan seluruh film. Di hilir, jejak audit yang sama adalah yang diminta regulator ketika data organ-on-a-chip menggantikan uji hewan. Langkah berikutnya: segmenter tiga dimensi terlatih, rekaman chip nyata dengan kanal akustik tersinkron, baru kemudian perangkat keras. AuraCell 4D: lebih sedikit pembelahan halusinasi, setiap angka berlabel, setiap keputusan bisa dijelaskan.

---

## Daftar shot

| Waktu | Layar | URL / sumber |
|---|---|---|
| 0:00 | Stepper tahap 5–6 + Fig. 5 | `?page=1&step=6`; `docs/figures/fig5_frame_overlay.png` |
| 0:30 | Workflow auto-advance | `?page=1` (tekan `a` bila ingin manual) |
| 1:05 | Tahap 6 + diagram ILP | `?page=1&step=6`; slide dari writeup §4.2 |
| 1:35 | Insiden utama bagian 1 | `?page=2&t=10&play=1` (2×, ≈9 s nyata) |
| 2:10 | Insiden utama bagian 2 | `?page=2&t=96&play=1` (≈3 s nyata), zoom KPI "naive vs AuraCell" |
| 2:35 | STOP penyumbatan | `?page=2&t=55` (statis, 3–4 s) |
| 2:50 | Hasil terukur | `?page=3` |
| 3:30 | Penutup | `?page=4` |
