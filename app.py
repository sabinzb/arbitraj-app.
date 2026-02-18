import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurație High-End
st.set_page_config(page_title="ARBMaster Obsidian", layout="wide", page_icon="⚡")

# 2. Arhitectura Vizuală (CSS-ul care face diferența)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;700&display=swap');

    /* Fundal Cinematic */
    .stApp {
        background: #050505;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 212, 255, 0.05) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(0, 255, 136, 0.05) 0, transparent 50%);
    }

    /* Sidebar futurist */
    [data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 1px solid #1a1a1a;
    }

    /* Card-uri de tip Obsidian */
    .arb-card {
        background: rgba(15, 15, 15, 0.8);
        border: 1px solid #222;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .arb-card:hover {
        border-color: #00d4ff;
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }

    /* Header cu font de tip "Terminal" */
    .hero-text {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        background: linear-gradient(180deg, #fff 0%, #444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        text-align: center;
        letter-spacing: 5px;
    }

    /* Buton "Action" cu efect de pulse */
    .stButton>button {
        background: #00d4ff !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        border: none !important;
        height: 50px !important;
        width: 100% !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background: #00ff88 !important;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.6);
    }

    /* Metricile "Neon" */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88 !important;
        font-size: 1.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Centrul de Control
with st.sidebar:
    st.markdown("<h1 style='color: #fff; font-size: 1.2rem;'>SYSTEM CONFIG</h1>", unsafe_allow_html=True)
    api_key = st.text_input("ACCESS TOKEN", type="password")
    st.divider()
    market_filter = st.multiselect("EXCHANGES", ["Unibet", "Betfair", "Betano", "Pinnacle", "Bwin"], default=["Unibet", "Betfair"])
    capital = st.number_input("TOTAL CAPITAL (RON)", value=2000)
    st.divider()
    st.caption("v4.0 Obsidian Edition • Secure Connection")

# 4. Main Layout
st.markdown("<h1 class='hero-text'>ARBMASTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-family: Inter;'>QUANTITATIVE ARBITRAGE TERMINAL</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Indicatori de Stare (Top Grid)
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("STATUS", "SYNCED", delta="4ms")
with m2: st.metric("OPPORTUNITIES", "12 Active")
with m3: st.metric("AVG PROFIT", "3.12%")
with m4: st.metric("SESSION PnL", "420.50 RON")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Logică & Feed-ul de Date
if st.button("INITIALIZE GLOBAL SCAN"):
    if not api_key:
        st.error("❗ ACCESS DENIED: API TOKEN REQUIRED")
    else:
        with st.spinner("DECODING ODDS..."):
            # Exemplu de card pentru rezultat (Repetabil prin loop-ul de API)
            st.markdown("""
            <div class="arb-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #666; font-family: Inter;">🏆 CHAMPIONS LEAGUE</span>
                    <span style="color: #00ff88; font-family: Orbitron; font-weight: bold;">+4.25%</span>
                </div>
                <h2 style="margin: 15px 0; font-family: Orbitron; font-weight: 400;">REAL MADRID <span style="color: #00d4ff;">vs</span> MAN CITY</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px; border: 1px solid #222;">
                        <div style="font-size: 0.8rem; color: #888;">BETFAIR</div>
                        <div style="font-size: 1.5rem; color: #fff;">Cota 2.45</div>
                        <div style="color: #00d4ff; font-weight: bold;">Miză: 940 RON</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px; border: 1px solid #222;">
                        <div style="font-size: 0.8rem; color: #888;">UNIBET</div>
                        <div style="font-size: 1.5rem; color: #fff;">Cota 2.38</div>
                        <div style="color: #00d4ff; font-weight: bold;">Miză: 1060 RON</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 6. Analiza Grafică (Plotly Custom)
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📡 SPREAD ANALYSIS")
# Simulăm un set de date pentru grafic
chart_data = pd.DataFrame({'Time': range(10), 'Profit': [2, 5, 4, 8, 7, 12, 10, 15, 14, 20]})
fig = px.area(chart_data, x='Time', y='Profit', template='plotly_dark')
fig.update_traces(line_color='#00d4ff', fillcolor='rgba(0, 212, 255, 0.1)')
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'showgrid': False},
    yaxis={'showgrid': False}
)
st.plotly_chart(fig, use_container_width=True)
