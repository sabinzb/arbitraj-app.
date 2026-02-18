import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json

# ============================================================
# 1. CONFIG & STILURI
# ============================================================
st.set_page_config(
    page_title="ARBMaster // PLATINUM",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #04050a;
    --bg2:      #080c14;
    --border:   #12192a;
    --green:    #00e676;
    --green2:   #00c853;
    --red:      #ff1744;
    --yellow:   #ffd740;
    --muted:    #3a4560;
    --text:     #c8d8f0;
    --text2:    #6070a0;
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hide Streamlit default header/footer */
header, footer, #MainMenu { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* Input & selectbox */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #0a0f1e !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    border-radius: 6px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(0,230,118,0.15) !important;
}

/* Toggle */
.stToggle label { color: var(--text2) !important; }

/* Buttons */
.stButton > button {
    width: 100%;
    background: var(--green) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--green2) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,230,118,0.3) !important;
}

/* Metric */
[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}
[data-testid="stMetricLabel"] { color: var(--text2) !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Space Mono', monospace !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: 8px;
    border: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,230,118,0.1) !important;
    color: var(--green) !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--green) !important; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--green); }

/* Alerts */
.stAlert { border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. STATE MANAGEMENT
# ============================================================
defaults = {
    'history': [],
    'scan_results': [],
    'total_profit': 0.0,
    'total_scans': 0,
    'arb_found_total': 0,
    'registered_bets': [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# 3. FUNCȚII UTILITARE
# ============================================================
def calc_arbitrage_2way(p1, p2):
    inv = 1/p1 + 1/p2
    return inv, (1 - inv) * 100

def calc_arbitrage_3way(p1, pX, p2):
    inv = 1/p1 + 1/pX + 1/p2
    return inv, (1 - inv) * 100

def split_stakes(budget, inv_sum, p1, p2, pX=None):
    s1 = (1/p1 / inv_sum) * budget
    s2 = (1/p2 / inv_sum) * budget
    sX = (1/pX / inv_sum) * budget if pX else 0
    return s1, s2, sX

def round_to_5(x):
    return round(x / 5) * 5

def format_ron(x):
    return f"{x:,.0f} RON"

def profit_color(pct):
    if pct >= 3: return "#00e676"
    if pct >= 1.5: return "#ffd740"
    return "#ff6d00"

SPORT_ICONS = {
    "tennis": "🎾",
    "soccer": "⚽",
    "basketball": "🏀",
    "americanfootball_nfl": "🏈",
    "baseball_mlb": "⚾",
    "icehockey_nhl": "🏒",
}

SPORT_LABELS = {
    "tennis": "Tennis ATP/WTA",
    "soccer": "Fotbal",
    "basketball": "Baschet NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "Baseball MLB",
    "icehockey_nhl": "Hockey NHL",
}


# ============================================================
# 4. SIDEBAR CONFIG
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem; border-bottom: 1px solid #12192a; margin-bottom: 1rem;'>
        <p style='font-family: Space Mono, monospace; color: #3a4560; font-size: 0.7rem; margin:0; letter-spacing: 0.1em;'>// PANOU CONTROL</p>
        <h2 style='color: #00e676; font-size: 1.4rem; margin: 0.2rem 0 0; font-weight: 800;'>ARBMaster</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color:#3a4560; font-size:0.7rem; font-family: Space Mono, monospace; letter-spacing:0.1em;'>// AUTENTIFICARE</p>", unsafe_allow_html=True)
    api_key = st.text_input("ODDS API KEY", type="password", placeholder="••••••••••••••••••••••••••••••••")

    st.markdown("<p style='color:#3a4560; font-size:0.7rem; font-family: Space Mono, monospace; letter-spacing:0.1em; margin-top:1rem;'>// PARAMETRI</p>", unsafe_allow_html=True)
    
    sport_choice = st.selectbox(
        "SPORT",
        options=list(SPORT_LABELS.keys()),
        format_func=lambda x: f"{SPORT_ICONS.get(x,'')} {SPORT_LABELS[x]}",
        index=0
    )
    
    buget = st.number_input("CAPITAL (RON)", value=2000, step=100, min_value=100)
    
    min_profit = st.slider("PROFIT MINIM (%)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)

    st.markdown("<p style='color:#3a4560; font-size:0.7rem; font-family: Space Mono, monospace; letter-spacing:0.1em; margin-top:1rem;'>// OPȚIUNI</p>", unsafe_allow_html=True)
    
    anti_detect = st.toggle("ANTI-DETECTION (rotunjire la 5)", value=True)
    show_all = st.toggle("ARATĂ TOATE JOCURILE", value=False)

    st.divider()

    # Stats rapide în sidebar
    st.markdown(f"""
    <div style='font-family: Space Mono, monospace; font-size: 0.7rem; color: #3a4560;'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
            <span>SCANĂRI TOTALE</span><span style='color:#c8d8f0;'>{st.session_state.total_scans}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
            <span>ARB GĂSITE</span><span style='color:#00e676;'>{st.session_state.arb_found_total}</span>
        </div>
        <div style='display: flex; justify-content: space-between;'>
            <span>PROFIT TOTAL</span><span style='color:{"#00e676" if st.session_state.total_profit >= 0 else "#ff1744"};'>{st.session_state.total_profit:+.2f} RON</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.divider()
        if st.button("🗑️ RESETEAZĂ ISTORIC"):
            st.session_state.history = []
            st.session_state.total_profit = 0.0
            st.session_state.registered_bets = []
            st.rerun()


# ============================================================
# 5. HEADER PRINCIPAL
# ============================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div style='padding: 1.5rem 0 1rem;'>
        <p style='font-family: Space Mono, monospace; color: #3a4560; font-size: 0.7rem; letter-spacing: 0.15em; margin: 0;'>
            ⚡ SPORTS ARBITRAGE ENGINE v3.0
        </p>
        <h1 style='
            font-family: Syne, sans-serif; font-weight: 800; font-size: 2.8rem;
            background: linear-gradient(135deg, #ffffff 0%, #00e676 60%, #00c853 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 0.2rem 0 0; line-height: 1.1;
        '>ARBMaster<br><span style='font-size: 1.2rem; color: #3a4560; -webkit-text-fill-color: #3a4560;'>PLATINUM EDITION</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
    now = datetime.now().strftime("%d.%m.%Y  %H:%M")
    st.markdown(f"""
    <div style='
        background: #080c14; border: 1px solid #12192a; border-radius: 8px;
        padding: 0.75rem 1rem; text-align: right; margin-top: 1rem;
    '>
        <p style='font-family: Space Mono, monospace; font-size: 0.65rem; color: #3a4560; margin:0;'>SISTEM ACTIV</p>
        <p style='font-family: Space Mono, monospace; font-size: 0.75rem; color: #00e676; margin:0;'>● ONLINE</p>
        <p style='font-family: Space Mono, monospace; font-size: 0.65rem; color: #6070a0; margin:0;'>{now}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 6. METRICI PRINCIPALE
# ============================================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("CAPITAL ACTIV", format_ron(buget))
with m2:
    st.metric("ARB ÎNREGISTRATE", len(st.session_state.registered_bets))
with m3:
    profit_total = st.session_state.total_profit
    st.metric("PROFIT REALIZAT", f"{profit_total:+.2f} RON", delta=None)
with m4:
    roi = (profit_total / (buget * max(len(st.session_state.registered_bets), 1))) * 100
    st.metric("ROI MEDIU", f"{roi:.2f}%" if st.session_state.registered_bets else "N/A")

st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)


# ============================================================
# 7. TABS PRINCIPALE
# ============================================================
tab_scan, tab_history, tab_analytics, tab_help = st.tabs([
    "⚡  SCAN LIVE",
    "📋  ISTORIC PARIURI",
    "📊  ANALYTICS",
    "ℹ️  GHID"
])


# ============================================================
# TAB 1: SCAN ENGINE
# ============================================================
with tab_scan:
    
    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        run_scan = st.button(f"⚡  RUN SCAN — {SPORT_ICONS.get(sport_choice,'')} {SPORT_LABELS[sport_choice].upper()}")
    with col_info:
        st.markdown(f"""
        <div style='
            font-family: Space Mono, monospace; font-size: 0.72rem; color: #6070a0;
            padding: 0.6rem 1rem; background: #080c14; border: 1px solid #12192a; border-radius: 6px;
        '>
            Capital: <span style='color:#c8d8f0;'>{format_ron(buget)}</span> &nbsp;|&nbsp; 
            Profit minim: <span style='color:#ffd740;'>{min_profit}%</span> &nbsp;|&nbsp;
            Anti-detect: <span style='color:{"#00e676" if anti_detect else "#ff1744"};'>{"ON" if anti_detect else "OFF"}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    if run_scan:
        if not api_key:
            st.error("⛔ API KEY LIPSĂ — introduceți cheia în panoul din stânga")
        else:
            progress_bar = st.progress(0, text="// INIȚIALIZARE CONEXIUNE...")
            time.sleep(0.3)
            progress_bar.progress(20, text="// FETCH DATE PIAȚĂ...")

            try:
                is_soccer = ("soccer" in sport_choice)
                url = (
                    f"https://api.the-odds-api.com/v4/sports/{sport_choice}/odds/"
                    f"?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
                )
                response = requests.get(url, timeout=15)
                progress_bar.progress(60, text="// PROCESARE DATE...")

                if response.status_code != 200:
                    progress_bar.empty()
                    err_data = response.json() if response.content else {}
                    st.error(f"⛔ EROARE API {response.status_code}: {err_data.get('message', 'Unknown error')}")
                    st.stop()

                data = response.json()
                remaining = response.headers.get("x-requests-remaining", "?")
                used = response.headers.get("x-requests-used", "?")

                st.session_state.total_scans += 1
                results = []

                for game in data:
                    h_team = game.get('home_team', 'N/A')
                    a_team = game.get('away_team', 'N/A')
                    
                    # Găsire cote maxime per outcome
                    best = {
                        '1': {'p': 0.0, 'b': '', 'b_key': ''},
                        'X': {'p': 0.0, 'b': '', 'b_key': ''},
                        '2': {'p': 0.0, 'b': '', 'b_key': ''},
                    }

                    bookmaker_odds = []  # toate cotele pentru afișare

                    for bk in game.get('bookmakers', []):
                        for mkt in bk.get('markets', []):
                            if mkt['key'] == 'h2h':
                                row = {'bookmaker': bk['title']}
                                for out in mkt.get('outcomes', []):
                                    p, name = out['price'], out['name']
                                    if name == h_team:
                                        row['1'] = p
                                        if p > best['1']['p']:
                                            best['1'] = {'p': p, 'b': bk['title'], 'b_key': bk['key']}
                                    elif name == a_team:
                                        row['2'] = p
                                        if p > best['2']['p']:
                                            best['2'] = {'p': p, 'b': bk['title'], 'b_key': bk['key']}
                                    elif name.lower() == 'draw':
                                        row['X'] = p
                                        if p > best['X']['p']:
                                            best['X'] = {'p': p, 'b': bk['title'], 'b_key': bk['key']}
                                bookmaker_odds.append(row)

                    p1, p2, pX = best['1']['p'], best['2']['p'], best['X']['p']
                    if p1 <= 0 or p2 <= 0:
                        continue

                    use_draw = is_soccer and pX > 0
                    inv_sum, prof_pct = (
                        calc_arbitrage_3way(p1, pX, p2) if use_draw
                        else calc_arbitrage_2way(p1, p2)
                    )

                    is_arb = inv_sum < 1.0 and prof_pct >= min_profit

                    # Calculează stakuri optime
                    s1, s2, sX = split_stakes(buget, inv_sum, p1, p2, pX if use_draw else None)
                    if anti_detect:
                        s1, s2, sX = round_to_5(s1), round_to_5(s2), round_to_5(sX)

                    guaranteed = buget / inv_sum
                    net_profit = guaranteed - buget

                    results.append({
                        'is_arb': is_arb,
                        'game': game,
                        'h_team': h_team,
                        'a_team': a_team,
                        'best': best,
                        'p1': p1, 'p2': p2, 'pX': pX,
                        'use_draw': use_draw,
                        'inv_sum': inv_sum,
                        'prof_pct': prof_pct,
                        's1': s1, 's2': s2, 'sX': sX,
                        'net_profit': net_profit,
                        'bookmaker_odds': bookmaker_odds,
                    })

                progress_bar.progress(100, text="// SCAN COMPLET ✓")
                time.sleep(0.4)
                progress_bar.empty()

                # Actualizează state
                arbs = [r for r in results if r['is_arb']]
                st.session_state.scan_results = results
                st.session_state.arb_found_total += len(arbs)

                # Status bar
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.markdown(f"""
                    <div style='background:#080c14;border:1px solid #12192a;border-radius:8px;padding:0.75rem 1rem;'>
                        <p style='font-family:Space Mono,monospace;font-size:0.65rem;color:#3a4560;margin:0;'>JOCURI ANALIZATE</p>
                        <p style='font-family:Space Mono,monospace;font-size:1.3rem;color:#c8d8f0;margin:0;font-weight:700;'>{len(results)}</p>
                    </div>""", unsafe_allow_html=True)
                with col_s2:
                    arb_color = "#00e676" if arbs else "#ff1744"
                    st.markdown(f"""
                    <div style='background:#080c14;border:1px solid {"rgba(0,230,118,0.3)" if arbs else "#12192a"};border-radius:8px;padding:0.75rem 1rem;'>
                        <p style='font-family:Space Mono,monospace;font-size:0.65rem;color:#3a4560;margin:0;'>ARBITRAJE GĂSITE</p>
                        <p style='font-family:Space Mono,monospace;font-size:1.3rem;color:{arb_color};margin:0;font-weight:700;'>{len(arbs)}</p>
                    </div>""", unsafe_allow_html=True)
                with col_s3:
                    st.markdown(f"""
                    <div style='background:#080c14;border:1px solid #12192a;border-radius:8px;padding:0.75rem 1rem;'>
                        <p style='font-family:Space Mono,monospace;font-size:0.65rem;color:#3a4560;margin:0;'>CERERI API RĂMASE</p>
                        <p style='font-family:Space Mono,monospace;font-size:1.3rem;color:#ffd740;margin:0;font-weight:700;'>{remaining}</p>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

                display_results = arbs if not show_all else results
                if not display_results:
                    if show_all and results:
                        display_results = results
                    else:
                        st.markdown("""
                        <div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'>
                            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.9rem;'>
                                // SCAN COMPLET<br><br>
                                <span style='color:#6070a0;font-size:0.75rem;'>Nu s-au găsit arbitraje peste pragul de {min_profit}%<br>
                                Încearcă alt sport sau reduce pragul minim de profit.</span>
                            </p>
                        </div>
                        """.replace("{min_profit}", str(min_profit)), unsafe_allow_html=True)

                for idx, r in enumerate(display_results):
                    is_arb = r['is_arb']
                    card_border = "#00e676" if is_arb else "#1a2540"
                    card_bg = "rgba(0,230,118,0.03)" if is_arb else "#080c14"
                    badge_html = f"""<span style='
                        font-family:Space Mono,monospace; font-size:0.7rem;
                        background:rgba(0,230,118,0.1); color:#00e676;
                        padding:3px 10px; border-radius:4px; border:1px solid #00e676; font-weight:700;
                    '>+{r["prof_pct"]:.2f}% PROFIT</span>""" if is_arb else f"""<span style='
                        font-family:Space Mono,monospace; font-size:0.7rem;
                        background:rgba(255,23,68,0.08); color:#ff6d00;
                        padding:3px 10px; border-radius:4px; border:1px solid #3a1a00;
                    '>FĂRĂ ARB ({100*(1-r["inv_sum"]):.2f}%)</span>"""

                    # Construiește coloanele de pariuri
                    stake_cols = []
                    stake_cols.append({
                        'label': f'(1) {r["h_team"][:18]}',
                        'bk': r['best']['1']['b'],
                        'odd': r['p1'],
                        'stake': r['s1'],
                        'color': '#00e676'
                    })
                    if r['use_draw']:
                        stake_cols.append({
                            'label': '(X) Egal',
                            'bk': r['best']['X']['b'],
                            'odd': r['pX'],
                            'stake': r['sX'],
                            'color': '#ffd740'
                        })
                    stake_cols.append({
                        'label': f'(2) {r["a_team"][:18]}',
                        'bk': r['best']['2']['b'],
                        'odd': r['p2'],
                        'stake': r['s2'],
                        'color': '#00e676'
                    })

                    grid_cols = " ".join(["1fr"] * len(stake_cols))
                    boxes_html = ""
                    for sc in stake_cols:
                        boxes_html += f"""
                        <div style='border-left:2px solid {sc["color"]};padding-left:12px;'>
                            <p style='font-size:0.65rem;color:#3a4560;margin:0;font-family:Space Mono,monospace;'>{sc["label"]}</p>
                            <p style='font-size:0.7rem;color:#6070a0;margin:0;font-family:Space Mono,monospace;'>@ {sc["bk"]}</p>
                            <p style='font-family:Space Mono,monospace;font-size:1.3rem;margin:4px 0;color:#fff;'>@{sc["odd"]:.2f}</p>
                            <p style='color:{sc["color"]};font-weight:700;margin:0;font-family:Space Mono,monospace;'>{int(sc["stake"])} RON</p>
                            <p style='color:#3a4560;font-size:0.65rem;margin:0;'>= {int(sc["stake"] * sc["odd"])} RON retur</p>
                        </div>"""

                    match_time = r['game'].get('commence_time', '')[:16].replace('T', ' ') if r['game'].get('commence_time') else 'N/A'

                    st.markdown(f"""
                    <div style='
                        background:{card_bg};border:1px solid {card_border};border-radius:12px;
                        padding:1.5rem;margin-bottom:1rem;
                        box-shadow:{"0 0 20px rgba(0,230,118,0.05)" if is_arb else "none"};
                    '>
                        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;'>
                            <div>
                                <span style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.65rem;'>
                                    {r["game"].get("sport_title","")}&nbsp;&nbsp;|&nbsp;&nbsp;{match_time}
                                </span>
                            </div>
                            {badge_html}
                        </div>
                        <h3 style='
                            font-family:Syne,sans-serif;font-weight:700;font-size:1.15rem;
                            color:#c8d8f0;margin:0 0 1rem;
                        '>{r["h_team"]} <span style='color:#3a4560;'>vs</span> {r["a_team"]}</h3>
                        <div style='display:grid;grid-template-columns:{grid_cols};gap:20px;margin-bottom:1rem;'>
                            {boxes_html}
                        </div>
                        <div style='
                            border-top:1px solid #12192a;padding-top:0.75rem;
                            display:flex;justify-content:space-between;align-items:center;
                        '>
                            <span style='font-family:Space Mono,monospace;font-size:0.7rem;color:#6070a0;'>
                                PROFIT GARANTAT: 
                                <span style='color:{"#00e676" if is_arb else "#ff6d00"};font-weight:700;'>
                                    {r["net_profit"]:+.2f} RON
                                </span>
                                &nbsp;|&nbsp; RETURN: {int(buget / r["inv_sum"])} RON
                            </span>
                            <span style='font-family:Space Mono,monospace;font-size:0.65rem;color:#3a4560;'>
                                1/Σ = {r["inv_sum"]:.4f}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Buton înregistrare — stocat în pending și procesat după render
                    if is_arb:
                        btn_key = f"reg_{idx}_{r['h_team'][:5]}_{r['a_team'][:5]}"
                        if st.button(f"✓ ÎNREGISTREAZĂ PARIU #{idx+1}", key=btn_key):
                            bet_record = {
                                "id": len(st.session_state.registered_bets) + 1,
                                "time": datetime.now().strftime("%d.%m %H:%M"),
                                "match": f"{r['h_team']} vs {r['a_team']}",
                                "sport": r['game'].get('sport_title', ''),
                                "profit_pct": round(r['prof_pct'], 2),
                                "net_profit": round(r['net_profit'], 2),
                                "capital": buget,
                                "stakes": f"{int(r['s1'])} / {int(r['s2'])}" + (f" / {int(r['sX'])}" if r['use_draw'] else ""),
                                "bookmakers": f"{r['best']['1']['b']} / {r['best']['2']['b']}",
                            }
                            st.session_state.registered_bets.append(bet_record)
                            st.session_state.history.append({
                                "T": datetime.now().strftime("%H:%M"),
                                "P": round(r['net_profit'], 2),
                                "Match": f"{r['h_team'][:8]} vs {r['a_team'][:8]}",
                            })
                            st.session_state.total_profit += round(r['net_profit'], 2)
                            st.success(f"✅ Pariu înregistrat! Profit estimat: +{r['net_profit']:.2f} RON")
                            time.sleep(0.8)
                            st.rerun()

            except requests.exceptions.Timeout:
                progress_bar.empty()
                st.error("⛔ TIMEOUT — serverul nu a răspuns în 15 secunde")
            except requests.exceptions.ConnectionError:
                progress_bar.empty()
                st.error("⛔ EROARE CONEXIUNE — verificați internetul")
            except json.JSONDecodeError:
                progress_bar.empty()
                st.error("⛔ RĂSPUNS INVALID de la API — posibil cheie greșită")
            except Exception as e:
                progress_bar.empty()
                st.error(f"⛔ EROARE NEAȘTEPTATĂ: {str(e)}")

    elif not st.session_state.scan_results:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
            <p style='font-family:Space Mono,monospace;font-size:3rem;margin:0;'>⚡</p>
            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.85rem;margin:0.5rem 0;'>
                SISTEM GATA DE SCANARE
            </p>
            <p style='font-family:Space Mono,monospace;color:#1a2540;font-size:0.7rem;'>
                Configurați parametrii din stânga și apăsați RUN SCAN
            </p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 2: ISTORIC PARIURI
# ============================================================
with tab_history:
    if not st.session_state.registered_bets:
        st.markdown("""
        <div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'>
            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.85rem;'>
                // NICIUN PARIU ÎNREGISTRAT ÎNCĂ
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_bets = pd.DataFrame(st.session_state.registered_bets)
        
        # Summary cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("TOTAL PARIURI", len(df_bets))
        with c2:
            st.metric("PROFIT TOTAL ESTIMAT", f"{df_bets['net_profit'].sum():+.2f} RON")
        with c3:
            st.metric("PROFIT MEDIU / PARIU", f"{df_bets['net_profit'].mean():.2f} RON")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Tabel stilizat
        st.markdown("""
        <style>
        .bet-table { width:100%; border-collapse:collapse; font-family:Space Mono,monospace; font-size:0.75rem; }
        .bet-table th { color:#3a4560; padding:8px 12px; border-bottom:1px solid #12192a; text-align:left; font-weight:400; }
        .bet-table td { color:#c8d8f0; padding:10px 12px; border-bottom:1px solid #0d1525; }
        .bet-table tr:hover td { background:rgba(0,230,118,0.02); }
        </style>
        """, unsafe_allow_html=True)

        rows_html = ""
        for _, row in df_bets.iterrows():
            profit_color_val = "#00e676" if row['net_profit'] > 0 else "#ff1744"
            rows_html += f"""
            <tr>
                <td style='color:#3a4560;'>#{int(row['id'])}</td>
                <td>{row['time']}</td>
                <td>{row['match']}</td>
                <td style='color:#6070a0;'>{row['sport']}</td>
                <td>{row['stakes']} RON</td>
                <td style='color:#ffd740;'>+{row['profit_pct']}%</td>
                <td style='color:{profit_color_val};font-weight:700;'>{row['net_profit']:+.2f} RON</td>
            </tr>"""

        st.markdown(f"""
        <table class='bet-table'>
            <thead><tr>
                <th>#</th><th>ORA</th><th>MECI</th><th>SPORT</th><th>STAKE-URI</th><th>%</th><th>PROFIT</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Export CSV
        csv_data = df_bets.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ EXPORT CSV",
            data=csv_data,
            file_name=f"arbmaster_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )


# ============================================================
# TAB 3: ANALYTICS
# ============================================================
with tab_analytics:
    if not st.session_state.history:
        st.markdown("""
        <div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'>
            <p style='font-family:Space Mono,monospace;color:#3a4560;'>
                // NICIUN DATE DE AFIȘAT — înregistrați pariuri pentru statistici
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_h = pd.DataFrame(st.session_state.history)
        df_h['Cumul'] = df_h['P'].cumsum()
        df_h.index = range(1, len(df_h) + 1)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_h.index, y=df_h['Cumul'],
                mode='lines+markers',
                line=dict(color='#00e676', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,230,118,0.07)',
                marker=dict(size=6, color='#00e676'),
                name='Profit cumulativ'
            ))
            fig1.update_layout(
                template='plotly_dark', paper_bgcolor='#080c14', plot_bgcolor='#04050a',
                title=dict(text='PROFIT CUMULATIV (RON)', font=dict(family='Space Mono', size=11, color='#6070a0')),
                xaxis=dict(gridcolor='#12192a', tickfont=dict(family='Space Mono', size=9)),
                yaxis=dict(gridcolor='#12192a', tickfont=dict(family='Space Mono', size=9)),
                margin=dict(l=10, r=10, t=40, b=10), height=300,
                showlegend=False,
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            fig2 = go.Figure()
            colors = ['#00e676' if p >= 0 else '#ff1744' for p in df_h['P']]
            fig2.add_trace(go.Bar(
                x=df_h.index, y=df_h['P'],
                marker_color=colors,
                name='Profit per pariu'
            ))
            fig2.update_layout(
                template='plotly_dark', paper_bgcolor='#080c14', plot_bgcolor='#04050a',
                title=dict(text='PROFIT PER PARIU (RON)', font=dict(family='Space Mono', size=11, color='#6070a0')),
                xaxis=dict(gridcolor='#12192a', tickfont=dict(family='Space Mono', size=9)),
                yaxis=dict(gridcolor='#12192a', tickfont=dict(family='Space Mono', size=9)),
                margin=dict(l=10, r=10, t=40, b=10), height=300,
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Statistici avansate
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        profits = df_h['P']
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("MAX PROFIT SINGLE", f"{profits.max():.2f} RON")
        with c2: st.metric("MIN PROFIT SINGLE", f"{profits.min():.2f} RON")
        with c3: st.metric("RATA SUCCES", f"{(profits > 0).mean()*100:.0f}%")
        with c4: st.metric("DEVIAȚIE STD", f"{profits.std():.2f} RON")


# ============================================================
# TAB 4: GHID
# ============================================================
with tab_help:
    st.markdown("""
    <div style='max-width: 700px;'>
    
    <h3 style='font-family:Space Mono,monospace;color:#00e676;font-size:1rem;'>// CE ESTE ARBITRAJUL SPORTIV?</h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.7;'>
    Arbitrajul sportiv (surebetting) constă în a paria pe toate rezultatele posibile ale unui eveniment,
    la case de pariuri diferite, astfel încât suma cotelor inverse să fie sub 1. Rezultatul este un
    profit garantat indiferent de deznodământ.
    </p>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;font-size:1rem;margin-top:1.5rem;'>// FORMULA</h3>
    <p style='font-family:Space Mono,monospace;color:#c8d8f0;font-size:0.8rem;background:#080c14;padding:1rem;border-radius:8px;border:1px solid #12192a;'>
    &Sigma; = 1/cotă1 + 1/cotă2 [+ 1/cotăX]<br><br>
    Dacă &Sigma; &lt; 1.0 → ARBITRAJ EXISTENT<br>
    Profit (%) = (1 - &Sigma;) × 100<br>
    Stake optim i = (1/cotăi / &Sigma;) × capital_total
    </p>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;font-size:1rem;margin-top:1.5rem;'>// CONFIGURARE</h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.7;'>
    1. Obțineți o cheie API gratuită de la <strong style='color:#c8d8f0;'>the-odds-api.com</strong> (500 cereri/lună gratis)<br>
    2. Introduceți cheia în câmpul ACCESS_TOKEN din sidebar<br>
    3. Alegeți sportul, capitalul și pragul minim de profit<br>
    4. Apăsați RUN SCAN și așteptați rezultatele
    </p>

    <h3 style='font-family:Space Mono,monospace;color:#ff6d00;font-size:1rem;margin-top:1.5rem;'>// ATENȚIE</h3>
    <p style='color:#6070a0;font-size:0.85rem;line-height:1.7;'>
    ⚠️ Casele de pariuri pot limita/bloca conturile care practică arbitraj.<br>
    ⚠️ Cotele se pot modifica rapid — acționați imediat după identificare.<br>
    ⚠️ Arbitrajele sub 1% profit pot deveni neprofitabile din cauza taxelor.<br>
    ⚠️ Folosiți funcția ANTI-DETECTION pentru sume mai puțin "rotunde".
    </p>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div style='
    text-align:center; padding:2rem 0 1rem;
    font-family:Space Mono,monospace; font-size:0.65rem; color:#1a2540;
    border-top:1px solid #0d1525; margin-top:2rem;
'>
    ARBMaster Platinum v3.0 &nbsp;|&nbsp; Powered by The Odds API &nbsp;|&nbsp;
    Build {datetime.now().strftime("%Y.%m.%d")}
</div>
""", unsafe_allow_html=True)
