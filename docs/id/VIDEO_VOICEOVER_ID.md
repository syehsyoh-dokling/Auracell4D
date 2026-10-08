# AuraCell 4D — Naskah Voice-Over (Bahasa Indonesia, ≈450 kata, target ≈4:00)

> Versi positif, berfokus pada nilai produk. Limitasi lengkap ada di Technical Report §8 dan Audit Log, dibahas saat tanya-jawab.
> Dua jangkar fakta dipertahankan: monitor langsung adalah *skenario terprogram*, dan angka TRA diukur *dengan deteksi acuan*.
> Cue layar dalam *miring*; parameter URL untuk halaman demo `gui/demo/index.html`.

---

**[0:00–0:25] PELUANG**
*Layar: `?page=1&step=6`, lalu Fig. 5.*

Eksperimen organ-on-a-chip menghasilkan ribuan frame tiga dimensi sel hidup. Untuk tahu obat bekerja atau tidak, silsilah setiap sel harus direkonstruksi: siapa bergerak, membelah, dan mati. Tracker konvensional memutuskan frame demi frame — begitu dua inti bersentuhan, ia mengarang pembelahan: pada satu sekuens publik dengan empat pembelahan nyata, tracker greedy mengusulkan seratus tujuh puluh delapan. AuraCell 4D dibangun agar silsilah itu dapat dipercaya — dan dapat diaudit.

**[0:25–0:55] DI MANA ALAT INI BEKERJA**
*Layar: `?page=1`, auto-advance tahap 1→8.*

Inilah alurnya. Laboratorium membuat cartridge dan menanam sel. AuraCell 4D mengambil alih saat docking: geometri dan laju aliran dicatat, baseline fisika dihitung — tegangan geser satu koma nol dyn per sentimeter persegi untuk kanal seribu kali seratus mikrometer. Sejak perfusi dimulai, kanal akustik mendengar terus-menerus, sementara mikroskop memotret berkala tiap sembilan setengah menit. Lalu algoritma berjalan: deteksi, penautan global, gerbang biologi. Setiap peristiwa mendapat sertifikat — lanjut, tandai, atau hentikan — peneliti tetap memegang kendali, dan siklus berulang di dosis berikutnya.

**[0:55–1:15] ALGORITMA**
*Layar: `?page=1&step=6`, diagram ILP.*

Untuk setiap pasangan frame kami menyelesaikan satu program linear integer: setiap inti mengambil tepat satu nasib — tersambung, membelah, atau hilang — dan setiap inti di frame berikutnya punya tepat satu asal. Biologi masuk sebagai biaya, bukan larangan: pembelahan dengan volume anak yang janggal menjadi mahal, dan biaya itu dikalibrasi dari data.

**[1:15–2:10] INSIDEN UTAMA — OBAT ATAU GELEMBUNG?**
*Layar: `?page=2&t=10&play=1`, 2×, sampai menit ≈28.*

Sekarang monitor langsung, menjalankan skenario terprogram. Menit dua belas: kanal akustik menangkap letupan seratus sembilan koma enam kilohertz — frekuensi Minnaert gelembung tiga puluh mikrometer. Sistem mencatat waktu T dan meminta satu snapshot tambahan. Frame berikutnya: track tiga dan sepuluh lenyap. AuraCell 4D mengenalinya sebagai kandidat artefak mekanik dan mengeluarkannya dari hitungan kematian obat — dengan alasan tertulis. Lihat penghitungnya: naif dua, AuraCell nol.
*Layar: menit 24.* Menit dua puluh empat: transien enam puluh dua kilohertz — di luar pita gelembung, harmonik pompa. Dicatat, diabaikan. Sistem bereaksi pada bukti, bukan pada derau.
*Layar: `?page=2&t=96&play=1`.* Menit sembilan puluh delapan: track tujuh berakhir tanpa peristiwa mekanik — kematian terkait obat yang sesungguhnya, dan itu dihitung. Naif tiga, AuraCell satu — dengan kedua pengecualian dijelaskan di jejak audit. Itulah angka yang bisa dipertanggungjawabkan.

**[2:10–2:22] KESELAMATAN — OPERATOR MEMEGANG KENDALI**
*Layar: `?page=2&t=55`.*

Di antaranya, tekanan naik dua koma enam kali baseline. Sistem menandai lebih awal dan merekomendasikan berhenti; operator menurunkan aliran. Keputusan tetap di tangan manusia, buktinya dari alat.

**[2:22–3:05] HASIL**
*Layar: `?page=3`.*

Diukur dengan metrik resmi Cell Tracking Challenge pada data publik, dengan deteksi acuan: ILP menaikkan skor TRA dari nol koma sembilan dua delapan menjadi nol koma sembilan sembilan delapan pada sekuens satu, dan dari nol koma sembilan empat tiga menjadi nol koma sembilan sembilan enam pada sekuens dua. Pembelahan palsu turun dari seratus tujuh puluh delapan menjadi lima. Seluruh evaluasi tereproduksi identik di Colab dan laptop lokal dengan satu perintah — dan GUI menjalankannya dari satu tombol, lalu mengekspor jejak audit.

**[3:05–3:50] PENERIMA MANFAAT & PENUTUP**
*Layar: `?page=4`.*

Penerima manfaat pertama adalah peneliti bangku, yang kini cukup meninjau segelintir peristiwa bertanda, bukan seluruh film. Di hilir, jejak audit yang sama persis yang diminta regulator saat data organ-on-a-chip menggantikan uji hewan. Setiap angka dalam laporan kami berlabel — terukur atau desain. Berikutnya: segmenter tiga dimensi terlatih, rekaman chip nyata dengan kanal akustik tersinkron, lalu perangkat keras. AuraCell 4D: silsilah yang dapat dipercaya, setiap angka berlabel, setiap keputusan dapat dijelaskan.
