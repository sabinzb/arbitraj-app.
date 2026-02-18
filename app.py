import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pytz

# 1. Configurație de Top
st.set_page_config(page_title="ArbMaster Platinum", layout="wide", page_icon="💎")

# 2. Injectare CSS pentru Interfață de Lux (Glassmorphism)
st.markdown("""
    <style>
    /* Fundal gradient profund */
    .main { 
        background: radial-gradient(circle at 50% 50%, #1a1f2c 0%, #0b0e14 100%); 
        color: #e6edf3; 
    }
    
    /* Sidebar stilizat */
    [data-testid="stSidebar"] { 
        background-color: rgba(13, 17, 23, 0.95); 
        border-right: 1px solid #30363d; 
    }
    
    /* Carduri cu efect de sticlă */
    .arb-card { 
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 20px; 
        padding: 25px; 
        margin-bottom: 25px; 
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .arb-card:hover { 
        transform: translateY(-5px); 
        border-color: #00d4ff; 
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.1);
    }
    
    /* Badge Profit Neon */
    .profit-badge {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        color: #000;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 0.9rem;
    }

    /* Butoane Premium */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0055ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        height: 3em !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;
        transform: scale(1.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Control & Calculator Manual
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135673.png", width=70)
    st.title("ArbMaster")
    st.caption("Platinum Edition v3.0")
    
    st.divider()
    
    with st.expander("🧮 Calculator Instant", expanded=False):
        c1 = st.number_input("Cota 1", value=2.10)
        c2 = st.number_input("Cota 2", value=2.05)
        bm = st.number_input("Buget", value=100)
        inv = (1/c1) + (1/c2)
        if inv < 1:
            st.success(f"Profit: {((1-inv)*100):.2f}%")
        else:
            st.error("Fără profit")

    st.divider()
    api_key = st.text_input("🔑 Cheie API", type="password")
    buget_auto = st.number_input("💰 Buget Scanare (RON)", value=1000)
    sport_sel = st.selectbox("Sport", ["soccer", "tennis", "basketball", "Toate"])
    round_on = st.toggle("Anti-Detect (Mize Rotunde)", value=True)

# 4. Main Dashboard
st.markdown("<h1 style='text-align: center; color: #00d4ff;'>💎 Terminal Arbitraj Premium</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7;'>Analiză multi-market în timp real între cele mai mari case de pariuri din Europa</p>", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    scan_btn = st.button("🚀 SCANEAZĂ PIAȚA ACUM", use_container_width=True)

if scan_btn:
    if not api_key:
        st.warning("⚠️ Introduceți cheia API în sidebar pentru a începe.")
    else:
        with st.spinner("Se accesează fluxul de date Platinum..."):
            try:
                sport_path = "upcoming" if sport_sel == "Toate" else sport_sel
                url = f"https://api.the-odds-api.com/v4/sports/{sport_path}/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                data = requests.get(url).json()
                
                found = 0
                trust_list = ['Unibet', 'Betfair', '888sport', 'Betano', 'Pinnacle', 'Bwin', 'William Hill']

                for game in data:
                    h, a = game['home_team'], game['away_team']
                    bh, ba = {'p': 0, 'b': ''}, {'p': 0, 'b': ''}
                    
                    for bk in game['bookmakers']:
                        if bk['title'] in trust_list:
                            for out in bk['markets'][0]['outcomes']:
                                if out['name'] == h and out['price'] > bh['p']:
                                    bh = {'p': out['price'], 'b': bk['title']}
                                elif out['name'] == a and out['price'] > ba['p']:
                                    ba = {'p': out['price'], 'b': bk['title']}
                    
                    if bh['p'] > 1 and ba['p'] > 1:
                        margin = (1/bh['p']) + (1/ba['p'])
                        if margin < 1.0:
                            found += 1
                            p_pct = (1-margin)*100
                            s1_r = ((1/bh['p'])/margin)*buget_auto
                            s2_r = ((1/ba['p'])/margin)*buget_auto
                            
                            s1 = round(s1_r / 5) * 5 if round_on else round(s1_r, 2)
                            s2 = round(s2_r / 5) * 5 if round_on else round(s2_r, 2)
                            real_p = (s1 * bh['p']) - (s1 + s2)
                            
                            # CARD PREMIUM
                            st.markdown(f"""
                            <div class="arb-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <span style="opacity: 0.6;">🏆 {game['sport_title']}</span>
                                    <span class="profit-badge">+{round(p_pct, 2)}% PROFIT</span>
                                </div>
                                <h3 style="margin: 0; color: #fff;">{h} <span style="color: #00d4ff;">vs</span> {a}</h3>
                                <hr style="opacity: 0.1; margin: 20px 0;">
                                <div style="display: flex; justify-content: space-around; text-align: center;">
                                    <div>
                                        <p style="margin:0; opacity: 0.6;">{bh['b']}</p>
                                        <h2 style="margin:0; color: #00d4ff;">{bh['p']}</h2>
                                        <p style="margin:0; font-weight: bold;">Miză: {s1} RON</p>
                                    </div>
                                    <div style="border-left: 1px solid rgba(255,255,255,0.1);"></div>
                                    <div>
                                        <p style="margin:0; opacity: 0.6;">{ba['b']}</p>
                                        <h2 style="margin:0; color: #00d4ff;">{ba['p']}</h2>
                                        <p style="margin:0; font-weight: bold;">Miză: {s2} RON</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"ÎNREGISTREAZĂ +{round(real_p, 1)} RON", key=f"p_{found}"):
                                st.session_state.history.append({"T": datetime.now().strftime("%H:%M"), "P": real_p})
                                st.rerun()

                if found == 0:
                    st.info("🔎 Scanare completă. Nicio oportunitate profitabilă găsită acum.")
                else:
                    st.balloons()
            except:
                st.error("Eroare la conexiune. Verifică API Key.")

# 5. Statistici și Analiză
if st.session_state.history:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    col_stat1, col_stat2 = st.columns([1, 2])
    
    with col_stat1:
        st.markdown("<div style='padding-top: 20px;'>", unsafe_allow_html=True)
        st.metric("PROFIT TOTAL", f"{df['P'].sum():.2f} RON", delta=f"{df['P'].iloc[-1]} RON")
        st.metric("OPERAȚIUNI", len(df))
    
    with col_stat2:
        fig = px.area(df, x="T", y="P", title="Evoluție Portofoliu", template="plotly_dark")
        fig.update_traces(line_color='#00d4ff', fillcolor='rgba(0, 212, 255, 0.1)')
        st.plotly_chart(fig, use_container_width=True)
