# LAPORAN TUGAS KELOMPOK KECERDASAN BUATAN
## TOPIC: CONSTRAINT SATISFACTION PROBLEMS (CSP)
**Kelompok 3 — Studi Kasus: Penjadwalan Mini (Mini Course Scheduling)**

---

### Profil Kelompok & Tugas
- **Topik Kasus:** Masalah 4 — Penjadwalan Mini
- **Deskripsi Masalah:** Penjadwalan mata kuliah universitas (minimal 5 mata kuliah) dengan batasan (*constraints*) dosen, ruang kuliah/laboratorium, dan slot waktu.
- **Implementasi Bahasa:** Python 3 (dengan library visualisasi `matplotlib` dan `networkx`).
- **File Kode Program:** [`penjadwalan_csp.py`](file:///C:/Users/user/Downloads/Kecerdasan%20Buatan%20CSP/penjadwalan_csp.py)

---

## 1. Formulasi CSP Formal

CSP didefinisikan secara matematis melalui triplet formal:
$$\text{CSP} = \langle X, D, C \rangle$$

### 1.1 Himpunan Variabel ($X$)
Variabel merepresentasikan mata kuliah yang wajib dijadwalkan ke dalam matriks waktu dan ruang:
$$X = \{MK_1, MK_2, MK_3, MK_4, MK_5, MK_6\}$$

| Variabel | Kode & Nama Mata Kuliah | Dosen Pengampu | Kelompok Mahasiswa | Fasilitas / Syarat Khusus |
| :---: | :--- | :--- | :---: | :--- |
| **$MK_1$** | Kecerdasan Buatan | Dr. Ahmad | Semester 5 | Wajib Lab-A (Komputasi GPU) & Hari Senin |
| **$MK_2$** | Basis Data | Dr. Budi | Semester 3 | Fleksibel (Lab-A / Lab-B) |
| **$MK_3$** | Machine Learning | Dr. Ahmad | Semester 5 | Wajib Lab-B & Hari Senin |
| **$MK_4$** | Pemrograman Web | Dr. Citra | Semester 3 | Fleksibel (Lab-A / Lab-B) |
| **$MK_5$** | Struktur Data | Dr. Budi | Semester 3 | Wajib Lab-A |
| **$MK_6$** | Jaringan Komputer | Dr. Citra | Semester 5 | Wajib Lab-B |

---

### 1.2 Himpunan Domain ($D$)
Setiap variabel mengambil nilai berupa pasangan tuple:
$$v = (\text{Slot\_Waktu}, \text{Ruangan})$$

- **Slot Waktu ($T$):** $\{\text{Sen-08:00}, \text{Sen-10:00}, \text{Sel-08:00}, \text{Sel-10:00}\}$
- **Ruangan ($R$):** $\{\text{Lab-A}, \text{Lab-B}\}$
- **Ruang Nilai Total ($T \times R$):** Terdapat 8 kemungkinan pasangan nilai alokasi.

Setelah penyaringan oleh batasan unary (*unary constraints* ketersediaan dosen dan spesifikasi ruangan), ukuran domain awal untuk masing-masing variabel adalah:
- $D(MK_1) = \{(\text{Sen-08:00}, \text{Lab-A}), (\text{Sen-10:00}, \text{Lab-A})\}$ *(2 nilai)*
- $D(MK_2) = T \times R$ *(8 nilai)*
- $D(MK_3) = \{(\text{Sen-08:00}, \text{Lab-B}), (\text{Sen-10:00}, \text{Lab-B})\}$ *(2 nilai)*
- $D(MK_4) = T \times R$ *(8 nilai)*
- $D(MK_5) = \{(\text{Sen-08:00}, \text{Lab-A}), (\text{Sen-10:00}, \text{Lab-A}), (\text{Sel-08:00}, \text{Lab-A}), (\text{Sel-10:00}, \text{Lab-A})\}$ *(4 nilai)*
- $D(MK_6) = \{(\text{Sen-08:00}, \text{Lab-B}), (\text{Sen-10:00}, \text{Lab-B}), (\text{Sel-08:00}, \text{Lab-B}), (\text{Sel-10:00}, \text{Lab-B})\}$ *(4 nilai)*

---

### 1.3 Himpunan Constraint ($C$)
Batasan biner (*binary constraints*) antara dua mata kuliah sembarang $MK_i$ dan $MK_j$ ($i \neq j$) dengan penugasan $(s_i, r_i)$ dan $(s_j, r_j)$:

1. **$C_{\text{ruang}}$ (Physical Room Conflict):**
   Tidak boleh ada dua kelas berbeda di ruangan yang sama pada slot waktu yang sama.
   $$s_i = s_j \implies r_i \neq r_j$$
2. **$C_{\text{dosen}}$ (Lecturer Conflict):**
   Seorang dosen tidak dapat mengajar dua kelas berbeda pada waktu bersamaan.
   $$\text{Dosen}(MK_i) = \text{Dosen}(MK_j) \implies s_i \neq s_j$$
3. **$C_{\text{kurikulum}}$ (Student Cohort Conflict):**
   Mata kuliah untuk angkatan/semester yang sama tidak boleh bersamaan agar tidak terjadi bentrok jadwal kuliah bagi mahasiswa.
   $$\text{Semester}(MK_i) = \text{Semester}(MK_j) \implies s_i \neq s_j$$

---

### 1.4 Graf Constraint (Constraint Graph)
Pada graf constraint:
- **Node:** Merepresentasikan mata kuliah $MK_1 \dots MK_6$.
- **Edge:** Merepresentasikan relasi pembatas antar mata kuliah (konflik dosen, konflik semester, dan kompetisi ruang fisik).

*(File visualisasi graf tersimpan di: [`visualisasi_graf_constraint.png`](file:///C:/Users/user/Downloads/Kecerdasan%20Buatan%20CSP/visualisasi_graf_constraint.png))*

---

### 1.5 Mengapa Masalah Ini Cocok Dimodelkan Sebagai CSP?
1. **Representasi Terstruktur:** Dibandingkan pencarian keadaan murni (*black-box search*), CSP merepresentasikan jadwal secara modular menjadi variabel diskrit dengan domain terdefinisi.
2. **Deteksi Kegagalan Dini (*Early Pruning*):** Pelanggaran jadwal langsung terdeteksi pada level penugasan lokal (*incremental check*), tanpa perlu menunggu seluruh jadwal 6 mata kuliah terisi penuh.
3. **Pemanfaatan Propagasi Konsistensi:** Batasan dosen dan ruangan dapat saling menular (*arc consistency*), secara drastis memotong ruang pencarian kombinasional dari $8^6 = 262.144$ kemungkinan menjadi beberapa langkah evaluasi saja.

---

## 2. Implementasi Backtracking Dasar (Baseline)

### 2.1 Mekanisme
Algoritma Backtracking Dasar menggunakan Depth-First Search (DFS) dengan urutan pemilihan variabel statis (`MK4`, `MK2`, `MK6`, `MK5`, `MK3`, `MK1`) dan urutan nilai domain sekuensial tanpa rekayasa heuristik.

### 2.2 Hasil Eksekusi Baseline
- **Status Solusi:** Ditemukan Solusi Valid (100% konsisten).
- **Jumlah Node yang Dieksplorasi:** **27 Node** (terjadi 20 kali evaluasi cabang buntu/backtracking karena penugasan variabel berdomain besar terlebih dahulu sebelum menyentuh variabel ketat).
- **Waktu Eksekusi:** **0.495 ms**

---

## 3. Penerapan Heuristik (MRV, Degree Heuristic, LCV)

### 3.1 Heuristik yang Diterapkan
1. **MRV (Minimum Remaining Values / Fail-First):** Memilih variabel yang memiliki sisa opsi legal paling sedikit untuk di-assign lebih awal. Variabel kritis ($MK_1$ dan $MK_3$ yang hanya memiliki 2 opsi) langsung diprioritaskan.
2. **Degree Heuristic (Tie-Breaker):** Jika ada variabel dengan ukuran domain sama, dipilih variabel yang memiliki keterikatan constraint terbanyak dengan variabel yang belum di-assign.
3. **LCV (Least Constraining Value / Succeed-First):** Nilai domain diurutkan berdasarkan nilai yang paling sedikit membatasi pilihan tetangga.

### 3.2 Hasil Perbandingan BT Dasar vs BT + Heuristik

| Algoritma / Strategi | Jumlah Node Dieksplorasi | Efisiensi Reduksi Node | Waktu Eksekusi (ms) | Status Solusi |
| :--- | :---: | :---: | :---: | :---: |
| **Backtracking Dasar (Baseline)** | 27 | Baseline (0%) | 0.495 ms | Valid |
| **BT + Heuristik (MRV + LCV)** | **7** | **74.07% Penghematan Node** | 0.529 ms | Valid |

> **Catatan Analisis:** Dengan heuristik MRV, algoritma langsung menemukan rantai solusi optimal tanpa mengalami satupun *backtrack* gagal (7 node merefleksikan 6 langkah penugasan variabel + 1 leaf validasi penutup).

---

## 4. Propagasi Constraint: Algoritma AC-3 dan MAC

### 4.1 Mekanisme AC-3 (Arc Consistency 3)
Algoritma AC-3 memelihara antrean busur terarah $(X_i, X_j)$. Untuk setiap busur, fungsi `REVISE` memeriksa apakah setiap nilai di domain $X_i$ memiliki pasangan yang valid di $X_j$. Nilai yang kehilangan dukungan (*support*) langsung dieliminasi.

### 4.2 Trace Perubahan Domain (Minimal 3 Langkah Demonstrasi)
Ketika variabel $MK_1$ di-assign ke $(\text{Sen-08:00}, \text{Lab-A})$, AC-3 memicu propagasi berantai (*cascade pruning*) sebagai berikut:

- **Langkah 1: Revisi Busur ($MK_2 \to MK_1$)**
  - Domain $MK_2$ sebelum: 8 nilai
  - Nilai Tereliminasi: `('Sen-08:00', 'Lab-A')` *(karena Lab-A slot Sen-08 telah terisi $MK_1$)*
  - Domain $MK_2$ sesudah: **7 nilai**

- **Langkah 2: Revisi Busur ($MK_3 \to MK_1$)**
  - Domain $MK_3$ sebelum: 2 nilai `[('Sen-08:00', 'Lab-B'), ('Sen-10:00', 'Lab-B')]`
  - Nilai Tereliminasi: `('Sen-08:00', 'Lab-B')` *(karena Dr. Ahmad tidak bisa mengajar bersamaan & angkatan Semester 5 tidak boleh bentrok)*
  - Domain $MK_3$ sesudah: **1 nilai tersisa: `[('Sen-10:00', 'Lab-B')]`** *(Domain $MK_3$ langsung terkunci!)*

- **Langkah 3: Revisi Busur ($MK_5 \to MK_1$)**
  - Domain $MK_5$ sebelum: 4 nilai
  - Nilai Tereliminasi: `('Sen-08:00', 'Lab-A')` *(konflik ruangan Lab-A)*
  - Domain $MK_5$ sesudah: **3 nilai**

- **Langkah 4: Revisi Efek Berantai ($MK_6 \to MK_3$)**
  - Karena pada Langkah 2 domain $MK_3$ telah terkunci menjadi `('Sen-10:00', 'Lab-B')`, maka busur ke $MK_6$ (sama-sama semester 5) langsung merevisi domain $MK_6$:
  - Nilai Tereliminasi: `('Sen-10:00', 'Lab-B')`
  - Domain $MK_6$ sesudah: **3 nilai**

*(File visualisasi reduksi domain AC-3 tersimpan di: [`visualisasi_propagasi_ac3.png`](file:///C:/Users/user/Downloads/Kecerdasan%20Buatan%20CSP/visualisasi_propagasi_ac3.png))*

### 4.3 Penggabungan AC-3 dengan Backtracking (MAC)
Pada algoritma **Maintaining Arc Consistency (MAC)**, propagasi AC-3 dijalankan secara berkala pada setiap level pohon penugasan.
- **Node Eksplorasi MAC:** **7 Node**
- **Waktu Eksekusi MAC:** **1.182 ms**

---

## 5. Analisis Kinerja Komparatif

### 5.1 Tabel Perbandingan Tiga Pendekatan

| Pendekatan Algoritma | Node Dieksplorasi | Waktu Eksekusi (ms) | Kebenaran Solusi (*Validity*) | Karakteristik Utama |
| :--- | :---: | :---: | :---: | :--- |
| **1. Backtracking Dasar** | 27 | 0.495 ms | 100% Konsisten | Sederhana, namun mudah terjebak *dead-end* jika urutan variabel suboptimal. |
| **2. BT + Heuristik (MRV+LCV)** | **7** | **0.529 ms** | 100% Konsisten | Sangat efisien, mendeteksi variabel sulit terlebih dahulu dengan *overhead* minimal. |
| **3. BT + MAC (AC-3)** | **7** | 1.182 ms | 100% Konsisten | Pemangkasan domain agresif, mendeteksi *dead-end* di muka, memiliki overhead antrean busur. |

*(File visualisasi perbandingan kinerja tersimpan di: [`visualisasi_perbandingan_kinerja.png`](file:///C:/Users/user/Downloads/Kecerdasan%20Buatan%20CSP/visualisasi_perbandingan_kinerja.png))*

---

### 5.2 Analisis dan Kesimpulan Rekayasa
1. **Pendekatan Paling Efisien untuk Masalah Ini:**
   - **Pemenang Keseluruhan:** **BT + Heuristik (MRV + LCV)**.
   - **Alasan:** Pendekatan ini memangkas jumlah node sebesar **74%** dibandingkan BT Dasar (turun dari 27 node menjadi 7 node) dengan waktu komputasi yang tetap sangat cepat (0.529 ms). Heuristik MRV secara instan memilih variabel berdomain sempit ($MK_1$ dan $MK_3$), menghilangkan potensi cabang buntu tanpa beban komputasi antrean busur berulang.
2. **Kapan BT + MAC Lebih Unggul?**
   - Pada masalah berukuran mini/menengah (seperti 6 mata kuliah ini), MAC memerlukan 1.182 ms karena adanya *overhead* rutin pemeliharaan antrean pasangan busur (`deque queue`).
   - Namun, pada masalah **skala riil universitas** (ratusan mata kuliah, puluhan ruang kuliah), **BT + MAC adalah standar emas**, karena pemangkasan domain berantai (*arc consistency*) mencegah terjadinya ledakan kombinasional eksponensial ($O(d^n)$) yang akan melumpuhkan backtracking murni.

---

## 6. Solusi Jadwal Final (Matriks Bebas Konflik)

Solusi penugasan jadwal kuliah optimal yang memenuhi seluruh batasan:

| Hari & Jam Slot | Ruangan Lab-A | Ruangan Lab-B | Keterangan Verifikasi |
| :---: | :---: | :---: | :--- |
| **Senin 08:00 - 10:00** | **$MK_1$: Kecerdasan Buatan**<br>*(Dr. Ahmad \| Smt 5)* | **$MK_4$: Pemrograman Web**<br>*(Dr. Citra \| Smt 3)* | Ruang beda, Dosen beda, Semester beda. **Valid.** |
| **Senin 10:00 - 12:00** | **$MK_5$: Struktur Data**<br>*(Dr. Budi \| Smt 3)* | **$MK_3$: Machine Learning**<br>*(Dr. Ahmad \| Smt 5)* | Ruang beda, Dosen beda, Semester beda. **Valid.** |
| **Selasa 08:00 - 10:00** | **$MK_2$: Basis Data**<br>*(Dr. Budi \| Smt 3)* | **$MK_6$: Jaringan Komputer**<br>*(Dr. Citra \| Smt 5)* | Ruang beda, Dosen beda, Semester beda. **Valid.** |
| **Selasa 10:00 - 12:00** | *[ Slot Terbuka / Kosong ]* | *[ Slot Terbuka / Kosong ]* | Cadangan kegiatan praktikum mandiri. |

*(File visualisasi visual grid jadwal tersimpan di: [`visualisasi_jadwal_kuliah.png`](file:///C:/Users/user/Downloads/Kecerdasan%20Buatan%20CSP/visualisasi_jadwal_kuliah.png))*

---
**Disusun oleh: Kelompok 3 (Penjadwalan Mini) — Program Studi Sains Data**
