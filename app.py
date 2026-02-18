import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare pagină
st.set_page_config(page_title="Arbitraj Sportiv Pro", layout="wide", page_icon="📈")

# 2. CSS pentru Interfață Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stExpander { background-color: #1a1c24 !important; border: 1px solid #30363d !important; border-radius: 12px !important; }
    .calc-box { padding: 20px; border-radius: 15px; border: 1px solid #00ff88; background-color: #0d2a1f; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Control & Calculator Manual
with st.sidebar:
    st.title("🛡️ Smart Arb")
    
    # --- SECȚIUNE CALCULATOR MANUAL ---
    st.subheader("🧮 Calculator Rapid")
    with st.container():
        m_cota1 = st.number_input("Cota 1", value=2.10, step=0.01)
        m_cota2 = st.number_input("Cota 2", value=2.05, step=0.01)
        m_buget = st.number_input("Suma Totală", value=100.0, step=10.0)
        
        # Matematica pentru calculatorul manual
        inv_total = (1/m_cota1) + (1/m_cota2)
        if inv_total < 1.0:
            p_manual = (1 - inv_total) * 100
            s1_m = ( (1/m_cota1) / inv_total ) * m_buget
            s2_m = ( (1/m_cota2) / inv_total ) * m_buget
            st.success(f"PROFIT: {round(p_manual, 2)}%")
            st.code(f"Miză 1: {round(s1_m, 2)}\nMiză 2: {round(s2_m, 2)}")
        else:
            st.error("Nu este Arbitraj")
    
    st.divider()
    
    # --- SETĂRI SCANNER ---
    st.subheader("🛰️ Setări Scanner")
    api_key = st.text_input("Cheie API", type="password")
    buget_auto = st.number_input("Buget Scanner (RON)", value=1000)

# 4. Main Content
st.title("🚀 Scanner Surebet Live")
st.caption("Analiză automată între Unibet, Betfair, Betano, Pinnacle și 888sport")

if 'history' not in st.session_state:
    st.session_state.history = []

# Scanare automată
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    if st.button("🔄 SCANEAZĂ PIAȚA ACUM"):
        if not api_key:
            st.warning("⚠️ Te rog introdu cheia API în sidebar.")
        else:
            with st.spinner("Se caută oportunități..."):
                try:
                    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                    data = requests.get(url).json()
                    
                    found = 0
                    consacrate = ['Unibet', 'Betfair', '888sport', 'Pinnacle', 'Betano', 'Bwin']
                    
                    for game in data:
                        home, away = game['home_team'], game['away_team']
                        bh, ba = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}
                        
                        for bk in game['bookmakers']:
                            if bk['title'] in consacrate:
                                for out in bk['markets'][0]['outcomes']:
                                    if out['name'] == home and out['price'] > bh['p']:
                                        bh = {'p': out['price'], 'b': bk['title']}
                                    elif out['name'] == away and out['price'] > ba['p']:
                                        ba = {'p': out['price'], 'b': bk['title']}
                        
                        if bh['p'] > 1 and ba['p'] > 1:
                            m = (1/bh['p']) + (1/ba['p'])
                            if m < 1.0:
                                found += 1
                                p_pct = (1-m)*100
                                s1 = ((1/bh['p'])/m)*buget_auto
                                s2 = ((1/ba['p'])/m)*buget_auto
                                
                                with st.expander(f"✨ PROFIT {round(p_pct, 2)}% | {home} vs {away}"):
                                    c1, c2, c3 = st.columns(3)
                                    c1.metric(bh['b'], f"{bh['p']}", f"{round(s1, 1)} RON")
                                    c2.metric(ba['b'], f"{ba['p']}", f"{round(s2, 1)} RON")
                                    c3.metric("Profit Net", f"+{round(buget_auto*(p_pct/100), 2)} RON")
                                    if st.button(f"Salvează {found}", key=f"s_{found}"):
                                        st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": buget_auto*(p_pct/100)})
                    
                    if found > 0: st.balloons()
                    else: st.info("Nicio oportunitate găsită în acest moment.")
                except Exception as e:
                    st.error(f"Eroare: {e}")

# 5. Dashboard Analitic
if st.session_state.history:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    col1, col2 = st.columns([1, 2])
    col1.metric("TOTAL PROFIT", f"{df['P'].sum():.2f} RON")
    fig = px.area(df, x="T", y="P", title="Performanță Sesiune", template="plotly_dark")
    fig.update_traces(line_color='#00ff88', fillcolor='rgba(0, 255, 136, 0.2)')
    col2.plotly_chart(fig, use_container_width=True)
