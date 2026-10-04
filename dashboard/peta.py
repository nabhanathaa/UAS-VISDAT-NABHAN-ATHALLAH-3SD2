# -*- coding: utf-8 -*-
"""Pembangun peta Plotly (MapLibre) yang ringan: GeoJSON dirujuk lewat URL statis, satu trace per peta."""
import numpy as np
import plotly.graph_objects as go

from .core import DIV, GEO_KAB, GEO_PROV, INK, angka, cbar, pusat, step_cs

BASEMAP = "white-bg"   # tanpa ubin eksternal: ringan dan tetap tampil walau jaringan membatasi CDN peta


def _geo(level):
    return (GEO_KAB, "properties.kode_bps", "kode_bps") if level == "kab" else (GEO_PROV, "properties.kode_prov", "kode_prov")


def _hover(D, nama, extra):
    cd = np.c_[D[nama].astype(str), D["provinsi"].astype(str) if "provinsi" in D and nama != "provinsi" else D["pulau"].astype(str),
               extra]
    return cd, "<b>%{customdata[0]}</b><br><span style='color:#7a8799'>%{customdata[1]}</span><br>%{customdata[2]}<extra></extra>"


def kategori(D, col, cmap, level="kab", nama="nama", ket=None, view=None, line=.35, legenda=False):
    """Choropleth kategori (identitas) — satu trace, kelas → colorscale bertangga, legenda = colorbar berlabel."""
    geo, fk, key = _geo(level)
    labels = list(cmap)
    idx = D[col].map({k: i for i, k in enumerate(labels)}).astype(float)
    extra = (D[col].astype(str) if ket is None else ket).values
    cd, ht = _hover(D, nama, extra)
    n = len(labels)
    tr = go.Choroplethmap(geojson=geo, featureidkey=fk, locations=D[key], z=idx, zmin=-.5, zmax=n - .5,
                          colorscale=step_cs(list(cmap.values())), marker=dict(opacity=.92, line=dict(width=line, color="white")),
                          customdata=cd, hovertemplate=ht, showscale=legenda,
                          colorbar=cbar("", tickvals=list(range(n)), ticktext=labels, len=.08 * n + .06, thickness=12))
    fig = go.Figure(tr)
    fig.update_layout(map=dict(style=BASEMAP, **(view or pusat(D))))
    return fig


def kelas(D, col, edges_labels, colors, level="kab", nama="nama", ket=None, view=None, title=""):
    """Choropleth berkelas (kuantil / Jenks / interval sama) dengan palet sekuensial."""
    idx, labels = edges_labels
    geo, fk, key = _geo(level)
    cd, ht = _hover(D, nama, ket.values)
    n = len(labels)
    tr = go.Choroplethmap(geojson=geo, featureidkey=fk, locations=D[key], z=idx, zmin=-.5, zmax=n - .5,
                          colorscale=step_cs(colors[:n]), marker=dict(opacity=.93, line=dict(width=.35, color="white")),
                          selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=.45)),
                          customdata=cd, hovertemplate=ht,
                          colorbar=cbar(title, tickvals=list(range(n)), ticktext=labels, len=.07 * n + .1, thickness=12, x=.01, xanchor="left"))
    fig = go.Figure(tr)
    fig.update_layout(map=dict(style=BASEMAP, **(view or pusat(D))))
    return fig


def divergen(D, col, mid, rng, level="kab", nama="nama", ket=None, view=None, title=""):
    geo, fk, key = _geo(level)
    cd, ht = _hover(D, nama, ket.values)
    tr = go.Choroplethmap(geojson=geo, featureidkey=fk, locations=D[key], z=D[col], zmin=mid - rng, zmax=mid + rng,
                          colorscale=DIV, marker=dict(opacity=.93, line=dict(width=.35, color="white")),
                          customdata=cd, hovertemplate=ht, colorbar=cbar(title, len=.45, x=.01, xanchor="left"))
    fig = go.Figure(tr)
    fig.update_layout(map=dict(style=BASEMAP, **(view or pusat(D))))
    return fig


def lapisan_dasar(locs, level="prov", warna="#e7edf5"):
    geo, fk, _ = _geo(level)
    return go.Choroplethmap(geojson=geo, featureidkey=fk, locations=locs, z=np.zeros(len(locs)),
                            colorscale=[[0, warna], [1, warna]], showscale=False, hoverinfo="skip",
                            marker=dict(line=dict(width=.6, color="white")))


def simbol(D, val, nama, teks_nilai, warna="rgba(235,104,52,.62)", maks=34, name="Simbol"):
    """Simbol proporsional: LUAS lingkaran ∝ nilai (diameter ∝ √nilai)."""
    s = D[val].clip(lower=0).astype(float)
    d = np.sqrt(s / s.max()) * maks
    return go.Scattermap(lon=D.lon, lat=D.lat, mode="markers", name=name,
                         marker=dict(size=d.clip(lower=3), color=warna, sizemode="diameter"),
                         customdata=np.c_[D[nama].astype(str), teks_nilai],
                         hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"), s.max(), maks


def legenda_simbol(vmax, maks, satuan, fmt=lambda v: angka(v, 0)):
    """Legenda ukuran — tiga lingkaran referensi (luas ∝ nilai) agar pembaca dapat membandingkan besaran."""
    it = ""
    for v in (vmax, vmax / 4, vmax / 16):
        d = max(np.sqrt(v / vmax) * maks, 3)
        it += (f"<span style='display:inline-flex;align-items:center;gap:5px'><span style='display:inline-block;width:{d:.0f}px;"
               f"height:{d:.0f}px;border-radius:50%;background:rgba(235,104,52,.45);border:1px solid #eb6834'></span>{fmt(v)}</span>")
    return f"<div class='leg' style='align-items:center;gap:6px 16px'><b style='color:#45566d'>Luas lingkaran ∝ {satuan}:</b>{it}</div>"


def legenda_html(cmap, counts=None):
    """Legenda kategori HTML ringkas (di atas peta) — hemat ruang, tidak menutupi wilayah."""
    it = ""
    for k, w in cmap.items():
        n = "" if counts is None else f" <span style='color:#7a8799'>({int(counts.get(k, 0))})</span>"
        it += f"<span><i style='background:{w}'></i>{k}{n}</span>"
    return f"<div class='leg'>{it}</div>"
