# -*- coding: utf-8 -*-
"""Tab 3 — Cahaya vs Ekonomi: scatter log-log + garis OLS (nasional & wilayah terfilter), residual paling menyimpang."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .core import (BLUE_D, GOLD, INK, KUADRAN_C, MUTED, NAVY, PULAU, PULAU_C, RED, ROYAL, STATUS_C, angka, kepala, kpi_grid,
                   pendek, sumber, tampil, tema)


def render(c):
    K, R = c["K"].copy(), c["ring"]
    o = R["ols"]
    K["x"], K["y"] = np.log1p(K.cahaya_pk), np.log(K.pdrb_kapita_ribu)
    n = len(K)
    b1 = b0 = r2l = None
    if n > 10 and n < len(c["kab"]):
        b1, b0 = np.polyfit(K.x, K.y, 1)
        r2l = np.corrcoef(K.x, K.y)[0, 1] ** 2
    L, Rt = st.columns([1.6, 1])
    with L, st.container(key="c_g_sc"):
        kepala("Semakin terang semakin kaya — tetapi banyak pengecualian",
               "Setiap titik = satu kab/kota. Sumbu log-log: kemiringan garis = elastisitas. Titik jauh dari garis = tidak selaras.",
               ("RELASI 2 VARIABEL", "SCATTER + OLS"))
        warna = st.segmented_control("Warna titik", ["Status", "Kuadran", "Pulau"], default="Status", key="g_w",
                                     label_visibility="collapsed") or "Status"
        col, cmap = {"Status": ("status_selaras", STATUS_C), "Kuadran": ("kuadran", KUADRAN_C), "Pulau": ("pulau", PULAU_C)}[warna]
        fig = go.Figure()
        cd_cols = ["nama", "provinsi", "cahaya_pk", "pdrb_kapita_juta", "z_residual", col]
        for kat, warna_k in cmap.items():
            d = K[K[col] == kat]
            if d.empty:
                continue
            fig.add_trace(go.Scattergl(
                x=d.x, y=d.y, mode="markers", name=kat,
                marker=dict(size=np.clip(np.sqrt(d.penduduk_2024 / 1e4), 5, 18), color=warna_k, opacity=.85 if kat != "Selaras" else .6,
                            line=dict(width=.7, color="white")),
                customdata=d[cd_cols].values,
                hovertemplate="<b>%{customdata[0]}</b><br><span style='color:#7a8799'>%{customdata[1]}</span><br>"
                              "Cahaya/kap %{customdata[2]:.2f} · PDRB/kap Rp%{customdata[3]:.1f} jt<br>"
                              "z residual %{customdata[4]:+.2f}<br>%{customdata[5]}<extra></extra>"))
        xs = np.linspace(K.x.min(), K.x.max(), 40)
        fig.add_trace(go.Scatter(x=xs, y=o["const"] + o["beta"] * xs, mode="lines", line=dict(color=NAVY, width=2.4),
                                 name=f"OLS nasional (β = {angka(o['beta'], 2)})", hoverinfo="skip"))
        if b1 is not None:
            fig.add_trace(go.Scatter(x=xs, y=b0 + b1 * xs, mode="lines", line=dict(color=GOLD, width=2.4, dash="dash"),
                                     name=f"OLS {c['label_pulau']} (β = {angka(b1, 2)})", hoverinfo="skip"))
        for i, r in enumerate(pd.concat([K.nlargest(4, "z_residual"), K.nsmallest(2, "z_residual")]).itertuples()):
            fig.add_annotation(x=r.x, y=r.y, text=pendek(r.nama), font=dict(size=10, color=INK), showarrow=True, arrowwidth=.8,
                               arrowcolor=MUTED, ax=0 if i < 4 else [70, -70][i - 4], ay=-20 if i < 4 else [30, 34][i - 4],
                               bgcolor="rgba(255,255,255,.85)", borderpad=1)
        tema(fig, legend=True, l=8, r=8, t=28, b=6).update_layout(
            xaxis_title="ln(1 + cahaya per kapita)   [nW/cm²/sr per 1.000 jiwa]", yaxis_title="ln(PDRB per kapita ADHB, ribu Rp)",
            legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, font=dict(size=10.5)), hovermode="closest")
        tampil(fig, "g_sc", cfg={"modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage"]})
        sumber("Sumber: BPS (2024) PDRB per kapita & penduduk; VIIRS VNL V2.2 (2024). Ukuran titik ∝ √penduduk.")
    with Rt:
        kpi_grid([
            ("Elastisitas nasional", angka(o["beta"], 3), f"SE {angka(o['se'], 3)} (HC3) · p < 0,001", NAVY),
            ("R² nasional", angka(o["r2"], 3), f"n = {R['n']} kab/kota", ROYAL),
            (f"Elastisitas {c['label_pulau']}" if b1 is not None else "Elastisitas robust",
             angka(b1, 3) if b1 is not None else angka(R["ols_robust"]["ln_cahaya_pk"], 3),
             f"R² {angka(r2l, 2)} · n = {n}" if b1 is not None else "+ ln kepadatan & IKK", GOLD),
        ])
        with st.container(key="c_g_res"):
            kepala("Paling menyimpang dari garis", "z residual terstandar; |z| > 1,5 = tidak selaras", ("DIVERGEN",))
            r = pd.concat([K.nlargest(7, "z_residual"), K.nsmallest(7, "z_residual")]).drop_duplicates("kode_bps").sort_values("z_residual")
            f2 = go.Figure(go.Bar(x=r.z_residual, y=r.nama.map(pendek), orientation="h",
                                  marker=dict(color=np.where(r.z_residual > 0, RED, BLUE_D), cornerradius=3),
                                  customdata=r.provinsi, hovertemplate="<b>%{y}</b> (%{customdata})<br>z = %{x:+.2f}<extra></extra>"))
            f2.add_vline(x=0, line_color=MUTED, line_width=1)
            for xv in (-1.5, 1.5):
                f2.add_vline(x=xv, line_color=MUTED, line_width=1, line_dash="dot")
            tema(f2, l=4, r=8, t=4, b=4).update_layout(yaxis=dict(tickfont=dict(size=10, color=INK)),
                                                     xaxis_title="← lebih terang dari ekonominya  |  lebih kaya dari cahayanya →",
                                                     xaxis_title_font=dict(size=10.5), bargap=.25)
            tampil(f2, "g_res", cfg={"displayModeBar": False, "scrollZoom": False})
        with st.container(key="t_g_int"):
            kepala("Interpretasi", chips=("INSIGHT",))
            n_k, n_t = (K.status_selaras == "Lebih kaya dari cahayanya").sum(), (K.status_selaras == "Lebih terang dari ekonominya").sum()
            gz = K.groupby("pulau").z_residual.mean()
            lok = ""
            if b1 is not None:
                beda = "lebih kuat" if b1 > o["beta"] else "lebih lemah"
                lok = f"<p>Di <b>{c['label_pulau']}</b>, hubungan cahaya–ekonomi {beda} (β = {angka(b1, 2)}) dibanding nasional.</p>"
            st.html(f"""<div class='txt'>{lok}<p><b>{n_k}</b> wilayah <span style='color:{RED};font-weight:700'>lebih kaya dari
cahayanya</span> — umumnya pusat jasa/keuangan (Jakarta) dan ekonomi tambang/migas yang padat modal tetapi tidak terang.
<b>{n_t}</b> wilayah <span style='color:{BLUE_D};font-weight:700'>lebih terang dari ekonominya</span> — padat penduduk dengan
produktivitas rendah (mis. Madura).</p><p>Rata-rata z residual per pulau: paling positif <b>{gz.idxmax()}</b> ({angka(gz.max(), 2, True)}), paling negatif
<b>{gz.idxmin()}</b> ({angka(gz.min(), 2, True)}) → {'wilayah ini cenderung lebih kaya daripada yang “diprediksi” cahayanya.' if gz.max() > 0 else ''}</p>
<p style='color:#7a8799'>Uji kekokohan: menambah kepadatan & IKK → β =
{angka(R['ols_robust']['ln_cahaya_pk'], 3)} (stabil). Breusch–Pagan p = {angka(o['bp_p'], 3)}.</p></div>""")
