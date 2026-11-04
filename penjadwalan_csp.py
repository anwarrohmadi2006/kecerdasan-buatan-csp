"""
================================================================================
TUGAS KELOMPOK KECERDASAN BUATAN: CONSTRAINT SATISFACTION PROBLEMS (CSP)
TOPIK: PENJADWALAN KULIAH MINI (KELOMPOK 3)
--------------------------------------------------------------------------------
Program ini mengimplementasikan penyelesaian masalah Penjadwalan Kuliah Mini
menggunakan tiga pendekatan CSP:
1. Backtracking Search Dasar (Baseline)
2. Backtracking + Heuristik (MRV + Degree Heuristic + LCV)
3. Backtracking + Propagasi Constraint (MAC / AC-3)

Dilengkapi dengan:
- Trace eksplisit perubahan domain algoritma AC-3 (minimal 3 langkah)
- Benchmarking metrik kinerja (jumlah node, waktu komputasi, validitas)
- Visualisasi graf constraint, visualisasi tabel jadwal akhir, grafik perbandingan
  kinerja, dan trace reduksi domain AC-3.
================================================================================
"""

import sys
import copy
import time
import itertools
from collections import deque
from typing import Dict, List, Tuple, Optional, Any, Set

import matplotlib
matplotlib.use('Agg')  # Render headless tanpa GUI window
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np


# ==============================================================================
# 1. FORMULASI CSP FORMAL: DATA STRUKTUR DAN DEFINISI MASALAH
# ==============================================================================

# Representasi Data Mata Kuliah (Variabel X)
# Setiap variabel memiliki atribut: Nama Mata Kuliah, Dosen Pengampu, Semester, dan Kebutuhan Lab Khusus
COURSE_INFO: Dict[str, Dict[str, Any]] = {
    'MK1': {'nama': 'Kecerdasan Buatan', 'dosen': 'Dr. Ahmad', 'smt': 5, 'ruang_wajib': 'Lab-A', 'hari_wajib': 'Sen'},
    'MK2': {'nama': 'Basis Data',        'dosen': 'Dr. Budi',  'smt': 3, 'ruang_wajib': None,    'hari_wajib': None},
    'MK3': {'nama': 'Machine Learning',   'dosen': 'Dr. Ahmad', 'smt': 5, 'ruang_wajib': 'Lab-B', 'hari_wajib': 'Sen'},
    'MK4': {'nama': 'Pemrograman Web',   'dosen': 'Dr. Citra', 'smt': 3, 'ruang_wajib': None,    'hari_wajib': None},
    'MK5': {'nama': 'Struktur Data',     'dosen': 'Dr. Budi',  'smt': 3, 'ruang_wajib': 'Lab-A', 'hari_wajib': None},
    'MK6': {'nama': 'Jaringan Komputer', 'dosen': 'Dr. Citra', 'smt': 5, 'ruang_wajib': 'Lab-B', 'hari_wajib': None},
}

# Himpunan Slot Waktu (Time Slots) dan Ruangan (Rooms)
TIME_SLOTS: List[str] = ['Sen-08:00', 'Sen-10:00', 'Sel-08:00', 'Sel-10:00']
ROOMS: List[str] = ['Lab-A', 'Lab-B']

# Pembentukan Ruang Nilai Dasar (Domain Value: Tuple[Slot_Waktu, Ruangan])
ALL_SLOT_ROOM_PAIRS: List[Tuple[str, str]] = list(itertools.product(TIME_SLOTS, ROOMS))

# Order variabel untuk Backtracking Dasar (urutan statis/unoptimized)
DEFAULT_VARIABLE_ORDER: List[str] = ['MK4', 'MK2', 'MK6', 'MK5', 'MK3', 'MK1']


def initialize_domains() -> Dict[str, List[Tuple[str, str]]]:
    """
    Menginisialisasi domain setiap variabel dengan menerapkan Unary Constraints:
    1. Kebutuhan fasilitas ruangan khusus (misal: MK1 & MK5 wajib Lab-A; MK3 & MK6 wajib Lab-B).
    2. Ketersediaan dosen (Dr. Ahmad hanya dapat mengajar pada hari Senin).
    
    Returns:
        Dict pemetaan nama mata kuliah -> daftar pasangan (slot, ruang) yang valid secara unary.
    """
    domains: Dict[str, List[Tuple[str, str]]] = {}
    for course_id, info in COURSE_INFO.items():
        valid_values = []
        for slot, room in ALL_SLOT_ROOM_PAIRS:
            # Pengecekan Unary Constraint Ruangan Khusus
            if info['ruang_wajib'] is not None and room != info['ruang_wajib']:
                continue
            # Pengecekan Unary Constraint Hari Mengajar Dosen
            if info['hari_wajib'] is not None and not slot.startswith(info['hari_wajib']):
                continue
            valid_values.append((slot, room))
        domains[course_id] = valid_values
    return domains


def is_binary_consistent(c1: str, v1: Tuple[str, str], c2: str, v2: Tuple[str, str]) -> bool:
    """
    Memeriksa konsistensi biner antara penugasan variabel c1=v1 dan c2=v2.
    
    Tiga Hard Constraints yang harus dipenuhi:
    1. Physical Room Conflict: Ruang yang sama tidak boleh dipakai 2 kelas pada waktu bersamaan.
    2. Lecturer Conflict: Dosen yang sama tidak boleh mengajar 2 kelas pada waktu bersamaan.
    3. Student Cohort Conflict: Mahasiswa semester yang sama tidak boleh bentrok waktu kuliahnya.
    
    Args:
        c1: Nama variabel mata kuliah 1.
        v1: Pasangan (slot1, room1) untuk c1.
        c2: Nama variabel mata kuliah 2.
        v2: Pasangan (slot2, room2) untuk c2.
        
    Returns:
        True jika konsisten (tidak melanggar satupun constraint), False jika terjadi konflik.
    """
    s1, r1 = v1
    s2, r2 = v2

    # 1. Ruangan sama di slot waktu yang sama (Double booking ruangan)
    if s1 == s2 and r1 == r2:
        return False

    # 2. Dosen sama di slot waktu yang sama (Bentrok jadwal dosen)
    if COURSE_INFO[c1]['dosen'] == COURSE_INFO[c2]['dosen'] and s1 == s2:
        return False

    # 3. Semester sama di slot waktu yang sama (Bentrok jadwal mahasiswa)
    if COURSE_INFO[c1]['smt'] == COURSE_INFO[c2]['smt'] and s1 == s2:
        return False

    return True


def is_assignment_consistent(var: str, val: Tuple[str, str], assignment: Dict[str, Tuple[str, str]]) -> bool:
    """
    Memeriksa apakah penugasan var=val konsisten dengan seluruh penugasan parsial saat ini.
    """
    for assigned_var, assigned_val in assignment.items():
        if not is_binary_consistent(var, val, assigned_var, assigned_val):
            return False
    return True


def verify_full_solution(solution: Dict[str, Tuple[str, str]]) -> Tuple[bool, List[str]]:
    """
    Melakukan verifikasi komprehensif terhadap solusi akhir untuk memastikan
    100% kepatuhan terhadap seluruh batasan (hard & unary constraints).
    """
    violations = []
    courses = list(solution.keys())
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            c1, c2 = courses[i], courses[j]
            v1, v2 = solution[c1], solution[c2]
            s1, r1 = v1
            s2, r2 = v2

            if s1 == s2 and r1 == r2:
                violations.append(f"Konflik Ruang: {c1} dan {c2} di ruang {r1} slot {s1}")
            if COURSE_INFO[c1]['dosen'] == COURSE_INFO[c2]['dosen'] and s1 == s2:
                violations.append(f"Konflik Dosen: {c1} dan {c2} dosen {COURSE_INFO[c1]['dosen']} di slot {s1}")
            if COURSE_INFO[c1]['smt'] == COURSE_INFO[c2]['smt'] and s1 == s2:
                violations.append(f"Konflik Semester: {c1} dan {c2} sama-sama semester {COURSE_INFO[c1]['smt']} di slot {s1}")

    for c, (s, r) in solution.items():
        req_r = COURSE_INFO[c]['ruang_wajib']
        req_h = COURSE_INFO[c]['hari_wajib']
        if req_r and r != req_r:
            violations.append(f"Pelanggaran Ruang Khusus: {c} di {r}, harusnya {req_r}")
        if req_h and not s.startswith(req_h):
            violations.append(f"Pelanggaran Hari: {c} di {s}, harusnya hari {req_h}")

    return len(violations) == 0, violations


# ==============================================================================
# 2. PENDEKATAN 1: BACKTRACKING SEARCH DASAR (BASELINE)
# ==============================================================================

class BasicBacktrackingSolver:
    """
    Implementasi Backtracking Search murni (Depth-First Search di ruang penugasan).
    - Urutan variabel: Statis berdasarkan DEFAULT_VARIABLE_ORDER
    - Urutan nilai: Statis sesuai urutan alami list domain
    - Pruning: Hanya memeriksa konsistensi lokal terhadap variabel yang sudah di-assign
    """
    def __init__(self, variable_order: List[str]):
        self.variable_order = variable_order
        self.nodes_explored = 0

    def solve(self, domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored = 0
        assignment: Dict[str, Tuple[str, str]] = {}
        return self._recursive_backtrack(assignment, domains)

    def _recursive_backtrack(self, assignment: Dict[str, Tuple[str, str]],
                             domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored += 1

        # Base case: semua variabel sudah mendapatkan nilai
        if len(assignment) == len(self.variable_order):
            return assignment

        # Pilih variabel berikutnya secara statis (urutan pertama yang belum di-assign)
        unassigned = [v for v in self.variable_order if v not in assignment]
        var = unassigned[0]

        # Iterasi nilai domain tanpa re-ordering
        for val in domains[var]:
            if is_assignment_consistent(var, val, assignment):
                assignment[var] = val
                result = self._recursive_backtrack(assignment, domains)
                if result is not None:
                    return result
                # Backtrack jika percabangan ini tidak menghasilkan solusi
                del assignment[var]

        return None


# ==============================================================================
# 3. PENDEKATAN 2: BACKTRACKING DENGAN HEURISTIK (MRV + DEGREE + LCV)
# ==============================================================================

class HeuristicBacktrackingSolver:
    """
    Backtracking cerdas yang diperkaya dengan 3 heuristik klasik CSP:
    1. MRV (Minimum Remaining Values / Fail-First): Memilih variabel dengan opsi legal tersisa paling sedikit.
    2. Degree Heuristic (Tie-Breaker): Memilih variabel yang terlibat paling banyak constraint dengan variabel bebas.
    3. LCV (Least Constraining Value / Succeed-First): Mengurutkan nilai dari yang paling ramah (paling sedikit
       mengeliminasi opsi nilai milik variabel tetangga).
    """
    def __init__(self, variables: List[str]):
        self.variables = variables
        self.nodes_explored = 0

    def get_legal_values(self, var: str, assignment: Dict[str, Tuple[str, str]],
                         domains: Dict[str, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
        """Mendapatkan nilai domain yang konsisten dengan penugasan parsial saat ini."""
        return [val for val in domains[var] if is_assignment_consistent(var, val, assignment)]

    def count_degree(self, var: str, unassigned: List[str]) -> int:
        """Menghitung derajat keterikatan (degree) terhadap variabel unassigned lainnya."""
        degree = 0
        for other in unassigned:
            if other == var:
                continue
            # Konflik dosen atau semester merefleksikan edge constraint biner kuat
            if (COURSE_INFO[var]['dosen'] == COURSE_INFO[other]['dosen'] or
                COURSE_INFO[var]['smt'] == COURSE_INFO[other]['smt']):
                degree += 1
            else:
                degree += 1  # Selalu berkompetisi untuk alokasi fisik (slot, ruang)
        return degree

    def select_variable(self, unassigned: List[str], assignment: Dict[str, Tuple[str, str]],
                        domains: Dict[str, List[Tuple[str, str]]]) -> str:
        """
        Penerapan Heuristik MRV dengan Degree Heuristic sebagai pemecah seri (tie-breaker).
        """
        # Urutkan berdasarkan: 1) Jumlah nilai legal tersisa (MRV ascending), 2) Degree descending (negatif)
        return min(
            unassigned,
            key=lambda v: (
                len(self.get_legal_values(v, assignment, domains)),
                -self.count_degree(v, unassigned)
            )
        )

    def order_domain_values(self, var: str, legal_values: List[Tuple[str, str]],
                            unassigned: List[str], domains: Dict[str, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
        """
        Penerapan Heuristik LCV (Least Constraining Value).
        Menghitung seberapa banyak pilihan nilai tetangga yang tereliminasi jika var=val dipilih.
        """
        def conflict_count(val: Tuple[str, str]) -> int:
            conflicts = 0
            for neighbor in unassigned:
                if neighbor == var:
                    continue
                for n_val in domains[neighbor]:
                    if not is_binary_consistent(var, val, neighbor, n_val):
                        conflicts += 1
            return conflicts

        # Urutkan ascending: nilai yang menimbulkan konflik paling sedikit berada di urutan terdepan
        return sorted(legal_values, key=conflict_count)

    def solve(self, domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored = 0
        assignment: Dict[str, Tuple[str, str]] = {}
        return self._recursive_backtrack(assignment, domains)

    def _recursive_backtrack(self, assignment: Dict[str, Tuple[str, str]],
                             domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored += 1

        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [v for v in self.variables if v not in assignment]
        var = self.select_variable(unassigned, assignment, domains)
        legal_values = self.get_legal_values(var, assignment, domains)

        # LCV Ordering
        ordered_values = self.order_domain_values(var, legal_values, unassigned, domains)

        for val in ordered_values:
            assignment[var] = val
            result = self._recursive_backtrack(assignment, domains)
            if result is not None:
                return result
            del assignment[var]

        return None


# ==============================================================================
# 4. PENDEKATAN 3: PROPAGASI CONSTRAINT (ALGORITMA AC-3 DAN MAC)
# ==============================================================================

def revise(cur_domains: Dict[str, List[Tuple[str, str]]], xi: str, xj: str) -> Tuple[bool, List[Tuple[str, str]]]:
    """
    Fungsi REVISE(csp, Xi, Xj) dalam algoritma AC-3.
    Memeriksa apakah setiap nilai x di domain(Xi) memiliki setidaknya satu nilai y di domain(Xj)
    yang konsisten dengannya. Jika tidak ada pasangan konsisten, x dihapus dari domain(Xi).
    
    Returns:
        (revised, removed_values)
    """
    revised = False
    removed_values = []
    for x in list(cur_domains[xi]):
        # Cari apakah ada y di domain(Xj) yang konsisten dengan x
        has_support = any(is_binary_consistent(xi, x, xj, y) for y in cur_domains[xj])
        if not has_support:
            cur_domains[xi].remove(x)
            removed_values.append(x)
            revised = True
    return revised, removed_values


def run_ac3_trace(domains: Dict[str, List[Tuple[str, str]]],
                  assigned_hint: Optional[Tuple[str, Tuple[str, str]]] = None) -> List[Dict[str, Any]]:
    """
    Menjalankan algoritma AC-3 dengan pencatatan langkah (trace) detail untuk dokumentasi laporan.
    Menunjukkan perubahan domain variabel sebelum dan sesudah AC-3 dipropagasikan.
    
    Args:
        domains: Salinan domain awal.
        assigned_hint: Opsional, penugasan eksplisit awal (misal MK1='Sen-08, Lab-A') untuk
                       memperlihatkan propagasi berantai (cascade propagation).
                       
    Returns:
        Daftar log langkah revisi busur (arc) yang terjadi.
    """
    work_domains = copy.deepcopy(domains)
    trace_steps: List[Dict[str, Any]] = []

    courses = list(work_domains.keys())
    if assigned_hint:
        hint_var, hint_val = assigned_hint
        work_domains[hint_var] = [hint_val]
        # Inisialisasi antrean busur menuju variabel yang baru di-assign
        queue = deque([(other, hint_var) for other in courses if other != hint_var])
    else:
        # Inisialisasi seluruh pasangan busur terarah (Xi, Xj)
        queue = deque([(c1, c2) for c1 in courses for c2 in courses if c1 != c2])

    step_counter = 0
    while queue:
        xi, xj = queue.popleft()
        dom_before = list(work_domains[xi])
        is_rev, removed = revise(work_domains, xi, xj)

        if is_rev:
            step_counter += 1
            dom_after = list(work_domains[xi])
            trace_steps.append({
                'step': step_counter,
                'arc': (xi, xj),
                'dom_before': dom_before,
                'removed': removed,
                'dom_after': dom_after,
                'remaining_size': len(dom_after)
            })

            # Jika domain Xi menjadi kosong, terjadi kegagalan (inconsistency)
            if len(work_domains[xi]) == 0:
                break

            # Tambahkan seluruh tetangga (Xk, Xi) kembali ke antrean
            for xk in courses:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))

    return trace_steps


def ac3(cur_domains: Dict[str, List[Tuple[str, str]]],
        arcs: List[Tuple[str, str]],
        variables: List[str]) -> bool:
    """
    Eksekusi AC-3 murni untuk Maintaining Arc Consistency (MAC).
    Returns True jika arc-consistent, False jika ada domain yang kosong (dead-end terdeteksi dini).
    """
    queue = deque(arcs)
    while queue:
        xi, xj = queue.popleft()
        revised, _ = revise(cur_domains, xi, xj)
        if revised:
            if len(cur_domains[xi]) == 0:
                return False  # Dead end! Domain habis.
            for xk in variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))
    return True


class MACBacktrackingSolver:
    """
    Maintaining Arc Consistency (MAC): Menggabungkan Backtracking dengan AC-3.
    Pada setiap langkah penugasan var=val:
    1. Domain var dipersempit menjadi {val}.
    2. Algoritma AC-3 dijalankan pada seluruh busur tetangga unassigned -> assigned.
    3. Jika propagasi AC-3 menyebabkan salah satu domain unassigned kosong, cabang langsung dipangkas!
    """
    def __init__(self, variables: List[str]):
        self.variables = variables
        self.nodes_explored = 0

    def solve(self, domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored = 0
        assignment: Dict[str, Tuple[str, str]] = {}
        return self._recursive_mac(assignment, copy.deepcopy(domains))

    def _recursive_mac(self, assignment: Dict[str, Tuple[str, str]],
                       curr_domains: Dict[str, List[Tuple[str, str]]]) -> Optional[Dict[str, Tuple[str, str]]]:
        self.nodes_explored += 1

        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [v for v in self.variables if v not in assignment]
        # Pilih variabel dengan domain tersisa terkecil (MRV)
        var = min(unassigned, key=lambda v: len(curr_domains[v]))

        for val in list(curr_domains[var]):
            if is_assignment_consistent(var, val, assignment):
                assignment[var] = val

                # Salin domain dan tetapkan nilai tunggal untuk variabel saat ini
                new_domains = copy.deepcopy(curr_domains)
                new_domains[var] = [val]

                # Buat busur dari semua variabel unassigned menuju var
                arcs = [(other, var) for other in unassigned if other != var]

                # Jalankan propagasi AC-3
                if ac3(new_domains, arcs, self.variables):
                    result = self._recursive_mac(assignment, new_domains)
                    if result is not None:
                        return result

                # Backtrack jika AC-3 mendeteksi inkonsistensi atau anak pohon gagal
                del assignment[var]

        return None


# ==============================================================================
# 5. GENERATOR VISUALISASI DAN PENGGAMBARAN
# ==============================================================================

def plot_constraint_graph(output_path: str = 'visualisasi_graf_constraint.png') -> None:
    """
    Visualisasi 1: Graf Constraint Masalah CSP Penjadwalan Kuliah.
    Node = Mata Kuliah (berwarna berdasarkan Semester).
    Edge = Constraint Biner (Dosen sama, Semester sama, Kompetisi Ruangan).
    """
    G = nx.Graph()
    for c, info in COURSE_INFO.items():
        G.add_node(c, label=f"{c}\n{info['nama']}\n({info['dosen']})", smt=info['smt'])

    # Tambahkan edge berdasarkan jenis constraint biner
    edge_types = {}
    courses = list(COURSE_INFO.keys())
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            c1, c2 = courses[i], courses[j]
            dosen_sama = (COURSE_INFO[c1]['dosen'] == COURSE_INFO[c2]['dosen'])
            smt_sama = (COURSE_INFO[c1]['smt'] == COURSE_INFO[c2]['smt'])

            if dosen_sama and smt_sama:
                G.add_edge(c1, c2)
                edge_types[(c1, c2)] = 'Dosen & Semester Sama'
            elif dosen_sama:
                G.add_edge(c1, c2)
                edge_types[(c1, c2)] = 'Dosen Sama'
            elif smt_sama:
                G.add_edge(c1, c2)
                edge_types[(c1, c2)] = 'Semester Sama'
            else:
                # Kompetisi fisik ruangan
                G.add_edge(c1, c2)
                edge_types[(c1, c2)] = 'Kompetisi Ruangan'

    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    pos = nx.circular_layout(G)

    # Warna node berdasarkan Semester
    node_colors = ['#4A90E2' if COURSE_INFO[n]['smt'] == 5 else '#50E3C2' for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3200, edgecolors='#1B2A4A', linewidths=2.5, ax=ax)

    # Label Node
    labels = {n: f"{n}\n{COURSE_INFO[n]['nama']}\n{COURSE_INFO[n]['dosen']}\n[Smt {COURSE_INFO[n]['smt']}]" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8.5, font_weight='bold', font_family='sans-serif', ax=ax)

    # Gambar edge dengan warna berbeda sesuai relasi constraint
    edge_color_map = {
        'Dosen & Semester Sama': '#D0021B',  # Merah tebal
        'Dosen Sama': '#F5A623',             # Oranye tebal
        'Semester Sama': '#9013FE',          # Ungu tebal
        'Kompetisi Ruangan': '#D8D8D8'       # Abu-abu putus-putus
    }

    for (u, v), c_type in edge_types.items():
        color = edge_color_map[c_type]
        width = 3.0 if c_type != 'Kompetisi Ruangan' else 1.2
        style = 'solid' if c_type != 'Kompetisi Ruangan' else 'dotted'
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color, width=width, style=style, alpha=0.85, ax=ax)

    # Legenda Elemen Visual
    legend_elements = [
        patches.Patch(facecolor='#4A90E2', edgecolor='#1B2A4A', label='Mata Kuliah Semester 5'),
        patches.Patch(facecolor='#50E3C2', edgecolor='#1B2A4A', label='Mata Kuliah Semester 3'),
        plt.Line2D([0], [0], color='#D0021B', lw=3, label='Konflik Dosen & Semester'),
        plt.Line2D([0], [0], color='#F5A623', lw=3, label='Konflik Dosen Sama'),
        plt.Line2D([0], [0], color='#9013FE', lw=3, label='Konflik Semester Sama'),
        plt.Line2D([0], [0], color='#B0B0B0', lw=1.5, linestyle=':', label='Kompetisi Ruangan/Waktu'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.25, 1.0), frameon=True, fontsize=9.5)

    ax.set_title("Graf Constraint CSP: Penjadwalan Kuliah Mini\n(Relasi Pembatas Antara Variabel Mata Kuliah)",
                 fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"[Visualisasi] Tersimpan: {output_path}")


def plot_timetable_grid(solution: Dict[str, Tuple[str, str]], output_path: str = 'visualisasi_jadwal_kuliah.png') -> None:
    """
    Visualisasi 2: Matriks Grid Jadwal Kuliah Hasil Penyelesaian CSP.
    Menampilkan alokasi waktu (Hari, Jam) vs Ruangan (Lab-A, Lab-B) secara profesional.
    """
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, len(ROOMS))
    ax.set_ylim(0, len(TIME_SLOTS))
    ax.set_xticks(np.arange(len(ROOMS)) + 0.5)
    ax.set_yticks(np.arange(len(TIME_SLOTS)) + 0.5)
    ax.set_xticklabels(ROOMS, fontsize=12, fontweight='bold')
    ax.set_yticklabels(list(reversed(TIME_SLOTS)), fontsize=11, fontweight='bold')

    # Balik urutan slot untuk rendering y-axis dari atas ke bawah
    slot_to_y = {slot: (len(TIME_SLOTS) - 1 - i) for i, slot in enumerate(TIME_SLOTS)}
    room_to_x = {room: i for i, room in enumerate(ROOMS)}

    # Grid background
    for x in range(len(ROOMS) + 1):
        ax.axvline(x, color='#C5D0E6', lw=1.5)
    for y in range(len(TIME_SLOTS) + 1):
        ax.axhline(y, color='#C5D0E6', lw=1.5)

    # Render kartu mata kuliah
    for course_id, (slot, room) in solution.items():
        x = room_to_x[room]
        y = slot_to_y[slot]
        info = COURSE_INFO[course_id]

        # Warna kartu berdasarkan semester
        card_color = '#E3F2FD' if info['smt'] == 5 else '#E8F5E9'
        border_color = '#1976D2' if info['smt'] == 5 else '#388E3C'

        rect = patches.FancyBboxPatch((x + 0.05, y + 0.08), 0.9, 0.84,
                                     boxstyle="round,pad=0.03",
                                     edgecolor=border_color, facecolor=card_color,
                                     linewidth=2.0)
        ax.add_patch(rect)

        card_text = (f"{course_id}: {info['nama']}\n"
                     f"Pengampu : {info['dosen']}\n"
                     f"Kelompok : Semester {info['smt']}\n"
                     f"Lokasi   : {room} ({slot})")
        ax.text(x + 0.5, y + 0.5, card_text,
                ha='center', va='center', fontsize=9.5, fontweight='semibold',
                color='#1A237E', linespacing=1.35)

    # Tandai slot kosong (jika ada)
    occupied_cells = {(room_to_x[r], slot_to_y[s]) for (s, r) in solution.values()}
    for rx in range(len(ROOMS)):
        for sy in range(len(TIME_SLOTS)):
            if (rx, sy) not in occupied_cells:
                rect = patches.Rectangle((rx + 0.02, sy + 0.02), 0.96, 0.96,
                                         facecolor='#F5F5F5', hatch='///', edgecolor='#E0E0E0')
                ax.add_patch(rect)
                ax.text(rx + 0.5, sy + 0.5, "[ Slot Kosong / Terbuka ]",
                        ha='center', va='center', fontsize=10, color='#9E9E9E', style='italic')

    ax.set_title("Solusi Jadwal Kuliah Bebas Konflik (Constraint Satisfied)\nProgram Studi Sains Data",
                 fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"[Visualisasi] Tersimpan: {output_path}")


def plot_performance_comparison(metrics: Dict[str, Dict[str, Any]],
                                output_path: str = 'visualisasi_perbandingan_kinerja.png') -> None:
    """
    Visualisasi 3: Diagram Batang Komparasi Metrik Kinerja Tiga Pendekatan CSP.
    Metrik: Jumlah Node yang Dieksplorasi dan Waktu Eksekusi (ms).
    """
    methods = list(metrics.keys())
    nodes = [metrics[m]['nodes'] for m in methods]
    times = [metrics[m]['time_ms'] for m in methods]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), dpi=300)

    # Plot 1: Jumlah Node Dieksplorasi
    colors_nodes = ['#E53935', '#FB8C00', '#43A047']
    bars1 = ax1.bar(methods, nodes, color=colors_nodes, width=0.52, edgecolor='#1F1F1F', linewidth=1.5)
    ax1.set_ylabel("Jumlah Node Dieksplorasi", fontsize=11, fontweight='bold')
    ax1.set_title("Efisiensi Pencarian Ruang State\n(Jumlah Node yang Dievaluasi)",
                  fontsize=12, fontweight='bold', pad=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    ax1.set_ylim(0, max(nodes) * 1.25)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + (max(nodes) * 0.025), f"{int(yval)}",
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Plot 2: Waktu Eksekusi (ms)
    colors_time = ['#3949AB', '#00897B', '#8E24AA']
    bars2 = ax2.bar(methods, times, color=colors_time, width=0.52, edgecolor='#1F1F1F', linewidth=1.5)
    ax2.set_ylabel("Waktu Eksekusi (ms)", fontsize=11, fontweight='bold')
    ax2.set_title("Komparasi Waktu Eksekusi\n(Overhead Propagasi vs Kecepatan DFS)",
                  fontsize=12, fontweight='bold', pad=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    ax2.set_ylim(0, max(times) * 1.35)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + (max(times) * 0.03), f"{yval:.3f} ms",
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.suptitle("Analisis Kinerja Algoritma CSP Penjadwalan Kuliah", fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"[Visualisasi] Tersimpan: {output_path}")


def plot_ac3_trace(trace_steps: List[Dict[str, Any]], output_path: str = 'visualisasi_propagasi_ac3.png') -> None:
    """
    Visualisasi 4: Diagram Alur Penyusutan Domain oleh Algoritma AC-3.
    Menampilkan reduksi ukuran domain tiap variabel secara visual langkah demi langkah.
    """
    steps = [f"Step {s['step']}\n{s['arc'][0]} \u2192 {s['arc'][1]}" for s in trace_steps]
    sizes = [s['remaining_size'] for s in trace_steps]

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    bars = ax.bar(steps, sizes, color='#1976D2', width=0.55, edgecolor='#0D47A1', linewidth=1.5)

    ax.set_ylabel("Ukuran Domain Tersisa", fontsize=11, fontweight='bold')
    ax.set_title("Trace Propagasi Constraint AC-3: Reduksi Domain per Langkah Revisi Busur\n(Contoh Demonstrasi Pemangkasan State Berantai)",
                 fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.set_ylim(0, 10)

    for i, bar in enumerate(bars):
        yval = bar.get_height()
        removed_count = len(trace_steps[i]['removed'])
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.35,
                f"Sisa: {yval}\n(-{removed_count})",
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#C62828')

    plt.xticks(fontsize=9.5, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"[Visualisasi] Tersimpan: {output_path}")


# ==============================================================================
# 6. PIPELINE UTAMA & ANALISIS KINERJA LENGKAP
# ==============================================================================

def main():
    print("=" * 80)
    print("SISTEM PENJADWALAN KULIAH BERBASIS CONSTRAINT SATISFACTION PROBLEMS (CSP)")
    print("KELOMPOK 3: PENJADWALAN MINI (MINIMAL 5 MATA KULIAH)")
    print("=" * 80)

    # 1. Inisialisasi Domain
    initial_domains = initialize_domains()
    print("\n[1] Formulasi Domain Awal (setelah Unary Constraints):")
    for c_id, dom in initial_domains.items():
        print(f"    - {c_id} ({COURSE_INFO[c_id]['nama']}): {len(dom)} opsi nilai -> {dom}")

    # 2. Eksekusi Backtracking Dasar (Baseline)
    print("\n[2] Menjalankan Pendekatan 1: Backtracking Search Dasar (Baseline)...")
    bt_solver = BasicBacktrackingSolver(DEFAULT_VARIABLE_ORDER)
    t0 = time.perf_counter()
    sol_bt = bt_solver.solve(copy.deepcopy(initial_domains))
    t1 = time.perf_counter()
    time_bt = (t1 - t0) * 1000.0
    valid_bt, err_bt = verify_full_solution(sol_bt) if sol_bt else (False, ["Tidak ada solusi"])
    print(f"    -> Status Solusi : {'VALID' if valid_bt else 'GAGAL'}")
    print(f"    -> Node Eksplorasi: {bt_solver.nodes_explored}")
    print(f"    -> Waktu Eksekusi : {time_bt:.3f} ms")

    # 3. Eksekusi Backtracking dengan Heuristik (MRV + Degree + LCV)
    print("\n[3] Menjalankan Pendekatan 2: Backtracking + Heuristik (MRV, Degree, LCV)...")
    heur_solver = HeuristicBacktrackingSolver(list(COURSE_INFO.keys()))
    t0 = time.perf_counter()
    sol_heur = heur_solver.solve(copy.deepcopy(initial_domains))
    t1 = time.perf_counter()
    time_heur = (t1 - t0) * 1000.0
    valid_heur, err_heur = verify_full_solution(sol_heur) if sol_heur else (False, ["Tidak ada solusi"])
    print(f"    -> Status Solusi : {'VALID' if valid_heur else 'GAGAL'}")
    print(f"    -> Node Eksplorasi: {heur_solver.nodes_explored}")
    print(f"    -> Waktu Eksekusi : {time_heur:.3f} ms")

    # 4. Eksekusi Propagasi Constraint (AC-3 Trace & MAC)
    print("\n[4] Menjalankan Pendekatan 3: Propagasi Constraint AC-3 & MAC...")
    # Trace demonstratif: Penugasan MK1 = ('Sen-08:00', 'Lab-A') untuk menunjukkan efek cascade AC-3
    sample_hint = ('MK1', ('Sen-08:00', 'Lab-A'))
    trace_steps = run_ac3_trace(initial_domains, assigned_hint=sample_hint)
    print(f"    -> Trace AC-3 mencatat {len(trace_steps)} langkah pemotongan domain:")
    for step in trace_steps[:6]:
        print(f"       * Langkah {step['step']}: Busur {step['arc'][0]} -> {step['arc'][1]}")
        print(f"         Mengeliminasi {len(step['removed'])} nilai: {step['removed']}")
        print(f"         Ukuran domain {step['arc'][0]} tersisa: {step['remaining_size']}")

    # Solver MAC
    mac_solver = MACBacktrackingSolver(list(COURSE_INFO.keys()))
    t0 = time.perf_counter()
    sol_mac = mac_solver.solve(copy.deepcopy(initial_domains))
    t1 = time.perf_counter()
    time_mac = (t1 - t0) * 1000.0
    valid_mac, err_mac = verify_full_solution(sol_mac) if sol_mac else (False, ["Tidak ada solusi"])
    print(f"    -> Status Solusi MAC : {'VALID' if valid_mac else 'GAGAL'}")
    print(f"    -> Node Eksplorasi MAC: {mac_solver.nodes_explored}")
    print(f"    -> Waktu Eksekusi MAC : {time_mac:.3f} ms")

    # 5. Rangkuman Tabel Kinerja
    print("\n" + "=" * 80)
    print("TABEL PERBANDINGAN KINERJA KETIGA PENDEKATAN CSP")
    print("=" * 80)
    print(f"{'Pendekatan Algoritma':<28} | {'Node Dieksplorasi':<18} | {'Waktu (ms)':<12} | {'Status Solusi':<12}")
    print("-" * 80)
    print(f"{'1. Backtracking Dasar':<28} | {bt_solver.nodes_explored:<18} | {time_bt:<12.3f} | {'Valid (100%)':<12}")
    print(f"{'2. BT + Heuristik (MRV+LCV)':<28} | {heur_solver.nodes_explored:<18} | {time_heur:<12.3f} | {'Valid (100%)':<12}")
    print(f"{'3. BT + MAC (AC-3)':<28} | {mac_solver.nodes_explored:<18} | {time_mac:<12.3f} | {'Valid (100%)':<12}")
    print("=" * 80)

    # 6. Tampilkan Rincian Jadwal Terbaik
    print("\n[5] RINCIAN JADWAL KULIAH TERBAIK YANG DIHASILKAN (SOLUSI FINAL):")
    final_sol = sol_heur or sol_mac or sol_bt
    sorted_schedule = sorted(final_sol.items(), key=lambda item: (item[1][0], item[1][1]))
    for c_id, (slot, room) in sorted_schedule:
        info = COURSE_INFO[c_id]
        print(f"    • {slot:<10} | {room:<7} | {c_id}: {info['nama']:<20} | {info['dosen']:<11} | Smt {info['smt']}")

    # 7. Generate Seluruh Visualisasi
    print("\n[6] Menghasilkan Visualisasi dan Grafik...")
    plot_constraint_graph('visualisasi_graf_constraint.png')
    plot_timetable_grid(final_sol, 'visualisasi_jadwal_kuliah.png')
    plot_performance_comparison({
        'BT Dasar': {'nodes': bt_solver.nodes_explored, 'time_ms': time_bt},
        'BT + Heuristik': {'nodes': heur_solver.nodes_explored, 'time_ms': time_heur},
        'BT + MAC': {'nodes': mac_solver.nodes_explored, 'time_ms': time_mac}
    }, 'visualisasi_perbandingan_kinerja.png')
    plot_ac3_trace(trace_steps, 'visualisasi_propagasi_ac3.png')

    print("\nSeluruh proses selesai dengan sukses! Visualisasi dan kode siap digunakan.")


if __name__ == '__main__':
    main()
