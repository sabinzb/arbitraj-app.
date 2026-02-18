import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare Sistem
st.set_page_config(page_title="ARBMaster Platinum", layout="wide", page_icon="⚡")

# 2. CSS Design (Neo-Terminal)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700;900&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #1a1a1a; }
    .terminal-header { font-family: 'JetBrains Mono', monospace; font-weight: 900; color: #ffffff; font-size: 3rem; background: linear-gradient(90deg, #fff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .arb-card { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
    .profit-tag { font-family: 'JetBrains Mono', monospace; background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 10px; border-radius: 6px; border: 1px solid #00ff88; }
    .stButton>button { width: 100%; background: #00ff88 !important; color: #000 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #444; font-size: 0.8rem;'># SYSTEM_CONFIG</h2>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS_TOKEN", type="password")
    buget = st.number_input("CAPITAL (RON)", value=2000, step=500)
    sport_choice = st.selectbox("TARGET_MARKET", ["soccer", "tennis", "basketball"])
    st.divider()
    anti_detect = st.toggle("ANTI_DETECTION", value=True)

# 4. Header
st.markdown("<h1 class='terminal-header'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #00ff88; font-size: 0.8rem;'>>> SYSTEM_STATUS: ONLINE</p>", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

# Top Bar Statistici
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Uptime", "100%", "LIVE")
with m2: st.metric("Nodes", "14/14")
with m3: st.metric("Total_Profit", f"{sum([item['P'] for item in st.session_state.history]):.2f} RON")
with m4: st.metric("Speed", "125ms")

# 5. Logica de Scanare
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! API_KEY_REQUIRED")
    else:
        with st.spinner("// SYNCING..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_choice}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    found = 0
                    for game in data:
                        h, a = game['home_team'], game['away_team']
                        b1, bX, b2 = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}, {'p': 0, 'b': ''}
                        
                        for bk in game.get('bookmakers', []):
                            for mkt in bk.get('markets', []):
                                if mkt['key'] == 'h2h':
                                    for out in mkt['outcomes']:
                                        p, n = out['price'], out['name']
                                        if n == h and p > b1['p']: b1 = {'p': p, 'b': bk['title']}
                                        elif n == a and p > b2['p']: b2 = {'p': p, 'b': bk['title']}
                                        elif n == 'Draw' and p > bX['p']: bX = {'p': p, 'b': bk['title']}

                        has_draw = bX['p'] > 0
                        inv_sum = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if has_draw else 0)) if (b1['p'] > 0 and b2['p'] > 0) else 1.1

                        if inv_sum < 1.0:
                            found += 1
                            prof_pct = (1 - inv_sum) * 100
                            m1 = ((1/b1['p'])/inv_sum) * buget
                            m2 = ((1/b2['p'])/inv_sum) * buget
                            mX = ((1/bX['p'])/inv_sum) * buget if has_draw else 0
                            
                            if anti_detect: m1, m2, mX = round(m1/5)*5, round(m2/5)*5, round(mX/5)*5
                            
                            # AFISARE CARD - SOLUTIA PENTRU PROBLEMA TA: unsafe_allow_html=True
                            card_html = f"""
                            <div class="arb-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                    <span style="font-family: 'JetBrains Mono'; color: #444;">[ {game['sport_title']} ]</span>
                                    <span class="profit-tag">PROFIT: +{prof_pct:.2f}%</span>
                                </div>
                                <h2 style="margin-bottom: 1.5rem;">{h} vs {a}</h2>
                                <div style="display: flex; gap: 1rem; justify-content: space-between;">
                                    <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                        <p style="font-size: 0.7rem; color: #666; margin:0;">(1) {b1['b']}</p>
                                        <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b1['p']}</p>
                                        <p style="color: #00ff88; font-weight: bold; margin:0;">{m1} RON</p>
                                    </div>
                                    {f'<div style="border-left: 2px solid #888; padding-left: 10px;"><p style="font-size: 0.7rem; color: #666; margin:0;">(X) {bX["b"]}</p><p style="font-family: \'JetBrains Mono\'; font-size: 1.2rem; margin:0;">@{bX["p"]}</p><p style="color: #00ff88; font-weight: bold; margin:0;">{mX} RON</p></div>' if has_draw else ''}
                                    <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                        <p style="font-size: 0.7rem; color: #666; margin:0;">(2) {b2['b']}</p>
                                        <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b2['p']}</p>
                                        <p style="color: #00ff88; font-weight: bold; margin:0;">{m2} RON</p>
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                            if st.button(f"SAVE TRADE: {h[:5]}", key=f"t_{found}"):
                                st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": (m1*b1['p'])-(m1+m2+mX)})
                    
                    if found == 0: st.warning("// NO ARBITRAGE FOUND")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"// SYSTEM_EXCEPTION: {str(e)}")

# 6. Analitice
if st.session_state.history:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    st.plotly_chart(px.area(df, x="T", y="P", template="plotly_dark").update_traces(line_color='#00ff88'), use_container_width=True)
