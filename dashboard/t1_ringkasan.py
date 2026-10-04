# -*- coding: utf-8 -*-
"""Tab 1 — Ringkasan: KPI, peta kuadran (cerita utama), tiga temuan, dan komposisi kuadran."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from . import peta
from .core import (CAT4, GOLD, INK, KUADRAN_C, NAVY, RED, ROYAL, SRC, angka, kepala, kpi_grid, pendek, sumber, tampil, tema)


def render(c):
    K, R, kab = c["K"], c["ring"], c["kab"]
    o = R["ols"]
    n = len(K)
    tidak = K[K.status_selaras != "Selaras"]
    tkp = (K.kuadran == "Terang – Kurang sejahtera").sum()
    lokal = ""
    if n < len(kab) and n > 10:
        b1, b0 = np.polyfit(np.log1p(K.cahaya_pk), np.log(K.pdrb_kapita_ribu), 1)
        lokal = f" · {c['label_pulau']}: {angka(b1, 2)}"
    kpi_grid([
        ("Kabupaten/kota", angka(n, 0), f"{K.provinsi.nunique()} provinsi · {len(c['pulau_sel'])} pulau", NAVY),
        ("Elastisitas cahaya → PDRB", angka(o["beta"], 2), f"Nasional, R² {angka(o['r2'], 2)}{lokal}", ROYAL),
        ("Wilayah tidak selaras", angka(len(tidak), 0), f"{angka(len(tidak) / n * 100, 0)}% · |z residual| > 1,5", RED),
        ("Terang tapi kurang sejahtera", angka(tkp, 0), f"{angka(tkp / n * 100, 0)}% wilayah terpilih", CAT4[1]),
        ("Moran's I ketidakselarasan", angka(R["moran"]["z_residual"]["I"], 2), "Nasional · p = 0,001 → mengelompok", GOLD),
    ])
    L, Rt = st.columns([1.62, 1])
    with L, st.container(key="c_r_map"):
        kepala("Tidak semua yang terang itu sejahtera",
               "Kuadran = median cahaya per kapita × indeks kesejahteraan [z(IPM) − z(P0)]/2. Arahkan kursor untuk detail; gulir untuk zoom.",
               ("GEOSPASIAL", "CHOROPLETH KATEGORI"))
        ket = ("Kuadran: " + K.kuadran + "<br>IPM " + K.ipm.map(lambda v: angka(v, 2)) + " · P0 " + K.p0.map(lambda v: angka(v, 2))
               + "%<br>Cahaya/kap " + K.cahaya_pk.map(lambda v: angka(v, 2)) + " · PDRB/kap Rp" + K.pdrb_kapita_juta.map(lambda v: angka(v, 1)) + " jt")
        st.html(peta.legenda_html(KUADRAN_C, K.kuadran.value_counts()))
        fig = peta.kategori(K, "kuadran", KUADRAN_C, ket=ket, view=None)
        tampil(tema(fig), "r_map")
        sumber(SRC)
    with Rt:
        ct = K.kuadran.value_counts().reindex(list(KUADRAN_C)).fillna(0).astype(int)
        top_k = ", ".join(pendek(x) for x in K.nlargest(3, "z_residual").nama)
        top_t = ", ".join(pendek(x) for x in K.nsmallest(3, "z_residual").nama)
        kl = K.klaster.value_counts()
        tip = []
        if kl.get("Kantong pertumbuhan pesat (SDA/IKN)", 0):
            contoh = ", ".join(pendek(x) for x in K[K.klaster.str.startswith("Kantong")].nlargest(2, "laju_pdrb_pct").nama)
            tip.append(f"{kl['Kantong pertumbuhan pesat (SDA/IKN)']} kantong pertumbuhan SDA/IKN (mis. {contoh})")
        if kl.get("Pedalaman tertinggal: gelap & mahal", 0):
            tip.append(f"{kl['Pedalaman tertinggal: gelap & mahal']} wilayah pedalaman yang gelap, mahal, dan tertinggal")
        tip_txt = (" Tipologi menemukan " + " serta ".join(tip) + ".") if tip else ""
        with st.container(key="t_r_story"):
            kepala("Cerita data: tiga temuan utama", chips=("STORYTELLING",))
            st.html(f"""<div class='txt'>
<div class='ins'><div class='no'>1</div><div><b>Cahaya mencerminkan ekonomi, tetapi hanya sebagian.</b> Setiap cahaya per kapita
naik 10%, PDRB per kapita naik ±{angka((1.1 ** o['beta'] - 1) * 100, 1)}% (β = {angka(o['beta'], 2)}); cahaya menjelaskan
{angka(o['r2'] * 100, 0)}% variasi ekonomi antarwilayah.</div></div>
<div class='ins'><div class='no'>2</div><div><b>Terang belum tentu sejahtera.</b> {ct.iloc[2]} wilayah terang tetapi kurang sejahtera
dan {ct.iloc[1]} wilayah gelap tetapi sejahtera.{tip_txt}</div></div>
<div class='ins'><div class='no'>3</div><div><b>Penyimpangan bersifat regional.</b> <span style='color:{RED};font-weight:700'>Lebih kaya
dari cahayanya</span>: {top_k}. <span style='color:{ROYAL};font-weight:700'>Lebih terang dari ekonominya</span>: {top_t}.
Moran's I = {angka(R['moran']['z_residual']['I'], 2)} → pola mengelompok, bukan acak.</div></div>
<div class='src' style='margin-top:6px'><b>Cara membaca:</b> biru = terang & sejahtera (selaras), ungu = gelap & tertinggal (selaras),
oranye/hijau = tidak selaras — sorotan kebijakan. Telusuri detail di tab Peta, Multivariat, dan Hierarki.</div></div>""")
        with st.container(key="c_r_bar"):
            kepala("Komposisi kuadran", f"Jumlah kab/kota per kuadran · {c['label_pulau']}", ("BATANG",))
            fig = go.Figure(go.Bar(x=ct.values, y=[k.replace(" – ", " ·<br>") for k in ct.index], orientation="h",
                                   marker=dict(color=[KUADRAN_C[i] for i in ct.index], cornerradius=4),
                                   text=[f"{v}  ({angka(v / n * 100, 0)}%)" for v in ct.values], textposition="outside", cliponaxis=False,
                                   textfont=dict(color=INK, size=11),
                                   hovertemplate="%{y}: %{x} kab/kota<extra></extra>"))
            tema(fig, l=4, r=70, t=2, b=2).update_layout(yaxis=dict(autorange="reversed", tickfont=dict(size=10.5, color=INK)),
                                                         xaxis=dict(visible=False), bargap=.32)
            tampil(fig, "r_bar", cfg={"displayModeBar": False, "scrollZoom": False})
            sumber("Sumber: BPS (2024), diolah")
