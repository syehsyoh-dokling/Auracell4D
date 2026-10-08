# AuraCell 4D — Naskah Voice-Over Pengenalan Produk (Bahasa Indonesia, ≈450 kata, ≈4:00)

> Nada pengenalan produk profesional. Tanpa penanda menit, tanpa instruksi "lihat layar", tanpa gaya laporan penelitian dalam narasi. Limitasi ada di Technical Report §8 dan Audit Log, dibahas saat tanya-jawab.
> Dua jangkar fakta tetap ada dalam bahasa alami: urutan pemantauan adalah *skenario demonstrasi*, dan angka benchmark diperoleh *dengan deteksi acuan*.

---

## Narasi

**Dari cawan ke chip.** Selama puluhan tahun, obat diuji pada cawan dua dimensi dan hewan percobaan — dan sembilan dari sepuluh kandidat yang lolos di sana tetap gagal pada manusia. Organ-on-a-chip mengubahnya: sel manusia hidup dalam kanal mikro yang dialiri seperti pembuluh darah, dan kini diterima regulator sebagai pengganti uji hewan. Tetapi chip membawa tantangan baru. Ia menghasilkan ribuan frame tiga dimensi yang harus ditafsirkan — sel mana yang bergerak, membelah, dan mati. Tracker konvensional memutuskan frame demi frame; begitu dua inti bersentuhan, ia mengarang pembelahan: pada satu benchmark publik dengan empat pembelahan nyata, tracker standar mengusulkan seratus tujuh puluh delapan. AuraCell 4D dibangun agar silsilah itu dapat dipercaya — dan dapat diaudit.

**Di mana ia bekerja.** Laboratorium membuat cartridge dan menanam sel. AuraCell 4D mengambil alih saat docking: geometri dan laju aliran dicatat, baseline fisikanya dihitung. Sejak perfusi dimulai, kanal akustik mendengar terus-menerus, sementara mikroskop memotret dengan ritme berkalanya. Lalu algoritma berjalan — deteksi, penautan global, gerbang biologi. Setiap peristiwa mendapat sertifikat: lanjut, tandai, atau hentikan. Peneliti tetap memegang kendali, dan siklus berulang pada dosis berikutnya.

**Algoritmanya.** Untuk setiap pasangan frame, AuraCell 4D menyelesaikan satu program linear integer: setiap inti mengambil tepat satu nasib — tersambung, membelah, atau hilang — dan setiap inti di frame berikutnya punya tepat satu asal. Biologi masuk sebagai biaya, bukan larangan: pembelahan dengan volume anak yang janggal menjadi mahal, sehingga pengoptimal menghindarinya kecuali buktinya kuat. Biaya itu dikalibrasi dari data.

**Obat atau gelembung?** Dalam skenario demonstrasi ini, kanal akustik menangkap letupan pada frekuensi resonansi gelembung tiga puluh mikrometer. Sistem mencatat momennya dan meminta snapshot tambahan. Dua sel lenyap pada frame berikutnya. Tracker biasa akan menghitung dua kematian karena obat. AuraCell 4D mengenalinya sebagai kandidat artefak mekanik dan mengeluarkannya dari hitungan — dengan alasan tertulis. Harmonik pompa di luar pita gelembung dicatat dan diabaikan: sistem bereaksi pada bukti, bukan derau. Kemudian satu sel berakhir tanpa peristiwa mekanik di sekitarnya — kematian terkait obat yang sesungguhnya, dan itu dihitung. Hasilnya adalah angka yang bisa dipertanggungjawabkan, dengan setiap pengecualian dijelaskan di jejak audit. Saat tekanan naik, sistem menandainya lebih awal dan merekomendasikan berhenti; operator yang memutuskan. Manusia memegang kendali, bukti datang dari alat.

**Terbukti pada data publik.** Diukur dengan metrik resmi Cell Tracking Challenge, dengan deteksi acuan, AuraCell 4D menaikkan skor pelacakan dari nol koma sembilan tiga menjadi nol koma sembilan sembilan delapan, dan memangkas pembelahan palsu dari seratus tujuh puluh delapan menjadi lima. Seluruh evaluasi tereproduksi identik di Colab dan di laptop dengan satu perintah — dan antarmukanya menjalankan evaluasi itu dari satu tombol, lalu mengekspor jejak audit.

**Siapa yang diuntungkan.** Peneliti bangku cukup meninjau segelintir peristiwa bertanda, bukan seluruh film. Regulator menerima persis keterlacakan yang mereka minta saat data organ-on-a-chip menggantikan uji hewan. Dan setiap angka dalam dokumentasi kami berlabel — terukur atau desain. Berikutnya: segmenter tiga dimensi terlatih, rekaman chip nyata dengan kanal akustik tersinkron, lalu perangkat keras.

AuraCell 4D: silsilah yang dapat dipercaya, setiap angka berlabel, setiap keputusan dapat dijelaskan.

---

## Peta layar untuk editor (tidak diucapkan)

| Blok narasi | Visual | Sumber |
|---|---|---|
| Dari cawan ke chip | transisi cawan → chip; Fig. 5 | `docs/figures/fig5_frame_overlay.png` |
| Di mana ia bekerja | stepper workflow auto-advance | `gui/demo/index.html?page=1` |
| Algoritmanya | tahap 6 + diagram ILP | `?page=1&step=6` |
| Obat atau gelembung? | monitor langsung dari burst hingga penghitung naif-vs-AuraCell; sekilas flag tekanan | `?page=2&t=10&play=1`, `?page=2&t=96&play=1`, `?page=2&t=55` |
| Terbukti pada data publik | batang TRA animasi, counter 178 → 5; GUI Step 4 | `?page=3`, `docs/figures/gui_step4.png` |
| Siapa yang diuntungkan | slide penutup | `?page=4` |
