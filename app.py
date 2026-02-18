import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare pagină
st.set_page_config(page_title="Scanner Profit Garantat", layout="wide", page_icon="📈")

# Stil vizual (CSS) pentru a face cardurile mai lizibile
st.markdown("""
    <style>
    .stSuccess { background-color: #f0fff4; border: 1px solid #c6f6d5; padding: 20px; border-radius: 10px; }
    .stWarning { background-color: #fffaf0; border: 1px solid #feebc8; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Configurare simplă
st.sidebar.header("🚀 Setări Scanner")
api_key = st.sidebar.text_input("Cheia API (The Odds API)", type="password")
buget = st.sidebar.number_input("Suma totală pe care o pariezi (RON)", value=1000, step=100)

# Filtru case consacrate
st.sidebar.subheader("🏦 Case de Pariuri Monitorizate")
st.sidebar.info("Scannerul verifică: Unibet, Betfair, 888Sport, William Hill, Betano, Pinnacle, Bwin.")

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💰 Ghid Pariuri Fără Risc (Arbitraj)")
st.write("Aplicația caută diferențe de cote între casele mari și calculează miza optimă pentru profit garantat.")

# 3. Butonul de execuție
if st.button("🔎 CAUTĂ OCAZII DE PARIERE"):
    if not api_key:
        st.error("⚠️ Te rugăm să introduci cheia API în stânga pentru a începe.")
    else:
        with st.spinner("Se scanează piețele de Fotbal și Tenis..."):
            try:
                # Interogăm API-ul pentru evenimentele viitoare
                url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                
                if response.status_code != 200:
                    st.error(f"Eroare API (Cod {response.status_code}). Verifică dacă cheia este corectă.")
                else:
                    data = response.json()
                    found_count = 0
                    
                    for game in data:
                        home = game.get('home_team')
                        away = game.get('away_team')
                        sport = game.get('sport_title')
                        
                        best_h = {'p': 0, 'b': ''}
                        best_a = {'p': 0, 'b': ''}
                        
                        # Lista caselor "consacrate" (numele din API)
                        consacrate = ['Unibet', 'Betfair', '888sport', 'William Hill', 'Pinnacle', 'Betano', 'Bwin', 'Ladbrokes']

                        for bk in game.get('bookmakers', []):
                            if bk['title'] in consacrate:
                                for mkt in bk.get('markets', []):
                                    if mkt['key'] == 'h2h':
                                        for out in mkt['outcomes']:
                                            if out['name'] == home and out['price'] > best_h['p']:
                                                best_h = {'p': out['price'], 'b': bk['title']}
                                            elif out['name'] == away and out['price'] > best_a['p']:
                                                best_a = {'p': out['price'], 'b': bk['title']}
                        
                        # Calcul Arbitraj
                        if best_h['p'] > 1 and best_a['p'] > 1:
                            margin = (1/best_h['p']) + (1/best_a['p'])
                            
                            if margin < 1.0:
                                found_count += 1
                                profit_pct = (1 - margin) * 100
                                s1 = ( (1/best_h['p']) / margin ) * buget
                                s2 = ( (1/best_a['p']) / margin ) * buget
                                total_profit = buget * (profit_pct/100)

                                st.subheader(f"✅ OCAZIE GĂSITĂ: {home} vs {away}")
                                st.info(f"Sport: {sport} | Profit garantat la final: **{round(total_profit, 2)} RON** ({round(profit_pct, 2)}%)")
                                
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.success(f"**PARIUL 1**\n\n🏠 Echipa: **{home}**\n\n🏦 Casa: **{best_h['b']}**\n\n📈 Cota: **{best_h['p']}**\n\n💰 Miză: **{round(s1, 2)} RON**")
                                with c2:
                                    st.success(f"**PARIUL 2**\n\n🚀 Echipa: **{away}**\n\n🏦 Casa: **{best_a['b']}**\n\n📈 Cota: **{best_a['a' if 'a' in best_a else 'p']}**\n\n💰 Miză: **{round(s2, 2)} RON**")
                                
                                if st.button(f"Înregistrează Profit {round(total_profit, 1)} RON", key=f"rec_{found_count}"):
                                    st.session_state.history.append({
                                        "Timp": datetime.now().strftime("%H:%M"), 
                                        "Profit": total_profit
                                    })
                                st.markdown("---")

                    if found_count == 0:
                        st.warning("📉 Nu am găsit oportunități între casele consacrate în acest moment. Revino peste 15 minute.")
                    else:
                        st.balloons()

            except Exception as e:
                st.error(f"Eroare: {str(e)}")

# Istoric
if st.session_state.history:
    st.subheader("📊 Rezultatele tale de astăzi")
    df = pd.DataFrame(st.session_state.history)
    st.metric("Total Profit acumulat", f"{df['Profit'].sum():.2f} RON")
    fig = px.bar(df, x="Timp", y="Profit", color_discrete_sequence=['#2ecc71'])
    st.plotly_chart(fig, use_container_width=True)
