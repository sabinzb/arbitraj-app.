import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configurare pagină
st.set_page_config(page_title="Arbitraj Sportiv RO", layout="wide")

st.sidebar.title("⚙️ Setări")
api_key = st.sidebar.text_input("Cheie API (The Odds API)", type="password")
buget = st.sidebar.number_input("Buget Total (RON)", value=1000)

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💰 Scanner Arbitraj Sportiv")

if st.button("🚀 SCANEAZĂ ACUM"):
    if not api_key:
        st.error("⚠️ Te rugăm să introduci cheia API în bara laterală!")
    else:
        with st.spinner("🔎 Se verifică cotele în timp real..."):
            try:
                # Interogăm API-ul
                url = f"https://api.the-odds-api.com/v4/sports/tennis_atp/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                
                if response.status_code == 401:
                    st.error("❌ Eroare 401: Cheia API este invalidă sau nu a fost activată.")
                elif response.status_code == 429:
                    st.error("⚠️ Eroare 429: Ai atins limita de scanări (500/lună). Revino mai târziu!")
                elif response.status_code != 200:
                    st.error(f"❌ Eroare neașteptată: Cod {response.status_code}")
                else:
                    data = response.json()
                    
                    if not data or not isinstance(data, list):
                        st.info("ℹ️ Nu sunt meciuri de tenis disponibile acum. Încearcă mai târziu.")
                    else:
                        found = False
                        for game in data:
                            # Verificăm dacă datele meciului sunt complete
                            if 'home_team' not in game or 'bookmakers' not in game:
                                continue
                                
                            home = game['home_team']
                            away = game['away_team']
                            
                            best_h = {'p': 0, 'b': ''}
                            best_a = {'p': 0, 'b': ''}
                            
                            for bk in game['bookmakers']:
                                for mkt in bk['markets']:
                                    if mkt['key'] == 'h2h':
                                        for out in mkt['outcomes']:
                                            if out['name'] == home and out['price'] > best_h['p']:
                                                best_h = {'p': out['price'], 'b': bk['title']}
                                            elif out['name'] == away and out['price'] > best_a['p']:
                                                best_a = {'p': out['price'], 'b': bk['title']}
                            
                            if best_h['p'] > 1 and best_a['p'] > 1:
                                margin = (1/best_h['p']) + (1/best_a['p'])
                                if margin < 1.0:
                                    found = True
                                    profit_pct = (1 - margin) * 100
                                    s1 = ( (1/best_h['p']) / margin ) * buget
                                    s2 = ( (1/best_a['p']) / margin ) * buget
                                    
                                    with st.expander(f"✅ PROFIT {profit_pct:.2f}% | {home} vs {away}"):
                                        st.write(f"📍 **{home}**: {best_h['p']} ({best_h['b']}) -> **{round(s1, 2)} RON**")
                                        st.write(f"📍 **{away}**: {best_a['p']} ({best_a['b']}) -> **{round(s2, 2)} RON**")
                                        if st.button(f"Salvează Profit {home}", key=f"btn_{home}"):
                                            st.session_state.history.append({
                                                "Data": datetime.now().strftime("%H:%M"), 
                                                "Profit": round(buget*(profit_pct/100), 2)
                                            })
                        if not found:
                            st.warning("📉 Scanare completă: Nu am găsit arbitraj acum (marja caselor este peste 100%).")
            except Exception as e:
                st.error(f"🚨 Eroare critică în aplicație: {str(e)}")

# Afișare Istoric și Grafic
if st.session_state.history:
    st.divider()
    st.subheader("📈 Performanța Ta")
    df_hist = pd.DataFrame(st.session_state.history)
    fig = px.line(df_hist, x="Data", y="Profit", title="Evoluție Profit (RON)", markers=True)
    st.plotly_chart(fig, use_container_width=True)
