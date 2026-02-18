import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare Sistem
st.set_page_config(page_title="ArbMaster // Neo-Terminal", layout="wide", page_icon="📟")

# 2. Design UI Neo-Terminal (Hyper-Refined)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@200;400;800&display=swap');

    .stApp { background-color: #08090a; color: #d1d5db; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #050607 !important; border-right: 1px solid #1a1c1e; }
    
    .terminal-title {
        font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #ffffff;
        font-size: 2.5rem; letter-spacing: -1px; border-bottom: 2px solid #00ff88;
        display: inline-block; margin-bottom: 0.5rem;
    }
    
    .data-card {
        background: rgba(13, 15, 17, 0.8); border: 1px solid #1f2226;
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .data-card:hover { border-color: #00ff88; box-shadow: 0 0 15px rgba(0, 255, 136, 0.1); }
    
    .stButton>button {
        width: 100%; background: #00ff88 !important; color: #000 !important;
        font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important;
        border-radius: 6px !important; border: none !important; padding: 0.8rem !important;
    }
    
    .profit-badge {
        font-family: 'JetBrains Mono', monospace; background: rgba(0, 255, 136, 0.1);
        color: #00ff88; padding: 4px 12px; border-radius: 6px; border: 1px solid #00ff88;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #4b5563;'># SYS_CONTROL</p>", unsafe_allow_html=True)
    api_key = st.text_input(">> ACCESS_KEY", type="password")
    buget = st.number_input(">> CAPITAL (RON)", value=2000, step=500)
    sport_choice = st.selectbox(">> TARGET_SPORT", ["soccer", "tennis", "basketball"])
    st.divider()
    anti_detect = st.toggle("ANTI_DETECT", value=True)

# 4. Header
st.markdown("<h1 class='terminal-title'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #00ff88;'>>> STATUS: READY_FOR_SCAN</p>", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

# 5. Motorul de Scanare (1X2 Integrat)
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! ACCESS_DENIED: API_KEY_REQUIRED")
    else:
        with st.spinner("// SYNCING_WITH_EXCHANGES..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_choice}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code != 200:
                    st.error(f"API Error: {data.get('message', 'Unknown error')}")
                else:
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
                        
                        # Verificăm dacă e meci cu 3 variante (Fotbal) sau 2 (Tenis)
                        has_draw = bX['p'] > 0
                        prob = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if has_draw else 0))
                        
                        if prob < 1.0 and b1['p'] > 0 and b2['p'] > 0:
                            found += 1
                            prof_pct = (1 - prob) * 100
                            m1 = ((1/b1['p'])/prob) * buget
                            m2 = ((1/b2['p'])/prob) * buget
                            mX = ((1/bX['p'])/prob) * buget if has_draw else 0
                            
                            if anti_detect:
                                m1, m2, mX = round(m1/5)*5, round(m2/5)*5, round(mX/5)*5
                            
                            real_p = (m1 * b1['p']) - (m1 + m2 + mX)

                            st.markdown(f"""
                            <div class="data-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-family: 'JetBrains Mono'; color: #4b5563;">[ {game['sport_title']} ]</span>
                                    <span class="profit-badge">+{prof_pct:.2f}% PROFIT</span>
                                </div>
                                <h3 style="margin: 1rem 0;">{home} vs {away}</h3>
                                <div style="display: grid; grid-template-columns: repeat({3 if has_draw else 2}, 1fr); gap: 1rem;">
                                    <div style="border-left: 2px solid #3b82f6; padding-left: 10px;">
                                        <p style="font-size: 0.7rem; color: #4b5563; margin:0;">(1) {b1['b']}</p>
                                        <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b1['p']}</p>
                                        <p style="color: #00ff88; font-weight: bold; margin:0;">{m1} RON</p>
                                    </div>
                                    {"<div style='border-left: 2px solid #6b7280; padding-left: 10px;'><p style='font-size: 0.7rem; color: #4b5563; margin:0;'>(X) " + bX['b'] + "</p><p style='font-family: \"JetBrains Mono\"; font-size: 1.2rem; margin:0;'>@" + str(bX['p']) + "</p><p style='color: #00ff88; font-weight: bold; margin:0;'>" + str(mX) + " RON</p></div>" if has_draw else ""}
                                    <div style="border-left: 2px solid #3b82f6; padding-left: 10px;">
                                        <p style="font-size: 0.7rem; color: #4b5563; margin:0;">(2) {b2['b']}</p>
                                        <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b2['p']}</p>
                                        <p style="color: #00ff88; font-weight: bold; margin:0;">{m2} RON</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"SAVE TRADE: {home[:5]}", key=f"sv_{found}"):
                                st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": real_p})

                    if found == 0:
                        st.warning("// SCAN_COMPLETE: NO_INEFFICIENCIES_DETECTED")
                    else:
                        st.balloons()
            except Exception as e:
                st.error(f"// SYSTEM_CRASH: {str(e)}")

# 6. Analitice
if st.session_state.history:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    st.metric("SESSION_PROFIT", f"{df['P'].sum():.2f} RON")
    fig = px.area(df, x="T", y="P", template="plotly_dark")
    fig.update_traces(line_color='#00ff88', fillcolor='rgba(0, 255, 136, 0.1)')
    st.plotly_chart(fig, use_container_width=True)
