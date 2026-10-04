# -*- coding: utf-8 -*-
"""Tab 6 — Aliran migrasi risen 2015–2020: Sankey (asal → tujuan), peta aliran berarah, matriks OD, model gravitasi."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from . import peta
from .core import (BLUE_D, GRAY, INK, PULAU, PULAU_C, RED, SEQ_CONT, angka, kepala, rgba, sumber, tampil, tema)

SUMBER_MIG = ("Sumber: BPS, Statistik Migrasi Indonesia Hasil Long Form SP2020, Tabel 5.3 (hlm. 55–57; baris = provinsi tinggal sekarang = "
              "tujuan, kolom = provinsi 5 tahun lalu = asal) & Tabel 7 · migrasi risen 2015–2020, L+P")


def render(c):
    od, neto, mat, prov, R = c["od"], c["neto"], c["mat"], c["prov"], c["ring"]
    with st.container(key="tb_a"):
        a, b, d, e, f = st.columns([1.15, 1.45, 1.45, 1.1, 1.05], vertical_alignment="center")
        tingkat = a.segmented_control("Tingkat", ["Antar pulau", "Antar provinsi"], default="Antar provinsi", key="a_tk") or "Antar provinsi"
        pil = PULAU if tingkat == "Antar pulau" else sorted(od.provinsi_asal.unique())
        asal = b.multiselect("Filter asal", pil, placeholder="Semua asal", key=f"a_as_{tingkat}")
        tuju = d.multiselect("Filter tujuan", pil, placeholder="Semua tujuan", key=f"a_tj_{tingkat}")
        topn = e.slider("Arus teratas", 10, 80, 25, 5, key="a_n")
        panel = f.segmented_control("Panel kanan", ["Peta aliran", "Matriks OD"], default="Peta aliran", key="a_p") or "Peta aliran"
    a_col, t_col = ("pulau_asal", "pulau_tujuan") if tingkat == "Antar pulau" else ("provinsi_asal", "provinsi_tujuan")
    O = od.copy()
    if asal:
        O = O[O[a_col].isin(asal)]
    if tuju:
        O = O[O[t_col].isin(tuju)]
    F = O.groupby([a_col, t_col], as_index=False).jumlah_migran.sum()
    F = F[F[a_col] != F[t_col]].nlargest(topn, "jumlah_migran")
    p_of = dict(zip(od.provinsi_asal, od.pulau_asal)) | dict(zip(od.provinsi_tujuan, od.pulau_tujuan))
    warna_p = lambda n: PULAU_C.get(n if n in PULAU else p_of.get(n), GRAY)  # noqa: E731
    L, Rt = st.columns([1.1, 1])
    with L, st.container(key="c_a_sk"):
        kepala(f"Siapa pindah ke mana? {len(F)} arus migrasi risen terbesar",
               "Kiri = daerah asal, kanan = daerah tujuan; tebal pita ∝ jumlah migran; warna pita = pulau asal. Seret simpul untuk menata ulang.",
               ("ALIRAN", "SANKEY"))
        nodes_a = [f"{n} " for n in F[a_col].unique()]        # spasi pembeda node asal vs tujuan
        nodes_t = list(F[t_col].unique())
        nodes = nodes_a + nodes_t
        ix = {n: i for i, n in enumerate(nodes)}
        vin = F.groupby(t_col).jumlah_migran.sum()
        vout = F.groupby(a_col).jumlah_migran.sum()
        sk = go.Figure(go.Sankey(
            arrangement="snap", valueformat=",.0f",
            node=dict(label=[n.strip() for n in nodes], pad=9, thickness=13, color=[warna_p(n.strip()) for n in nodes], line=dict(width=0),
                      customdata=[angka(vout.get(n.strip(), 0), 0) if n.endswith(" ") else angka(vin.get(n, 0), 0) for n in nodes],
                      hovertemplate="<b>%{label}</b><br>%{customdata} migran (arus tampil)<extra></extra>"),
            link=dict(source=[ix[f"{x} "] for x in F[a_col]], target=[ix[t] for t in F[t_col]], value=F.jumlah_migran,
                      color=[rgba(warna_p(x), .38) for x in F[a_col]],
                      hovertemplate="%{source.label} → %{target.label}<br><b>%{value:,.0f}</b> migran<extra></extra>")))
        tema(sk, l=4, r=4, t=4, b=4).update_layout(font=dict(size=11, color=INK))
        tampil(sk, f"a_sk", cfg={"displayModeBar": False, "scrollZoom": False})
        sumber(SUMBER_MIG + " · arus di dalam provinsi/pulau sendiri tidak ditampilkan")
    with Rt:
        with st.container(key="c_a_map"):
            if panel == "Peta aliran":
                kepala("Peta aliran berarah antarprovinsi",
                       "Garis melengkung searah jarum jam dari asal → tujuan, titik kecil = tujuan; tebal ∝ volume. Lingkaran: "
                       "<span style='color:#b42e2e;font-weight:700'>merah = neto masuk</span>, "
                       "<span style='color:#1c5cab;font-weight:700'>biru = neto keluar</span>.", ("ALIRAN", "FLOW MAP"))
                P = O.groupby(["provinsi_asal", "provinsi_tujuan", "lon_asal", "lat_asal", "lon_tujuan", "lat_tujuan"],
                              as_index=False).jumlah_migran.sum().nlargest(topn, "jumlah_migran")
                fm = go.Figure(peta.lapisan_dasar(prov.kode_prov, "prov"))
                mx = P.jumlah_migran.max() if len(P) else 1
                lon, lat, txt = [], [], []
                widths = {}
                for r in P.itertuples():
                    dx, dy = r.lon_tujuan - r.lon_asal, r.lat_tujuan - r.lat_asal
                    t = np.linspace(0, 1, 18)
                    cx, cy = (r.lon_asal + r.lon_tujuan) / 2 + dy * .22, (r.lat_asal + r.lat_tujuan) / 2 - dx * .22   # lengkung ke kanan arah gerak
                    xs = (1 - t) ** 2 * r.lon_asal + 2 * (1 - t) * t * cx + t ** 2 * r.lon_tujuan
                    ys = (1 - t) ** 2 * r.lat_asal + 2 * (1 - t) * t * cy + t ** 2 * r.lat_tujuan
                    w = round(1 + 7 * r.jumlah_migran / mx)
                    widths.setdefault(w, ([], [], []))
                    widths[w][0].extend(list(xs) + [None]); widths[w][1].extend(list(ys) + [None])
                    widths[w][2].extend([f"{r.provinsi_asal} → {r.provinsi_tujuan}: {angka(r.jumlah_migran, 0)} migran"] * 18 + [None])
                for w, (xs, ys, tx) in sorted(widths.items()):
                    fm.add_trace(go.Scattermap(lon=xs, lat=ys, mode="lines", line=dict(width=w, color="rgba(55,65,95,.55)"),
                                               text=tx, hoverinfo="text", showlegend=False))
                fm.add_trace(go.Scattermap(lon=P.lon_tujuan, lat=P.lat_tujuan, mode="markers", hoverinfo="skip", showlegend=False,
                                           marker=dict(size=6, color="#37415f")))
                N = neto
                fm.add_trace(go.Scattermap(
                    lon=N.lon, lat=N.lat, mode="markers", showlegend=False,
                    marker=dict(size=(np.sqrt(N.neto_risen.abs() / N.neto_risen.abs().max()) * 30).clip(lower=5),
                                color=np.where(N.neto_risen >= 0, RED, BLUE_D), opacity=.72),
                    customdata=np.c_[N.provinsi, N.masuk_risen.map(lambda v: angka(v, 0)), N.keluar_risen.map(lambda v: angka(v, 0)),
                                     N.neto_risen.map(lambda v: angka(v, 0, True))],
                    hovertemplate="<b>%{customdata[0]}</b><br>Masuk %{customdata[1]} · Keluar %{customdata[2]}<br>Neto <b>%{customdata[3]}</b><extra></extra>"))
                fm.update_layout(map=dict(style=peta.BASEMAP, center=dict(lat=-2.3, lon=117.6), zoom=3.55))
                tampil(tema(fm), "a_map", cfg={"displayModeBar": False})
            else:
                kepala("Matriks asal–tujuan (OD) 34 provinsi", "Baris = asal, kolom = tujuan; warna = log10 jumlah migran; diagonal dikosongkan.",
                       ("ALIRAN", "MATRIKS OD"))
                Mx = mat.drop(columns=["Luar Negeri", "Total"], errors="ignore")
                idx = [i for i in Mx.index if i in Mx.columns]
                V = Mx.loc[idx, idx].to_numpy(dtype=float, copy=True)
                np.fill_diagonal(V, np.nan)
                # matriks sumber: baris = tujuan, kolom = asal → transpos agar baris = asal
                V = V.T
                hm = go.Figure(go.Heatmap(z=np.log10(V + 1), x=idx, y=idx, colorscale=SEQ_CONT, customdata=V, xgap=1, ygap=1,
                                          colorbar=dict(thickness=9, title=dict(text="log10", font=dict(size=10))),
                                          hovertemplate="%{y} → %{x}<br><b>%{customdata:,.0f}</b> migran<extra></extra>"))
                tema(hm, l=4, r=4, t=4, b=4).update_layout(xaxis=dict(tickfont=dict(size=7.5), tickangle=-60, title="Tujuan"),
                                                         yaxis=dict(tickfont=dict(size=7.5), autorange="reversed", title="Asal"))
                tampil(hm, "a_od", cfg={"displayModeBar": False})
            sumber(SUMBER_MIG)
        with st.container(key="t_a_int"):
            kepala("Interpretasi", chips=("INSIGHT",))
            g = R["gravitasi"]
            co = lambda k: g[k]["coef"]  # noqa: E731
            sig = lambda k: "signifikan" if g[k]["p"] < .05 else "tidak signifikan"  # noqa: E731
            top = F.head(3)
            antar = od[od.provinsi_asal != od.provinsi_tujuan]
            ke_jawa = antar[antar.pulau_tujuan == "Jawa"].jumlah_migran.sum() / antar.jumlah_migran.sum() * 100
            dari_jawa = antar[antar.pulau_asal == "Jawa"].jumlah_migran.sum() / antar.jumlah_migran.sum() * 100
            nn = neto.sort_values("neto_risen")
            st.html(f"""<div class='txt'><p>Arus terbesar: {'; '.join(f'<b>{r[a_col]} → {r[t_col]}</b> ({angka(r.jumlah_migran, 0)})' for _, r in top.iterrows())}.
Penerima neto terbesar <b>{nn.iloc[-1].provinsi}</b> ({angka(nn.iloc[-1].neto_risen, 0, True)}); pengirim neto terbesar
<b>{nn.iloc[0].provinsi}</b> ({angka(nn.iloc[0].neto_risen, 0, True)}) — pola suburbanisasi Jabodetabek.</p>
<p>Dari seluruh migran antarprovinsi, <b>{angka(ke_jawa, 1)}%</b> menuju provinsi di Jawa dan <b>{angka(dari_jawa, 1)}%</b>
berasal dari Jawa — arus didominasi perpindahan jarak dekat di dalam Jawa.</p>
<p><b>Model gravitasi</b> (Poisson PPML, {angka(len(od), 0)} pasangan): elastisitas jarak {angka(co('np.log(jarak_km)'), 2, True)},
penduduk tujuan {angka(co('np.log(pend_d)'), 2, True)}, cahaya tujuan {angka(co('np.log(cahaya_pk20_d)'), 2, True)}
({sig('np.log(cahaya_pk20_d)')}) → migrasi lebih ditentukan jarak & ukuran daerah daripada terangnya tujuan.</p></div>""")
