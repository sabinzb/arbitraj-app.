import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import json

# ============================================================
# CONFIG PAGE
# ============================================================
st.set_page_config(
    page_title="ARBMaster // PLATINUM",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS GLOBAL
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:     #04050a;
    --bg2:    #080c14;
    --bg3:    #0a0f1e;
    --border: #12192a;
    --green:  #00e676;
    --green2: #00c853;
    --red:    #ff1744;
    --yellow: #ffd740;
    --orange: #ff6d00;
    --muted:  #3a4560;
    --text:   #c8d8f0;
    --text2:  #6070a0;
}

*, *::before, *::after { box-sizing: border-box; }

.stApp { background: var(--bg); color: var(--text); font-family: 'Syne', sans-serif; }

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

header, footer, #MainMenu { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

.stTextInput input, .stNumberInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    border-radius: 6px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(0,230,118,0.15) !important;
}

.stButton > button {
    background: var(--green) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: var(--green2) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,230,118,0.25) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
}
[data-testid="stMetricLabel"] {
    color: var(--text2) !important;
    font-size: 0.7rem !important;
    font-family: 'Space Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.1rem !important;
}

hr { border-color: var(--border) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: 8px;
    border: 1px solid var(--border);
    gap: 0;
    padding: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    border-radius: 6px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,230,118,0.12) !important;
    color: var(--green) !important;
}

.stAlert {
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
}

.stDownloadButton > button {
    background: transparent !important;
    color: var(--text2) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    width: auto !important;
}
.stDownloadButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green) !important;
    transform: none !important;
    box-shadow: none !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

.arb-card {
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 0.5rem;
}
.arb-card-yes {
    background: rgba(0,230,118,0.025);
    border: 1px solid #00e676;
    box-shadow: 0 0 24px rgba(0,230,118,0.06);
}
.arb-card-no {
    background: #080c14;
    border: 1px solid #12192a;
}
.card-meta {
    font-family: 'Space Mono', monospace;
    color: #3a4560;
    font-size: 0.62rem;
    letter-spacing: 0.04em;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #c8d8f0;
    margin: 0.5rem 0 1rem;
}
.card-footer {
    border-top: 1px solid #12192a;
    padding-top: 0.75rem;
    margin-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #6070a0;
}
.stake-box { border-left: 2px solid; padding-left: 12px; }
.stake-label { font-size: 0.62rem; color: #3a4560; margin: 0; font-family: 'Space Mono', monospace; }
.stake-bk    { font-size: 0.68rem; color: #6070a0; margin: 2px 0; font-family: 'Space Mono', monospace; }
.stake-odd   { font-family: 'Space Mono', monospace; font-size: 1.25rem; margin: 4px 0 2px; color: #fff; font-weight: 700; }
.stake-amt   { font-weight: 700; margin: 0; font-family: 'Space Mono', monospace; font-size: 0.95rem; }
.stake-ret   { color: #3a4560; font-size: 0.62rem; margin: 2px 0 0; font-family: 'Space Mono', monospace; }
.badge-arb {
    background: rgba(0,230,118,0.12);
    color: #00e676;
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid #00e676;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    white-space: nowrap;
}
.badge-no {
    background: rgba(255,109,0,0.08);
    color: #ff6d00;
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid #3a2000;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    white-space: nowrap;
}
.stat-box {
    background: #080c14;
    border: 1px solid #12192a;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}
.stat-label { font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #3a4560; margin: 0; }
.stat-value { font-family: 'Space Mono', monospace; font-size: 1.25rem; margin: 4px 0 0; font-weight: 700; }
.tbl { width:100%; border-collapse:collapse; font-family:'Space Mono',monospace; font-size:0.72rem; }
.tbl th { color:#3a4560; padding:7px 10px; border-bottom:1px solid #12192a; text-align:left; font-weight:400; }
.tbl td { color:#c8d8f0; padding:9px 10px; border-bottom:1px solid #0d1525; }
.tbl tr:hover td { background:rgba(0,230,118,0.02); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
_defaults = {
    'history':         [],
    'scan_results':    [],
    'total_profit':    0.0,
    'total_scans':     0,
    'arb_found_total': 0,
    'registered_bets': [],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ============================================================
# FUNCTII PURE
# ============================================================
def inv_2way(p1: float, p2: float) -> float:
    return 1.0 / p1 + 1.0 / p2

def inv_3way(p1: float, pX: float, p2: float) -> float:
    return 1.0 / p1 + 1.0 / pX + 1.0 / p2

def profit_pct(inv: float) -> float:
    return (1.0 - inv) * 100.0

def optimal_stakes(budget: float, inv: float, odds: list) -> list:
    return [(1.0 / o / inv) * budget for o in odds]

def round5(x: float) -> int:
    return int(round(x / 5.0) * 5)

def fmt_ron(x: float) -> str:
    return f"{x:,.0f} RON"

def profit_color(pct: float) -> str:
    if pct >= 3.0:
        return "#00e676"
    if pct >= 1.5:
        return "#ffd740"
    return "#ff6d00"


SPORTS = {
    "tennis":               ("🎾", "Tennis ATP/WTA"),
    "soccer":               ("⚽", "Fotbal"),
    "basketball":           ("🏀", "Baschet NBA"),
    "americanfootball_nfl": ("🏈", "NFL"),
    "baseball_mlb":         ("⚾", "Baseball MLB"),
    "icehockey_nhl":        ("🏒", "Hockey NHL"),
}


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 0.75rem;border-bottom:1px solid #12192a;margin-bottom:1rem;'>
        <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.62rem;
                  margin:0;letter-spacing:0.12em;'>// PANOU CONTROL</p>
        <h2 style='color:#00e676;font-size:1.35rem;margin:0.3rem 0 0;
                   font-weight:800;letter-spacing:-0.02em;'>ARBMaster ⚡</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;"
        "letter-spacing:0.1em;margin-bottom:4px;'>// AUTENTIFICARE</p>",
        unsafe_allow_html=True
    )
    api_key = st.text_input("ODDS API KEY", type="password", placeholder="Introduceți cheia API")

    st.markdown(
        "<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;"
        "letter-spacing:0.1em;margin:1rem 0 4px;'>// PARAMETRI</p>",
        unsafe_allow_html=True
    )
    sport_key = st.selectbox(
        "SPORT",
        options=list(SPORTS.keys()),
        format_func=lambda k: f"{SPORTS[k][0]}  {SPORTS[k][1]}",
    )
    buget    = st.number_input("CAPITAL (RON)", value=2000, step=100, min_value=100)
    min_prag = st.slider("PROFIT MINIM (%)", 0.1, 5.0, 0.5, 0.1)

    st.markdown(
        "<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;"
        "letter-spacing:0.1em;margin:1rem 0 4px;'>// OPTIUNI</p>",
        unsafe_allow_html=True
    )
    anti_detect = st.toggle("ANTI-DETECTION (rotunjire x5 RON)", value=True)
    show_all    = st.toggle("AFISEAZA TOATE MECIURILE", value=False)

    st.divider()

    tp = st.session_state.total_profit
    tp_color = "#00e676" if tp >= 0 else "#ff1744"
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace;font-size:0.7rem;'>
        <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='color:#3a4560;'>SCANARI</span>
            <span style='color:#c8d8f0;'>{st.session_state.total_scans}</span>
        </div>
        <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='color:#3a4560;'>ARB GASITE</span>
            <span style='color:#00e676;'>{st.session_state.arb_found_total}</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span style='color:#3a4560;'>PROFIT TOTAL</span>
            <span style='color:{tp_color};'>{tp:+.2f} RON</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.registered_bets:
        st.divider()
        if st.button("🗑  RESETEAZA TOT"):
            for k in ('history', 'registered_bets', 'scan_results'):
                st.session_state[k] = []
            st.session_state.total_profit    = 0.0
            st.session_state.total_scans     = 0
            st.session_state.arb_found_total = 0
            st.rerun()


# ============================================================
# HEADER
# ============================================================
col_h, col_s = st.columns([3, 1])
with col_h:
    st.markdown("""
    <div style='padding:1.2rem 0 0.75rem;'>
        <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.62rem;
                  letter-spacing:0.15em;margin:0;'>SPORTS ARBITRAGE ENGINE v4.0</p>
        <h1 style='font-family:Syne,sans-serif;font-weight:800;font-size:2.6rem;
                   background:linear-gradient(130deg,#ffffff 0%,#00e676 55%,#00c853 100%);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   margin:0.2rem 0 0;line-height:1.05;'>
            ARBMaster
            <span style='font-size:1rem;-webkit-text-fill-color:#3a4560;'>PLATINUM</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)

with col_s:
    st.markdown(f"""
    <div style='background:#080c14;border:1px solid #12192a;border-radius:8px;
                padding:0.75rem 1rem;text-align:right;margin-top:1.4rem;'>
        <p style='font-family:Space Mono,monospace;font-size:0.6rem;color:#3a4560;margin:0;'>SISTEM</p>
        <p style='font-family:Space Mono,monospace;font-size:0.72rem;color:#00e676;margin:2px 0;'>● ONLINE</p>
        <p style='font-family:Space Mono,monospace;font-size:0.6rem;color:#6070a0;margin:0;'>
            {datetime.now().strftime("%d.%m.%Y  %H:%M")}
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# METRICI PRINCIPALE
# ============================================================
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.metric("CAPITAL", fmt_ron(buget))
with mc2:
    st.metric("PARIURI INREG.", len(st.session_state.registered_bets))
with mc3:
    st.metric("PROFIT REALIZAT", f"{st.session_state.total_profit:+.2f} RON")
with mc4:
    n_bets = len(st.session_state.registered_bets)
    if n_bets > 0:
        roi_val = st.session_state.total_profit / (buget * n_bets) * 100
        st.metric("ROI MEDIU", f"{roi_val:.2f}%")
    else:
        st.metric("ROI MEDIU", "—")

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
tab_scan, tab_hist, tab_analytics, tab_help = st.tabs([
    "⚡  SCAN LIVE",
    "📋  ISTORIC",
    "📊  ANALYTICS",
    "ℹ️  GHID",
])


# ──────────────────────────────────────────────────────────────
# TAB 1 — SCAN LIVE
# ──────────────────────────────────────────────────────────────
with tab_scan:

    btn_col, info_col = st.columns([2, 3])
    with btn_col:
        sport_icon, sport_label = SPORTS[sport_key]
        run_scan = st.button(f"⚡  RUN SCAN  {sport_icon} {sport_label.upper()}")
    with info_col:
        anti_str   = "ON"  if anti_detect else "OFF"
        anti_color = "#00e676" if anti_detect else "#ff1744"
        st.markdown(f"""
        <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#6070a0;
                    padding:0.55rem 1rem;background:#080c14;border:1px solid #12192a;border-radius:6px;'>
            Capital: <span style='color:#c8d8f0;'>{fmt_ron(buget)}</span>
            &nbsp;|&nbsp;
            Prag: <span style='color:#ffd740;'>{min_prag}%</span>
            &nbsp;|&nbsp;
            Anti-detect: <span style='color:{anti_color};'>{anti_str}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if run_scan:
        if not api_key:
            st.error("LIPSA CHEIE API — introduceti in sidebar")
        else:
            pbar = st.progress(0, text="// INITIALIZARE...")
            time.sleep(0.2)
            pbar.progress(15, text="// CONECTARE LA THE-ODDS-API...")

            try:
                is_soccer = "soccer" in sport_key
                url = (
                    f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
                    f"?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
                )
                resp = requests.get(url, timeout=15)
                pbar.progress(55, text="// PROCESARE DATE...")

                if resp.status_code != 200:
                    pbar.empty()
                    try:
                        msg = resp.json().get("message", "eroare necunoscuta")
                    except Exception:
                        msg = resp.text[:120]
                    st.error(f"EROARE API {resp.status_code}: {msg}")
                    st.stop()

                data      = resp.json()
                remaining = resp.headers.get("x-requests-remaining", "?")
                st.session_state.total_scans += 1

                # ── Procesare jocuri ────────────────────────────
                results = []
                for game in data:
                    h_team = game.get("home_team", "N/A")
                    a_team = game.get("away_team", "N/A")

                    best = {
                        "1": {"p": 0.0, "b": ""},
                        "X": {"p": 0.0, "b": ""},
                        "2": {"p": 0.0, "b": ""},
                    }

                    for bk in game.get("bookmakers", []):
                        for mkt in bk.get("markets", []):
                            if mkt["key"] != "h2h":
                                continue
                            for out in mkt.get("outcomes", []):
                                p    = float(out["price"])
                                name = out["name"]
                                if name == h_team and p > best["1"]["p"]:
                                    best["1"] = {"p": p, "b": bk["title"]}
                                elif name == a_team and p > best["2"]["p"]:
                                    best["2"] = {"p": p, "b": bk["title"]}
                                elif name.lower() == "draw" and p > best["X"]["p"]:
                                    best["X"] = {"p": p, "b": bk["title"]}

                    p1 = best["1"]["p"]
                    p2 = best["2"]["p"]
                    pX = best["X"]["p"]

                    if p1 <= 0 or p2 <= 0:
                        continue

                    use_draw = is_soccer and pX > 0

                    if use_draw:
                        inv  = inv_3way(p1, pX, p2)
                        odds = [p1, pX, p2]
                    else:
                        inv  = inv_2way(p1, p2)
                        odds = [p1, p2]

                    pct    = profit_pct(inv)
                    is_arb = inv < 1.0 and pct >= min_prag

                    stakes_raw = optimal_stakes(buget, inv, odds)
                    if anti_detect:
                        stakes_int = [round5(s) for s in stakes_raw]
                    else:
                        stakes_int = [int(round(s)) for s in stakes_raw]

                    if use_draw:
                        s1, sX, s2 = stakes_int
                    else:
                        s1, s2 = stakes_int
                        sX = 0

                    # Profit garantat — formula corecta
                    net_profit = round(buget / inv - buget, 2)

                    ct         = game.get("commence_time", "")
                    match_time = ct[:16].replace("T", "  ") if ct else "N/A"

                    results.append({
                        "is_arb":      is_arb,
                        "h_team":      h_team,
                        "a_team":      a_team,
                        "sport_title": game.get("sport_title", ""),
                        "match_time":  match_time,
                        "best":        best,
                        "p1":  p1,  "p2":  p2,  "pX": pX,
                        "use_draw":    use_draw,
                        "inv":         inv,
                        "pct":         pct,
                        "s1":  s1,  "s2":  s2,  "sX": sX,
                        "net_profit":  net_profit,
                    })

                pbar.progress(100, text="// SCAN COMPLET")
                time.sleep(0.35)
                pbar.empty()

                arbs = [r for r in results if r["is_arb"]]
                st.session_state.scan_results     = results
                st.session_state.arb_found_total += len(arbs)

                # Status summary
                sc1, sc2, sc3 = st.columns(3)
                arb_border = "rgba(0,230,118,0.35)" if arbs else "#12192a"
                arb_color  = "#00e676"              if arbs else "#ff1744"

                with sc1:
                    st.markdown(f"""
                    <div class='stat-box'>
                        <p class='stat-label'>MECIURI ANALIZATE</p>
                        <p class='stat-value' style='color:#c8d8f0;'>{len(results)}</p>
                    </div>""", unsafe_allow_html=True)
                with sc2:
                    st.markdown(f"""
                    <div class='stat-box' style='border-color:{arb_border};'>
                        <p class='stat-label'>ARBITRAJE GASITE</p>
                        <p class='stat-value' style='color:{arb_color};'>{len(arbs)}</p>
                    </div>""", unsafe_allow_html=True)
                with sc3:
                    st.markdown(f"""
                    <div class='stat-box'>
                        <p class='stat-label'>CERERI API RAMASE</p>
                        <p class='stat-value' style='color:#ffd740;'>{remaining}</p>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

                display = arbs if not show_all else results

                if not display:
                    st.markdown(f"""
                    <div style='text-align:center;padding:3rem;background:#080c14;
                                border:1px dashed #1a2540;border-radius:12px;'>
                        <p style='font-family:Space Mono,monospace;color:#3a4560;
                                  font-size:0.85rem;margin:0;'>
                            SCAN COMPLET — NICIUN ARBITRAJ GASIT
                        </p>
                        <p style='font-family:Space Mono,monospace;color:#1a2540;
                                  font-size:0.7rem;margin:0.5rem 0 0;'>
                            Prag curent {min_prag}% — incearca alt sport sau reduce pragul
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # ──────────────────────────────────────────────────
                # RANDARE CARDURI
                #
                # Fiecare card este randat intr-un st.container()
                # dedicat. Tot HTML-ul unui card (meta, badge, titlu,
                # stake-uri, footer) se afla intr-un SINGUR apel
                # st.markdown(). Butonul de inregistrare vine imediat
                # dupa, in acelasi container.
                #
                # Astfel badge-ul, cotele si butonul corespund
                # intotdeauna aceluiasi meci — nu pot "aluneca".
                # ──────────────────────────────────────────────────
                for idx, r in enumerate(display):
                    with st.container():

                        # Badge — calculat o singura data pentru acest card
                        if r["is_arb"]:
                            badge_html = f"<span class='badge-arb'>+{r['pct']:.2f}% PROFIT</span>"
                        else:
                            badge_html = f"<span class='badge-no'>NO ARB ({r['pct']:.2f}%)</span>"

                        card_css = "arb-card arb-card-yes" if r["is_arb"] else "arb-card arb-card-no"

                        # Construim coloanele de stake pentru acest meci
                        stake_items = []
                        stake_items.append({
                            "label": f"(1) {r['h_team'][:22]}",
                            "bk":    r["best"]["1"]["b"],
                            "odd":   r["p1"],
                            "stake": r["s1"],
                            "color": "#00e676",
                        })
                        if r["use_draw"]:
                            stake_items.append({
                                "label": "(X) EGAL",
                                "bk":    r["best"]["X"]["b"],
                                "odd":   r["pX"],
                                "stake": r["sX"],
                                "color": "#ffd740",
                            })
                        stake_items.append({
                            "label": f"(2) {r['a_team'][:22]}",
                            "bk":    r["best"]["2"]["b"],
                            "odd":   r["p2"],
                            "stake": r["s2"],
                            "color": "#00e676",
                        })

                        grid_css   = " ".join(["1fr"] * len(stake_items))
                        boxes_html = ""
                        for si in stake_items:
                            retur = int(si["stake"] * si["odd"])
                            boxes_html += (
                                f"<div class='stake-box' style='border-color:{si['color']};'>"
                                f"<p class='stake-label'>{si['label']}</p>"
                                f"<p class='stake-bk'>@ {si['bk']}</p>"
                                f"<p class='stake-odd'>@{si['odd']:.2f}</p>"
                                f"<p class='stake-amt' style='color:{si['color']};'>{si['stake']} RON</p>"
                                f"<p class='stake-ret'>= {retur} RON retur</p>"
                                f"</div>"
                            )

                        pcolor_val     = profit_color(r["pct"]) if r["is_arb"] else "#ff6d00"
                        guaranteed_ret = int(buget / r["inv"])

                        # Singurul apel st.markdown() pentru acest card
                        st.markdown(
                            f"<div class='{card_css}'>"
                            f"<div style='display:flex;justify-content:space-between;"
                            f"align-items:flex-start;margin-bottom:0.4rem;'>"
                            f"<span class='card-meta'>{r['sport_title']}  |  {r['match_time']}</span>"
                            f"{badge_html}"
                            f"</div>"
                            f"<p class='card-title'>"
                            f"{r['h_team']} <span style='color:#3a4560;'> vs </span> {r['a_team']}"
                            f"</p>"
                            f"<div style='display:grid;grid-template-columns:{grid_css};gap:18px;"
                            f"margin-bottom:0.25rem;'>"
                            f"{boxes_html}"
                            f"</div>"
                            f"<div class='card-footer'>"
                            f"<span>PROFIT GARANTAT:&nbsp;"
                            f"<span style='color:{pcolor_val};font-weight:700;'>"
                            f"{r['net_profit']:+.2f} RON</span>"
                            f"&nbsp;|&nbsp;RETURN: {guaranteed_ret} RON</span>"
                            f"<span>1/&Sigma; = {r['inv']:.4f}</span>"
                            f"</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                        # Buton de inregistrare — in acelasi container, imediat dupa card
                        if r["is_arb"]:
                            btn_key = f"reg_{idx}_{r['h_team'][:6]}_{r['a_team'][:6]}_{r['p1']}_{r['p2']}"
                            b_col, _ = st.columns([1, 3])
                            with b_col:
                                if st.button(f"INREGISTREAZA #{idx + 1}", key=btn_key):
                                    if r["use_draw"]:
                                        stakes_str = f"{r['s1']} / {r['sX']} / {r['s2']}"
                                        bks_str    = (
                                            f"{r['best']['1']['b']} / "
                                            f"{r['best']['X']['b']} / "
                                            f"{r['best']['2']['b']}"
                                        )
                                    else:
                                        stakes_str = f"{r['s1']} / {r['s2']}"
                                        bks_str    = f"{r['best']['1']['b']} / {r['best']['2']['b']}"

                                    record = {
                                        "id":         len(st.session_state.registered_bets) + 1,
                                        "time":       datetime.now().strftime("%d.%m  %H:%M"),
                                        "match":      f"{r['h_team']} vs {r['a_team']}",
                                        "sport":      r["sport_title"],
                                        "profit_pct": round(r["pct"], 2),
                                        "net_profit": r["net_profit"],
                                        "capital":    buget,
                                        "stakes":     stakes_str,
                                        "bookmakers": bks_str,
                                    }
                                    st.session_state.registered_bets.append(record)
                                    st.session_state.history.append({
                                        "T":     datetime.now().strftime("%H:%M"),
                                        "P":     r["net_profit"],
                                        "Match": f"{r['h_team'][:10]} vs {r['a_team'][:10]}",
                                    })
                                    st.session_state.total_profit += r["net_profit"]
                                    st.success(f"Inregistrat! Profit estimat: +{r['net_profit']:.2f} RON")
                                    time.sleep(0.6)
                                    st.rerun()

                        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

            except requests.exceptions.Timeout:
                pbar.empty()
                st.error("TIMEOUT — serverul nu a raspuns in 15s")
            except requests.exceptions.ConnectionError:
                pbar.empty()
                st.error("EROARE CONEXIUNE — verificati internetul")
            except json.JSONDecodeError:
                pbar.empty()
                st.error("RASPUNS INVALID — cheie API gresita?")
            except Exception as exc:
                pbar.empty()
                st.error(f"EROARE NEASTEPTATA: {exc}")

    elif not st.session_state.scan_results:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
            <p style='font-size:2.5rem;margin:0;'>⚡</p>
            <p style='font-family:Space Mono,monospace;color:#3a4560;
                      font-size:0.82rem;margin:0.75rem 0 0;'>
                SISTEM GATA — configurati si apasati RUN SCAN
            </p>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# TAB 2 — ISTORIC
# ──────────────────────────────────────────────────────────────
with tab_hist:
    bets = st.session_state.registered_bets
    if not bets:
        st.markdown("""
        <div style='text-align:center;padding:3rem;background:#080c14;
                    border:1px dashed #1a2540;border-radius:12px;'>
            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.82rem;'>
                NICIUN PARIU INREGISTRAT
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = pd.DataFrame(bets)

        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.metric("TOTAL PARIURI", len(df))
        with hc2:
            st.metric("PROFIT TOTAL EST.", f"{df['net_profit'].sum():+.2f} RON")
        with hc3:
            st.metric("PROFIT MEDIU", f"{df['net_profit'].mean():+.2f} RON")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        rows_html = ""
        for _, row in df.iterrows():
            pc = "#00e676" if row["net_profit"] >= 0 else "#ff1744"
            rows_html += (
                f"<tr>"
                f"<td style='color:#3a4560;'>#{int(row['id'])}</td>"
                f"<td>{row['time']}</td>"
                f"<td style='color:#c8d8f0;'>{row['match']}</td>"
                f"<td style='color:#6070a0;'>{row['sport']}</td>"
                f"<td>{row['stakes']} RON</td>"
                f"<td style='color:#ffd740;'>+{row['profit_pct']}%</td>"
                f"<td style='color:{pc};font-weight:700;'>{row['net_profit']:+.2f} RON</td>"
                f"</tr>"
            )

        st.markdown(
            f"<table class='tbl'>"
            f"<thead><tr>"
            f"<th>#</th><th>ORA</th><th>MECI</th><th>SPORT</th>"
            f"<th>STAKE-URI</th><th>%</th><th>PROFIT</th>"
            f"</tr></thead>"
            f"<tbody>{rows_html}</tbody>"
            f"</table>",
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "EXPORT CSV",
            data=csv,
            file_name=f"arbmaster_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )


# ──────────────────────────────────────────────────────────────
# TAB 3 — ANALYTICS
# ──────────────────────────────────────────────────────────────
with tab_analytics:
    hist = st.session_state.history
    if not hist:
        st.markdown("""
        <div style='text-align:center;padding:3rem;background:#080c14;
                    border:1px dashed #1a2540;border-radius:12px;'>
            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.82rem;'>
                INREGISTRATI PARIURI PENTRU A VEDEA STATISTICI
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_h          = pd.DataFrame(hist)
        df_h["Cumul"] = df_h["P"].cumsum()
        df_h.index    = range(1, len(df_h) + 1)

        base_layout = dict(
            template="plotly_dark",
            paper_bgcolor="#080c14",
            plot_bgcolor="#04050a",
            margin=dict(l=10, r=10, t=38, b=10),
            height=290,
            showlegend=False,
            xaxis=dict(
                gridcolor="#12192a",
                tickfont=dict(family="Space Mono", size=9),
                title=None
            ),
            yaxis=dict(
                gridcolor="#12192a",
                tickfont=dict(family="Space Mono", size=9),
                title=None
            ),
        )

        gc1, gc2 = st.columns(2)

        with gc1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_h.index,
                y=df_h["Cumul"],
                mode="lines+markers",
                line=dict(color="#00e676", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,230,118,0.07)",
                marker=dict(size=5, color="#00e676"),
            ))
            fig1.update_layout(
                **base_layout,
                title=dict(
                    text="PROFIT CUMULATIV (RON)",
                    font=dict(family="Space Mono", size=10, color="#3a4560")
                ),
            )
            st.plotly_chart(fig1, use_container_width=True)

        with gc2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_h.index,
                y=df_h["P"],
                marker_color=["#00e676" if p >= 0 else "#ff1744" for p in df_h["P"]],
            ))
            fig2.update_layout(
                **base_layout,
                title=dict(
                    text="PROFIT PER PARIU (RON)",
                    font=dict(family="Space Mono", size=10, color="#3a4560")
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)

        profits = df_h["P"]
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1: st.metric("MAX PROFIT",   f"{profits.max():.2f} RON")
        with ac2: st.metric("MIN PROFIT",   f"{profits.min():.2f} RON")
        with ac3: st.metric("RATA SUCCES",  f"{(profits > 0).mean() * 100:.0f}%")
        with ac4: st.metric("DEVIATIE STD", f"{profits.std():.2f} RON")


# ──────────────────────────────────────────────────────────────
# TAB 4 — GHID
# ──────────────────────────────────────────────────────────────
with tab_help:
    st.markdown("""
    <div style='max-width:700px;'>

    <h3 style='font-family:Space Mono,monospace;color:#00e676;
               font-size:0.95rem;margin-top:0;'>
        // CE ESTE ARBITRAJUL SPORTIV?
    </h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.75;'>
        Arbitrajul sportiv (surebetting) consta in a paria simultan pe toate rezultatele
        posibile ale unui eveniment, la case de pariuri diferite, astfel incat suma
        cotelor inverse sa fie subunitara. Rezultatul este un profit garantat matematic,
        indiferent de deznodamant.
    </p>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;
               font-size:0.95rem;margin-top:1.5rem;'>
        // FORMULA MATEMATICA
    </h3>
    <div style='font-family:Space Mono,monospace;color:#c8d8f0;font-size:0.8rem;
                background:#080c14;padding:1.1rem 1.2rem;border-radius:8px;
                border:1px solid #12192a;line-height:1.9;'>
        Sigma = 1/cota1 + 1/cota2 [+ 1/cotaX]<br>
        Daca Sigma &lt; 1.0 &rarr; <span style='color:#00e676;'>ARBITRAJ EXISTENT</span><br>
        Profit (%) = (1 - Sigma) x 100<br>
        Profit (RON) = Capital / Sigma - Capital<br>
        Stake_i = (1/cota_i / Sigma) x Capital
    </div>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;
               font-size:0.95rem;margin-top:1.5rem;'>
        // EXEMPLU CONCRET
    </h3>
    <div style='font-family:Space Mono,monospace;color:#c8d8f0;font-size:0.78rem;
                background:#080c14;padding:1.1rem 1.2rem;border-radius:8px;
                border:1px solid #12192a;line-height:1.9;'>
        Andreeva @2.07 (Pinnacle) | Anisimova @1.99 (Matchbook)<br>
        Sigma = 1/2.07 + 1/1.99 = 0.4831 + 0.5025 =
        <span style='color:#ffd740;'>0.9856</span><br>
        Profit = (1 - 0.9856) x 100 =
        <span style='color:#00e676;'>+1.44%</span><br>
        Capital 2000 RON: Stake A = 980 RON | Stake B = 1020 RON<br>
        Return garantat ~2029 RON &rarr; Profit net:
        <span style='color:#00e676;'>+29 RON</span>
    </div>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;
               font-size:0.95rem;margin-top:1.5rem;'>
        // CONFIGURARE RAPIDA
    </h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.75;'>
        1. Obtineti cheie API gratuita de la
        <span style='color:#c8d8f0;'>the-odds-api.com</span>
        (500 cereri/luna gratuit)<br>
        2. Introduceti cheia in campul din sidebar<br>
        3. Alegeti sportul, capitalul si pragul minim de profit<br>
        4. Apasati RUN SCAN si actionati rapid — cotele se schimba in secunde
    </p>

    <h3 style='font-family:Space Mono,monospace;color:#ff6d00;
               font-size:0.95rem;margin-top:1.5rem;'>
        // RISCURI SI AVERTISMENTE
    </h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.75;'>
        ⚠ Casele de pariuri pot limita sau bloca conturile suspecte de arbitraj<br>
        ⚠ Cotele se modifica rapid — verificati inainte de plasare<br>
        ⚠ Arbitrajele sub 1% pot deveni neprofitabile dupa comisioane<br>
        ⚠ Activati ANTI-DETECTION pentru sume mai putin „rotunde"<br>
        ⚠ Nu investiti capital pe care nu va permiteti sa il pierdeti
    </p>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"<div style='text-align:center;padding:2rem 0 1rem;"
    f"font-family:Space Mono,monospace;font-size:0.62rem;color:#1a2540;"
    f"border-top:1px solid #0d1525;margin-top:2rem;'>"
    f"ARBMaster Platinum v4.0 &nbsp;|&nbsp; Powered by The Odds API &nbsp;|&nbsp;"
    f"Build {datetime.now().strftime('%Y.%m.%d')}"
    f"</div>",
    unsafe_allow_html=True
)
