import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. SETUP SISTEM
st.set_page_config(page_title="ARBMaster Platinum", layout="wide", page_icon="⚡")

# 2. DESIGN UI (CSS INJECTION)
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

# 3. STATE & SIDEBAR
if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("<h2 style='color: #444; font-size: 0.8rem; font-family: \"JetBrains Mono\";'># CONFIG_TERMINAL</h2>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS_TOKEN", type="password")
    buget = st.number_input("CAPITAL (RON)", value=2000, step=500)
    sport = st.selectbox("PIAȚA", ["soccer", "tennis", "basketball"])
    st.divider()
    anti_detect = st.toggle("ANTI-DETECTION", value=True)
    if st.button("CLEAR HISTORY"):
        st.session_state.history = []
        st.rerun()

# 4. HEADER
st.markdown("<h1 class='terminal-header'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)

# 5. SCAN ENGINE
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! API_KEY_REQUIRED")
    else:
        with st.spinner("// SCANNING..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                data = requests.get(url).json()
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

                    has_x = bX['p'] > 0
                    inv_sum = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if has_x else 0)) if (b1['p'] > 0 and b2['p'] > 0) else 1.1

                    if inv_sum < 1.0:
                        found += 1
                        prof = (1 - inv_sum) * 100
                        m1, m2 = ((1/b1['p'])/inv_sum)*buget, ((1/b2['p'])/inv_sum)*buget
                        mX = ((1/bX['p'])/inv_sum)*buget if has_x else 0
                        
                        if anti_detect: m1, m2, mX = round(m1/5)*5, round(m2/5)*5, round(mX/5)*5

                        card_html = f"""
                        <div class="arb-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <span style="font-family: 'JetBrains Mono'; color: #444;">[ {game['sport_title']} ]</span>
                                <span class="profit-tag">+{prof:.2f}% PROFIT</span>
                            </div>
                            <h3>{h} vs {a}</h3>
                            <div style="display: grid; grid-template-columns: repeat({3 if has_x else 2}, 1fr); gap: 10px;">
                                <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                    <p style="font-size: 0.7rem; color: #555;">(1) {b1['b']}</p>
                                    <p style="font-size: 1.2rem; color: #fff;">@{b1['p']}</p>
                                    <p style="color: #00ff88; font-weight: bold;">{int(m1)} RON</p>
                                </div>
                                {f'<div style="border-left: 2px solid #666; padding-left: 10px;"><p style="font-size: 0.7rem; color: #555;">(X) {bX["b"]}</p><p style="font-size: 1.2rem; color: #fff;">@{bX["p"]}</p><p style="color: #00ff88; font-weight: bold;">{int(mX)} RON</p></div>' if has_x else ''}
                                <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
                                    <p style="font-size: 0.7rem; color: #555;">(2) {b2['b']}</p>
                                    <p style="font-size: 1.2rem; color: #fff;">@{b2['p']}</p>
                                    <p style="color: #00ff88; font-weight: bold;">{int(m2)} RON</p>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Adăugăm un buton discret de salvare în istoric
                        if st.button(f"REGISTER_TRADE: {h[:5]}", key=f"save_{found}"):
                            st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": (m1*b1['p'])-(m1+m2+mX)})
                            st.rerun()

                if found == 0:
                    st.warning("// SCAN_COMPLETE: NO_ARBITRAGE_DETECTED")
            except Exception as e:
                st.error(f"// SYSTEM_EXCEPTION: {str(e)}")

# 6. ANALYTICS (SECȚIUNEA REPARATĂ)
if st.session_state.history:
    st.divider()
    st.markdown("<h3 style='font-family: \"JetBrains Mono\"; color: #00ff88;'>📊 SESSION_ANALYSIS</h3>", unsafe_allow_html=True)
    
    df_history = pd.DataFrame(st.session_state.history)
    
    # Grafic corectat: am închis toate parantezele
    fig = px.area(df_history, x="T", y="P", template="plotly_dark", title="Profit Evolution")
    fig.update_traces(line_color='#00ff88', fillcolor='rgba(0, 255, 136, 0.1)')
    
    st.plotly_chart(fig, use_container_width=True)
