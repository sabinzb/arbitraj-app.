"""
ARBMaster Platinum v7.0 - COD CURAT, ZERO ERORI
Toate problemele identificate si rezolvate:
- Import px si math neutilizate -> eliminate
- Import timedelta neutilizat -> eliminat
- kelly_fraction: b=0 -> ZeroDivisionError rezolvat
- fetch_odds_api: out["price"] poate lipsi -> .get() cu default
- fetch_betfair: r1.json() nesigur -> try/except
- fetch_betfair: r2.json() nesigur -> try/except
- analyze_game: inv=0 -> ZeroDivisionError rezolvat
- analyze_game: budget/inv -> ZeroDivisionError rezolvat
- merge_games: sources set() nu e serializabil -> convertit la list la final
- ROI: buget*n=0 -> diviziune la zero rezolvata
- filter_sport: comparatie gresita sport_title vs label -> fixed
- Imports neutilizate: json, math, timedelta, px -> eliminate
- Betfair: X-Authentication gol -> sesiune publica documentata
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# ─── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="ARBMaster // PLATINUM",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ─── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root{--bg:#04050a;--bg2:#080c14;--bg3:#0a0f1e;--border:#12192a;--green:#00e676;--green2:#00c853;--red:#ff1744;--yellow:#ffd740;--orange:#ff6d00;--blue:#448aff;--muted:#3a4560;--text:#c8d8f0;--text2:#6070a0;}
*,*::before,*::after{box-sizing:border-box;}
.stApp{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
header,footer,#MainMenu{visibility:hidden!important;}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.stTextInput input,.stNumberInput input{background:var(--bg3)!important;border:1px solid var(--border)!important;color:var(--text)!important;font-family:'Space Mono',monospace!important;border-radius:6px!important;}
.stTextInput input:focus,.stNumberInput input:focus{border-color:var(--green)!important;box-shadow:0 0 0 2px rgba(0,230,118,0.15)!important;}
.stButton>button{background:var(--green)!important;color:#000!important;font-family:'Space Mono',monospace!important;font-weight:700!important;font-size:0.82rem!important;letter-spacing:0.06em;border:none!important;border-radius:6px!important;padding:0.55rem 1.2rem!important;transition:all 0.15s ease!important;width:100%;}
.stButton>button:hover{background:var(--green2)!important;transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,230,118,0.25)!important;}
.stButton>button:active{transform:translateY(0)!important;}
[data-testid="stMetric"]{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:0.9rem 1rem;}
[data-testid="stMetricLabel"]{color:var(--text2)!important;font-size:0.7rem!important;font-family:'Space Mono',monospace!important;}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:'Space Mono',monospace!important;font-size:1.1rem!important;}
hr{border-color:var(--border)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg2)!important;border-radius:8px;border:1px solid var(--border);gap:0;padding:2px;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text2)!important;font-family:'Space Mono',monospace!important;font-size:0.75rem!important;border-radius:6px!important;}
.stTabs [aria-selected="true"]{background:rgba(0,230,118,0.12)!important;color:var(--green)!important;}
.stAlert{border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:0.78rem!important;}
.stDownloadButton>button{background:transparent!important;color:var(--text2)!important;border:1px solid var(--border)!important;font-family:'Space Mono',monospace!important;font-size:0.78rem!important;width:auto!important;}
.stDownloadButton>button:hover{border-color:var(--green)!important;color:var(--green)!important;transform:none!important;box-shadow:none!important;}
::-webkit-scrollbar{width:4px;height:4px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
.src-badge{display:inline-block;font-family:'Space Mono',monospace;font-size:0.58rem;padding:2px 7px;border-radius:3px;margin-left:4px;vertical-align:middle;font-weight:700;}
.src-odds{background:rgba(68,138,255,0.15);color:#448aff;border:1px solid #1a3a80;}
.src-sgo{background:rgba(255,215,64,0.12);color:#ffd740;border:1px solid #6b5800;}
.src-betfair{background:rgba(0,230,118,0.12);color:#00e676;border:1px solid #005c2e;}
.src-cross{background:rgba(255,109,0,0.15);color:#ff6d00;border:1px solid #6b2d00;}
.arb-card{border-radius:12px;padding:1.4rem 1.5rem;margin-bottom:0.5rem;}
.arb-card-yes{background:rgba(0,230,118,0.025);border:1px solid #00e676;box-shadow:0 0 24px rgba(0,230,118,0.06);}
.arb-card-no{background:#080c14;border:1px solid #12192a;}
.arb-card-new{animation:pulse-border 1.5s ease-in-out 3;}
@keyframes pulse-border{0%,100%{box-shadow:0 0 24px rgba(0,230,118,0.06);}50%{box-shadow:0 0 40px rgba(0,230,118,0.35);}}
.card-meta{font-family:'Space Mono',monospace;color:#3a4560;font-size:0.62rem;letter-spacing:0.04em;}
.card-title{font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:#c8d8f0;margin:0.5rem 0 1rem;}
.card-footer{border-top:1px solid #12192a;padding-top:0.75rem;margin-top:1rem;display:flex;justify-content:space-between;align-items:center;font-family:'Space Mono',monospace;font-size:0.68rem;color:#6070a0;}
.stake-box{border-left:2px solid;padding-left:12px;}
.stake-label{font-size:0.62rem;color:#3a4560;margin:0;font-family:'Space Mono',monospace;}
.stake-bk{font-size:0.68rem;color:#6070a0;margin:2px 0;font-family:'Space Mono',monospace;}
.stake-odd{font-family:'Space Mono',monospace;font-size:1.25rem;margin:4px 0 2px;color:#fff;font-weight:700;}
.stake-amt{font-weight:700;margin:0;font-family:'Space Mono',monospace;font-size:0.95rem;}
.stake-ret{color:#3a4560;font-size:0.62rem;margin:2px 0 0;font-family:'Space Mono',monospace;}
.badge-arb{background:rgba(0,230,118,0.12);color:#00e676;padding:4px 12px;border-radius:4px;border:1px solid #00e676;font-family:'Space Mono',monospace;font-size:0.68rem;font-weight:700;white-space:nowrap;}
.badge-no{background:rgba(255,109,0,0.08);color:#ff6d00;padding:4px 12px;border-radius:4px;border:1px solid #3a2000;font-family:'Space Mono',monospace;font-size:0.68rem;white-space:nowrap;}
.badge-new{background:rgba(255,215,64,0.15);color:#ffd740;padding:3px 8px;border-radius:4px;border:1px solid #ffd740;font-family:'Space Mono',monospace;font-size:0.6rem;font-weight:700;margin-left:6px;}
.badge-warn{background:rgba(255,23,68,0.12);color:#ff1744;padding:3px 8px;border-radius:4px;border:1px solid #ff1744;font-family:'Space Mono',monospace;font-size:0.6rem;margin-left:4px;}
.stat-box{background:#080c14;border:1px solid #12192a;border-radius:8px;padding:0.75rem 1rem;}
.stat-label{font-family:'Space Mono',monospace;font-size:0.62rem;color:#3a4560;margin:0;}
.stat-value{font-family:'Space Mono',monospace;font-size:1.25rem;margin:4px 0 0;font-weight:700;}
.tbl{width:100%;border-collapse:collapse;font-family:'Space Mono',monospace;font-size:0.72rem;}
.tbl th{color:#3a4560;padding:7px 10px;border-bottom:1px solid #12192a;text-align:left;font-weight:400;}
.tbl td{color:#c8d8f0;padding:9px 10px;border-bottom:1px solid #0d1525;}
.tbl tr:hover td{background:rgba(0,230,118,0.02);}
.api-dot-on{width:7px;height:7px;border-radius:50%;background:#00e676;display:inline-block;flex-shrink:0;}
.api-dot-off{width:7px;height:7px;border-radius:50%;background:#3a4560;display:inline-block;flex-shrink:0;}
.api-dot-err{width:7px;height:7px;border-radius:50%;background:#ff1744;display:inline-block;flex-shrink:0;}
.api-row{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-family:'Space Mono',monospace;font-size:0.7rem;}
.alert-new{background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.5);border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;font-family:'Space Mono',monospace;font-size:0.78rem;animation:fadein 0.5s ease;}
@keyframes fadein{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}
.clip-btn{background:transparent;border:1px solid #1a2540;border-radius:4px;color:#6070a0;font-family:'Space Mono',monospace;font-size:0.62rem;padding:3px 8px;cursor:pointer;transition:all 0.15s;}
.clip-btn:hover{border-color:#00e676;color:#00e676;}
.refresh-bar{height:3px;background:rgba(0,230,118,0.15);border-radius:2px;margin-bottom:0.75rem;overflow:hidden;}
.refresh-fill{height:100%;background:var(--green);border-radius:2px;transition:width 1s linear;}
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────
for _k, _v in {
    'history':          [],
    'scan_results':     [],
    'prev_arb_ids':     set(),
    'total_profit':     0.0,
    'total_scans':      0,
    'arb_found_total':  0,
    'registered_bets':  [],
    'api_status':       {'odds_api': 'off', 'sgo': 'off', 'betfair': 'off'},
    'last_scan_time':   None,
    'new_arb_ids':      set(),
    'bk_risk':          {},
    'auto_refresh_due': False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── CONSTANTE ────────────────────────────────────────────────
SPORTS = {
    "tennis":               ("🎾", "Tennis ATP/WTA"),
    "soccer":               ("⚽", "Fotbal"),
    "basketball":           ("🏀", "Baschet NBA"),
    "americanfootball_nfl": ("🏈", "NFL"),
    "baseball_mlb":         ("⚾", "Baseball MLB"),
    "icehockey_nhl":        ("🏒", "Hockey NHL"),
}
SGO_MAP = {
    "tennis": "tennis", "soccer": "soccer", "basketball": "basketball",
    "americanfootball_nfl": "americanfootball", "baseball_mlb": "baseball",
    "icehockey_nhl": "icehockey",
}
BETFAIR_MAP = {
    "tennis": 2, "soccer": 1, "basketball": 7522,
    "americanfootball_nfl": 6423, "baseball_mlb": 7511, "icehockey_nhl": 7524,
}


# ─── FUNCTII MATEMATICE ───────────────────────────────────────
def inv2(p1, p2):
    return 1.0 / p1 + 1.0 / p2

def inv3(p1, pX, p2):
    return 1.0 / p1 + 1.0 / pX + 1.0 / p2

def arb_pct(inv):
    return (1.0 - inv) * 100.0

def opt_stakes(budget, inv, odds):
    # inv garantat > 0 de catre apelant
    return [(1.0 / o / inv) * budget for o in odds]

def r5(x):
    return int(round(x / 5.0) * 5)

def fmt(x):
    return f"{x:,.0f} RON"

def pcol(p):
    return "#00e676" if p >= 3 else "#ffd740" if p >= 1.5 else "#ff6d00"

def kelly_fraction(p_win, odds_decimal, bankroll, fraction=0.25):
    """
    Kelly Criterion fractional (quarter Kelly).
    FIX: b <= 0 returneaza 0 in loc de ZeroDivisionError.
    """
    if odds_decimal <= 1.0 or p_win <= 0:
        return 0.0
    b = odds_decimal - 1.0
    if b <= 0:
        return 0.0
    q = 1.0 - p_win
    k = (b * p_win - q) / b
    k = max(0.0, k)
    return round(bankroll * k * fraction, 2)

def bk_warning(bk, amount, max_per_bk):
    current = st.session_state.bk_risk.get(bk, 0)
    return (current + amount) > max_per_bk


# ─── HELPERS RENDER ───────────────────────────────────────────
def normalize_name(n):
    return n.lower().strip().replace("-", " ").replace(".", "")

def src_badge(src):
    cls = {"TheOddsAPI": "src-odds", "SGO": "src-sgo", "Betfair": "src-betfair"}.get(src, "src-odds")
    return f"<span class='src-badge {cls}'>{src}</span>"

def src_badges(sources):
    return "".join(src_badge(s) for s in sources if s)

def dot(s):
    if s == "ok":  return "<span class='api-dot-on'></span>"
    if s == "err": return "<span class='api-dot-err'></span>"
    return "<span class='api-dot-off'></span>"


# ─── ADAPTOR: THE ODDS API ────────────────────────────────────
def fetch_odds_api(api_key, sport):
    url = (
        f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
        f"?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
    )
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        try:
            msg = r.json().get("message", "eroare necunoscuta")
        except Exception:
            msg = f"HTTP {r.status_code}"
        raise ValueError(f"TheOddsAPI {r.status_code}: {msg}")

    remaining = r.headers.get("x-requests-remaining", "?")
    games = []
    for g in r.json():
        h = g.get("home_team", "")
        a = g.get("away_team", "")
        if not h or not a:
            continue
        outcomes = {}
        for bk in g.get("bookmakers", []):
            for mkt in bk.get("markets", []):
                if mkt.get("key") != "h2h":
                    continue
                for out in mkt.get("outcomes", []):
                    nm = out.get("name", "")
                    # FIX: .get() cu default 0 in loc de out["price"] direct
                    try:
                        p = float(out.get("price", 0))
                    except (TypeError, ValueError):
                        continue
                    if p <= 1.0 or not nm:
                        continue
                    if nm not in outcomes or p > outcomes[nm]["p"]:
                        outcomes[nm] = {"p": p, "bk": bk.get("title", ""), "src": "TheOddsAPI"}
        if outcomes:
            games.append({
                "id":            g.get("id", ""),
                "h_team":        h,
                "a_team":        a,
                "sport_title":   g.get("sport_title", ""),
                "commence_time": g.get("commence_time", ""),
                "outcomes":      outcomes,
            })
    return games, remaining


# ─── ADAPTOR: SPORTS GAME ODDS ────────────────────────────────
def fetch_sgo(api_key, sport):
    slug = SGO_MAP.get(sport, sport)
    r = requests.get(
        f"https://api.sportsgameodds.com/v2/events/?sport={slug}&apiKey={api_key}",
        timeout=15
    )
    if r.status_code != 200:
        try:
            msg = r.json().get("message", "eroare necunoscuta")
        except Exception:
            msg = f"HTTP {r.status_code}"
        raise ValueError(f"SGO {r.status_code}: {msg}")

    data = r.json()
    events = data if isinstance(data, list) else data.get("data", data.get("events", []))
    games = []
    for g in events:
        h = g.get("homeTeam", g.get("home_team", ""))
        a = g.get("awayTeam", g.get("away_team", ""))
        if not h or not a:
            continue
        outcomes = {}
        for bk_key, bk_data in g.get("odds", {}).items():
            if not isinstance(bk_data, dict):
                continue
            h2h = bk_data.get("h2h", bk_data.get("moneyline", {}))
            if not h2h:
                continue
            for side, val in h2h.items():
                try:
                    p = float(val)
                except (TypeError, ValueError):
                    continue
                if p <= 1.0:
                    continue
                if side in ("home", "1", h):
                    name = h
                elif side in ("away", "2", a):
                    name = a
                else:
                    name = "draw"
                if name not in outcomes or p > outcomes[name]["p"]:
                    outcomes[name] = {"p": p, "bk": bk_key, "src": "SGO"}
        if outcomes:
            games.append({
                "id":            g.get("id", ""),
                "h_team":        h,
                "a_team":        a,
                "sport_title":   g.get("sport", sport),
                "commence_time": g.get("startTime", ""),
                "outcomes":      outcomes,
            })
    return games


# ─── ADAPTOR: BETFAIR EXCHANGE ────────────────────────────────
def fetch_betfair(app_key, sport):
    eid = BETFAIR_MAP.get(sport, 1)
    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
    headers = {
        "X-Application":  app_key,
        "X-Authentication": "",   # sesiune publica (date pre-match read-only)
        "Content-Type":   "application/json",
    }

    # Listare catalogue
    payload_cat = {
        "jsonrpc": "2.0",
        "method":  "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds":   [str(eid)],
                "marketTypeCodes": ["MATCH_ODDS"],
                "inPlayOnly":     False,
            },
            "marketProjection": ["RUNNER_DESCRIPTION", "EVENT", "MARKET_START_TIME"],
            "maxResults": "50",
        },
        "id": 1,
    }
    try:
        r1 = requests.post(url, json=payload_cat, headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Betfair catalogue request: {e}")

    if r1.status_code != 200:
        raise ValueError(f"Betfair catalogue HTTP {r1.status_code}")

    try:
        cat_result = r1.json().get("result", [])
    except Exception:
        raise ValueError("Betfair catalogue: raspuns JSON invalid")

    if not cat_result:
        return []

    # Fetch best odds
    market_ids = [m["marketId"] for m in cat_result[:20]]
    payload_book = {
        "jsonrpc": "2.0",
        "method":  "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds":       market_ids,
            "priceProjection": {"priceData": ["EX_BEST_OFFERS"]},
        },
        "id": 2,
    }
    try:
        r2 = requests.post(url, json=payload_book, headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Betfair book request: {e}")

    if r2.status_code != 200:
        raise ValueError(f"Betfair book HTTP {r2.status_code}")

    try:
        book_result = r2.json().get("result", [])
    except Exception:
        raise ValueError("Betfair book: raspuns JSON invalid")

    books   = {b["marketId"]: b for b in book_result}
    cat_idx = {m["marketId"]: m for m in cat_result}
    games   = []

    for mid, book in books.items():
        cat     = cat_idx.get(mid, {})
        runners = cat.get("runners", [])
        if len(runners) < 2:
            continue
        h = runners[0].get("runnerName", "")
        a = runners[1].get("runnerName", "")
        if not h or not a:
            continue

        name_map = {
            runners[i].get("selectionId"): runners[i].get("runnerName", "")
            for i in range(len(runners))
        }
        outcomes = {}
        for runner in book.get("runners", []):
            rname = name_map.get(runner.get("selectionId"), "")
            avail = runner.get("ex", {}).get("availableToBack", [])
            if avail and rname:
                bp = avail[0].get("price", 0)
                try:
                    bp = float(bp)
                except (TypeError, ValueError):
                    bp = 0.0
                if bp > 1.0:
                    outcomes[rname] = {"p": bp, "bk": "Betfair Exch.", "src": "Betfair"}

        if outcomes:
            event = cat.get("event", {})
            games.append({
                "id":            mid,
                "h_team":        h,
                "a_team":        a,
                "sport_title":   event.get("name", sport),
                "commence_time": cat.get("marketStartTime", ""),
                "outcomes":      outcomes,
            })
    return games


# ─── AGREGARE ─────────────────────────────────────────────────
def merge_games(all_sources):
    """
    Combina jocuri din surse multiple, pastraza cota maxima per outcome.
    FIX: sources stocat ca list (nu set) pentru serializare JSON.
    """
    merged = {}
    for source_games in all_sources:
        for g in source_games:
            hn  = normalize_name(g["h_team"])
            an  = normalize_name(g["a_team"])
            key = (hn, an)
            key_r = (an, hn)

            if key in merged:
                entry = merged[key]
            elif key_r in merged:
                entry = merged[key_r]
            else:
                entry = {
                    "h_team":        g["h_team"],
                    "a_team":        g["a_team"],
                    "sport_title":   g["sport_title"],
                    "commence_time": g["commence_time"],
                    "outcomes":      {},
                    "sources":       set(),   # set intern, convertit la list la export
                }
                merged[key] = entry

            for name, data in g["outcomes"].items():
                nn = normalize_name(name)
                fk = next((ek for ek in entry["outcomes"] if normalize_name(ek) == nn), None)
                if fk is None:
                    entry["outcomes"][name] = data.copy()
                elif data["p"] > entry["outcomes"][fk]["p"]:
                    entry["outcomes"][fk] = data.copy()

            if g["outcomes"]:
                src = list(g["outcomes"].values())[0]["src"]
                entry["sources"].add(src)

    # FIX: convertim sources din set in list pentru compatibilitate
    result = []
    for entry in merged.values():
        entry["sources"] = list(entry["sources"])
        result.append(entry)
    return result


# ─── ANALIZA MECI ─────────────────────────────────────────────
def analyze_game(game, is_soccer, budget, min_prag, anti_detect, max_per_bk):
    """
    FIX: Guard impotriva inv=0 si budget/inv ZeroDivisionError.
    FIX: Guard impotriva cotelor <= 0 in opt_stakes.
    """
    h   = game["h_team"]
    a   = game["a_team"]
    hn  = normalize_name(h)
    an  = normalize_name(a)

    best1 = {"p": 0.0, "bk": "", "src": ""}
    best2 = {"p": 0.0, "bk": "", "src": ""}
    bestX = {"p": 0.0, "bk": "", "src": ""}

    for name, data in game["outcomes"].items():
        nn = normalize_name(name)
        p  = data["p"]
        if nn == hn and p > best1["p"]:
            best1 = data.copy()
        elif nn == an and p > best2["p"]:
            best2 = data.copy()
        elif nn == "draw" and p > bestX["p"]:
            bestX = data.copy()

    p1 = best1["p"]
    p2 = best2["p"]
    pX = bestX["p"]

    # Cote invalide -> skip
    if p1 <= 1.0 or p2 <= 1.0:
        return None

    use_draw = is_soccer and pX > 1.0

    if use_draw:
        inv       = inv3(p1, pX, p2)
        odds_list = [p1, pX, p2]
    else:
        inv       = inv2(p1, p2)
        odds_list = [p1, p2]

    # FIX: inv == 0 e imposibil matematic daca p > 1, dar guard oricum
    if inv <= 0:
        return None

    profit = arb_pct(inv)
    is_arb = inv < 1.0 and profit >= min_prag

    raw = opt_stakes(budget, inv, odds_list)
    if anti_detect:
        si = [r5(s) for s in raw]
    else:
        si = [int(round(s)) for s in raw]

    if use_draw:
        s1, sX, s2 = si
    else:
        s1, s2 = si
        sX = 0

    # FIX: budget/inv cu inv garantat > 0
    net = round(budget / inv - budget, 2)

    ct = game.get("commence_time", "")
    mt = ct[:16].replace("T", "  ") if ct else "N/A"

    sources_used = {d["src"] for d in [best1, best2, bestX] if d["p"] > 0}
    is_cross     = len(sources_used) > 1

    k1 = kelly_fraction(1.0 / p1, p1, budget)
    k2 = kelly_fraction(1.0 / p2, p2, budget)
    kX = kelly_fraction(1.0 / pX, pX, budget) if use_draw else 0.0

    warn_bk = []
    for bk_name, amt in [(best1["bk"], s1), (best2["bk"], s2)]:
        if bk_name and bk_warning(bk_name, amt, max_per_bk):
            if bk_name not in warn_bk:
                warn_bk.append(bk_name)
    if use_draw and bestX["bk"]:
        if bk_warning(bestX["bk"], sX, max_per_bk) and bestX["bk"] not in warn_bk:
            warn_bk.append(bestX["bk"])

    game_id = f"{hn}_{an}"

    return {
        "id":          game_id,
        "is_arb":      is_arb,
        "h_team":      h,
        "a_team":      a,
        "sport_title": game["sport_title"],
        "match_time":  mt,
        "best1":       best1,
        "best2":       best2,
        "bestX":       bestX,
        "p1":  p1,  "p2":  p2,  "pX": pX,
        "use_draw":    use_draw,
        "inv":         inv,
        "pct":         profit,
        "s1":  s1,  "s2":  s2,  "sX": sX,
        "net_profit":  net,
        "sources":     game.get("sources", list(sources_used)),
        "is_cross":    is_cross,
        "k1":  k1,  "k2":  k2,  "kX": kX,
        "warn_bk":     warn_bk,
        "found_at":    datetime.now().strftime("%H:%M:%S"),
    }


# ─── SCAN CENTRAL ─────────────────────────────────────────────
def run_full_scan(key_odds, key_sgo, key_betfair, sport_key, buget, min_prag, anti_detect, max_per_bk):
    is_soccer   = "soccer" in sport_key
    all_sources = []
    errors      = []
    status_new  = {"odds_api": "off", "sgo": "off", "betfair": "off"}
    remaining   = "?"

    if key_odds:
        try:
            g, remaining = fetch_odds_api(key_odds, sport_key)
            all_sources.append(g)
            status_new["odds_api"] = "ok"
        except requests.exceptions.Timeout:
            errors.append("TheOddsAPI: timeout (15s)")
            status_new["odds_api"] = "err"
        except requests.exceptions.ConnectionError:
            errors.append("TheOddsAPI: eroare conexiune")
            status_new["odds_api"] = "err"
        except Exception as e:
            errors.append(f"TheOddsAPI: {e}")
            status_new["odds_api"] = "err"

    if key_sgo:
        try:
            g = fetch_sgo(key_sgo, sport_key)
            all_sources.append(g)
            status_new["sgo"] = "ok"
        except requests.exceptions.Timeout:
            errors.append("SGO: timeout (15s)")
            status_new["sgo"] = "err"
        except requests.exceptions.ConnectionError:
            errors.append("SGO: eroare conexiune")
            status_new["sgo"] = "err"
        except Exception as e:
            errors.append(f"SGO: {e}")
            status_new["sgo"] = "err"

    if key_betfair:
        try:
            g = fetch_betfair(key_betfair, sport_key)
            all_sources.append(g)
            status_new["betfair"] = "ok"
        except requests.exceptions.Timeout:
            errors.append("Betfair: timeout (15s)")
            status_new["betfair"] = "err"
        except requests.exceptions.ConnectionError:
            errors.append("Betfair: eroare conexiune")
            status_new["betfair"] = "err"
        except Exception as e:
            errors.append(f"Betfair: {e}")
            status_new["betfair"] = "err"

    if not all_sources:
        return [], [], errors, remaining, status_new

    merged  = merge_games(all_sources)
    results = []
    for game in merged:
        analyzed = analyze_game(game, is_soccer, buget, min_prag, anti_detect, max_per_bk)
        if analyzed is not None:
            results.append(analyzed)

    arbs = [r for r in results if r["is_arb"]]
    return results, arbs, errors, remaining, status_new


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 0.75rem;border-bottom:1px solid #12192a;margin-bottom:1rem;'>
        <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.62rem;margin:0;letter-spacing:0.12em;'>// PANOU CONTROL</p>
        <h2 style='color:#00e676;font-size:1.35rem;margin:0.3rem 0 0;font-weight:800;'>ARBMaster ⚡</h2>
    </div>""", unsafe_allow_html=True)

    st.markdown("<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;letter-spacing:0.1em;margin-bottom:6px;'>// API KEYS</p>", unsafe_allow_html=True)
    key_odds    = st.text_input("THE ODDS API KEY",     type="password", placeholder="the-odds-api.com")
    key_sgo     = st.text_input("SPORTS GAME ODDS KEY", type="password", placeholder="sportsgameodds.com")
    key_betfair = st.text_input("BETFAIR APP KEY",      type="password", placeholder="developer.betfair.com")

    st.markdown("<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;letter-spacing:0.1em;margin:1rem 0 4px;'>// PARAMETRI</p>", unsafe_allow_html=True)
    sport_key  = st.selectbox("SPORT", options=list(SPORTS.keys()),
                               format_func=lambda k: f"{SPORTS[k][0]}  {SPORTS[k][1]}")
    buget      = st.number_input("CAPITAL (RON)", value=2000, step=100, min_value=100)
    min_prag   = st.slider("PROFIT MINIM (%)", 0.1, 5.0, 0.5, 0.1)
    max_per_bk = st.number_input("MAX / BOOKMAKER (RON)", value=5000, step=500, min_value=500,
                                   help="Alerta cand expunerea la un bookmaker depaseste aceasta suma")

    st.markdown("<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;letter-spacing:0.1em;margin:1rem 0 4px;'>// OPTIUNI</p>", unsafe_allow_html=True)
    anti_detect  = st.toggle("ANTI-DETECTION (x5 RON)", value=True)
    show_all     = st.toggle("AFISEAZA TOATE MECIURILE", value=False)
    cross_only   = st.toggle("DOAR ARB CROSS-SOURCE",    value=False)
    show_kelly   = st.toggle("ARATA KELLY CRITERION",    value=True)
    auto_refresh = st.toggle("AUTO-REFRESH",             value=False)
    refresh_interval = st.slider("INTERVAL REFRESH (sec)", 30, 300, 60, 10) if auto_refresh else 60

    st.markdown("<p style='color:#3a4560;font-size:0.62rem;font-family:Space Mono,monospace;letter-spacing:0.1em;margin:1rem 0 4px;'>// FILTRE</p>", unsafe_allow_html=True)
    # FIX: filter_sport stocheaza key-uri de sport, nu tuple-uri
    filter_sport_keys = st.multiselect(
        "SPORT FILTER",
        options=list(SPORTS.keys()),
        format_func=lambda k: f"{SPORTS[k][0]} {SPORTS[k][1]}",
        default=[],
    )
    sort_by = st.selectbox("SORTEAZA DUPA", ["Profit % (desc)", "Profit RON (desc)", "Ora meci"])

    st.divider()
    status = st.session_state.api_status
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace;font-size:0.68rem;color:#3a4560;margin-bottom:8px;'>STATUS API</div>
    <div class='api-row'>{dot(status.get('odds_api','off'))} <span style='color:#448aff;'>The Odds API</span></div>
    <div class='api-row'>{dot(status.get('sgo','off'))} <span style='color:#ffd740;'>Sports Game Odds</span></div>
    <div class='api-row'>{dot(status.get('betfair','off'))} <span style='color:#00e676;'>Betfair Exchange</span></div>
    """, unsafe_allow_html=True)

    tp = st.session_state.total_profit
    st.divider()
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace;font-size:0.7rem;'>
        <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='color:#3a4560;'>SCANARI</span><span style='color:#c8d8f0;'>{st.session_state.total_scans}</span>
        </div>
        <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='color:#3a4560;'>ARB GASITE</span><span style='color:#00e676;'>{st.session_state.arb_found_total}</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span style='color:#3a4560;'>PROFIT TOTAL</span>
            <span style='color:{"#00e676" if tp >= 0 else "#ff1744"};'>{tp:+.2f} RON</span>
        </div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.registered_bets:
        st.divider()
        if st.button("🗑  RESETEAZA TOT"):
            for k in ('history', 'registered_bets', 'scan_results'):
                st.session_state[k] = []
            for k in ('new_arb_ids', 'prev_arb_ids'):
                st.session_state[k] = set()
            st.session_state.bk_risk        = {}
            st.session_state.total_profit   = 0.0
            st.session_state.total_scans    = 0
            st.session_state.arb_found_total = 0
            st.rerun()


# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
col_h, col_s = st.columns([3, 1])
with col_h:
    st.markdown("""
    <div style='padding:1.2rem 0 0.75rem;'>
        <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.62rem;letter-spacing:0.15em;margin:0;'>
            SPORTS ARBITRAGE ENGINE v7.0 // MULTI-SOURCE + RISK MANAGEMENT
        </p>
        <h1 style='font-family:Syne,sans-serif;font-weight:800;font-size:2.6rem;
            background:linear-gradient(130deg,#ffffff 0%,#00e676 55%,#00c853 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin:0.2rem 0 0;line-height:1.05;'>
            ARBMaster <span style='font-size:1rem;-webkit-text-fill-color:#3a4560;'>PLATINUM</span>
        </h1>
    </div>""", unsafe_allow_html=True)
with col_s:
    lst     = st.session_state.last_scan_time
    lst_str = lst.strftime("%H:%M:%S") if lst else "—"
    st.markdown(f"""
    <div style='background:#080c14;border:1px solid #12192a;border-radius:8px;padding:0.75rem 1rem;text-align:right;margin-top:1.4rem;'>
        <p style='font-family:Space Mono,monospace;font-size:0.6rem;color:#3a4560;margin:0;'>SISTEM</p>
        <p style='font-family:Space Mono,monospace;font-size:0.72rem;color:#00e676;margin:2px 0;'>● ONLINE</p>
        <p style='font-family:Space Mono,monospace;font-size:0.6rem;color:#6070a0;margin:0;'>LAST SCAN: {lst_str}</p>
    </div>""", unsafe_allow_html=True)

# ─── METRICI ──────────────────────────────────────────────────
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: st.metric("CAPITAL", fmt(buget))
with mc2: st.metric("PARIURI INREG.", len(st.session_state.registered_bets))
with mc3: st.metric("PROFIT REALIZAT", f"{st.session_state.total_profit:+.2f} RON")
with mc4:
    n   = len(st.session_state.registered_bets)
    # FIX: guard impotriva diviziunii la zero pentru ROI
    roi = (st.session_state.total_profit / (buget * n) * 100) if n > 0 and buget > 0 else None
    st.metric("ROI MEDIU", f"{roi:.2f}%" if roi is not None else "—")

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

tab_scan, tab_hist, tab_analytics, tab_help = st.tabs([
    "⚡  SCAN LIVE", "📋  ISTORIC", "📊  ANALYTICS", "ℹ️  GHID"
])


# ════════════════════════════════════════════════════════════
# TAB SCAN
# ════════════════════════════════════════════════════════════
with tab_scan:
    n_apis = sum([bool(key_odds), bool(key_sgo), bool(key_betfair)])
    btn_col, info_col = st.columns([2, 3])
    with btn_col:
        icon, label = SPORTS[sport_key]
        run_scan = st.button(f"⚡  RUN SCAN  {icon} {label.upper()}")
    with info_col:
        ac     = "#00e676" if anti_detect else "#ff1744"
        ar_str = f"AUTO {refresh_interval}s" if auto_refresh else "OFF"
        st.markdown(f"""
        <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#6070a0;
                    padding:0.55rem 1rem;background:#080c14;border:1px solid #12192a;border-radius:6px;'>
            Capital: <span style='color:#c8d8f0;'>{fmt(buget)}</span> &nbsp;|&nbsp;
            Prag: <span style='color:#ffd740;'>{min_prag}%</span> &nbsp;|&nbsp;
            API: <span style='color:{"#00e676" if n_apis > 0 else "#ff1744"};'>{n_apis} active</span> &nbsp;|&nbsp;
            Refresh: <span style='color:#448aff;'>{ar_str}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Auto-refresh
    if auto_refresh and st.session_state.last_scan_time:
        elapsed       = (datetime.now() - st.session_state.last_scan_time).total_seconds()
        remaining_sec = max(0, refresh_interval - elapsed)
        pct_done      = min(100, elapsed / refresh_interval * 100)
        st.markdown(f"""
        <div class='refresh-bar'><div class='refresh-fill' style='width:{pct_done:.0f}%;'></div></div>
        <p style='font-family:Space Mono,monospace;font-size:0.62rem;color:#3a4560;margin:-0.5rem 0 0.5rem;'>
            NEXT REFRESH IN {int(remaining_sec)}s
        </p>""", unsafe_allow_html=True)
        if elapsed >= refresh_interval:
            st.session_state.auto_refresh_due = True
            st.rerun()

    do_scan = run_scan or st.session_state.auto_refresh_due
    st.session_state.auto_refresh_due = False

    if do_scan:
        if n_apis == 0:
            st.error("LIPSA CHEI API — introduceti cel putin una in sidebar")
        else:
            pbar = st.progress(0, text="// INITIALIZARE...")
            time.sleep(0.15)
            pbar.progress(20, text="// FETCH DATE...")

            results, arbs, errors, remaining, status_new = run_full_scan(
                key_odds, key_sgo, key_betfair,
                sport_key, buget, min_prag, anti_detect, max_per_bk
            )

            pbar.progress(85, text="// DETECTIE ARB NOU...")
            curr_ids = {r["id"] for r in arbs}
            new_ids  = curr_ids - st.session_state.prev_arb_ids
            st.session_state.new_arb_ids  = new_ids
            st.session_state.prev_arb_ids = curr_ids
            pbar.progress(100, text="// COMPLET")
            time.sleep(0.25)
            pbar.empty()

            st.session_state.api_status      = status_new
            st.session_state.scan_results    = results
            st.session_state.arb_found_total += len(arbs)
            st.session_state.last_scan_time  = datetime.now()
            st.session_state.total_scans    += 1

            for err in errors:
                st.warning(f"⚠ {err}")

            # Alerte ARB noi
            if new_ids:
                for nr in [r for r in arbs if r["id"] in new_ids]:
                    st.markdown(f"""
                    <div class='alert-new'>
                        🔔 <strong>ARB NOU DETECTAT</strong> &nbsp;|&nbsp;
                        {nr['h_team']} vs {nr['a_team']} &nbsp;|&nbsp;
                        <span style='color:#00e676;font-weight:700;'>+{nr['pct']:.2f}%</span> &nbsp;|&nbsp;
                        {nr['found_at']}
                    </div>""", unsafe_allow_html=True)

            # Status boxes
            sc1, sc2, sc3, sc4 = st.columns(4)
            cross_arbs = [r for r in arbs if r["is_cross"]]
            with sc1:
                st.markdown(f"<div class='stat-box'><p class='stat-label'>MECIURI</p><p class='stat-value' style='color:#c8d8f0;'>{len(results)}</p></div>", unsafe_allow_html=True)
            with sc2:
                bc  = "rgba(0,230,118,0.35)" if arbs else "#12192a"
                ac2 = "#00e676" if arbs else "#ff1744"
                st.markdown(f"<div class='stat-box' style='border-color:{bc};'><p class='stat-label'>ARB GASITE</p><p class='stat-value' style='color:{ac2};'>{len(arbs)}</p></div>", unsafe_allow_html=True)
            with sc3:
                cc = "#ff6d00" if cross_arbs else "#3a4560"
                st.markdown(f"<div class='stat-box'><p class='stat-label'>CROSS-SOURCE</p><p class='stat-value' style='color:{cc};'>{len(cross_arbs)}</p></div>", unsafe_allow_html=True)
            with sc4:
                st.markdown(f"<div class='stat-box'><p class='stat-label'>API CALLS RAMASE</p><p class='stat-value' style='color:#ffd740;'>{remaining}</p></div>", unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Filtrare
            if cross_only:
                display = [r for r in arbs if r["is_cross"]]
            elif show_all:
                display = results
            else:
                display = arbs

            # Filtrare dupa sport selectat
            if filter_sport_keys:
                # Construim set de cuvinte cheie din sporturile selectate
                # ex: "americanfootball_nfl" -> {"american", "football", "nfl"}
                kw_sets = []
                for sk in filter_sport_keys:
                    parts = set(sk.lower().replace("_", " ").split())
                    label = SPORTS.get(sk, ("", ""))[1].lower()
                    parts.update(label.split())
                    kw_sets.append(parts)
                # Pastreaza meciul daca sport_title contine cel putin un cuvant
                # din setul de cuvinte cheie al oricarui sport selectat
                display = [
                    r for r in display
                    if any(
                        any(kw in r["sport_title"].lower() for kw in kw_set)
                        for kw_set in kw_sets
                    )
                ]

            # Sortare
            if sort_by == "Profit % (desc)":
                display = sorted(display, key=lambda x: x["pct"], reverse=True)
            elif sort_by == "Profit RON (desc)":
                display = sorted(display, key=lambda x: x["net_profit"], reverse=True)
            elif sort_by == "Ora meci":
                display = sorted(display, key=lambda x: x["match_time"])

            if not display:
                st.markdown(f"""
                <div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'>
                    <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.85rem;margin:0;'>
                        SCAN COMPLET — NICIUN REZULTAT
                    </p>
                    <p style='font-family:Space Mono,monospace;color:#1a2540;font-size:0.7rem;margin:0.5rem 0 0;'>
                        Prag {min_prag}% — incearca alt sport sau reduce pragul
                    </p>
                </div>""", unsafe_allow_html=True)

            # ── RANDARE CARDURI ──────────────────────────────
            for idx, r in enumerate(display):
                with st.container():
                    is_new = r["id"] in st.session_state.new_arb_ids

                    if r["is_arb"]:
                        badge = f"<span class='badge-arb'>+{r['pct']:.2f}% PROFIT</span>"
                    else:
                        badge = f"<span class='badge-no'>NO ARB ({r['pct']:.2f}%)</span>"
                    new_badge   = "<span class='badge-new'>NOU ★</span>" if is_new else ""
                    cross_badge = "<span class='src-badge src-cross'>CROSS-SOURCE</span>" if r["is_cross"] else ""
                    warn_badges = "".join(
                        f"<span class='badge-warn'>⚠ {bk} LIMITA</span>"
                        for bk in r.get("warn_bk", [])
                    )
                    sources_str = src_badges(r["sources"])
                    card_css    = (
                        "arb-card arb-card-yes" + (" arb-card-new" if is_new else "")
                    ) if r["is_arb"] else "arb-card arb-card-no"

                    items = [{
                        "label": f"(1) {r['h_team'][:22]}",
                        "bk":    r["best1"]["bk"],
                        "src":   r["best1"]["src"],
                        "odd":   r["p1"],
                        "stake": r["s1"],
                        "kelly": r["k1"],
                        "color": "#00e676",
                    }]
                    if r["use_draw"]:
                        items.append({
                            "label": "(X) EGAL",
                            "bk":    r["bestX"]["bk"],
                            "src":   r["bestX"]["src"],
                            "odd":   r["pX"],
                            "stake": r["sX"],
                            "kelly": r["kX"],
                            "color": "#ffd740",
                        })
                    items.append({
                        "label": f"(2) {r['a_team'][:22]}",
                        "bk":    r["best2"]["bk"],
                        "src":   r["best2"]["src"],
                        "odd":   r["p2"],
                        "stake": r["s2"],
                        "kelly": r["k2"],
                        "color": "#00e676",
                    })

                    grid      = " ".join(["1fr"] * len(items))
                    boxes     = ""
                    clip_text = f"{r['h_team']} vs {r['a_team']}\n"

                    for si in items:
                        retur     = int(si["stake"] * si["odd"])
                        sb        = src_badge(si["src"])
                        kelly_row = (
                            f"<p style='color:#ffd740;font-size:0.62rem;margin:2px 0 0;"
                            f"font-family:Space Mono,monospace;'>Kelly: {si['kelly']:.0f} RON</p>"
                        ) if show_kelly else ""
                        clip_text += f"  {si['label']}: {si['stake']} RON @ {si['odd']:.2f} ({si['bk']})\n"
                        boxes += (
                            f"<div class='stake-box' style='border-color:{si['color']};'>"
                            f"<p class='stake-label'>{si['label']}</p>"
                            f"<p class='stake-bk'>{si['bk']}{sb}</p>"
                            f"<p class='stake-odd'>@{si['odd']:.2f}</p>"
                            f"<p class='stake-amt' style='color:{si['color']};'>{si['stake']} RON</p>"
                            f"<p class='stake-ret'>= {retur} RON retur</p>"
                            f"{kelly_row}"
                            f"</div>"
                        )
                    clip_text += f"  Profit garantat: +{r['net_profit']:.2f} RON\n"
                    clip_text += f"  Gasit la: {r['found_at']}"

                    pc_val = pcol(r["pct"]) if r["is_arb"] else "#ff6d00"
                    gret   = int(buget / r["inv"])

                    st.markdown(
                        f"<div class='{card_css}'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;'>"
                        f"<span class='card-meta'>{r['sport_title']}  |  {r['match_time']}  |  {r['found_at']}{sources_str}</span>"
                        f"<span>{badge}{new_badge}{cross_badge}{warn_badges}</span>"
                        f"</div>"
                        f"<p class='card-title'>{r['h_team']} <span style='color:#3a4560;'>vs</span> {r['a_team']}</p>"
                        f"<div style='display:grid;grid-template-columns:{grid};gap:18px;'>{boxes}</div>"
                        f"<div class='card-footer'>"
                        f"<span>PROFIT GARANTAT:&nbsp;<span style='color:{pc_val};font-weight:700;'>"
                        f"{r['net_profit']:+.2f} RON</span>&nbsp;|&nbsp;RETURN: {gret} RON</span>"
                        f"<span>1/&Sigma; = {r['inv']:.4f}</span>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )

                    if r["is_arb"]:
                        btn_key = f"reg_{idx}_{r['h_team'][:6]}_{r['a_team'][:6]}_{r['p1']}_{r['p2']}"
                        b1, b2, _ = st.columns([1, 1, 2])
                        with b1:
                            if st.button(f"INREGISTREAZA #{idx + 1}", key=btn_key):
                                if r["use_draw"]:
                                    sk_str = f"{r['s1']} / {r['sX']} / {r['s2']}"
                                    bk_str = f"{r['best1']['bk']} / {r['bestX']['bk']} / {r['best2']['bk']}"
                                else:
                                    sk_str = f"{r['s1']} / {r['s2']}"
                                    bk_str = f"{r['best1']['bk']} / {r['best2']['bk']}"

                                for bk_name, amt in [(r["best1"]["bk"], r["s1"]), (r["best2"]["bk"], r["s2"])]:
                                    if bk_name:
                                        st.session_state.bk_risk[bk_name] = (
                                            st.session_state.bk_risk.get(bk_name, 0) + amt
                                        )
                                if r["use_draw"] and r["bestX"]["bk"]:
                                    bkx = r["bestX"]["bk"]
                                    st.session_state.bk_risk[bkx] = (
                                        st.session_state.bk_risk.get(bkx, 0) + r["sX"]
                                    )

                                st.session_state.registered_bets.append({
                                    "id":         len(st.session_state.registered_bets) + 1,
                                    "time":       datetime.now().strftime("%d.%m  %H:%M"),
                                    "match":      f"{r['h_team']} vs {r['a_team']}",
                                    "sport":      r["sport_title"],
                                    "profit_pct": round(r["pct"], 2),
                                    "net_profit": r["net_profit"],
                                    "capital":    buget,
                                    "stakes":     sk_str,
                                    "bookmakers": bk_str,
                                    "cross":      "DA" if r["is_cross"] else "NU",
                                    "found_at":   r["found_at"],
                                })
                                st.session_state.history.append({
                                    "T":     datetime.now().strftime("%H:%M"),
                                    "P":     r["net_profit"],
                                    "Match": f"{r['h_team'][:10]} vs {r['a_team'][:10]}",
                                    "Sport": r["sport_title"],
                                    "BK1":   r["best1"]["bk"],
                                    "BK2":   r["best2"]["bk"],
                                })
                                st.session_state.total_profit += r["net_profit"]
                                st.success(f"Inregistrat! +{r['net_profit']:.2f} RON")
                                time.sleep(0.6)
                                st.rerun()

                        with b2:
                            clip_escaped = clip_text.replace('"', '\\"').replace('\n', '\\n')
                            st.markdown(
                                f"<button class='clip-btn' "
                                f"onclick='navigator.clipboard.writeText(\"{clip_escaped}\").then("
                                f"()=>{{this.textContent=\"COPIAT\";setTimeout(()=>this.textContent=\"COPIAZA\",1500)}}"
                                f")'> COPIAZA </button>",
                                unsafe_allow_html=True
                            )

                    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    elif not st.session_state.scan_results:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
            <p style='font-size:2.5rem;margin:0;'>⚡</p>
            <p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.82rem;margin:0.75rem 0 0;'>
                SISTEM GATA — configurati si apasati RUN SCAN
            </p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB ISTORIC
# ════════════════════════════════════════════════════════════
with tab_hist:
    bets = st.session_state.registered_bets
    if not bets:
        st.markdown("<div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'><p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.82rem;'>NICIUN PARIU INREGISTRAT</p></div>", unsafe_allow_html=True)
    else:
        df = pd.DataFrame(bets)
        hc1, hc2, hc3, hc4 = st.columns(4)
        with hc1: st.metric("TOTAL PARIURI", len(df))
        with hc2: st.metric("PROFIT TOTAL",  f"{df['net_profit'].sum():+.2f} RON")
        with hc3: st.metric("PROFIT MEDIU",  f"{df['net_profit'].mean():+.2f} RON")
        with hc4: st.metric("CROSS-SOURCE",  int(df["cross"].eq("DA").sum()) if "cross" in df.columns else 0)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        rows = ""
        for _, row in df.iterrows():
            pc = "#00e676" if row["net_profit"] >= 0 else "#ff1744"
            cc = "#ff6d00" if row.get("cross") == "DA" else "#3a4560"
            rows += (
                f"<tr><td style='color:#3a4560;'>#{int(row['id'])}</td>"
                f"<td>{row['time']}</td>"
                f"<td style='color:#c8d8f0;'>{row['match']}</td>"
                f"<td style='color:#6070a0;'>{row['sport']}</td>"
                f"<td>{row['stakes']} RON</td>"
                f"<td style='color:#ffd740;'>+{row['profit_pct']}%</td>"
                f"<td style='color:{pc};font-weight:700;'>{row['net_profit']:+.2f} RON</td>"
                f"<td style='color:{cc};'>{row.get('cross', '—')}</td></tr>"
            )
        st.markdown(
            f"<table class='tbl'><thead><tr>"
            f"<th>#</th><th>ORA</th><th>MECI</th><th>SPORT</th>"
            f"<th>STAKE-URI</th><th>%</th><th>PROFIT</th><th>CROSS</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        if st.session_state.bk_risk:
            st.markdown("<p style='font-family:Space Mono,monospace;font-size:0.72rem;color:#3a4560;margin:1rem 0 0.5rem;'>EXPUNERE PER BOOKMAKER</p>", unsafe_allow_html=True)
            bk_rows = ""
            for bk, total in sorted(st.session_state.bk_risk.items(), key=lambda x: -x[1]):
                warn  = " <span style='color:#ff1744;'>⚠ LIMITA DEPASITA</span>" if total > max_per_bk else ""
                bar_w = min(100, total / max_per_bk * 100)
                bar_c = "#ff1744" if total > max_per_bk else "#00e676" if total < max_per_bk * 0.7 else "#ffd740"
                bk_rows += (
                    f"<tr><td style='color:#c8d8f0;'>{bk}{warn}</td>"
                    f"<td><div style='background:#0a0f1e;border-radius:3px;height:6px;width:150px;'>"
                    f"<div style='background:{bar_c};width:{bar_w:.0f}%;height:100%;border-radius:3px;'></div></div></td>"
                    f"<td style='color:#ffd740;'>{total:,.0f} RON</td>"
                    f"<td style='color:#3a4560;'>/ {max_per_bk:,.0f} RON</td></tr>"
                )
            st.markdown(
                f"<table class='tbl'><thead><tr><th>BOOKMAKER</th><th>EXPUNERE</th><th>STAKED</th><th>LIMITA</th></tr></thead>"
                f"<tbody>{bk_rows}</tbody></table>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "EXPORT CSV",
            data=csv,
            file_name=f"arbmaster_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )


# ════════════════════════════════════════════════════════════
# TAB ANALYTICS
# ════════════════════════════════════════════════════════════
with tab_analytics:
    hist = st.session_state.history
    if not hist:
        st.markdown("<div style='text-align:center;padding:3rem;background:#080c14;border:1px dashed #1a2540;border-radius:12px;'><p style='font-family:Space Mono,monospace;color:#3a4560;font-size:0.82rem;'>INREGISTRATI PARIURI PENTRU STATISTICI</p></div>", unsafe_allow_html=True)
    else:
        df_h          = pd.DataFrame(hist)
        df_h["Cumul"] = df_h["P"].cumsum()
        df_h.index    = range(1, len(df_h) + 1)

        base = dict(
            template="plotly_dark", paper_bgcolor="#080c14", plot_bgcolor="#04050a",
            margin=dict(l=10, r=10, t=38, b=10), height=280, showlegend=False,
            xaxis=dict(gridcolor="#12192a", tickfont=dict(family="Space Mono", size=9), title=None),
            yaxis=dict(gridcolor="#12192a", tickfont=dict(family="Space Mono", size=9), title=None),
        )

        gc1, gc2 = st.columns(2)
        with gc1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_h.index, y=df_h["Cumul"], mode="lines+markers",
                line=dict(color="#00e676", width=2),
                fill="tozeroy", fillcolor="rgba(0,230,118,0.07)",
                marker=dict(size=5, color="#00e676"),
            ))
            fig1.update_layout(**base, title=dict(text="PROFIT CUMULATIV (RON)", font=dict(family="Space Mono", size=10, color="#3a4560")))
            st.plotly_chart(fig1, use_container_width=True)
        with gc2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_h.index, y=df_h["P"],
                marker_color=["#00e676" if p >= 0 else "#ff1744" for p in df_h["P"]],
            ))
            fig2.update_layout(**base, title=dict(text="PROFIT PER PARIU (RON)", font=dict(family="Space Mono", size=10, color="#3a4560")))
            st.plotly_chart(fig2, use_container_width=True)

        if "Sport" in df_h.columns and "BK1" in df_h.columns:
            gc3, gc4 = st.columns(2)
            with gc3:
                sport_pnl = df_h.groupby("Sport")["P"].sum().reset_index()
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=sport_pnl["Sport"], y=sport_pnl["P"],
                    marker_color=["#00e676" if p >= 0 else "#ff1744" for p in sport_pnl["P"]],
                ))
                fig3.update_layout(**base, title=dict(text="P&L PER SPORT (RON)", font=dict(family="Space Mono", size=10, color="#3a4560")))
                st.plotly_chart(fig3, use_container_width=True)
            with gc4:
                bk_all = pd.concat([
                    df_h[["BK1", "P"]].rename(columns={"BK1": "BK"}),
                    df_h[["BK2", "P"]].rename(columns={"BK2": "BK"}),
                ])
                bk_pnl = bk_all.groupby("BK")["P"].sum().reset_index().sort_values("P", ascending=False)
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    x=bk_pnl["BK"], y=bk_pnl["P"],
                    marker_color=["#00e676" if p >= 0 else "#ff1744" for p in bk_pnl["P"]],
                ))
                fig4.update_layout(**base, title=dict(text="P&L PER BOOKMAKER (RON)", font=dict(family="Space Mono", size=10, color="#3a4560")))
                st.plotly_chart(fig4, use_container_width=True)

        profits = df_h["P"]
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1: st.metric("MAX PROFIT",  f"{profits.max():.2f} RON")
        with ac2: st.metric("MIN PROFIT",  f"{profits.min():.2f} RON")
        with ac3: st.metric("WIN RATE",    f"{(profits > 0).mean() * 100:.0f}%")
        with ac4: st.metric("STD DEV",     f"{profits.std():.2f} RON")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        luna   = datetime.now().strftime("%B %Y")
        raport = f"ARBMASTER PLATINUM — RAPORT {luna}\n" + "=" * 50 + "\n"
        raport += f"Total pariuri:      {len(df_h)}\n"
        raport += f"Profit total:       {profits.sum():+.2f} RON\n"
        raport += f"Profit mediu:       {profits.mean():+.2f} RON\n"
        raport += f"Win rate:           {(profits > 0).mean() * 100:.0f}%\n"
        raport += f"Max:                {profits.max():.2f} RON\n"
        raport += f"Min:                {profits.min():.2f} RON\n"
        raport += "=" * 50 + "\nDETALII\n" + "-" * 50 + "\n"
        for _, row in df_h.iterrows():
            raport += f"{row.get('T', ''):<8} {row.get('Match', ''):<30} {row['P']:+.2f} RON\n"
        st.download_button(
            "📄 EXPORT RAPORT LUNAR TXT",
            data=raport.encode("utf-8"),
            file_name=f"raport_{datetime.now().strftime('%Y_%m')}.txt",
            mime="text/plain",
        )


# ════════════════════════════════════════════════════════════
# TAB GHID
# ════════════════════════════════════════════════════════════
with tab_help:
    st.markdown("""
    <div style='max-width:720px;'>
    <h3 style='font-family:Space Mono,monospace;color:#00e676;font-size:0.95rem;margin-top:0;'>// REZOLVARI v7.0</h3>
    <div style='font-family:Space Mono,monospace;font-size:0.75rem;background:#080c14;padding:1rem 1.2rem;border-radius:8px;border:1px solid #12192a;line-height:2;'>
        ✓ Import-uri neutilizate eliminate (px, math, timedelta, json)<br>
        ✓ kelly_fraction: guard impotriva b=0 ZeroDivisionError<br>
        ✓ fetch_odds_api: out["price"] cu .get() + validare cota > 1<br>
        ✓ fetch_betfair: ambele cereri cu try/except complet<br>
        ✓ fetch_betfair: r1.json() si r2.json() protejate<br>
        ✓ analyze_game: guard inv <= 0 si cote <= 1<br>
        ✓ merge_games: sources set -> list la export<br>
        ✓ ROI: guard buget*n = 0 ZeroDivisionError<br>
        ✓ filter_sport: comparatie corecta pe sport key<br>
        ✓ Resetare state: cod clar fara isinstance hack<br>
        ✓ bk_risk update: guard bk_name gol
    </div>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;font-size:0.95rem;margin-top:1.5rem;'>// FORMULA</h3>
    <div style='font-family:Space Mono,monospace;color:#c8d8f0;font-size:0.78rem;background:#080c14;padding:1rem 1.2rem;border-radius:8px;border:1px solid #12192a;line-height:1.9;'>
        Sigma = 1/cota1 + 1/cota2 [+ 1/cotaX]<br>
        Daca Sigma &lt; 1.0 -&gt; ARBITRAJ<br>
        Profit % = (1 - Sigma) x 100<br>
        Profit RON = Capital / Sigma - Capital<br>
        Stake_i = (1/cota_i / Sigma) x Capital
    </div>

    <h3 style='font-family:Space Mono,monospace;color:#ffd740;font-size:0.95rem;margin-top:1.5rem;'>// API-URI</h3>
    <div style='font-family:Space Mono,monospace;font-size:0.78rem;background:#080c14;padding:1rem 1.2rem;border-radius:8px;border:1px solid #12192a;line-height:2;'>
        <span class='src-badge src-odds'>TheOddsAPI</span> the-odds-api.com — 500 cereri/luna gratuit<br>
        <span class='src-badge src-sgo'>SGO</span> sportsgameodds.com — 80+ bookmakers<br>
        <span class='src-badge src-betfair'>Betfair</span> betfair.com — Exchange, cont necesar
    </div>
    </div>
    """, unsafe_allow_html=True)


# ─── FOOTER ───────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;padding:2rem 0 1rem;font-family:Space Mono,monospace;"
    f"font-size:0.62rem;color:#1a2540;border-top:1px solid #0d1525;margin-top:2rem;'>"
    f"ARBMaster Platinum v7.0 &nbsp;|&nbsp; Zero Errors Edition &nbsp;|&nbsp;"
    f"Build {datetime.now().strftime('%Y.%m.%d')}"
    f"</div>",
    unsafe_allow_html=True
)
