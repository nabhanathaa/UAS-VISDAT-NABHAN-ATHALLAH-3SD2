# -*- coding: utf-8 -*-
"""Gaya visual (CSS) dashboard: tema biru–putih elegan, kartu, header navy-emas, tinggi kartu mengikuti layar."""
import streamlit as st

from .core import FONT, GOLD, GRID, INK, INK2, LINE, MUTED, NAVY, ROYAL

HDR = 122   # tinggi header (px)

# tinggi kartu (desktop). B = tinggi area isi di bawah header; semua kartu satu tab ≤ B → tanpa gulir halaman
TINGGI = {
    # Ringkasan
    "c_r_map": "calc(var(--B) - 104px)", "t_r_story": "calc((var(--B) - 104px) * .60 - 5px)",
    "c_r_bar": "calc((var(--B) - 104px) * .40 - 5px)",
    # Peta
    "c_p_map": "var(--B)", "t_p_ctrl": "226px", "t_p_int": "164px", "c_p_side": "calc(var(--B) - 226px - 164px - 20px)",
    # Cahaya vs ekonomi
    "c_g_sc": "var(--B)", "c_g_res": "calc((var(--B) - 104px) * .60 - 5px)", "t_g_int": "calc((var(--B) - 104px) * .40 - 5px)",
    # Multivariat
    "c_m_bi": "calc(var(--B) * .64 - 5px)", "t_m_int": "calc(var(--B) * .36 - 5px)",
    "c_m_pc": "calc(var(--B) * .47 - 5px)", "c_m_hm": "calc(var(--B) * .53 - 5px)", "c_m_map": "calc(var(--B) * .53 - 5px)",
    # Hierarki
    "tb_h": "64px", "c_h_tm": "calc(var(--B) - 74px)", "c_h_sb": "calc((var(--B) - 74px) * .64 - 5px)",
    "t_h_int": "calc((var(--B) - 74px) * .36 - 5px)",
    # Aliran
    "tb_a": "64px", "c_a_sk": "calc(var(--B) - 74px)", "c_a_map": "calc((var(--B) - 74px) * .66 - 5px)",
    "t_a_int": "calc((var(--B) - 74px) * .34 - 5px)",
    # Metodologi
    "t_x_src": "var(--B)", "t_x_enc": "var(--B)", "t_x_met": "var(--B)",
}


def pasang_css():
    tinggi = "\n".join(f"  .st-key-{k} {{height:{v} !important;}}" for k, v in TINGGI.items())
    st.html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {{ --B: max(560px, calc(100vh - {HDR}px - 34px)); }}
html, body, .stApp, button, input, textarea, select {{ font-family: {FONT}; }}
.stApp {{ background: radial-gradient(1100px 520px at 0% 0%, #dde9f8 0%, rgba(221,233,248,0) 62%),
                      radial-gradient(900px 500px at 100% 100%, #e4ecf8 0%, rgba(228,236,248,0) 60%),
                      linear-gradient(180deg, #eef3fa 0%, #f5f8fc 100%); }}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebarCollapsedControl"], footer, #MainMenu {{ display: none !important; }}
[data-testid="stMainBlockContainer"] {{ padding: 10px 16px 6px !important; max-width: 100% !important; }}
[data-testid="stVerticalBlock"] {{ gap: 10px; }}
[data-testid="stHorizontalBlock"] {{ gap: 10px; }}
[data-testid="stElementContainer"]:has(> .stHtml > style), [data-testid="stElementContainer"]:has(style:only-child) {{ display:none; }}

/* ---------- header ---------- */
.st-key-hdr {{ height:{HDR}px; flex:none !important; position:relative; overflow:hidden; gap:6px;
  background: linear-gradient(118deg, #071a33 0%, #0d2d55 48%, #164a86 100%);
  border-radius: 16px; padding: 10px 18px 8px; box-shadow: 0 10px 28px rgba(7,26,51,.28); }}
.st-key-hdr::before {{ content:""; position:absolute; right:-80px; top:-120px; width:420px; height:420px; border-radius:50%;
  background: radial-gradient(circle, rgba(242,181,68,.16) 0%, rgba(242,181,68,0) 62%); pointer-events:none; }}
.st-key-hdr::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px;
  background: linear-gradient(90deg, {GOLD} 0%, #f9dc9b 35%, rgba(242,181,68,0) 85%); }}
.brand {{ display:flex; align-items:center; gap:14px; }}
.brand img {{ width:54px; height:54px; border-radius:50%; box-shadow: 0 0 0 3px rgba(255,255,255,.14), 0 4px 14px rgba(0,0,0,.35); }}
.brand .eyebrow {{ color:{GOLD}; font-size:.68rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
.brand .ttl {{ color:#fff; font-size:1.42rem; font-weight:800; letter-spacing:-.015em; line-height:1.12; }}
.brand .ttl span {{ color:{GOLD}; }}
.brand .sub {{ color:#b9cde6; font-size:.78rem; margin-top:1px; }}
.ident {{ text-align:right; line-height:1.3; }}
.ident .nm {{ color:#fff; font-weight:700; font-size:.9rem; }}
.ident .nim {{ color:#cfe0f5; font-size:.76rem; letter-spacing:.02em; }}
.ident .kp {{ color:{GOLD}; font-size:.72rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
.st-key-hdr [data-testid="stButtonGroup"] button {{ background: rgba(255,255,255,.06); color:#d7e5f6; border-color: rgba(255,255,255,.16);
  font-weight:600; min-height:34px; padding: 2px 14px; }}
.st-key-hdr [data-testid="stButtonGroup"] button:hover {{ background: rgba(255,255,255,.14); color:#fff; border-color: rgba(255,255,255,.3); }}
.st-key-hdr [data-testid="stButtonGroup"] button[aria-checked="true"] {{
  background: linear-gradient(180deg, #ffffff 0%, #eef4fc 100%) !important; color:{NAVY} !important; border-color:#ffffff !important;
  box-shadow: 0 2px 10px rgba(0,0,0,.25); }}
.st-key-hdr [data-testid="stButtonGroup"] button[aria-checked="true"] * {{ color:{NAVY} !important; }}
.st-key-hdr [data-testid="stButtonGroup"] p {{ font-size:.84rem; }}
.st-key-hdr [data-baseweb="select"] > div {{ background: rgba(255,255,255,.95); border-color: rgba(255,255,255,.6); min-height:34px; }}
.st-key-hdr [data-testid="stWidgetLabel"] {{ display:none; }}

/* ---------- kartu ---------- */
[class*="st-key-c_"], [class*="st-key-t_"], [class*="st-key-tb_"] {{
  flex:none !important; background:#fff; border:1px solid {LINE}; border-radius:14px; padding: 10px 14px 6px;
  box-shadow: 0 1px 2px rgba(15,42,74,.05), 0 10px 24px rgba(15,42,74,.06); overflow:hidden; gap:4px; }}
[class*="st-key-t_"] {{ overflow:auto; padding: 11px 15px 10px; }}
[class*="st-key-tb_"] {{ padding: 8px 14px; justify-content:center; }}
{tinggi}
[class*="st-key-c_"] > [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {{ flex:1 1 0 !important; min-height:0 !important; height:auto !important; }}
[class*="st-key-c_"] [data-testid="stPlotlyChart"], [class*="st-key-c_"] [data-testid="stPlotlyChart"] > div {{ height:100% !important; }}
.kh {{ display:flex; align-items:center; justify-content:space-between; gap:8px; }}
.kt {{ color:{INK}; font-weight:750; font-size:.95rem; letter-spacing:-.005em; line-height:1.25; }}
.ks {{ color:{INK2}; font-size:.76rem; line-height:1.35; margin-top:1px; }}
.chips {{ display:flex; gap:4px; flex-wrap:wrap; justify-content:flex-end; }}
.chip {{ font-size:.64rem; font-weight:700; letter-spacing:.03em; color:{ROYAL}; background:#eaf2fd; border:1px solid #d3e3f8;
  padding:1px 7px; border-radius:999px; white-space:nowrap; }}
.src {{ color:{MUTED}; font-size:.66rem; line-height:1.25; }}
.lbl {{ color:{INK2}; font-size:.7rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; margin-bottom:2px; }}
.txt, .txt p, .txt li, .txt span, .txt div {{ color:{INK}; font-size:.84rem; line-height:1.52; }}
.txt p {{ margin:.1rem 0 .35rem; }} .txt ul {{ margin:.1rem 0 .3rem; padding-left:1.05rem; }} .txt li {{ margin:.12rem 0; }}
.txt b {{ color:{NAVY}; }}
.ins {{ display:flex; gap:10px; align-items:flex-start; padding:7px 0; border-bottom:1px dashed {GRID}; }}
.ins:last-child {{ border-bottom:none; }}
.ins .no {{ flex:none; width:22px; height:22px; border-radius:50%; background:{NAVY}; color:{GOLD}; font-weight:800; font-size:.72rem;
  display:flex; align-items:center; justify-content:center; margin-top:1px; }}
.pill {{ display:inline-block; padding:1px 8px; border-radius:999px; font-size:.68rem; font-weight:700; color:#fff; }}
.tbl {{ width:100%; border-collapse:collapse; font-size:.74rem; }}
.tbl th {{ text-align:left; color:{INK2}; font-weight:700; border-bottom:2px solid {LINE}; padding:4px 6px; position:sticky; top:0; background:#fff; }}
.tbl td {{ border-bottom:1px solid {GRID}; padding:4px 6px; vertical-align:top; color:{INK}; }}
.tbl a {{ color:{ROYAL}; text-decoration:none; }}
.st-key-c_p_side {{ overflow:auto !important; }}
.tblc td, .tblc th {{ padding:2px 5px; font-size:.7rem; }}
.bar {{ height:6px; background:{GRID}; border-radius:6px; overflow:hidden; }} .bar > i {{ display:block; height:100%; background:{ROYAL}; border-radius:6px; }}

/* ---------- KPI ---------- */
.kpis {{ display:grid; gap:10px; }}
.kpi {{ position:relative; background:#fff; border:1px solid {LINE}; border-radius:14px; padding:10px 14px 9px 17px; height:94px;
  box-shadow: 0 1px 2px rgba(15,42,74,.05), 0 10px 24px rgba(15,42,74,.06); overflow:hidden; }}
.kpi::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background: var(--ac); }}
.kpi .kl {{ color:{INK2}; font-size:.68rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.leg {{ display:flex; flex-wrap:wrap; gap:4px 12px; font-size:.72rem; color:{INK}; margin:2px 0 0; }}
.leg i {{ display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:5px; vertical-align:-1px; }}
.kpi .kv {{ color:{NAVY}; font-size:1.65rem; font-weight:800; line-height:1.15; letter-spacing:-.02em; margin-top:2px; }}
.kpi .kd {{ color:{MUTED}; font-size:.7rem; line-height:1.25; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

/* ---------- widget ---------- */
[data-testid="stDownloadButton"] button {{ background: linear-gradient(135deg, {ROYAL} 0%, #0d3b78 100%) !important; color:#fff !important;
  border:none !important; font-weight:700; min-height:40px; box-shadow: 0 6px 16px rgba(29,95,174,.35); border-radius:10px; }}
[data-testid="stDownloadButton"] button * {{ color:#fff !important; }}
[data-testid="stDownloadButton"] button:hover {{ filter: brightness(1.1); box-shadow: 0 8px 20px rgba(29,95,174,.45); }}
[data-testid="stWidgetLabel"] p {{ font-size:.72rem !important; color:{INK2}; font-weight:600; }}
[data-testid="stButtonGroup"] p {{ font-size:.8rem; }}
.stSelectbox, .stMultiSelect {{ margin-bottom:-2px; }}
div[data-baseweb="select"] > div {{ min-height:34px; }}
[data-testid="stPlotlyChart"] {{ border-radius:10px; }}
.modebar-container {{ opacity:.0; transition: opacity .2s; }} .js-plotly-plot:hover .modebar-container {{ opacity:1; }}

/* ---------- responsif ponsel & layar pendek ---------- */
@media (max-width: 900px) {{
  :root {{ --B: 620px; }}
  .st-key-hdr {{ height:auto; }}
  .brand .ttl {{ font-size:1.12rem; }} .ident {{ text-align:left; }}
  [class*="st-key-c_"] {{ height: 430px !important; }}
  [class*="st-key-t_"], [class*="st-key-tb_"] {{ height:auto !important; max-height:none; }}
  .kpis {{ grid-template-columns: repeat(2, 1fr) !important; }}
  .st-key-hdr [data-testid="stButtonGroup"] > div {{ flex-wrap: wrap; }}
}}
</style>""")
