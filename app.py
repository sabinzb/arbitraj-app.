import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. Configurare Pagină
st.set_page_config(page_title="ARBMaster Platinum", layout="wide")

# 2. Design UI Neo-Terminal
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .arb-card { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .profit-tag { background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 12px; border-radius: 6px; border: 1px solid #00ff88; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("⚙️ Control")
    api_key = st.text_input("API KEY", type="password")
    buget = st.number_input("CAPITAL (RON)", value=1000)
    sport = st.selectbox("SPORT", ["soccer", "tennis"])

# 4. Header & Statistici
st.title("📟 ARBMaster // PLATINUM")
c1, c2, c3 = st.columns(3)
c1.metric("Uptime", "100%", "LIVE")
c2.metric("Total Profit", "0.00 RON")
c3.metric("Speed", "125ms")

# 5. Logica de Scanare
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("Introdu cheia API!")
    else:
        with st.spinner("Sincronizare date..."):
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                data = response.json()

                if response.status_code == 200:
                    for game in data:
                        home = game['home_team']
                        away = game['away_team']
                        b1, bX, b2 = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}, {'p': 0, 'b': ''}

                        for bk in game.get('bookmakers', []):
                            for mkt in bk.get('markets', []):
                                if mkt['key'] == 'h2h':
                                    for out in mkt['outcomes']:
                                        p, n = out['price'], out['name']
                                        if n == home: b1 = {'p': p, 'b': bk['title']}
                                        elif n == away: b2 = {'p': p, 'b': bk['title']}
                                        elif n == 'Draw': bX = {'p': p, 'b': bk['title']}

                        # Calcul Arbitraj
                        has_draw = bX['p'] > 0
                        prob = (1/b1['p'] + 1/b2['p'] + (1/bX['p'] if has_draw else 0)) if (b1['p'] > 0 and b2['p'] > 0) else 1.1

                        if prob < 1.0:
                            prof_pct = (1 - prob) * 100
                            m1 = ((1/b1['p'])/prob) * buget
                            m2 = ((1/b2['p'])/prob) * buget
                            mX = ((1/bX['p'])/prob) * buget if has_draw else 0
                            
                            # AFISARE CARD - REPARATIE image_d96cd9.png
                            # Folosim unsafe_allow_html=True pentru a randa designul
                            st.markdown(f"""
                            <div class="arb-card">
                                <div style="display: flex; justify-content: space-between;">
                                    <span>{game['sport_title']}</span>
                                    <span class="profit-tag">+{prof_pct:.2f}%</span>
                                </div>
                                <h3>{home} vs {away}</h3>
                                <div style="display: flex; gap: 20px;">
                                    <div style="border-left: 3px solid #00ff88; padding-left: 10px;">
                                        <p style="margin:0; font-size: 12px;">(1) {b1['b']}</p>
                                        <p style="margin:0; font-size: 20px; font-weight: bold;">@{b1['p']}</p>
                                        <p style="margin:0; color:#00ff88;">{round(m1, 2)} RON</p>
                                    </div>
                                    {f'<div style="border-left: 3px solid #888; padding-left: 10px;"><p style="margin:0; font-size: 12px;">(X) {bX["b"]}</p><p style="margin:0; font-size: 20px; font-weight: bold;">@{bX["p"]}</p><p style="margin:0; color:#00ff88;">{round(mX, 2)} RON</p></div>' if has_draw else ''}
                                    <div style="border-left: 3px solid #00ff88; padding-left: 10px;">
                                        <p style="margin:0; font-size: 12px;">(2) {b2['b']}</p>
                                        <p style="margin:0; font-size: 20px; font-weight: bold;">@{b2['p']}</p>
                                        <p style="margin:0; color:#00ff88;">{round(m2, 2)} RON</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("Eroare API. Verifică cheia.")
            except Exception as e:
                st.error(f"Eroare sistem: {e}")
