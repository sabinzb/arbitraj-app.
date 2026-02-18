import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare Sistem Ultra-Wide
st.set_page_config(page_title="ARBMaster Platinum", layout="wide", page_icon="⚡")

# 2. Design UI Neo-Terminal (CSS injection verificat)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700;900&display=swap');

    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #1a1a1a; }
    
    .terminal-header {
        font-family: 'JetBrains Mono', monospace; font-weight: 900; color: #ffffff;
        font-size: 3.2rem; letter-spacing: -2px;
        background: linear-gradient(90deg, #fff, #00ff88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .arb-card {
        background: #0d0d0d; border: 1px solid #1f1f1f;
        border-radius: 12px; padding: 2rem; margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .arb-card:hover { border-color: #00ff88; background: #111111; }

    .profit-tag {
        font-family: 'JetBrains Mono', monospace; background: rgba(0, 255, 136, 0.1);
        color: #00ff88; padding: 6px 14px; border-radius: 6px;
        font-size: 0.9rem; font-weight: 700; border: 1px solid rgba(0, 255, 136, 0.3);
    }

    .stButton>button {
        width: 100%; background: #00ff88 !important; color: #000 !important;
        font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important;
        border-radius: 4px !important; border: none !important; padding: 1rem !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Control
with st.sidebar:
    st.markdown("<h2 style='color: #444; font-family: \"JetBrains Mono\"; font-size: 0.8rem;'># SYSTEM_CONFIG</h2>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS_TOKEN", type="password", placeholder="Introdu cheia API...")
    buget = st.number_input("TOTAL_CAPITAL (RON)", value=2000, step=500)
    sport_choice = st.selectbox("TARGET_MARKET", ["soccer", "tennis"])
    st.divider()
    anti_detect = st.toggle("ANTI_DETECTION (ROȚUNJIRE)", value=True)

# 4. Header Interfață
st.markdown("<h1 class='terminal-header'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #00ff88; font-size: 0.8rem; margin-top: -10px;'>>> SYSTEM_STATUS: ONLINE // READY_TO_SCAN</p>", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

# Top Bar Statistici
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Uptime", "100%", "LIVE")
with m2: st.metric("Active_Nodes", "14/14")
with m3: 
    total_p = sum([item['P'] for item in st.session_state.history])
    st.metric("Total_Profit", f"{total_p:.2f} RON")
with m4: st.metric("Market_Speed", "125ms")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Motorul de Scanare (Corectat și verificat)
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! ACCESS_DENIED: API_KEY_REQUIRED")
    else:
        with st.spinner("// INTERCEPTING_LIVE_ODDS..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_choice}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                
                if response.status_code != 200:
                    st.error(f"API Error: {response.status_code}")
                else:
                    data = response.json()
                    found = 0
                    
                    for game in data:
                        home, away = game['home_team'], game['away_team']
                        b1, bX, b2 = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}, {'p': 0, 'b': ''}
                        
                        for bk in game.get('bookmakers', []):
                            for mkt in bk.get('markets', []):
                                if mkt['key'] == 'h2h':
                                    for out in mkt['outcomes']:
                                        p, n = out['price'], out['name']
                                        if n == home and p > b1['p']: b1 = {'p': p, 'b': bk['title']}
                                        elif n == away and p > b2['p']: b2 = {'p': p, 'b': bk['title']}
                                        elif n == 'Draw' and p > bX['p']: bX = {'p': p, 'b': bk['title']}

                        has_draw = bX['p'] > 0
                        # Calcul probabilitate (1X2 sau H2H)
                        divizor = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if has_draw else 0)) if (b1['p'] > 0 and b2['p'] > 0) else 1.1

                        if divizor < 1.0:
                            found += 1
                            prof_pct = (1 - divizor) * 100
                            m1 = ((1/b1['p'])/divizor) * buget
                            m2 = ((1/b2['p'])/divizor) * buget
                            mX = ((1/bX['p'])/divizor) * buget if has_draw else 0
                            
                            if anti_detect:
                                m1, m2, mX = round(m1/5)*5, round(m2/5)*5, round(mX/5)*5
                            
                            p_real = (m1 * b1['p']) - (m1 + m2 + mX)

                            # Rândare Card (unsafe_allow_html activat)
                            card_html = f"""
                            <div class="arb-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                                    <span style="font-family: 'JetBrains Mono'; color: #444;">[ MARKET: {game['sport_title']} ]</span>
                                    <span class="profit-tag">PROFIT: +{prof_pct:.2f}%</span>
                                </div>
                                <h2 style="margin-bottom: 2rem; font-weight: 900;">{home} <span style="color:#00ff88">vs</span> {away}</h2>
                                <div style="display: grid; grid-template-columns: repeat({3 if has_draw else 2}, 1fr); gap: 1.5rem;">
                                    <div style="border-left: 3px solid #00ff88; padding-left: 15px;">
                                        <p style="font-size: 0.7rem; color: #666; margin:0;">(1) {b1['b']}</p>
                                        <p style="font-family: 'JetBrains Mono'; font-size:
