import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. SETUP & CONFIGURATION
# Setăm un mediu de lucru ultra-wide pentru o vizibilitate mai bună a datelor
st.set_page_config(page_title="ARBMaster Platinum", layout="wide", page_icon="⚡")

# 2. UI ARCHITECTURE (CSS INJECTION)
# Folosim un design "Obsidian Glass" pentru o experiență de utilizator premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700;900&display=swap');
    
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #1a1a1a; }
    
    .terminal-header {
        font-family: 'JetBrains Mono', monospace; font-weight: 900; 
        background: linear-gradient(90deg, #ffffff, #00ff88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3rem; margin-bottom: 0.5rem;
    }
    
    .arb-card {
        background: #0d0d0d; border: 1px solid #1f1f1f;
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
    }
    
    .profit-tag {
        font-family: 'JetBrains Mono', monospace; background: rgba(0, 255, 136, 0.1);
        color: #00ff88; padding: 4px 12px; border-radius: 6px; border: 1px solid #00ff88;
    }
    
    .stButton>button {
        width: 100%; background: #00ff88 !important; color: #000 !important;
        font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important;
        border-radius: 4px !important; transition: 0.3s;
    }
    
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3); }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. GLOBAL STATE & SIDEBAR
if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("<h2 style='color: #444; font-size: 0.8rem; font-family: \"JetBrains Mono\";'># CONFIG_TERMINAL</h2>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS_TOKEN", type="password", placeholder="Introdu API Key...")
    buget_operativ = st.number_input("CAPITAL TOTAL (RON)", value=2000, step=500)
    piata_tinta = st.selectbox("PIAȚA", ["soccer", "tennis", "basketball"])
    st.divider()
    anti_detect = st.toggle("MOD ANTI-DETECȚIE (ROUNDING)", value=True)
    if st.button("RESET SESSION"):
        st.session_state.history = []
        st.rerun()

# 4. MAIN INTERFACE HEADER
st.markdown("<h1 class='terminal-header'>ARBMaster // PLATINUM</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family: \"JetBrains Mono\"; color: #00ff88; font-size: 0.8rem; margin-top: -15px;'>>> CORE_ENGINE: READY // STATUS: ONLINE</p>", unsafe_allow_html=True)

# Dashboard rapid de monitorizare
m1, m2, m3 = st.columns(3)
with m1: st.metric("Uptime", "100%", "LIVE")
with m2: 
    current_profit = sum([item['P'] for item in st.session_state.history])
    st.metric("Total Profit", f"{current_profit:.2f} RON")
with m3: st.metric("Scanner Latency", "118ms")

st.markdown("<br>", unsafe_allow_html=True)

# 5. CORE LOGIC: SCANNING & CALCULATION
if st.button("RUN SCAN_PROTOCOL"):
    if not api_key:
        st.error("!! EROARE: Cheia API este necesară pentru interogare.")
    else:
        with st.spinner("// SE SINCRONIZEAZĂ DATELE..."):
            try:
                # Interogare endpoint API
                url = f"https://api.the-odds-api.com/v4/sports/{piata_tinta}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code != 200:
                    st.error(f"API Error {response.status_code}: {data.get('message', 'Eroare necunoscută')}")
                else:
                    found_count = 0
                    for game in data:
                        h_team, a_team = game['home_team'], game['away_team']
                        b1, bX, b2 = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}, {'p': 0, 'b': ''}
