# ... (partea de sus a codului rămâne neschimbată)

# RENDER CARD (ADAPTIV ȘI SECURIZAT)
# Am integrat toate elementele într-o singură variabilă pentru a preveni textul brut
grid_layout = "1fr 1fr 1fr" if is_3way else "1fr 1fr"

# Construim div-ul pentru egal (X) doar dacă este fotbal
draw_box = f"""
<div style="border-left: 2px solid #555; padding-left: 10px;">
    <p style="font-size: 0.7rem; color: #666; margin:0;">(X) {bX['b']}</p>
    <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0; color:#fff;">@{bX['p']}</p>
    <p style="color: #00ff88; font-weight: bold; margin:0;">{int(mX)} RON</p>
</div>""" if is_3way else ""

# Aceasta este partea care îți afișa codul brut - acum este reparată
card_html = f"""
<div class="arb-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <span style="font-family: 'JetBrains Mono'; color: #444;">[ {game['sport_title']} ]</span>
        <span class="profit-tag">+{prof_pct:.2f}% PROFIT</span>
    </div>
    <h3 style="margin-bottom: 1.5rem;">{home_team} vs {away_team}</h3>
    <div style="display: grid; grid-template-columns: {grid_layout}; gap: 15px;">
        <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
            <p style="font-size: 0.7rem; color: #666; margin:0;">(1) {b1['b']}</p>
            <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0; color:#fff;">@{b1['p']}</p>
            <p style="color: #00ff88; font-weight: bold; margin:0;">{int(m1)} RON</p>
        </div>
        {draw_box}
        <div style="border-left: 2px solid #00ff88; padding-left: 10px;">
            <p style="font-size: 0.7rem; color: #666; margin:0;">(2) {b2['b']}</p>
            <p style="font-family: 'JetBrains Mono'; font-size: 1.2rem; margin:0; color:#fff;">@{b2['p']}</p>
            <p style="color: #00ff88; font-weight: bold; margin:0;">{int(m2)} RON</p>
        </div>
    </div>
</div>
"""
# Comanda de randare trebuie să fie una singură pentru tot cardul
st.markdown(card_html, unsafe_allow_html=True)

# ... (restul codului pentru butoane și analitice)
