import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configurare pagină
st.set_page_config(page_title="Arbitraj Sportiv PRO", layout="wide", page_icon="💰")

# 2. Sidebar pentru setări
st.sidebar.title("⚙️ Panou de Control")
api_key = st.sidebar.text_input("Introdu Cheia API", type="password")
buget = st.sidebar.number_input("Buget Total (RON)", value=1000, step=50)

# 3. Inițializare istoric
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💰 Scanner Surebet - Multi-Sport")
st.markdown("---")

# 4. Butonul principal de scanare
if st.button("🚀 PORNEȘTE SCANAREA"):
    if not api_key:
        st.error("⚠️ Te rugăm să introduci cheia API în meniul din stânga!")
    else:
        with st.spinner("🔎 Analizăm cotele globale în timp real..."):
            try:
                # Folosim 'upcoming' pentru a evita eroarea 404
                url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={api_key}&regions=eu&markets=h2h"
                response = requests.get(url)
                
                if response.status_code != 200:
                    st.error(f"❌ Problemă API: Cod {response.status_code}")
                else:
                    data = response.json()
                    if not data:
                        st.info("ℹ️ Nu există meciuri listate în acest moment.")
                    else:
                        found_count = 0
                        for game in data:
                            home = game.get('home_team')
                            away = game.get('away_team')
                            sport = game.get('sport_title', 'Sport')
                            
                            best_h = {'p': 0, 'b': ''}
                            best_a = {'p': 0, 'b': ''}
                            
                            for bk in game.get('bookmakers', []):
                                for mkt in bk.get('markets', []):
                                    if mkt['key'] == 'h2h':
                                        for out in mkt['outcomes']:
                                            if out['name'] == home and out['price'] > best_h['p']:
                                                best_h = {'p': out['price'], 'b': bk['title']}
                                            elif out['name'] == away and out['price'] > best_a['p']:
                                                best_a = {'p': out['price'], 'b': bk['title']}
                            
                            if best_h['p'] > 1 and best_a['p'] > 1:
                                margin = (1/best_h['p']) + (1/best_a['p'])
                                if margin < 1.0:
                                    found_count += 1
                                    profit_pct = (1 - margin) * 100
                                    s1 = ( (1/best_h['p']) / margin ) * buget
                                    s2 = ( (1/best_a['p']) / margin ) * buget
                                    
                                    with st.expander(f"⭐ {profit_pct:.2f}% PROFIT | {sport}: {home} vs {away}"):
                                        st.success(f"**{home}** ({best_h['p']}) la {best_h['b']} -> **{round(s1, 2)} RON**")
                                        st.success(f"**{away}** ({best_a['p']}) la {best_a['b']} -> **{round(s2, 2)} RON**")
                                        
                                        if st.button(f"Salvează {home[:10]}", key=f"btn_{home}_{found_count}"):
                                            st.session_state.history.append({
                                                "Ora": datetime.now().strftime("%H:%M"), 
                                                "Profit": round(buget*(profit_pct/100), 2)
                                            })
                        
                        if found_count == 0:
                            st.warning("📉 Scanare terminată. Nu au fost găsite oportunități acum.")
                        else:
                            st.balloons()

            except Exception as e:
                st.error(f"🚨 Eroare neașteptată: {str(e)}")

# 5. Afișare Analitice (Secțiunea cu eroarea de paranteză corectată)
if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 Rezumat Profit")
    df = pd.DataFrame(st.session_state.history)
    
    col1, col2 = st.columns([1, 2])
    col1.metric("Profit Total", f"{df['Profit'].sum():.2f} RON")
    
    # Aici era paranteza lipsă - acum este închisă corect:
    fig = px.bar(df, x="Ora", y="Profit", title="Profit per Eveniment")
    col2.plotly_chart(fig, use_container_width=True)
