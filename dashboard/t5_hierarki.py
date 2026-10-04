# -*- coding: utf-8 -*-
"""Tab 5 — Hierarki ekonomi: treemap/icicle Indonesia → Pulau → Provinsi → 17 Lapangan Usaha → Subsektor
(ukuran = PDRB ADHB, warna = Location Quotient), sunburst struktur sektor satu provinsi."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .core import (DIV, INK, KAT_C, NAVY, PULAU, PULAU_C, angka, kepala, sumber, tampil, tema)

LQ_TICK = [0.25, 0.5, 1, 2, 4]


@st.cache_data(show_spinner=False)
def bangun_pohon(sek, pulau_sel, root="Indonesia"):
    """ids/parents/values/LQ untuk seluruh pohon (branchvalues='total')."""
    S = sek[sek.pulau.isin(pulau_sel)]
    rows = []
    tot = S.adhb_2024_miliar.sum()
    rows.append((root, "", root, tot, 1.0, "root", ""))
    multi = len(pulau_sel) > 1
    for pl, g in S.groupby("pulau"):
        pid = f"{root}/{pl}" if multi else root
        if multi:
            rows.append((pid, root, pl, g.adhb_2024_miliar.sum(), 1.0, "pulau", pl))
        for pv, gp in g.groupby("provinsi"):
            vid = f"{pid}/{pv}"
            rows.append((vid, pid, pv, gp.adhb_2024_miliar.sum(), 1.0, "provinsi", pl))
            for skt, gs in gp.groupby("sektor"):
                sid = f"{vid}/{skt}"
                rows.append((sid, vid, skt, gs.adhb_2024_miliar.sum(), float(gs.lq_sektor.iloc[0]), "sektor", pl))
                for r in gs[gs.daun_sub].itertuples():
                    rows.append((f"{sid}/{r.subkategori}", sid, r.subkategori, r.adhb_2024_miliar, float(r.lq_sub), "subsektor", pl))
    T = pd.DataFrame(rows, columns=["id", "parent", "label", "nilai", "lq", "tingkat", "pulau"])
    T["pangsa_induk"] = T.nilai / T.parent.map(T.set_index("id").nilai) * 100
    return T


def render(c):
    sek = c["sek"]
    tb = st.container(key="tb_h")
    with tb:
        a, b, d, e = st.columns([1.1, 1.15, 1.3, 2.2], vertical_alignment="center")
        rep = a.segmented_control("Representasi", ["Treemap", "Icicle"], default="Treemap", key="h_rep") or "Treemap"
        warna = b.segmented_control("Warna", ["LQ spesialisasi", "Pulau"], default="LQ spesialisasi", key="h_w") or "LQ spesialisasi"
        provs = (sek[sek.pulau.isin(c["pulau_sel"])].groupby("provinsi").adhb_2024_miliar.sum().sort_values(ascending=False).index.tolist())
        fokus = d.selectbox("Provinsi fokus (sunburst)", provs, key="h_prov",
                            index=provs.index("Kalimantan Timur") if "Kalimantan Timur" in provs else 0)
        e.html("<div class='ks'><b>Cara pakai:</b> klik kotak untuk <b>drill-down</b> (pulau → provinsi → sektor → subsektor); "
               "klik jalur <b>breadcrumb</b> di atas grafik untuk naik kembali. <b>Ukuran</b> = PDRB ADHB 2024; <b>warna</b> = LQ "
               "(&gt;1 = sektor basis/spesialisasi provinsi).</div>")
    root = "Indonesia" if len(c["pulau_sel"]) > 1 else c["pulau_sel"][0]
    T = bangun_pohon(sek, tuple(c["pulau_sel"]), root)
    if warna == "Pulau":
        mk = dict(colors=[PULAU_C.get(p, "#dfe5ee") if t != "root" else "#eef2f7" for p, t in zip(T.pulau, T.tingkat)])
        T_col = None
    else:
        z = np.log2(T.lq.clip(.2, 5))
        mk = dict(colors=z, colorscale=DIV, cmid=0, cmin=-2, cmax=2, showscale=True,
                  colorbar=dict(title=dict(text="LQ", font=dict(size=10.5)), tickvals=np.log2(LQ_TICK),
                                ticktext=[angka(v, 2 if v < 1 else 0) for v in LQ_TICK], thickness=10, len=.55, tickfont=dict(size=10)))
    cd = np.c_[T.nilai / 1000, T.pangsa_induk.fillna(100), T.lq, T.tingkat]
    ht = ("<b>%{label}</b> <span style='color:#7a8799'>(%{customdata[3]})</span><br>PDRB ADHB Rp%{customdata[0]:,.1f} triliun"
          "<br>%{customdata[1]:.1f}% dari induk · %{percentRoot:.1%} dari total<br>LQ %{customdata[2]:.2f}<extra></extra>")
    L, R = st.columns([1.5, 1])
    with L, st.container(key="c_h_tm"):
        kepala(f"Di mana ekonomi {root} berada — dan sektor apa yang menjadi basisnya?",
               "Hierarki 5 tingkat: Indonesia → Pulau → Provinsi → 17 Lapangan Usaha → Subsektor. Kotak terkecil = sektor tiap provinsi.",
               ("HIERARKI", rep.upper(), "DRILL-DOWN + BREADCRUMB"))
        kw = dict(ids=T.id, parents=T.parent, labels=T.label, values=T.nilai, branchvalues="total", maxdepth=4 if len(c["pulau_sel"]) > 1 else 3,
                  marker=dict(line=dict(width=1, color="white"), **mk), customdata=cd, hovertemplate=ht, root_color="#eef2f7",
                  pathbar=dict(visible=True, thickness=22, textfont=dict(size=11)))
        if rep == "Treemap":
            tr = go.Treemap(textinfo="label+percent parent", textfont=dict(size=11.5), tiling=dict(pad=1.5), **kw)
            tr.marker.cornerradius = 3
        else:
            tr = go.Icicle(textinfo="label+percent parent", tiling=dict(orientation="h", pad=1), textfont=dict(size=11.5), **kw)
        fig = go.Figure(tr)
        tema(fig, l=2, r=2, t=4, b=2)
        tampil(fig, f"h_{rep}", cfg={"displayModeBar": False, "scrollZoom": False})
        sumber("Sumber: BPS, PDRB Provinsi-Provinsi di Indonesia menurut Lapangan Usaha 2021–2025 (ADHB 2024), diolah (LQ).")
    F = sek[sek.provinsi == fokus]
    with R:
        with st.container(key="c_h_sb"):
            kepala(f"Struktur sektor {fokus}", "Cincin dalam = 17 lapangan usaha; cincin luar = subsektor. Klik cincin untuk zoom.",
                   ("HIERARKI", "SUNBURST"))
            ids, par, labs, val, col, lq = [fokus], [""], [fokus], [F.adhb_2024_miliar.sum()], ["#eef2f7"], [1.0]
            for skt, gs in F.groupby("sektor"):
                ids.append(f"{fokus}/{skt}"); par.append(fokus); labs.append(skt); val.append(gs.adhb_2024_miliar.sum())
                lq.append(float(gs.lq_sektor.iloc[0])); col.append(KAT_C.get(skt, "#bdbcb7"))
                for r in gs[gs.daun_sub].itertuples():
                    ids.append(f"{fokus}/{skt}/{r.subkategori}"); par.append(f"{fokus}/{skt}"); labs.append(r.subkategori)
                    val.append(r.adhb_2024_miliar); lq.append(float(r.lq_sub)); col.append(KAT_C.get(skt, "#bdbcb7"))
            if warna == "Pulau":
                mk2 = dict(colors=col)
            else:
                mk2 = dict(colors=np.log2(np.clip(lq, .2, 5)), colorscale=DIV, cmid=0, cmin=-2, cmax=2)
            sb = go.Figure(go.Sunburst(ids=ids, parents=par, labels=labs, values=val, branchvalues="total", maxdepth=3,
                                       insidetextorientation="radial", marker=dict(line=dict(width=1, color="white"), **mk2),
                                       customdata=np.c_[np.array(val) / 1000, lq],
                                       hovertemplate="<b>%{label}</b><br>Rp%{customdata[0]:,.1f} triliun · %{percentRoot:.1%} PDRB provinsi"
                                                     "<br>LQ %{customdata[1]:.2f}<extra></extra>"))
            tema(sb, l=2, r=2, t=2, b=2)
            tampil(sb, f"h_sb_{fokus}", cfg={"displayModeBar": False, "scrollZoom": False})
            sumber("Sumber: BPS (2024), diolah. Warna " + ("= 7 sektor terbesar nasional (abu-abu = lainnya)." if warna == "Pulau"
                                                          else "= LQ (biru < 1 < merah)."))
        with st.container(key="t_h_int"):
            kepala("Interpretasi", chips=("INSIGHT",))
            st_ = F.drop_duplicates("sektor").set_index("sektor")
            top_share = st_.pangsa_sektor.nlargest(3)
            basis = st_[st_.lq_sektor > 1].lq_sektor.nlargest(3)
            Sall = sek[sek.pulau.isin(c["pulau_sel"])]
            pul = Sall.groupby("pulau").adhb_2024_miliar.sum()
            share_p = pul / pul.sum() * 100
            st.html(f"""<div class='txt'><p><b>{fokus}</b>: tiga sektor terbesar {', '.join(f'{k} ({angka(v, 1)}%)' for k, v in top_share.items())}.
Sektor basis (LQ &gt; 1): {', '.join(f'<b>{k}</b> (LQ {angka(v, 2)})' for k, v in basis.items()) or '–'}.</p>
<p>{'Secara nasional, <b>' + share_p.idxmax() + '</b> menyumbang ' + angka(share_p.max(), 1) + '% PDRB 38 provinsi.' if len(share_p) > 1 else ''}
LQ menunjukkan spesialisasi relatif: LQ 2 berarti pangsa sektor itu dua kali pangsa nasionalnya.</p></div>""")
