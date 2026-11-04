"""
================================================================================
SCRIPT GENERATOR DOKUMEN LAPORAN DOCX PROFESIONAL
TUGAS KELOMPOK KECERDASAN BUATAN: CONSTRAINT SATISFACTION PROBLEMS (CSP)
STUDI KASUS: KELOMPOK 3 - PENJADWALAN MINI
================================================================================
Desain dokumen mengadopsi standar tipografi dan tata letak dokumen eksekutif
berdasarkan kaidah desain profesional (Reddit r/MicrosoftWord, r/graphic_design):
- Palet Warna Terkontrol: Deep Navy (#1A365D), Slate Blue (#2B6CB0), Charcoal (#2D3748)
- Tipografi: Keluarga Font Calibri tunggal dengan skala hierarki yang tegas
- Paragraf Mengalir Alami dengan Spacing Terkelola (tanpa Enter berulang)
- Tabel Bergaya Korporat: Header Navy, Zebra Striping, Padding Sel Nyaman
- Kotak Sorotan (Callout Box) Beraksen Garis Kiri
- Gambar In-line Berpusat dengan Keterangan Gambar (Captions) Terstandarisasi
================================================================================
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# ==============================================================================
# DEFINISI KONSTANTA WARNA DAN TEMA DESAIN
# ==============================================================================
COLOR_PRIMARY_HEX = "1A365D"       # Deep Navy (Warna Utama / Headings)
COLOR_SECONDARY_HEX = "2B6CB0"     # Slate Blue (Aksen Sekunder)
COLOR_ACCENT_HEX = "0D9488"        # Teal (Highlight / Solusi)
COLOR_BODY_HEX = "2D3748"          # Charcoal (Teks Tubuh Utama, non-harsh black)
COLOR_MUTED_HEX = "718096"         # Muted Gray (Subtitle / Captions / Borders)
COLOR_BG_LIGHT_HEX = "F7FAFC"      # Light Neutral (Zebra row / background)
COLOR_CALLOUT_BG_HEX = "EDF2F7"    # Callout background
COLOR_BORDER_HEX = "CBD5E0"        # Table Border Subtle Gray

RGB_PRIMARY = RGBColor(26, 54, 93)       # #1A365D
RGB_SECONDARY = RGBColor(43, 108, 176)   # #2B6CB0
RGB_BODY = RGBColor(45, 55, 72)          # #2D3748
RGB_MUTED = RGBColor(113, 128, 150)      # #718096
RGB_WHITE = RGBColor(255, 255, 255)


# ==============================================================================
# FUNGSI BANTUAN FORMATTING XML TINGKAT LANJUT
# ==============================================================================

def set_cell_background(cell, hex_color: str):
    """Mengatur warna latar belakang sel tabel secara rapi."""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """
    Mengatur padding internal sel tabel (dalam dxa, 20 dxa = 1 pt).
    Mencegah teks menempel pada tepi garis batas sel.
    """
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    cell._tc.get_or_add_tcPr().append(tcMar)


def set_table_borders(table, border_color=COLOR_BORDER_HEX):
    """Memberikan garis batas tipis dan elegan pada tabel (gaya profesional)."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_callout_box(doc, text: str, title: str = "CATATAN PENTING"):
    """
    Membuat kotak catatan beraksen (Callout Box) profesional:
    - Garis tepi kiri tebal berwarna Slate Blue (#2B6CB0)
    - Latar belakang abu-abu kebiruan lembut (#EDF2F7)
    - Tepi atas, kanan, dan bawah tanpa garis
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)

    # Shading dan Padding
    set_cell_background(cell, COLOR_CALLOUT_BG_HEX)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)

    # Border khusus hanya di sisi kiri
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="30" w:space="0" w:color="{COLOR_SECONDARY_HEX}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    # Isi teks
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"📌 {title}: ")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10)
    run_t.font.bold = True
    run_t.font.color.rgb = RGB_PRIMARY

    run_b = p.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGB_BODY

    # Beri spasi paragraf sesudah tabel
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)


def add_image_with_caption(doc, image_path: str, caption_text: str, width_inches: float = 6.0):
    """Menyisipkan gambar secara in-line dengan perataan tengah dan caption elegan."""
    if not os.path.exists(image_path):
        print(f"[Peringatan] Gambar tidak ditemukan: {image_path}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(image_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(12)
    run_cap = p_cap.add_run(caption_text)
    run_cap.font.name = "Calibri"
    run_cap.font.size = Pt(9)
    run_cap.font.italic = True
    run_cap.font.color.rgb = RGB_MUTED


# ==============================================================================
# PEMBUATAN DOKUMEN UTAMA
# ==============================================================================

def build_docx_report(output_filename: str = "Laporan_CSP_Kelompok_3_Penjadwalan_Mini.docx"):
    print(f"Memulai pembuatan dokumen profesional: {output_filename}...")
    doc = docx.Document()

    # 1. Konfigurasi Halaman (Margin 1 Inci Standar Eksekutif)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

        # Aktifkan footer dan header berbeda pada halaman pertama
        section.different_first_page_header_footer = True

        # Header halaman isi
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.text = "Laporan Praktikum Kecerdasan Buatan | Constraint Satisfaction Problems (CSP)"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.runs[0].font.name = "Calibri"
        p_hdr.runs[0].font.size = Pt(8.5)
        p_hdr.runs[0].font.color.rgb = RGB_MUTED

        # Footer halaman isi
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.text = "Kelompok 3 — Penjadwalan Mini | Program Studi Sains Data"
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_ftr.runs[0].font.name = "Calibri"
        p_ftr.runs[0].font.size = Pt(8.5)
        p_ftr.runs[0].font.color.rgb = RGB_MUTED

    # Inisialisasi default normal style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = RGB_BODY
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(5)

    # --------------------------------------------------------------------------
    # COVER PAGE / HALAMAN JUDUL MINIMALIS & ELEGAN
    # --------------------------------------------------------------------------
    # Metadata institusi di atas
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(20)
    p_inst.paragraph_format.space_after = Pt(30)
    run_inst = p_inst.add_run("PROGRAM STUDI SAINS DATA • FAKULTAS SAINS & TEKNOLOGI\nUIN RADEN MAS SAID SURAKARTA")
    run_inst.font.name = "Calibri"
    run_inst.font.size = Pt(9.5)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGB_MUTED

    # Judul Dokumen Utama
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    run_title = p_title.add_run("PENJADWALAN KULIAH BEBAS KONFLIK DENGAN CONSTRAINT SATISFACTION PROBLEMS (CSP)")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGB_PRIMARY

    # Subjudul Dokumen
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(30)
    run_sub = p_sub.add_run("Analisis Perbandingan Kinerja Algoritma Backtracking Dasar, Heuristik Cerdas (MRV, Degree, LCV), dan Propagasi Konsistensi AC-3 / MAC")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGB_SECONDARY

    # Kotak Informasi Kelompok (Tabel Minimalis Tanpa Border Luar)
    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.LEFT
    meta_info = [
        ("Mata Kuliah", ": Kecerdasan Buatan (Artificial Intelligence)"),
        ("Kelompok / Kasus", ": Kelompok 3 — Studi Kasus Penjadwalan Mini (6 Mata Kuliah)"),
        ("Dosen Pengampu", ": Wildan Nadiyal Ahsan, M.Kom."),
        ("Program Studi", ": Sains Data"),
        ("Tahun Akademik", ": Semester Gasal 2026/2027")
    ]
    for r_idx, (lbl, val) in enumerate(meta_info):
        c0, c1 = tbl_meta.cell(r_idx, 0), tbl_meta.cell(r_idx, 1)
        c0.width, c1.width = Inches(1.8), Inches(4.5)
        set_cell_margins(c0, 60, 60, 0, 100)
        set_cell_margins(c1, 60, 60, 0, 100)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(lbl)
        r0.font.bold = True
        r0.font.color.rgb = RGB_PRIMARY
        r0.font.size = Pt(9.5)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.color.rgb = RGB_BODY
        r1.font.size = Pt(9.5)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # RINGKASAN EKSEKUTIF (EXECUTIVE SUMMARY)
    # --------------------------------------------------------------------------
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(12)
    p_h1.paragraph_format.space_after = Pt(4)
    r = p_h1.add_run("Ringkasan Eksekutif")
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    add_callout_box(
        doc,
        "Proyek ini menyelesaikan masalah penjadwalan kuliah program studi menggunakan paradigma Constraint Satisfaction Problems (CSP). "
        "Evaluasi komparatif membuktikan bahwa penerapan Heuristik MRV + LCV berhasil memangkas jumlah node eksplorasi sebesar 74.07% "
        "(dari 27 node pada Backtracking Dasar menjadi hanya 7 node) dengan waktu komputasi 0.529 ms. "
        "Sementara itu, algoritma MAC (Maintaining Arc Consistency) memastikan konsistensi busur pada setiap langkah dan juga menemukan solusi dalam 7 node "
        "dengan kepatuhan 100% terhadap seluruh batasan fisik ruangan, ketersediaan dosen, dan jadwal kurikulum mahasiswa.",
        "TEMUAN UTAMA PENELITIAN"
    )

    # --------------------------------------------------------------------------
    # BAB 1: FORMULASI CSP FORMAL
    # --------------------------------------------------------------------------
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(14)
    p_sec1.paragraph_format.space_after = Pt(4)
    r = p_sec1.add_run("1. Formulasi CSP Formal")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    p = doc.add_paragraph(
        "Secara matematis, sistem penjadwalan kuliah dimodelkan sebagai triplet formal CSP = ⟨X, D, C⟩, di mana X adalah himpunan variabel mata kuliah, "
        "D adalah domain nilai yang dapat diambil, dan C adalah himpunan batasan yang harus dipenuhi tanpa kompromi (hard constraints)."
    )

    # 1.1 Variabel X
    p_sub1 = doc.add_paragraph()
    p_sub1.paragraph_format.space_before = Pt(8)
    p_sub1.paragraph_format.space_after = Pt(2)
    r = p_sub1.add_run("1.1 Definisi Variabel (X)")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph("Terdapat 6 variabel mata kuliah yang wajib dialokasikan ke dalam slot waktu dan ruang laboratorium:")

    # Tabel Variabel
    tbl_vars = doc.add_table(rows=7, cols=5)
    tbl_vars.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_vars)

    headers = ["Variabel", "Nama Mata Kuliah", "Dosen Pengampu", "Kelompok / Semester", "Batasan Unary Khusus"]
    col_widths = [Inches(0.9), Inches(1.8), Inches(1.2), Inches(1.3), Inches(1.3)]

    # Header Row
    for col_idx, text in enumerate(headers):
        cell = tbl_vars.cell(0, col_idx)
        cell.width = col_widths[col_idx]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGB_WHITE

    var_data = [
        ("MK1", "Kecerdasan Buatan", "Dr. Ahmad", "Semester 5", "Wajib Lab-A (GPU) & Hari Senin"),
        ("MK2", "Basis Data", "Dr. Budi", "Semester 3", "Fleksibel (Lab-A / Lab-B)"),
        ("MK3", "Machine Learning", "Dr. Ahmad", "Semester 5", "Wajib Lab-B & Hari Senin"),
        ("MK4", "Pemrograman Web", "Dr. Citra", "Semester 3", "Fleksibel (Lab-A / Lab-B)"),
        ("MK5", "Struktur Data", "Dr. Budi", "Semester 3", "Wajib Lab-A"),
        ("MK6", "Jaringan Komputer", "Dr. Citra", "Semester 5", "Wajib Lab-B")
    ]

    for row_idx, data in enumerate(var_data, start=1):
        bg = COLOR_BG_LIGHT_HEX if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tbl_vars.cell(row_idx, col_idx)
            cell.width = col_widths[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            if col_idx in [0, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            run.font.size = Pt(8.5)
            if col_idx == 0:
                run.font.bold = True
                run.font.color.rgb = RGB_PRIMARY

    # Spasi sesudah tabel
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(4)

    # 1.2 Domain D
    p_sub2 = doc.add_paragraph()
    p_sub2.paragraph_format.space_before = Pt(6)
    p_sub2.paragraph_format.space_after = Pt(2)
    r = p_sub2.add_run("1.2 Definisi Domain (D)")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Setiap variabel mengambil nilai dari pasangan terurut tuple v = (Slot_Waktu, Ruangan). "
        "Slot waktu yang tersedia terdiri atas 4 periode: Sen-08:00, Sen-10:00, Sel-08:00, dan Sel-10:00. "
        "Ruangan terdiri atas 2 unit: Lab-A dan Lab-B. Total ruang nilai gabungan adalah 4 × 2 = 8 kombinasi nilai. "
        "Setelah pemfilteran oleh unary constraints (spesifikasi laboratorium dan batasan hari dosen), ukuran domain awal adalah: "
        "D(MK1) = 2 nilai, D(MK2) = 8 nilai, D(MK3) = 2 nilai, D(MK4) = 8 nilai, D(MK5) = 4 nilai, dan D(MK6) = 4 nilai."
    )

    # 1.3 Constraints C
    p_sub3 = doc.add_paragraph()
    p_sub3.paragraph_format.space_before = Pt(6)
    p_sub3.paragraph_format.space_after = Pt(2)
    r = p_sub3.add_run("1.3 Himpunan Batasan / Constraint (C)")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Sistem menerapkan 3 batasan biner mutlak (hard constraints) yang wajib dipatuhi oleh setiap pasangan mata kuliah (MKi, MKj) dengan nilai (si, ri) dan (sj, rj):"
    )
    c_list = [
        ("Physical Room Conflict: ", "Dua mata kuliah berbeda tidak boleh berada pada ruangan yang sama di slot waktu yang sama (si = sj ⇒ ri ≠ rj)."),
        ("Lecturer Conflict: ", "Seorang dosen tidak dapat mengajar dua kelas berbeda pada waktu yang bersamaan (Dosen(MKi) = Dosen(MKj) ⇒ si ≠ sj)."),
        ("Student Cohort Conflict: ", "Mata kuliah pada kelompok angkatan/semester yang sama tidak boleh memiliki waktu kuliah bersamaan agar mahasiswa dapat mengikuti seluruh perkuliahan (Semester(MKi) = Semester(MKj) ⇒ si ≠ sj).")
    ]
    for b_title, b_desc in c_list:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(b_title)
        r1.font.bold = True
        r1.font.color.rgb = RGB_PRIMARY
        r2 = p.add_run(b_desc)
        r2.font.color.rgb = RGB_BODY

    # 1.4 Graf Constraint & Visualisasi
    p_sub4 = doc.add_paragraph()
    p_sub4.paragraph_format.space_before = Pt(8)
    p_sub4.paragraph_format.space_after = Pt(2)
    r = p_sub4.add_run("1.4 Representasi Graf Constraint")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Struktur hubungan pembatas antar variabel divisualisasikan dalam bentuk Graf Constraint. "
        "Setiap simpul (node) merepresentasikan variabel mata kuliah (berwarna biru untuk Semester 5 dan hijau untuk Semester 3). "
        "Garis penghubung (edge) memperlihatkan batasan langsung: garis merah tebal untuk konflik dosen sekaligus semester, "
        "oranye untuk konflik dosen, ungu untuk konflik semester, dan abu-abu putus-putus untuk potensi kompetisi fisik ruangan."
    )

    add_image_with_caption(
        doc,
        "visualisasi_graf_constraint.png",
        "Gambar 1: Graf Constraint Masalah Penjadwalan Kuliah Mini 6 Variabel",
        width_inches=5.8
    )

    # 1.5 Mengapa Cocok Dimodelkan Sebagai CSP
    p_sub5 = doc.add_paragraph()
    p_sub5.paragraph_format.space_before = Pt(6)
    p_sub5.paragraph_format.space_after = Pt(2)
    r = p_sub5.add_run("1.5 Mengapa Masalah Ini Cocok Dimodelkan Sebagai CSP?")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Masalah penjadwalan kuliah sangat ideal dimodelkan sebagai CSP karena:\n"
        "1. Struktur Deklaratif: Tidak seperti pencarian keadaan murni (seperti BFS/A*), CSP mengekspresikan kondisi keberhasilan secara deklaratif melalui variabel terstruktur dan relasi pembatas.\n"
        "2. Deteksi Kegagalan Dini (Early Pruning): Inkonsistensi terdeteksi langsung pada tingkat penugasan lokal tanpa harus menunggu jadwal lengkap terbentuk.\n"
        "3. Propagasi Independen: Aturan jadwal dapat disederhanakan melalui pemangkasan domain lokal secara berantai, mereduksi ruang pencarian eksponensial (8⁶ = 262.144 kemungkinan) secara drastis."
    )

    # --------------------------------------------------------------------------
    # BAB 2: IMPLEMENTASI BACKTRACKING DASAR (BASELINE)
    # --------------------------------------------------------------------------
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(14)
    p_sec2.paragraph_format.space_after = Pt(4)
    r = p_sec2.add_run("2. Implementasi Backtracking Dasar (Baseline)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    doc.add_paragraph(
        "Pendekatan pertama mengimplementasikan algoritma Backtracking Dasar (Depth-First Search) menggunakan pemilihan variabel statis "
        "(urutan: MK4 → MK2 → MK6 → MK5 → MK3 → MK1) dan urutan nilai domain sekuensial alami tanpa heuristik pemilihan cerdas. "
        "Pemeriksaan konsistensi dilakukan secara inkremental terhadap variabel yang telah di-assign sebelumnya."
    )

    doc.add_paragraph(
        "Hasil Pengujian Baseline:\n"
        "• Status Solusi: Ditemukan solusi valid (100% konsisten).\n"
        "• Jumlah Node Dieksplorasi: 27 Node.\n"
        "• Waktu Eksekusi: 0.495 ms.\n\n"
        "Analisis: Backtracking dasar mengalami 20 kali kegagalan evaluasi cabang (backtracking). "
        "Hal ini terjadi karena variabel dengan domain besar (MK4 dan MK2 dengan 8 opsi nilai) di-assign terlebih dahulu, "
        "sehingga konflik penjadwalan baru terdeteksi jauh di dalam kedalaman pohon ketika menyentuh variabel kritis (MK1 dan MK3)."
    )

    # --------------------------------------------------------------------------
    # BAB 3: PENERAPAN HEURISTIK CERDAS (MRV + DEGREE + LCV)
    # --------------------------------------------------------------------------
    p_sec3 = doc.add_paragraph()
    p_sec3.paragraph_format.space_before = Pt(14)
    p_sec3.paragraph_format.space_after = Pt(4)
    r = p_sec3.add_run("3. Penerapan Heuristik Cerdas (MRV, Degree Heuristic, LCV)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    doc.add_paragraph(
        "Untuk mengatasi kelemahan penelusuran buta, diterapkan tiga heuristik klasik CSP:\n"
        "1. Minimum Remaining Values (MRV / Fail-First): Memilih variabel dengan opsi legal tersisa paling sedikit untuk di-assign lebih awal. "
        "Variabel paling terkekang (MK1 dan MK3 dengan hanya 2 opsi) langsung diprioritaskan untuk mendeteksi kegagalan sedini mungkin.\n"
        "2. Degree Heuristic: Sebagai pemecah seri (tie-breaker) ketika ada beberapa variabel dengan ukuran domain sama, dipilih variabel yang memiliki constraint terbanyak dengan variabel yang belum ter-assign.\n"
        "3. Least Constraining Value (LCV / Succeed-First): Mengurutkan nilai domain berdasarkan dampak pemangkasan minimum terhadap opsi tetangga."
    )

    # Tabel Perbandingan BT Dasar vs Heuristik
    tbl_heur = doc.add_table(rows=3, cols=4)
    tbl_heur.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_heur)

    h_heads = ["Pendekatan Algoritma", "Node Dieksplorasi", "Efisiensi Reduksi", "Waktu Eksekusi (ms)"]
    h_widths = [Inches(2.5), Inches(1.3), Inches(1.4), Inches(1.3)]
    for c_idx, text in enumerate(h_heads):
        cell = tbl_heur.cell(0, c_idx)
        cell.width = h_widths[c_idx]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGB_WHITE

    h_rows = [
        ("1. Backtracking Dasar (Baseline)", "27 Node", "Baseline (0%)", "0.495 ms"),
        ("2. BT + Heuristik (MRV + LCV)", "7 Node", "Pangkas 74.07% Node", "0.529 ms")
    ]
    for r_idx, row in enumerate(h_rows, start=1):
        bg = COLOR_BG_LIGHT_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = tbl_heur.cell(r_idx, c_idx)
            cell.width = h_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(9)
            if c_idx == 0:
                run.font.bold = True

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # BAB 4: PROPAGASI CONSTRAINT (AC-3 DAN MAC)
    # --------------------------------------------------------------------------
    p_sec4 = doc.add_paragraph()
    p_sec4.paragraph_format.space_before = Pt(14)
    p_sec4.paragraph_format.space_after = Pt(4)
    r = p_sec4.add_run("4. Propagasi Constraint (Algoritma AC-3 dan MAC)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    doc.add_paragraph(
        "Algoritma AC-3 (Arc Consistency 3) memelihara antrean busur terarah (Xi, Xj). Fungsi REVISE memeriksa setiap nilai x ∈ D(Xi). "
        "Jika tidak ada satupun nilai y ∈ D(Xj) yang memenuhi constraint, nilai x dihapus dari D(Xi). "
        "Jika domain mengalami perubahan, seluruh busur tetangga (Xk, Xi) dimasukkan kembali ke antrean untuk memicu propagasi berantai."
    )

    p_sub_trace = doc.add_paragraph()
    p_sub_trace.paragraph_format.space_before = Pt(6)
    p_sub_trace.paragraph_format.space_after = Pt(2)
    r = p_sub_trace.add_run("4.1 Trace Perubahan Domain Langkah Demi Langkah (AC-3 Propagation)")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Sebagai demonstrasi nyata efektivitas propagasi AC-3, ketika variabel MK1 ditetapkan ke ('Sen-08:00', 'Lab-A'), "
        "algoritma AC-3 secara otomatis memangkas domain variabel tetangga dalam beberapa langkah berantai:"
    )

    # Tabel Trace AC-3
    tbl_trace = doc.add_table(rows=7, cols=5)
    tbl_trace.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_trace)

    tr_heads = ["Langkah", "Busur Direvisi", "Nilai yang Dieliminasi", "Ukuran Awal", "Ukuran Akhir"]
    tr_widths = [Inches(0.9), Inches(1.4), Inches(2.3), Inches(0.9), Inches(1.0)]
    for c_idx, text in enumerate(tr_heads):
        cell = tbl_trace.cell(0, c_idx)
        cell.width = tr_widths[c_idx]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGB_WHITE

    tr_data = [
        ("Langkah 1", "MK2 → MK1", "('Sen-08:00', 'Lab-A') [Konflik Ruang & Waktu]", "8 nilai", "7 nilai"),
        ("Langkah 2", "MK3 → MK1", "('Sen-08:00', 'Lab-B') [Konflik Dosen & Semester]", "2 nilai", "1 nilai (Terkunci!)"),
        ("Langkah 3", "MK4 → MK1", "('Sen-08:00', 'Lab-A') [Konflik Ruang & Waktu]", "8 nilai", "7 nilai"),
        ("Langkah 4", "MK5 → MK1", "('Sen-08:00', 'Lab-A') [Konflik Ruang Lab-A]", "4 nilai", "3 nilai"),
        ("Langkah 5", "MK6 → MK1", "('Sen-08:00', 'Lab-B') [Konflik Semester 5]", "4 nilai", "3 nilai"),
        ("Langkah 6", "MK6 → MK3", "('Sen-10:00', 'Lab-B') [Efek Berantai Semester 5]", "3 nilai", "2 nilai")
    ]
    for r_idx, row in enumerate(tr_data, start=1):
        bg = COLOR_BG_LIGHT_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = tbl_trace.cell(r_idx, c_idx)
            cell.width = tr_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if c_idx == 0:
                run.font.bold = True

    add_image_with_caption(
        doc,
        "visualisasi_propagasi_ac3.png",
        "Gambar 2: Diagram Batang Penyusutan Domain per Langkah Revisi Algoritma AC-3",
        width_inches=5.8
    )

    # 4.2 Maintaining Arc Consistency (MAC)
    p_sub_mac = doc.add_paragraph()
    p_sub_mac.paragraph_format.space_before = Pt(6)
    p_sub_mac.paragraph_format.space_after = Pt(2)
    r = p_sub_mac.add_run("4.2 Maintaining Arc Consistency (MAC)")
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_SECONDARY

    doc.add_paragraph(
        "Algoritma MAC menggabungkan ketangguhan Backtracking dengan eksekusi AC-3 pada setiap cabang rekursif. "
        "Setiap kali sebuah variabel di-assign, AC-3 langsung membersihkan seluruh nilai yang tidak konsisten pada variabel unassigned. "
        "Hasil pengujian menunjukkan MAC mengeksplorasi tepat 7 Node dengan waktu komputasi 1.182 ms, tanpa terjadi kegagalan eksplorasi cabang."
    )

    # --------------------------------------------------------------------------
    # BAB 5: ANALISIS KINERJA KOMPARATIF
    # --------------------------------------------------------------------------
    p_sec5 = doc.add_paragraph()
    p_sec5.paragraph_format.space_before = Pt(14)
    p_sec5.paragraph_format.space_after = Pt(4)
    r = p_sec5.add_run("5. Analisis Kinerja Komparatif")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    # Tabel Tolok Ukur 3 Pendekatan
    tbl_bench = doc.add_table(rows=4, cols=4)
    tbl_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_bench)

    b_heads = ["Pendekatan Algoritma", "Node Dieksplorasi", "Waktu Eksekusi (ms)", "Validitas Solusi"]
    b_widths = [Inches(2.5), Inches(1.3), Inches(1.3), Inches(1.4)]
    for c_idx, text in enumerate(b_heads):
        cell = tbl_bench.cell(0, c_idx)
        cell.width = b_widths[c_idx]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGB_WHITE

    b_data = [
        ("1. Backtracking Dasar (Baseline)", "27 Node", "0.495 ms", "100% Valid (Konsisten)"),
        ("2. BT + Heuristik (MRV + LCV)", "7 Node", "0.529 ms", "100% Valid (Konsisten)"),
        ("3. BT + MAC (Propagasi AC-3)", "7 Node", "1.182 ms", "100% Valid (Konsisten)")
    ]
    for r_idx, row in enumerate(b_data, start=1):
        bg = COLOR_BG_LIGHT_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = tbl_bench.cell(r_idx, c_idx)
            cell.width = b_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(9)
            if c_idx == 0:
                run.font.bold = True

    add_image_with_caption(
        doc,
        "visualisasi_perbandingan_kinerja.png",
        "Gambar 3: Perbandingan Efisiensi Pencarian Node dan Waktu Komputasi Antar Algoritma",
        width_inches=6.0
    )

    doc.add_paragraph(
        "Analisis Mendalam:\n"
        "1. Pendekatan Paling Efisien untuk Masalah Ini: Backtracking + Heuristik (MRV + LCV) adalah pemenang optimal. "
        "Pendekatan ini mencapai pemangkasan node sempurna (hanya 7 node, memangkas 74% dari baseline) dengan waktu komputasi yang sangat singkat (0.529 ms). "
        "Hal ini disebabkan overhead heuristik MRV sangat ringan (hanya menghitung panjang domain tersisa).\n\n"
        "2. Karakteristik dan Keunggulan BT + MAC: Algoritma MAC menghasilkan jumlah node yang sama (7 node) namun membutuhkan waktu 1.182 ms karena adanya overhead antrean busur (deque) pada setiap level rekursi. "
        "Meskipun pada masalah mini ini waktu eksekusi MAC sedikit lebih tinggi, pada masalah skala besar (ratusan kelas kuliah), "
        "MAC jauh lebih unggul karena mampu mencegah kombinatorial explosion yang dapat menyebabkan Backtracking biasa gagal menyelesaikan pencarian."
    )

    # --------------------------------------------------------------------------
    # BAB 6: SOLUSI JADWAL FINAL
    # --------------------------------------------------------------------------
    p_sec6 = doc.add_paragraph()
    p_sec6.paragraph_format.space_before = Pt(14)
    p_sec6.paragraph_format.space_after = Pt(4)
    r = p_sec6.add_run("6. Solusi Matriks Jadwal Kuliah Bebas Konflik")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    doc.add_paragraph(
        "Solusi optimal yang dihasilkan oleh solver CSP berhasil mengalokasikan seluruh 6 mata kuliah ke dalam 3 slot waktu, "
        "menyisakan 1 slot cadangan, dengan kepatuhan 100% terhadap seluruh batasan:"
    )

    # Tabel Jadwal Kuliah
    tbl_sched = doc.add_table(rows=5, cols=4)
    tbl_sched.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_sched)

    s_heads = ["Slot Waktu", "Laboratorium Komputasi A", "Laboratorium Komputasi B", "Keterangan Integritas"]
    s_widths = [Inches(1.5), Inches(2.0), Inches(2.0), Inches(1.0)]
    for c_idx, text in enumerate(s_heads):
        cell = tbl_sched.cell(0, c_idx)
        cell.width = s_widths[c_idx]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGB_WHITE

    s_data = [
        ("Senin 08:00 - 10:00", "MK1: Kecerdasan Buatan\n(Dr. Ahmad | Smt 5)", "MK4: Pemrograman Web\n(Dr. Citra | Smt 3)", "Bebas Konflik\n(100% Valid)"),
        ("Senin 10:00 - 12:00", "MK5: Struktur Data\n(Dr. Budi | Smt 3)", "MK3: Machine Learning\n(Dr. Ahmad | Smt 5)", "Bebas Konflik\n(100% Valid)"),
        ("Selasa 08:00 - 10:00", "MK2: Basis Data\n(Dr. Budi | Smt 3)", "MK6: Jaringan Komputer\n(Dr. Citra | Smt 5)", "Bebas Konflik\n(100% Valid)"),
        ("Selasa 10:00 - 12:00", "[ Slot Bebas / Terbuka ]", "[ Slot Bebas / Terbuka ]", "Slot Cadangan")
    ]
    for r_idx, row in enumerate(s_data, start=1):
        bg = COLOR_BG_LIGHT_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = tbl_sched.cell(r_idx, c_idx)
            cell.width = s_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if c_idx == 0:
                run.font.bold = True
                run.font.color.rgb = RGB_PRIMARY

    add_image_with_caption(
        doc,
        "visualisasi_jadwal_kuliah.png",
        "Gambar 4: Visualisasi Grid Matriks Jadwal Kuliah Hasil Penugasan CSP",
        width_inches=6.0
    )

    # --------------------------------------------------------------------------
    # BAB 7: DAFTAR PUSTAKA
    # --------------------------------------------------------------------------
    p_sec7 = doc.add_paragraph()
    p_sec7.paragraph_format.space_before = Pt(14)
    p_sec7.paragraph_format.space_after = Pt(4)
    r = p_sec7.add_run("Referensi & Daftar Pustaka")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGB_PRIMARY

    refs = [
        "Russell, S. J., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Prentice Hall. [Chapter 5: Constraint Satisfaction Problems].",
        "Dechter, R. (2003). Constraint Processing. Morgan Kaufmann Publishers.",
        "Mackworth, A. K. (1977). Consistency in networks of relations. Artificial Intelligence, 8(1), 99–118.",
        "Kumar, V. (1992). Algorithms for constraint satisfaction problems: A survey. AI Magazine, 13(1), 32–44.",
        "Ahsan, W. N. (2026). Diktat Kuliah Kecerdasan Buatan: Constraint Satisfaction Problems (CSP). Program Studi Sains Data, UIN Raden Mas Said Surakarta."
    ]
    for ref in refs:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(ref)
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGB_BODY

    # Simpan dokumen
    doc.save(output_filename)
    print(f"[Sukses] Dokumen Word (.docx) berhasil dibuat: {output_filename}")


if __name__ == "__main__":
    build_docx_report()
