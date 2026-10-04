# -*- coding: utf-8 -*-
"""Tab 2 — Peta tematik: choropleth berkelas / divergen / kategori + simbol proporsional, klik wilayah → profil."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import peta
from .core import (CAT_MAP, INK, INK2, NAVY, PULAU, ROYAL, SEQ5, SRC, VAR, angka, fmtv, kepala, pendek, pusat, sumber,
                   tampil, tema)

KLAS = ["Kuantil", "Natural breaks (Jenks)", "Interval sama"]
UKURAN = {"pdrb_adhb_miliar": ("PDRB ADHB total", "Rp{} triliun", 1e3, "Rp triliun"),
          "penduduk_2024": ("Jumlah penduduk", "{} ribu jiwa", 1e3, "ribu jiwa"),
          "rad_sum_2024": ("Total radiance cahaya", "{} nW/cm²/sr", 1, "nW/cm²/sr")}


def klasifikasi(s, metode, k=5):
    s = s.astype(float)
    if metode.startswith("Natural"):
        import mapclassify as mc
        b = list(mc.FisherJenks(s.dropna(), k=k).bins)
    elif metode == "Interval sama":
        b = list(np.linspace(s.min(), s.max(), k + 1)[1:])
    else:
        b = list(np.nanquantile(s, np.linspace(0, 1, k + 1))[1:])
    b = sorted(set(np.round(b, 6)))
    b[-1] = s.max()
    lo = [s.min()] + b[:-1]
    d = 0 if s.max() > 300 else 1 if s.max() > 20 else 2
    labels = [f"{angka(a, d)} – {angka(c, d)}" for a, c in zip(lo, b)]
    idx = np.searchsorted(b, s.values, side="left").clip(0, len(b) - 1)
    return idx.astype(float), labels


def render(c):
    kab, prov = c["kab"], c["prov"]
    L, R = st.columns([1.75, 1])
    with R, st.container(key="t_p_ctrl"):
        kepala("Pengaturan peta", chips=("KONTROL LAPISAN",))
        a, b = st.columns([1, 1.25])
        level = a.segmented_control("Tingkat wilayah", ["Kab/Kota", "Provinsi"], default="Kab/Kota", key="p_lvl") or "Kab/Kota"
        jenis_peta = b.segmented_control("Lapisan", ["Choropleth", "Simbol", "Keduanya"], default="Choropleth", key="p_jenis") \
            or "Choropleth"
        opsi = [k for k, v in VAR.items() if level == "Kab/Kota" or v[4]]
        var = st.selectbox("Variabel (warna choropleth)", opsi, key="p_var", format_func=lambda k: f"{VAR[k][5]} · {VAR[k][0]}")
        lab, sat, jenis, fmt, _, _ = VAR[var]
        a, b = st.columns(2)
        metode = a.selectbox("Klasifikasi", KLAS, key="p_kls", disabled=jenis != "seq",
                             help="Kuantil: jumlah wilayah per kelas sama (baik untuk distribusi menceng). Jenks: memaksimalkan "
                                  "homogenitas dalam kelas. Interval sama: lebar kelas sama.")
        ukur = b.selectbox("Ukuran simbol", list(UKURAN), key="p_ukur", format_func=lambda k: UKURAN[k][0],
                           disabled=jenis_peta == "Choropleth", help="Simbol proporsional untuk besaran absolut (luas ∝ nilai).")
    isKab = level == "Kab/Kota"
    D = (c["K"] if isKab else prov[prov.pulau.isin(c["pulau_sel"])]).copy().reset_index(drop=True)
    nama = "nama" if isKab else "provinsi"
    lvl = "kab" if isKab else "prov"
    view = pusat(D)
    if jenis != "cat":
        ket = lab + ": <b>" + D[var].map(lambda v: fmtv(v, fmt)) + "</b> " + sat
    else:
        ket = lab + ": <b>" + D[var].astype(str) + "</b>"
    if jenis_peta == "Simbol":
        fig = go.Figure(peta.lapisan_dasar(D["kode_bps" if isKab else "kode_prov"], lvl))
        fig.update_layout(map=dict(style=peta.BASEMAP, **view))
    elif jenis == "seq":
        idx, labels = klasifikasi(D[var], metode)
        fig = peta.kelas(D, var, (idx, labels), SEQ5, level=lvl, nama=nama, ket=ket, view=view, title=sat)
    elif jenis == "div":
        mid = 0.0 if var == "z_residual" else float(D[var].median())
        rng = float(np.nanquantile(np.abs(D[var] - mid), .96)) or 1
        fig = peta.divergen(D, var, mid, rng, level=lvl, nama=nama, ket=ket, view=view,
                            title=f"{sat}<br>tengah = {'0' if var == 'z_residual' else 'median ' + fmtv(mid, fmt)}")
    else:
        fig = peta.kategori(D, var, CAT_MAP[var], level=lvl, nama=nama, ket=ket, view=view)
    leg_simbol = ""
    if jenis_peta != "Choropleth":
        nm, pola, bagi, unit = UKURAN[ukur]
        col = ukur if ukur in D else None
        if col is None:
            D[ukur] = np.nan
        teks = nm + ": " + (D[ukur] / bagi).map(lambda v: pola.format(angka(v, 1)))
        tr, vmax, maks = peta.simbol(D, ukur, nama, teks, maks=40 if not isKab else 30, name=nm)
        fig.add_trace(tr)
        leg_simbol = peta.legenda_simbol(vmax / bagi, maks, f"{nm} ({unit})", fmt=lambda v: angka(v, 1 if v < 10 else 0))
    with L, st.container(key="c_p_map"):
        judul = f"{lab} — {level.lower()}" if jenis_peta != "Simbol" else f"{UKURAN[ukur][0]} — simbol proporsional"
        sub = ("Klik satu wilayah untuk melihat profil lengkapnya di panel kanan. " if isKab else "") + \
              ("Warna = rasio/indeks (bukan angka absolut) sesuai kaidah choropleth. " if jenis_peta != "Simbol" else "") + \
              ("Lingkaran = besaran absolut." if jenis_peta != "Choropleth" else "")
        chips = ["GEOSPASIAL", "CHOROPLETH" if jenis_peta == "Choropleth" else "SIMBOL PROPORSIONAL" if jenis_peta == "Simbol"
                 else "CHOROPLETH + SIMBOL"]
        if jenis == "seq" and jenis_peta != "Simbol":
            chips.append(metode.split(" (")[0].upper())
        kepala(judul, sub, chips)
        if jenis == "cat" and jenis_peta != "Simbol":
            st.html(peta.legenda_html(CAT_MAP[var], D[var].value_counts()))
        if leg_simbol:
            st.html(leg_simbol)
        ev = tampil(tema(fig), f"p_map_{lvl}", on_select="rerun", selection_mode="points")
        sumber(SRC + (f" · klasifikasi: {metode}" if jenis == "seq" and jenis_peta != "Simbol" else ""))
    # wilayah terklik
    pilih = None
    try:
        pts = ev.selection.points if ev else []
        if pts:
            p0 = pts[0]
            loc = p0.get("location")
            if loc is None and p0.get("customdata"):
                loc = D.loc[D[nama] == p0["customdata"][0], "kode_bps" if isKab else "kode_prov"].iloc[0]
            pilih = str(loc)
    except Exception:
        pilih = None
    with R:
        with st.container(key="c_p_side"):
            if pilih is not None and isKab and (kab.kode_bps == pilih).any():
                profil(kab, kab[kab.kode_bps == pilih].iloc[0])
            else:
                peringkat(D, var, nama, lab, sat, jenis, fmt)
        with st.container(key="t_p_int"):
            interpretasi(D, var, nama, lab, sat, jenis, fmt, metode, c)


def peringkat(D, var, nama, lab, sat, jenis, fmt):
    if jenis == "cat":
        from .core import CAT_MAP
        cm = CAT_MAP[var]
        ct = D[var].value_counts().reindex(list(cm)).dropna()
        kepala("Jumlah wilayah per kategori", chips=("BATANG",))
        fig = go.Figure(go.Bar(x=ct.values, y=[s.split(" (")[0] for s in ct.index], orientation="h",
                               marker=dict(color=[cm[i] for i in ct.index], cornerradius=4), text=ct.values.astype(int),
                               textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x}<extra></extra>"))
        tema(fig, l=4, r=34).update_layout(yaxis=dict(autorange="reversed", tickfont=dict(color=INK)), xaxis=dict(visible=False))
    else:
        arah = st.segmented_control("Peringkat", ["10 tertinggi", "10 terendah"], default="10 tertinggi", key="p_rk",
                                    label_visibility="collapsed") or "10 tertinggi"
        r = (D.nlargest(10, var) if arah == "10 tertinggi" else D.nsmallest(10, var))
        fig = go.Figure(go.Bar(x=r[var], y=r[nama].map(pendek), orientation="h",
                               marker=dict(color=SEQ5[3] if arah == "10 tertinggi" else SEQ5[1], cornerradius=4),
                               text=r[var].map(lambda v: fmtv(v, fmt)), textposition="outside", cliponaxis=False,
                               textfont=dict(color=INK, size=10.5),
                               hovertemplate="%{y}: %{x:" + fmt + "} " + sat + "<extra></extra>"))
        tema(fig, l=4, r=46).update_layout(yaxis=dict(autorange="reversed", tickfont=dict(size=10.5, color=INK)), xaxis=dict(visible=False),
                                           bargap=.28)
        st.html(f"<div class='ks'>{arah.capitalize()} · {lab} ({sat}) — klik peta untuk profil wilayah</div>")
    tampil(fig, "p_rank", cfg={"displayModeBar": False, "scrollZoom": False})


def profil(kab, r):
    """Profil detail-on-demand: posisi wilayah pada 9 indikator (persentil nasional)."""
    from .core import KUADRAN_C, KLASTER_C, STATUS_C
    baris = ""
    for v in ["cahaya_pk", "pct_menyala", "pertumbuhan_cahaya", "pdrb_kapita_juta", "laju_pdrb_pct", "ipm", "p0", "ikk", "kepadatan"]:
        lab, sat, _, fmt, _, _ = VAR[v]
        pct = (kab[v] < r[v]).mean() * 100
        rk = int((kab[v] > r[v]).sum() + 1)
        baris += (f"<tr><td>{lab}</td><td style='text-align:right;white-space:nowrap'><b>{fmtv(r[v], fmt)}</b> "
                  f"<span style='color:#7a8799'>{sat.split(' (')[0]}</span></td>"
                  f"<td style='width:30%'><div class='bar'><i style='width:{pct:.0f}%'></i></div>"
                  f"<div style='font-size:.62rem;color:#7a8799'>peringkat {rk}/514</div></td></tr>")
    pill = lambda t, cm: f"<span class='pill' style='background:{cm.get(t, '#888')}'>{t}</span>"  # noqa: E731
    st.html(f"""<div class='kh'><div class='kt'>{pendek(r.nama)}</div><div class='chips'><span class='chip'>DETAIL ON DEMAND</span></div></div>
<div class='ks'>{r.provinsi} · {r.pulau} · penduduk {angka(r.penduduk_2024 / 1000, 0)} ribu jiwa</div>
<div style='margin:5px 0 4px;display:flex;gap:4px;flex-wrap:wrap'>{pill(r.kuadran, KUADRAN_C)}{pill(r.status_selaras, STATUS_C)}
{pill(r.klaster, KLASTER_C)}</div>
<table class='tbl tblc'><tr><th>Indikator</th><th style='text-align:right'>Nilai</th><th>Posisi nasional</th></tr>{baris}</table>
<div class='src' style='margin-top:4px'>Batang = persentil nasional (makin penuh = makin tinggi). Klik area kosong peta untuk kembali ke peringkat.</div>""")


def interpretasi(D, var, nama, lab, sat, jenis, fmt, metode, c):
    kepala("Interpretasi", chips=("INSIGHT",))
    if jenis == "cat":
        top = D[var].value_counts()
        per_p = (D.groupby("pulau")[var].agg(lambda s: s.value_counts().index[0]) if "pulau" in D else pd.Series(dtype=str))
        st.html(f"""<div class='txt'><p>Kategori terbanyak: <b>{top.index[0]}</b> ({top.iloc[0]} wilayah,
{angka(top.iloc[0] / len(D) * 100, 0)}%).</p><p>Kategori dominan per pulau: {'; '.join(f'{k}: {v.split(" (")[0]}' for k, v in per_p.items())}.</p>
<p style='color:#7a8799'>Peta kategori memakai hue berbeda yang lolos uji buta warna; legenda = batang warna di kanan bawah.</p></div>""")
        return
    s = D[var]
    hi, lo = D.loc[s.idxmax()], D.loc[s.idxmin()]
    med = s.median()
    grp = "pulau" if D.pulau.nunique() > 1 else "provinsi"
    gp = D.groupby(grp)[var].median().dropna()
    rasio = (s.quantile(.9) / s.quantile(.1)) if s.quantile(.1) > 0 else np.nan
    alasan = {"Kuantil": "kuantil menjamin tiap kelas berisi jumlah wilayah sama — cocok untuk distribusi menceng",
              "Natural breaks (Jenks)": "Jenks meminimalkan variasi dalam kelas sehingga batas kelas mengikuti jeda alami data",
              "Interval sama": "interval sama mudah dibaca, tetapi peka terhadap pencilan"}[metode]
    st.html(f"""<div class='txt'><p>Median <b>{fmtv(med, fmt)}</b> {sat}. Tertinggi <b>{pendek(hi[nama])}</b> ({fmtv(hi[var], fmt)}),
terendah <b>{pendek(lo[nama])}</b> ({fmtv(lo[var], fmt)}){'; rasio persentil 90/10 = ×' + angka(rasio, 1) if rasio == rasio else ''}.</p>
<p>Median per {grp} tertinggi di <b>{gp.idxmax()}</b> ({fmtv(gp.max(), fmt)}) dan terendah di <b>{gp.idxmin()}</b> ({fmtv(gp.min(), fmt)}).</p>
<p style='color:#7a8799'>{'Klasifikasi: ' + alasan + '.' if jenis == 'seq' else 'Skala divergen biru–abu–merah: di bawah/di atas nilai tengah.'}</p></div>""")
