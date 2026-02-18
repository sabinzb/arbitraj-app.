import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Arbitraj Sportiv RO", layout="wide")

# Interfață Sidebar
st.sidebar.title("⚙️ Setări")
api_key = st.sidebar.text_input("Cheie API (The Odds API)", type="password")
buget = st.sidebar.number_input("Buget Total (RON)", value=1000)

# Istoric în sesiune
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💰 Scanner Arbitraj Sportiv")

if st.button("🚀 SCANEAZĂ ACUM"):
    if not api_key:
        st.error("Introdu cheia API în stânga!")
    else:
        with st.spinner("Caut cotele..."):
            # Exemplu pentru Tenis (poți schimba sportul)
            url = f"https://api.the-odds-api.com/v4/sports/tennis_atp/odds/?apiKey={api_key}&regions=eu&markets=h2h"
            data = requests.get(url).json()
            
            found = False
            for game in data:
                home = game['home_team']
                away = game['away_team']
                
                # Logică simplificată de identificare cele mai bune cote
                best_h = {'p': 0, 'b': ''}
                best_a = {'p': 0, 'b': ''}
                
                for bk in game['bookmakers']:
                    for mkt in bk['markets']:
                        for out in mkt['outcomes']:
                            if out['name'] == home and out['price'] > best_h['p']:
                                best_h = {'p': out['price'], 'b': bk['title']}
                            elif out['name'] == away and out['price'] > best_a['p']:
                                best_a = {'p': out['price'], 'b': bk['title']}
                
                if best_h['p'] > 0 and best_a['p'] > 0:
                    margin = (1/best_h['p']) + (1/best_a['p'])
                    if margin < 1.0:
                        found = True
                        profit_pct = (1 - margin) * 100
                        s1 = ( (1/best_h['p']) / margin ) * buget
                        s2 = ( (1/best_a['p']) / margin ) * buget
                        
                        with st.expander(f"✅ PROFIT {profit_pct:.2f}% | {home} vs {away}"):
                            st.write(f"📍 **{home}**: {best_h['p']} ({best_h['b']}) -> **{round(s1, 2)} RON**")
                            st.write(f"📍 **{away}**: {best_a['p']} ({best_a['b']}) -> **{round(s2, 2)} RON**")
                            if st.button(f"Salvează Profit {home}", key=home):
                                st.session_state.history.append({
                                    "Data": datetime.now().strftime("%H:%M"), 
                                    "Profit": round(buget*(profit_pct/100), 2)
                                })
            if not found: st.info("Nu am găsit oportunități în acest moment.")

# Afișare Istoric
if st.session_state.history:
    st.divider()
    df_hist = pd.DataFrame(st.session_state.history)
    st.subheader("📈 Evoluție Profit")
    fig = px.line(df_hist, x="Data", y="Profit", markers=True)
    st.plotly_chart(fig)
