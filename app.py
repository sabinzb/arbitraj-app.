import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare Sistem
st.set_page_config(page_title="ArbMaster // Neo-Terminal", layout="wide", page_icon="📟")

# 2. Arhitectura Vizuală (Hyper-Refined CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@200;400;800&display=swap');

    /* Resetare Fundal */
    .stApp {
        background-color: #08090a;
        color: #d1d5db;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Ultra-Minimalist */
    [data-testid="stSidebar"] {
        background-color: #050607 !important;
        border-right: 1px solid #1a1c1e;
        padding-top: 2rem;
    }

    /* Header Neo-Terminal */
    .terminal-title {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        color: #ffffff;
        font-size: 2.8rem;
        letter-spacing: -1px;
        border-bottom: 2px solid #00ff88;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .terminal-subtitle {
        font-family: 'JetBrains Mono', monospace;
        color: #00ff88;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 3rem;
    }

    /* Card-uri de Date (Fine-Line Design) */
    .data-card {
        background: #0d0f11;
        border: 1px solid #1f2226;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    .data-card:hover {
        border-color: #3b82f6;
        background: #111418;
    }

    /* Input-uri Stilizate */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d0f11 !important;
        border: 1px solid #1f2226 !important;
        color: #00ff88 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Buton "Execute" Style */
    .stButton>button {
        width: 100%;
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Profit Badge */
    .profit-tag {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        border: 1px solid #00ff88;
    }

    /* Ascundere UI Streamlit */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: System Control
with st.sidebar:
    st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #4b5563;'># SYS_CONTROL</p>", unsafe_allow_html=True)
    api_key = st.text_input(">> ACCESS_KEY", type="password")
    buget = st.number_input(">> TOTAL_CAPITAL (RON)", value=2000, step=500)
    round_on = st.toggle(">> ANTI_DETECT_MODE", value=True)
    st.divider()
    st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #4b5563;'>/ STATUS: ONLINE</p>", unsafe_allow_html=True)

# 4. Main Terminal Interface
st.markdown("<h1 class='terminal-title'>ARBMaster // NEO-TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p class='terminal-subtitle'>REAL-TIME PROBABILISTIC ARBITRAGE TERMINAL</p>", unsafe_allow_html=True)

# Grid Statistici
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Uptime", "99.9%", "LIVE", delta_color="normal")
with col2: st.metric("Active_Nodes", "14/14", "SYNC")
with col3: st.metric("Avg_Spread", "2.84%", "+0.2")
with col4: st.metric("Session_PnL", "0.00 RON", "0.0%")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Motorul de Scanare & Afișare
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! ERROR: UNAUTHORIZED_ACCESS. API_KEY_REQUIRED.")
    else:
        with st.spinner("// INITIALIZING_DATA_STREAM..."):
            try:
                # Interogăm API (Căutăm fotbal pentru 1X2)
                url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                data = requests.get(url).json()
                
                found = 0
                for game in data:
                    home, away = game['home_team'], game['away_team']
                    b1, bX, b2 = {'p': 0, 'b': ''}, {'p': 0, 'b': ''},
