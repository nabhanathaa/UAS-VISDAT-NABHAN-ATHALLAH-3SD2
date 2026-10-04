# -*- coding: utf-8 -*-
"""
Terang, Kaya, Sejahtera? — Dashboard UAS Visualisasi Data dan Informasi 2026
Nabhan Athallah (3SD2 / 222313272) · Politeknik Statistika STIS

Jalankan:  streamlit run app.py
Struktur:  dashboard/core.py (palet, utilitas, data) · dashboard/style.py (CSS) · dashboard/t*_*.py (satu berkas per tab)

Prinsip rancangan
- Satu tab = satu fungsi; tiap tab memenuhi tepat satu layar (tinggi kartu mengikuti tinggi jendela, tanpa gulir halaman).
- Ringan: batas wilayah (GeoJSON tersederhanakan) disajikan statis dari static/ dan di-cache peramban;
  figur peta hanya mengirim kode wilayah + nilai (±20 KB per peta, bukan ±7 MB).
- Palet ramah buta warna (diuji simulasi CVD); angka berformat Indonesia (1.234,5); "Sumber: BPS" di setiap grafik.
"""
import streamlit as st

from dashboard.core import PULAU, ROOT, logo_b64, muat

st.set_page_config(page_title="Terang, Kaya, Sejahtera? · UAS Visdat 2026 · Nabhan Athallah",
                   page_icon=str(ROOT / "assets" / "logo_stis_128.png"), layout="wide", initial_sidebar_state="collapsed")

from dashboard import style, t1_ringkasan, t2_peta, t3_regresi, t4_multivariat, t5_hierarki, t6_aliran, t7_metodologi  # noqa: E402

style.pasang_css()
kab, prov, sek, od, neto, mat, RING, ZALL = muat()

HAL = {
    "Ringkasan": (":material/space_dashboard:", t1_ringkasan),
    "Peta Tematik": (":material/map:", t2_peta),
    "Cahaya vs Ekonomi": (":material/scatter_plot:", t3_regresi),
    "Multivariat": (":material/hub:", t4_multivariat),
    "Hierarki Ekonomi": (":material/account_tree:", t5_hierarki),
    "Aliran Migrasi": (":material/swap_calls:", t6_aliran),
    "Metodologi": (":material/menu_book:", t7_metodologi),
}

# ------------------------------------------------------------------ header: identitas + navigasi + filter global
with st.container(key="hdr"):
    a, b = st.columns([3.2, 1], vertical_alignment="center")
    a.html(f"""<div class='brand'><img src='data:image/png;base64,{logo_b64()}' alt='Logo Politeknik Statistika STIS'>
      <div><div class='eyebrow'>UAS Visualisasi Data dan Informasi 2026</div>
      <div class='ttl'>Terang, Kaya, Sejahtera<span>?</span></div>
      <div class='sub'>Cahaya malam satelit × ekonomi × kesejahteraan · 514 kabupaten/kota Indonesia · 2024</div></div></div>""")
    b.html("""<div class='ident'><div class='nm'>Nabhan Athallah</div><div class='nim'>3SD2 · NIM 222313272</div>
      <div class='kp'>Politeknik Statistika STIS</div></div>""")
    n1, n2 = st.columns([3.6, 1], vertical_alignment="center")
    with n1:
        hal = st.segmented_control("Navigasi", list(HAL), default="Ringkasan", key="hal", label_visibility="collapsed",
                                   format_func=lambda h: f"{HAL[h][0]} {h}") or "Ringkasan"
    with n2:
        p = st.selectbox("Filter pulau", ["Semua pulau"] + PULAU, key="pulau", label_visibility="collapsed",
                         help="Filter global — berlaku di Ringkasan, Peta, Cahaya vs Ekonomi, Multivariat, dan Hierarki.")

pulau_sel = PULAU if p == "Semua pulau" else [p]
ctx = dict(kab=kab, K=kab[kab.pulau.isin(pulau_sel)].copy(), prov=prov, sek=sek, od=od, neto=neto, mat=mat, ring=RING,
           Z=ZALL, pulau_sel=pulau_sel, label_pulau=p)
HAL[hal][1].render(ctx)
