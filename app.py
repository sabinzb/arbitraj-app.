import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. SETUP & DESIGN
st.set_page_config(page_title="ARBMaster Platinum", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700;900&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #1a1a1a; }
    .terminal-header {
        font-family: 'JetBrains Mono', monospace; font-weight: 900; 
        background: linear-gradient(90deg, #ffffff, #00ff88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.5rem; margin-bottom: 0.5rem;
    }
    .arb-card { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
    .profit-tag { font-family: 'JetBrains Mono', monospace; background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 10px; border-radius: 6px; border: 1px solid #00ff88; }
    .stButton>button { width: 100%; background: #00ff88 !important; color: #000 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important; border: none; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE MANAGEMENT
if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("<h2 style='color: #444; font-size: 0.8rem; font-family: \"JetBrains Mono\";'># CONFIG</h2>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS_TOKEN", type="password")
    buget = st.number_input("CAPITAL (RON)", value=2000, step=500)
    sport_choice = st.selectbox("SPORT", ["tennis", "soccer", "basketball"])
    st.divider()
    anti_detect = st.toggle("ANTI-DETECTION", value=True)
    if st.button("CLEAR SESSION"):
        st.session_state.history = []
        st.rerun()

# 3. HEADER
st.markdown("<h1 class='terminal-header'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='font-family: \"JetBrains Mono\"; color: #00ff88; font-size: 0.8rem; margin-top: -15px;'>>> ENGINE: ACTIVE // TARGET: {sport_choice.upper()}</p>", unsafe_allow_html=True)

# 4. SCAN ENGINE (FIXED FOR TENNIS)
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! API_KEY_REQUIRED")
    else:
        with st.spinner("// INTERCEPTING DATA..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_choice}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code != 200:
                    st.error(f"API Error: {data.get('message', 'Check key')}")
                else:
                    found = 0
                    for game in data:
                        # Fix: folosim direct cheile din obiectul 'game'
                        home_team = game.get('home_team')
                        away_team = game.get('away_team')
                        
                        b1 = {'p': 0, 'b': 'N/A'}
                        bX = {'p': 0, 'b': 'N/A'} # Egal (doar pt fotbal)
                        b2 = {'p': 0, 'b': 'N/A'}
                        
                        for bk in game.get('bookmakers', []):
                            for mkt in bk.get('markets', []):
                                if mkt['key'] == 'h2h':
                                    for out in mkt['outcomes']:
                                        p, name = out['price'], out['name']
                                        if name == home_team and p > b1['p']: b1 = {'p': p, 'b': bk['title']}
                                        elif name == away_team and p > b2['p']: b2 = {'p': p, 'b': bk['title']}
                                        elif name.lower() == 'draw' and p > bX['p']: bX = {'p': p, 'b': bk['title']}

                        # Verificăm dacă avem cote valide pentru ambele părți
                        if b1['p'] > 0 and b2['p'] > 0:
                            is_football = (sport_choice == "soccer" and bX['p'] > 0)
                            
                            # Calcul inversă probabilitate
                            inv_sum = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if is_football else 0))
                            
                            if inv_sum < 1.0:
                                found += 1
                                prof_pct = (1 - inv_sum) * 100
                                
                                # Calcul mize
                                m1 = ((1/b1['p'])/inv_sum) * buget
                                m2 = ((1/b2['p'])/inv_sum) * buget
                                mX = ((1/bX['p'])/inv_sum) * buget if is_football else 0
                                
                                if anti_detect:
                                    m1, m2, mX = round(m1/5)*5, round(m2/5)*5, round(mX/5)*5
                                
                                profit_ron = (m1 * b1['p']) - (m1 + m2 + mX)

                                # Rulare design card
                                grid_cols = 3 if is_football else 2
                                card_html = f"""
                                <div class="arb-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                        <span style="font-family: 'JetBrains Mono'; color: #444;">[ {game['sport_title']} ]</span>
                                        <span class="profit-tag">+{prof_pct:.2f}% PROFIT</span>
                                    </div>
                                    <h3 style="margin-bottom: 1.5rem;">{home_team} vs {away_team}</h3>
                                    <div style="display: grid; grid-template-columns: repeat({grid_cols}, 1fr); gap: 10px;">
                                        <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                            <p style="font-size: 0.7rem; color: #555; margin:0;">(1) {b1['b']}</p>
                                            <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b1['p']}</p>
                                            <p style="color: #00ff88; font-weight: bold; margin:0;">{int(m1)} RON</p>
                                        </div>
                                        {f'<div style="border-left: 2px solid #666; padding-left: 10px;"><p style="font-size: 0.7rem; color: #555; margin:0;">(X) {bX["b"]}</p><p style="font-family: \'JetBrains Mono\'; font-size: 1.2rem; margin:0;">@{bX["p"]}</p><p style="color: #00ff88; font-weight: bold; margin:0;">{int(mX)} RON</p></div>' if is_football else ''}
                                        <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                            <p style="font-size: 0.7rem; color: #666; margin:0;">(2) {b2['b']}</p>
                                            <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0;">@{b2['p']}</p>
                                            <p style="color: #00ff88; font-weight: bold; margin:0;">{int(m2)} RON</p>
                                        </div>
                                    </div>
                                </div>
                                """
                                st.markdown(card_html, unsafe_allow_html=True)
                                
                                if st.button(f"REG: {home_team[:5]}", key=f"s_{found}"):
                                    st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": profit_ron})
                                    st.rerun()

                    if found == 0:
                        st.warning("// SCAN_COMPLETE: NO_ARBITRAGE_FOUND")
            except Exception as e:
                st.error(f"// CRITICAL_ERROR: {str(e)}")

# 5. ANALYTICS
if st.session_state.history:
    st.divider()
    df_h = pd.DataFrame(st.session_state.history)
    st.markdown("<h3 style='font-family: \"JetBrains Mono\"; color: #00ff88;'>📊 SESSION_ANALYSIS</h3>", unsafe_allow_html=True)
    
    # Grafic corectat și închis complet
    fig = px.area(df_h, x="T", y="P", template="plotly_dark", title="Profit Stream")
    fig.update_traces(line_color='#00ff88', fillcolor='rgba(0, 255, 136, 0.1)')
    st.plotly_chart(fig, use_container_width=True)
