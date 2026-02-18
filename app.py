import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configurare pagină
st.set_page_config(page_title="Arbitraj Sportiv PRO", layout="wide", page_icon="💰")

# Stil vizual pentru Sidebar
st.sidebar.title("⚙️ Panou de Control")
api_key = st.sidebar.text_input("Introdu Cheia API", type="password", help="Cheia primită de la The Odds API")
buget = st.sidebar.number_input("Buget Total (RON)", value=1000, step=50)

# Stocare istoric în sesiune
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💰 Scanner Surebet - Multi-Sport")
st.markdown("---")

# Butonul principal
if st.button("🚀 PORNEȘTE SCANAREA"):
    if not api_key:
        st.error("⚠️ Te rugăm să introduci cheia API în meniul din stânga!")
    else:
        with st.spinner("🔎 Analizăm cotele globale în timp real..."):
            try:
                # URL INTEGRAT: Căutăm 'upcoming' pentru a evita eroarea 404 (sporturi inexistente)
                # Această rută aduce meciuri din toate sporturile active acum
                url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                
                response = requests.get(url)
                
                if response.status_code == 401:
                    st.error("❌ Cheia API este invalidă. Verifică e-mailul de confirmare!")
                elif response.status_code == 404:
                    st.error("❌ Eroare 404: Resursa nu a fost găsită. Încearcă să schimbi regiunea în cod.")
                elif response.status_code == 429:
                    st.error("⚠️ Limită atinsă! Planul gratuit permite un număr limitat de cereri.")
                elif response.status_code != 200:
                    st.error(f"❌ Problemă tehnică: Cod {response.status_code}")
                else:
                    data = response.json()
                    
                    if not data:
                        st.info("ℹ️ Nu există meciuri listate în acest moment. Revino peste câteva minute.")
                    else:
                        found_count = 0
                        for game in data:
                            home = game.get('home_team')
                            away = game.get('away_team')
                            sport = game.get('sport_title', 'Sport necunoscut')
                            
                            best_h = {'p': 0, 'b': ''}
                            best_a = {'p': 0, 'b': ''}
                            
                            # Căutăm cele mai bune cote în lista de bookmakeri
                            for bk in game.get('bookmakers', []):
                                for mkt in bk.get('markets', []):
                                    if mkt['key'] == 'h2h':
                                        for out in mkt['outcomes']:
                                            if out['name'] == home and out['price'] > best_h['p']:
                                                best_h = {'p': out['price'], 'b': bk['title']}
                                            elif out['name'] == away and out['price'] > best_a['p']:
                                                best_a = {'p': out['price'], 'b': bk['title']}
                            
                            # Calculăm dacă există Arbitraj (Profit garantat)
                            if best_h['p'] > 1 and best_a['p'] > 1:
                                margin = (1/best_h['p']) + (1/best_a['p'])
                                
                                if margin < 1.0: # ACESTA ESTE UN SUREBET!
                                    found_count += 1
                                    profit_pct = (1 - margin) * 100
                                    s1 = ( (1/best_h['p']) / margin ) * buget
                                    s2 = ( (1/best_a['p']) / margin ) * buget
                                    
                                    with st.expander(f"⭐ {profit_pct:.2f}% PROFIT | {sport}: {home} vs {away}"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.success(f"**{home}**")
                                            st.write(f"Cota: **{best_h['p']}**")
                                            st.write(f"Casă: {best_h['b']}")
                                            st.info(f"Miză: **{round(s1, 2)} RON**")
                                        with col2:
                                            st.success(f"**{away}**")
                                            st.write(f"Cota: **{best_a['p']}**")
                                            st.write(f"Casă: {best_a['b']}")
                                            st.info(f"Miză: **{round(s2, 2)} RON**")
                                        
                                        if st.button(f"Confirmă Pariu: {home[:10]}", key=f"save_{home}_{found_count}"):
                                            st.session_state.history.append({
                                                "Ora": datetime.now().strftime("%H:%M"), 
                                                "Meci": f"{home} vs {away}",
                                                "Profit": round(buget*(profit_pct/100), 2)
                                            })
                                            st.toast("Pariu salvat în istoric!")

                        if found_count == 0:
                            st.warning("📉 Scanare terminată. Nu au fost găsite oportunități de arbitraj în cotele actuale.")
                        else:
                            st.balloons()
                            st.success(f"Am găsit {found_count} oportunități de profit!")

            except Exception as e:
                st.error(f"🚨 Eroare neașteptată la procesare: {str(e)}")

# Afișare Analitice
if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 Rezumatul Performanței")
    df = pd.DataFrame(st.session_state.history)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Total Pariuri Salvate", len(df))
        st.metric("Profit Total", f"{df['Profit'].sum():.2f} RON")
    with c2:
        fig = px.bar(df, x="Ora", y="Profit", title
