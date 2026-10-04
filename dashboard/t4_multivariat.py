# -*- coding: utf-8 -*-
"""Tab 4 — Multivariat: biplot PCA (brushing) → parallel coordinates, heatmap profil klaster / radar, peta tertaut (linking)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import peta
from .core import (CAT4, CHI2_975_9, DIV, INK, INK2, KLASTER_C, PENDEK, angka, kepala, pendek, rgba, sumber, tampil, tema)

ANK = {"Laju PDRB": "right"}                      # posisi label panah biplot agar tidak bertumpuk
YSH = {"IKK": -9, "P0": 8, "% menyala": -2, "Kepadatan": 8}


def render(c):
    R, kab = c["ring"], c["kab"]
    lab = R["var_label"]
    cols = list(lab)
    D = c["K"].reset_index(drop=True)
    Z = c["Z"].loc[c["K"].index].reset_index(drop=True)
    vp, ld = R["pca"]["varians_pct"], R["pca"]["loadings"]
    L, Rt = st.columns([1.05, 1.3])
    with L:
        with st.container(key="c_m_bi"):
            kepala("Biplot PCA — pilih titik dengan laso/kotak",
                   f"PC1 ({angka(vp[0], 1)}%) & PC2 ({angka(vp[1], 1)}%) dari 9 variabel terstandar; warna = tipologi k-means (k = 4); "
                   "panah = loading variabel. Seleksi menyorot semua tampilan lain (brushing & linking).",
                   ("REDUKSI DIMENSI", "BIPLOT"))
            fig = go.Figure()
            for k, w in KLASTER_C.items():
                d = D[D.klaster == k]
                fig.add_trace(go.Scatter(
                    x=d.PC1, y=d.PC2, mode="markers", name=k,
                    marker=dict(size=np.clip(np.sqrt(d.penduduk_2024 / 1e4), 5, 17), color=w, opacity=.82, line=dict(width=.6, color="white")),
                    customdata=np.c_[d.kode_bps, d.nama, d.provinsi, d.mahal.round(1)],
                    hovertemplate="<b>%{customdata[1]}</b><br><span style='color:#7a8799'>%{customdata[2]}</span><br>"
                                  "PC1 %{x:.2f} · PC2 %{y:.2f}<br>Jarak Mahalanobis %{customdata[3]}<extra></extra>"))
            sk = 6.0
            for nm, (a1, a2) in ld.items():
                pn = PENDEK[nm]
                fig.add_annotation(x=a1 * sk, y=a2 * sk, ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                                   arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor=INK, text="")
                fig.add_annotation(x=a1 * sk, y=a2 * sk, text=f"<b>{pn}</b>", showarrow=False, font=dict(size=10, color=INK),
                                   xanchor=ANK.get(pn, "left" if a1 >= 0 else "right"), xshift=4 if a1 >= 0 else -4,
                                   yshift=YSH.get(pn, 6 if a2 >= 0 else -6), bgcolor="rgba(255,255,255,.8)")
            out = D[D.mahal > CHI2_975_9].nlargest(4, "mahal")
            for r in out.itertuples():
                fig.add_annotation(x=r.PC1, y=r.PC2, text=pendek(r.nama), showarrow=True, arrowwidth=.7, arrowcolor="#9aa6b5",
                                   ax=18, ay=-16, font=dict(size=9.5, color=INK2), bgcolor="rgba(255,255,255,.8)")
            tema(fig, legend=True, l=6, r=6, t=40, b=4).update_layout(
                xaxis_title=f"PC1 ({angka(vp[0], 1)}%) → lebih sejahtera & urban", yaxis_title=f"PC2 ({angka(vp[1], 1)}%)",
                dragmode="lasso", legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, font=dict(size=10)), modebar=dict(orientation="v"))
            ev = tampil(fig, "m_bi", on_select="rerun", selection_mode=("box", "lasso"))
            sumber("Sumber: BPS (2024); VIIRS VNL – diolah (PCA & k-means). Ukuran titik ∝ √penduduk.")
        sel = []
        try:
            sel = [p["customdata"][0] for p in ev.selection.points if p.get("customdata")]
        except Exception:
            sel = []
    pilih = D.kode_bps.isin(sel) if sel else pd.Series(True, index=D.index)
    n_sel = int(pilih.sum())
    with Rt:
        with st.container(key="c_m_pc"):
            kepala(f"Parallel coordinates · {n_sel} kab/kota {'terpilih' if sel else '(semua)'}",
                   "Setiap garis = satu kab/kota melintasi 9 sumbu z-score. Seret pada sumbu untuk menyaring rentang nilai.",
                   ("MULTIVARIAT", "PARALLEL COORDINATES"))
            kid = D.klaster.map({n: i for i, n in enumerate(KLASTER_C)}).astype(float)
            warna = np.where(pilih, kid, -1.0)
            cs = [[0, "#e3e8ef"], [.2, "#e3e8ef"], [.2001, CAT4[0]], [.4, CAT4[0]], [.4001, CAT4[1]], [.6, CAT4[1]],
                  [.6001, CAT4[2]], [.8, CAT4[2]], [.8001, CAT4[3]], [1, CAT4[3]]]
            urut = np.argsort(pilih.values)       # garis terpilih digambar terakhir (di atas)
            dims = [dict(label=PENDEK[lab[cc]], values=Z[cc].clip(-3.5, 3.5).values[urut], range=[-3.5, 3.5],
                         tickvals=[-3, -2, -1, 0, 1, 2, 3], ticktext=["−3", "−2", "−1", "0", "1", "2", "3"]) for cc in cols]
            pc = go.Figure(go.Parcoords(line=dict(color=warna[urut], colorscale=cs, cmin=-1.5, cmax=3.5), dimensions=dims,
                                        labelfont=dict(size=11, color=INK, family="Open Sans, verdana, arial, sans-serif"), tickfont=dict(size=9, color="#8a96a6", family="Open Sans, verdana, arial, sans-serif"),
                                        rangefont=dict(size=1, color="rgba(0,0,0,0)"), labelangle=0))
            tema(pc, l=34, r=34, t=46, b=10).update_layout(separators=".,")   # tick parcoords bilangan bulat
            tampil(pc, "m_pc", cfg={"displayModeBar": False})
        a, b = st.columns([1.15, 1])
        with a, st.container(key="c_m_hm"):
            h1, h2 = st.columns([1.1, 1], vertical_alignment="center")
            with h1:
                kepala("Profil klaster", chips=("HEATMAP",) if st.session_state.get("m_v", "Heatmap") == "Heatmap" else ("RADAR",))
            v = h2.segmented_control("Tampilan", ["Heatmap", "Radar"], default="Heatmap", key="m_v", label_visibility="collapsed") \
                or "Heatmap"
            if v == "Heatmap":
                prof = Z.groupby(D.klaster).mean().reindex(list(KLASTER_C)).dropna(how="all")
                prof.columns = [PENDEK[lab[cc]] for cc in cols]
                hm = go.Figure(go.Heatmap(z=prof.values, x=prof.columns, y=[p.split(" (")[0].split(":")[0] for p in prof.index],
                                          colorscale=DIV, zmid=0, zmin=-2.5, zmax=2.5, text=np.round(prof.values, 1),
                                          texttemplate="%{text}", textfont=dict(size=9.5), xgap=2, ygap=2,
                                          colorbar=dict(thickness=8, len=.9, title=dict(text="z", font=dict(size=10))),
                                          hovertemplate="%{y}<br>%{x}: z = %{z:.2f}<extra></extra>"))
                tema(hm, l=4, r=4, t=4, b=4).update_layout(xaxis=dict(tickangle=-35, tickfont=dict(size=9.5, color=INK)),
                                                         yaxis=dict(tickfont=dict(size=9.5, color=INK), autorange="reversed"))
                tampil(hm, "m_hm", cfg={"displayModeBar": False, "scrollZoom": False})
            else:
                rd = go.Figure()
                th = [PENDEK[lab[cc]] for cc in cols] + [PENDEK[lab[cols[0]]]]
                for k, w in KLASTER_C.items():
                    zz = Z[D.klaster == k].mean()
                    if zz.isna().all():
                        continue
                    rr = list(zz.clip(-3, 3).values) + [zz.clip(-3, 3).values[0]]
                    rd.add_trace(go.Scatterpolar(r=rr, theta=th, name=k.split(" (")[0].split(":")[0], line=dict(color=w, width=2),
                                                 fill="toself", fillcolor=rgba(w, .08),
                                                 hovertemplate="%{theta}: z = %{r:.2f}<extra>" + k.split(":")[0] + "</extra>"))
                if sel:
                    zz = Z[pilih].mean()
                    rd.add_trace(go.Scatterpolar(r=list(zz.values) + [zz.values[0]], theta=th, name="Terpilih",
                                                 line=dict(color="#13233a", width=2.4, dash="dot")))
                tema(rd, legend=True, l=24, r=24, t=14, b=8).update_layout(
                    polar=dict(radialaxis=dict(range=[-3, 3], tickfont=dict(size=8), gridcolor="#e8edf4"),
                               angularaxis=dict(tickfont=dict(size=9.5, color=INK), gridcolor="#e8edf4"), bgcolor="rgba(0,0,0,0)"),
                    legend=dict(orientation="h", y=-.08, font=dict(size=9)))
                tampil(rd, "m_rd", cfg={"displayModeBar": False, "scrollZoom": False})
        with b, st.container(key="c_m_map"):
            kepala("Peta tertaut", "Wilayah terpilih berwarna sesuai klaster", ("LINKING",))
            M = D.assign(_s=np.where(pilih, D.klaster, "Tidak terpilih"))
            cm = dict(KLASTER_C, **{"Tidak terpilih": "#e9edf3"})
            ket = "Klaster: " + D.klaster
            fig = peta.kategori(M, "_s", cm, ket=ket, view=peta.pusat(D, 330, 260), line=0)
            fig.update_traces(showscale=False)
            tampil(tema(fig), "m_map", cfg={"displayModeBar": False})
    with L, st.container(key="t_m_int"):
        kepala("Interpretasi kelompok & pencilan", chips=("INSIGHT",))
        kl = D.klaster.value_counts()
        out_all = D[D.mahal > CHI2_975_9].sort_values("mahal", ascending=False)
        prof = Z.groupby(D.klaster).mean()
        teks = []
        for k in KLASTER_C:
            if k in prof.index:
                zz = prof.loc[k].rename(lambda x: PENDEK[lab[x]])
                hi = ", ".join(zz.nlargest(2).index)
                lo = ", ".join(zz.nsmallest(2).index)
                teks.append(f"<li><span style='color:{KLASTER_C[k]};font-weight:800'>●</span> <b>{k.split(':')[0]}</b> "
                            f"({kl.get(k, 0)}): ↑ {hi} · ↓ {lo}</li>")
        st.html(f"""<div class='txt'><ul>{''.join(teks)}</ul><p><b>Pencilan</b> (jarak Mahalanobis &gt; χ²<sub>0,975;9</sub> = 19,0):
<b>{len(out_all)}</b> wilayah, mis. {', '.join(pendek(x) for x in out_all.nama.head(4))}. <b>PC1</b> = sumbu kesejahteraan-urbanisasi
(IPM, cahaya, kepadatan ↔ P0, IKK); <b>PC2</b> memisahkan kantong pertumbuhan SDA.</p></div>""")
