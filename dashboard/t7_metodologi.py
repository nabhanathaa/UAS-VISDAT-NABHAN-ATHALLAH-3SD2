# -*- coding: utf-8 -*-
"""Tab 7 — Metodologi: sumber data (judul, tahun, URL, tanggal akses), rancangan encoding, metode, keterbatasan, deklarasi AI."""
import streamlit as st

from .core import excel_unduhan, kepala

AKSES = "2–3 Okt 2026"
BPS_PUB = "https://www.bps.go.id/id/publication"
BPS_TBL = "https://www.bps.go.id/id/statistics-table"
# (variabel, judul tabel/publikasi, tahun data, URL) — ganti URL generik dengan tautan persis halaman unduhan Anda bila perlu
SUMBER = [
    ("PDRB per kapita ADHB, PDRB ADHB, laju PDRB", "BPS — Produk Domestik Regional Bruto Kabupaten/Kota di Indonesia 2020–2024", "2024",
     "https://www.bps.go.id/id/publication/2025/06/10/ca543e942579ced46afd603b/produk-domestik-regional-bruto-kabupaten-kota-di-indonesia-2020-2024.html"),
    ("IPM (metode baru)", "BPS — [Metode Baru] Indeks Pembangunan Manusia (tabel dinamis)", "2024",
     "https://www.bps.go.id/id/statistics-table/2/NDEzIzI=/-metode-baru-indeks-pembangunan-manusia.html"),
    ("P0 (persentase penduduk miskin)", "BPS — Data dan Informasi Kemiskinan Kabupaten/Kota Tahun 2024", "2024 (Maret)",
     "https://www.bps.go.id/id/publication/2024/11/29/d2848c3990f081182125a416/data-dan-informasi-kemiskinan-kabupaten--kota-tahun-2024.html"),
    ("Indeks Kemahalan Konstruksi", "BPS — Indeks Kemahalan Konstruksi Provinsi dan Kabupaten/Kota 2024", "2024",
     "https://www.bps.go.id/id/publication/2024/10/01/a0ce996786e332d81a43d95f"),
    ("Jumlah penduduk kab/kota", "BPS — Jumlah Penduduk menurut Kabupaten/Kota dan Kelompok Umur (tabel dinamis)", "2024",
     "https://www.bps.go.id/id/statistics-table/2/Mjc5MCMy/-jumlah-penduduk-menurut-kabupaten-kota-dan-kelompok-umur.html"),
    ("Kepadatan penduduk", "BPS — Jumlah Penduduk, Laju Pertumbuhan, Distribusi, Kepadatan, Rasio Jenis Kelamin menurut Provinsi", "2024",
     "https://www.bps.go.id/id/statistics-table/3/V1ZSbFRUY3lTbFpEYTNsVWNGcDZjek53YkhsNFFUMDkjMyMwMDAw/jumlah-penduduk--laju-pertumbuhan-penduduk--distribusi-persentase-penduduk--kepadatan-penduduk--rasio-jenis-kelamin-penduduk-menurut-provinsi.html?year=2024"),
    ("PDRB 17 lapangan usaha (provinsi)", "BPS — PDRB Provinsi-Provinsi di Indonesia menurut Lapangan Usaha 2021–2025", "2024",
     "https://www.bps.go.id/id/publication/2026/04/13/71d97fa95c70c5049deecbab/produk-domestik-regional-bruto-provinsi-provinsi-di-indonesia-menurut-lapangan-usaha-2021-2025.html"),
    ("Migrasi risen antarprovinsi", "BPS — Statistik Migrasi Indonesia Hasil Long Form SP2020 (Tabel 5.3 & Tabel 7)", "2015–2020",
     "https://www.bps.go.id/id/publication/2023/07/20/97c956dd7ff3ece924911115/statistik-migrasi-indonesia-hasil-long-form-sensus-penduduk-2020.html"),
    ("Cahaya malam (radiance)", "NOAA/EOG VIIRS Nighttime Lights V2.1 (2020) & V2.2 (2024) — Google Earth Engine", "2020, 2024",
     "https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22"),
    ("Batas kab/kota (ADM2)", "geoBoundaries IDN ADM2 (sumber BPS–WFP–OCHA), CC BY 3.0 IGO", "2020", "https://www.geoboundaries.org/"),
]


def render(c):
    a, b, d = st.columns([1.3, 1, 1])
    with a, st.container(key="t_x_src"):
        kepala("Sumber data", f"Judul tabel/publikasi, tahun data, URL; diakses {AKSES}.", ("DATA BPS",))
        rows = "".join(f"<tr><td><b>{v}</b></td><td>{j}<br><a href='{u}' target='_blank'>{u.replace('https://', '')[:58]}"
                       f"{'…' if len(u) > 66 else ''}</a></td><td>{t}</td></tr>" for v, j, t, u in SUMBER)
        st.html(f"<table class='tbl'><tr><th>Variabel</th><th>Judul & URL</th><th>Tahun</th></tr>{rows}</table>")
        st.download_button(":material/download: Unduh data terolah (Excel · sheet KabKota 514 + Provinsi 38 + Keterangan)",
                           excel_unduhan(), "terang_kaya_sejahtera_data_2024.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", width="stretch")
        st.html("<div class='src'>Kode pengolahan (Jupyter Notebook) & data: lihat repositori GitHub proyek (README). "
                "Kemiskinan: hanya P0 yang dianalisis; P1, P2, garis kemiskinan disertakan di unduhan sebagai data pendukung.</div>")
    with b, st.container(key="t_x_enc"):
        kepala("Rancangan & alasan encoding", chips=("DESAIN",))
        st.html("""<div class='txt'><ul>
<li><b>Posisi</b> (scatter log-log) untuk relasi cahaya–PDRB: kanal persepsi paling akurat; kemiringan = elastisitas.</li>
<li><b>Warna sekuensial biru satu-hue</b> untuk besaran (choropleth rasio: per kapita, %, indeks); <b>divergen biru–abu–merah</b>
untuk nilai bertanda (residual, laju, LQ di sekitar 1).</li>
<li><b>Hue kategorikal</b> (4 & 7 warna) hanya untuk identitas (kuadran, klaster, pulau) — lolos uji simulasi deuteranopia,
protanopia, tritanopia.</li>
<li><b>Ukuran/luas</b> untuk besaran absolut (simbol PDRB/penduduk, tebal pita Sankey & garis aliran).</li>
<li><b>Klasifikasi</b> kuantil / Jenks / interval sama dapat dipilih; choropleth tidak memakai angka absolut.</li>
<li><b>Interaksi</b>: tooltip, zoom/pan, filter pulau, kontrol lapisan, klik wilayah (detail on demand), laso (brushing & linking),
drill-down + breadcrumb, filter asal/tujuan & ambang arus.</li>
<li><b>Tata letak</b>: satu tab satu pertanyaan; tanpa gulir; kartu putih di latar biru muda untuk hierarki visual.</li></ul></div>""")
    with d, st.container(key="t_x_met"):
        kepala("Metode, keterbatasan & deklarasi", chips=("METODE",))
        st.html("""<div class='txt'><ul>
<li><b>Zonal VIIRS</b> (GEE, 464 m): Σ radiance per poligon; ambang menyala 0,5 nW/cm²/sr; cahaya/kapita = Σ radiance ÷ penduduk.</li>
<li><b>OLS log-log</b> + galat baku HC3; residual terstandar |z| &gt; 1,5 = tidak selaras. <b>Moran's I & LISA</b> (Queen + KNN, 999 permutasi).</li>
<li><b>PCA</b> 9 variabel + <b>k-means</b> (k via silhouette); pencilan: jarak Mahalanobis &gt; χ²<sub>0,975;9</sub>.</li>
<li><b>LQ</b> = (X<sub>pk</sub>/X<sub>p</sub>)/(X<sub>k</sub>/X). <b>Gravitasi</b> migrasi: Poisson PPML.</li></ul>
<p><b>Keterbatasan:</b> cahaya hanya proksi (tambang & jasa padat modal kurang terlihat); data agregat (ecological fallacy);
VIIRS 2020 (V2.1) vs 2024 (V2.2); 47 kab/kota sering berawan; migrasi 2015–2020 (34 provinsi).</p>
<p><b>Deklarasi AI:</b> asisten AI (Claude, Anthropic) dipakai sebagai alat bantu ekstraksi tabel PDF, validasi data, penyusunan kode,
dan peninjauan rancangan; seluruh keputusan analitis diverifikasi penulis.</p>
<p style='color:#7a8799'>Nabhan Athallah · 3SD2 · 222313272 — UAS Visualisasi Data dan Informasi 2026, Politeknik Statistika STIS.</p></div>""")
