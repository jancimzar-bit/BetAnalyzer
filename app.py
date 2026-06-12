import streamlit as st
import anthropic
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SP 2026 · Stavni Analizator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0a0e1a;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid #1e2540;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label {
    color: #8892b0 !important;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e8eaf0 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e2540;
    border-radius: 12px;
    padding: 16px !important;
}

[data-testid="metric-container"] label {
    color: #8892b0 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 24px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a3a6b 0%, #0f2548 100%);
    color: #7eb8f7 !important;
    border: 1px solid #1e4080 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    letter-spacing: 0.03em;
    padding: 8px 20px !important;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e4a85 0%, #122d5a 100%) !important;
    border-color: #2d5fa8 !important;
    color: #a8d0ff !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d6b3a 0%, #0f3d20 100%) !important;
    color: #5fd68a !important;
    border-color: #1e5e35 !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #22804a 0%, #134826 100%) !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: #111827 !important;
    border-color: #1e2540 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}

/* Number input */
.stNumberInput > div > div > input {
    background: #111827 !important;
    border-color: #1e2540 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: #111827 !important;
    border-color: #1e2540 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}

/* Divider */
hr {
    border-color: #1e2540 !important;
    margin: 1.5rem 0 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #111827 !important;
    border: 1px solid #1e2540 !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1120;
    border-bottom: 1px solid #1e2540;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8892b0 !important;
    border-radius: 8px 8px 0 0;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: #111827 !important;
    color: #e8eaf0 !important;
    border-bottom: 2px solid #3b82f6 !important;
}

/* Info/success/warning boxes */
.stAlert {
    border-radius: 10px !important;
    border-width: 1px !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #3b82f6, #10b981) !important;
    border-radius: 4px !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #3b82f6 !important;
}

/* Custom match card */
.match-card {
    background: #111827;
    border: 1px solid #1e2540;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.match-card:hover {
    border-color: #2d4a8a;
    background: #131c2e;
}
.match-card.selected {
    border-color: #3b82f6;
    background: #0d1e3a;
}

/* Value bet highlight */
.value-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
}
.no-value-badge {
    display: inline-block;
    background: rgba(107, 114, 128, 0.15);
    color: #9ca3af;
    border: 1px solid rgba(107, 114, 128, 0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    letter-spacing: 0.04em;
}

/* Analysis section headers */
.section-label {
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 6px;
    font-weight: 500;
}

/* Confidence indicator */
.conf-high { color: #10b981; }
.conf-med  { color: #f59e0b; }
.conf-low  { color: #ef4444; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2540; border-radius: 4px; }

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@dataclass
class Match:
    id: int
    home: str
    away: str
    date: str
    group: str
    time: str
    flag_home: str
    flag_away: str

MATCHES = [
    # Skupina A
    Match(1,  "Mehika",       "J. Afrika",      "11. jun 2026", "A", "21:00", "", ""),
    Match(2,  "J. Koreja",    "Češka",          "11. jun 2026", "A", "04:00", "", ""),
    Match(3,  "Mehika",       "J. Koreja",      "17. jun 2026", "A", "21:00", "", ""),
    Match(4,  "Češka",        "J. Afrika",      "18. jun 2026", "A", "18:00", "", ""),
    Match(5,  "Mehika",       "Češka",          "23. jun 2026", "A", "22:00", "", ""),
    Match(6,  "J. Afrika",    "J. Koreja",      "23. jun 2026", "A", "22:00", "", ""),
    # Skupina B
    Match(7,  "Kanada",       "Bosna in Hercegovina", "12. jun 2026", "B", "21:00", "", ""),
    Match(8,  "Katar",        "Švica",          "13. jun 2026", "B", "21:00", "", ""),
    Match(9,  "Kanada",       "Katar",          "18. jun 2026", "B", "00:00", "", ""),
    Match(10, "Švica",        "Bosna in Hercegovina", "19. jun 2026", "B", "21:00", "", ""),
    Match(11, "Kanada",       "Švica",          "24. jun 2026", "B", "22:00", "", ""),
    Match(12, "Bosna in Hercegovina", "Katar",  "24. jun 2026", "B", "22:00", "", ""),
    # Skupina C
    Match(13, "Brazilija",    "Maroko",         "13. jun 2026", "C", "23:00", "", ""),
    Match(14, "Haiti",        "Škotska",        "14. jun 2026", "C", "03:00", "", ""),
    Match(15, "Brazilija",    "Haiti",          "20. jun 2026", "C", "00:00", "", ""),
    Match(16, "Škotska",      "Maroko",         "20. jun 2026", "C", "21:00", "", ""),
    Match(17, "Brazilija",    "Škotska",        "25. jun 2026", "C", "00:00", "", ""),
    Match(18, "Maroko",       "Haiti",          "25. jun 2026", "C", "00:00", "", ""),
    # Skupina D
    Match(19, "ZDA",          "Paragvaj",       "12. jun 2026", "D", "03:00", "", ""),
    Match(20, "Avstralija",   "Turčija",        "13. jun 2026", "D", "04:00", "", ""),
    Match(21, "ZDA",          "Avstralija",     "19. jun 2026", "D", "00:00", "", ""),
    Match(22, "Turčija",      "Paragvaj",       "19. jun 2026", "D", "21:00", "", ""),
    Match(23, "ZDA",          "Turčija",        "24. jun 2026", "D", "22:00", "", ""),
    Match(24, "Paragvaj",     "Avstralija",     "24. jun 2026", "D", "22:00", "", ""),
    # Skupina E
    Match(25, "Nemčija",      "Curacao",        "14. jun 2026", "E", "20:00", "", ""),
    Match(26, "Slonokoščena obala", "Ekvador", "15. jun 2026", "E", "00:00", "", ""),
    Match(27, "Nemčija",      "Slonokoščena obala", "20. jun 2026", "E", "21:00", "", ""),
    Match(28, "Ekvador",      "Curacao",        "21. jun 2026", "E", "00:00", "", ""),
    Match(29, "Nemčija",      "Ekvador",        "26. jun 2026", "E", "22:00", "", ""),
    Match(30, "Curacao",      "Slonokoščena obala", "26. jun 2026", "E", "22:00", "", ""),
    # Skupina F
    Match(31, "Nizozemska",   "Japonska",       "14. jun 2026", "F", "23:00", "", ""),
    Match(32, "Švedska",      "Tunizija",       "15. jun 2026", "F", "21:00", "", ""),
    Match(33, "Nizozemska",   "Švedska",        "21. jun 2026", "F", "21:00", "", ""),
    Match(34, "Japonska",     "Tunizija",       "21. jun 2026", "F", "00:00", "", ""),
    Match(35, "Nizozemska",   "Tunizija",       "26. jun 2026", "F", "22:00", "", ""),
    Match(36, "Japonska",     "Švedska",        "26. jun 2026", "F", "22:00", "", ""),
    # Skupina G
    Match(37, "Belgija",      "Egipt",          "15. jun 2026", "G", "21:00", "", ""),
    Match(38, "Iran",         "Nova Zelandija", "16. jun 2026", "G", "00:00", "", ""),
    Match(39, "Belgija",      "Iran",           "21. jun 2026", "G", "23:00", "", ""),
    Match(40, "Nova Zelandija","Egipt",          "22. jun 2026", "G", "00:00", "", ""),
    Match(41, "Belgija",      "Nova Zelandija", "27. jun 2026", "G", "22:00", "", ""),
    Match(42, "Egipt",        "Iran",           "27. jun 2026", "G", "22:00", "", ""),
    # Skupina H
    Match(43, "Španija",      "Zelenortski otoki", "15. jun 2026", "H", "18:00", "", ""),
    Match(44, "Savdska Arabija", "Urugvaj",     "16. jun 2026", "H", "21:00", "", ""),
    Match(45, "Španija",      "Savdska Arabija","21. jun 2026", "H", "18:00", "", ""),
    Match(46, "Urugvaj",      "Zelenortski otoki", "22. jun 2026", "H", "21:00", "", ""),
    Match(47, "Španija",      "Urugvaj",        "27. jun 2026", "H", "22:00", "", ""),
    Match(48, "Zelenortski otoki", "Savdska Arabija", "27. jun 2026", "H", "22:00", "", ""),
    # Skupina I
    Match(49, "Francija",     "Senegal",        "17. jun 2026", "I", "21:00", "", ""),
    Match(50, "Irak",         "Norveška",       "18. jun 2026", "I", "00:00", "", ""),
    Match(51, "Francija",     "Norveška",       "22. jun 2026", "I", "21:00", "", ""),
    Match(52, "Senegal",      "Irak",           "23. jun 2026", "I", "00:00", "", ""),
    Match(53, "Francija",     "Irak",           "27. jun 2026", "I", "22:00", "", ""),
    Match(54, "Norveška",     "Senegal",        "27. jun 2026", "I", "22:00", "", ""),
    # Skupina J
    Match(55, "Argentina",    "Alžirija",       "16. jun 2026", "J", "23:00", "", ""),
    Match(56, "Avstrija",     "Jordanija",      "17. jun 2026", "J", "04:00", "", ""),
    Match(57, "Argentina",    "Avstrija",       "22. jun 2026", "J", "03:00", "", ""),
    Match(58, "Jordanija",    "Alžirija",       "22. jun 2026", "J", "23:00", "", ""),
    Match(59, "Argentina",    "Jordanija",      "26. jun 2026", "J", "22:00", "", ""),
    Match(60, "Alžirija",     "Avstrija",       "26. jun 2026", "J", "22:00", "", ""),
    # Skupina K
    Match(61, "Portugalska",  "DR Kongo",       "13. jun 2026", "K", "19:00", "", ""),
    Match(62, "Uzbekistan",   "Kolumbija",      "14. jun 2026", "K", "00:00", "", ""),
    Match(63, "Portugalska",  "Uzbekistan",     "19. jun 2026", "K", "21:00", "", ""),
    Match(64, "Kolumbija",    "DR Kongo",       "19. jun 2026", "K", "21:00", "", ""),
    Match(65, "Portugalska",  "Kolumbija",      "25. jun 2026", "K", "22:00", "", ""),
    Match(66, "DR Kongo",     "Uzbekistan",     "25. jun 2026", "K", "22:00", "", ""),
    # Skupina L
    Match(67, "Anglija",      "Hrvaška",        "14. jun 2026", "L", "22:00", "", ""),
    Match(68, "Gana",         "Panama",         "15. jun 2026", "L", "00:00", "", ""),
    Match(69, "Anglija",      "Gana",           "20. jun 2026", "L", "21:00", "", ""),
    Match(70, "Panama",       "Hrvaška",        "20. jun 2026", "L", "23:00", "", ""),
    Match(71, "Anglija",      "Panama",         "25. jun 2026", "L", "22:00", "", ""),
    Match(72, "Hrvaška",      "Gana",           "25. jun 2026", "L", "22:00", "", ""),
]

GROUPS = sorted(set(m.group for m in MATCHES))


# ── Session state ─────────────────────────────────────────────────────────────
if "bankroll"       not in st.session_state: st.session_state.bankroll       = 20.0
if "analyses"       not in st.session_state: st.session_state.analyses       = {}
if "selected_match" not in st.session_state: st.session_state.selected_match = None
if "tg_token"       not in st.session_state: st.session_state.tg_token       = ""
if "tg_chat_id"     not in st.session_state: st.session_state.tg_chat_id     = ""


# ── Helpers ───────────────────────────────────────────────────────────────────
def max_stake() -> float:
    return min(5.0, st.session_state.bankroll * 0.25)

def kelly_stake() -> float:
    return round(st.session_state.bankroll * 0.02, 2)

def analyze_match(match: Match, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    # Korak 1: web search za podatke o tekmi
    search_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system="Si nogometni analitik. Poišči najnovejše informacije o navedeni tekmi SP 2026: poškodbe, suspenzije, forma ekip, trenerji, predvidene postave, kvote stavnic. Zberi VSE relevantne podatke in jih napiši v slovenščini.",
        messages=[{"role": "user", "content": f"Poišči informacije za tekmo SP 2026: {match.home} vs {match.away}, {match.date}, Skupina {match.group}. Potrebujem: poškodbe, forma zadnjih 5 tekem, trenerja obeh ekip, predvideno postavo, trenutne kvote stavnic."}],
    )
    search_text = " ".join(b.text for b in search_response.content if hasattr(b, "text"))

    # Korak 2: strukturirana JSON analiza na podlagi zbranih podatkov
    json_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=f"""Si vrhunski stavni analitik. Na podlagi podanih podatkov vrni IZKLJUČNO veljaven JSON objekt brez kakršnega koli besedila pred ali za njim, brez markdown, brez ```json.
Bankroll: {st.session_state.bankroll:.2f} EUR, max stavek: {max_stake():.2f} EUR.
Vsa besedila v slovenščini.""",
        messages=[{"role": "user", "content": f"""Na podlagi teh podatkov o tekmi {match.home} vs {match.away} ({match.date}, Skupina {match.group}):

{search_text}

Vrni JSON z natanko temi polji:
{{
  "analiza": "2-3 stavki splošne ocene tekme",
  "postava_doma": "ključni igralci in poškodovani",
  "postava_gostje": "ključni igralci in poškodovani",
  "forma_doma": "zadnjih 5 tekem npr: Z R Z Z P",
  "forma_gostje": "zadnjih 5 tekem npr: R R Z P R",
  "trener_doma": "ime trenerja in kratka ocena",
  "trener_gostje": "ime trenerja in kratka ocena",
  "ver_doma": "55",
  "ver_remi": "25",
  "ver_gostje": "20",
  "kvota_doma": "1.80",
  "kvota_remi": "3.40",
  "kvota_gostje": "4.50",
  "value_bet": "DA",
  "value_trg": "npr Zmaga {match.home} ali Obe ekipi dasta gol",
  "razlog_value": "zakaj je tu vrednost",
  "priporocilo": "točno kaj staviti in koliko EUR",
  "zaupanje": "nizko ali srednje ali visoko",
  "opozorilo": "morebitna tveganja"
}}"""}],
    )

    raw_json = " ".join(b.text for b in json_response.content if hasattr(b, "text"))

    # Poskusi parsati JSON
    try:
        clean = re.sub(r"```json|```", "", raw_json).strip()
        # Najdi JSON objekt
        json_match = re.search(r"\{.*\}", clean, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            data["raw"] = raw_json
            return data
    except Exception:
        pass

    # Fallback: vrni surovi tekst
    return {
        "raw": raw_json,
        "analiza": raw_json[:300] if len(raw_json) > 10 else "Napaka pri analizi",
        "postava_doma": "—", "postava_gostje": "—",
        "forma_doma": "—", "forma_gostje": "—",
        "trener_doma": "—", "trener_gostje": "—",
        "ver_doma": "—", "ver_remi": "—", "ver_gostje": "—",
        "kvota_doma": "—", "kvota_remi": "—", "kvota_gostje": "—",
        "value_bet": "NE", "value_trg": "—", "razlog_value": "—",
        "priporocilo": "—", "zaupanje": "—", "opozorilo": "—",
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ SP 2026")
    st.markdown("<p style='color:#6b7280; font-size:12px; margin-top:-10px;'>Stavni analizator</p>", unsafe_allow_html=True)
    st.divider()

    # Najprej poskusi iz Streamlit Secrets, sicer iz ročnega vnosa
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
    if api_key:
        st.success("🔑 API ključ naložen iz Secrets", icon="✅")
    else:
        st.markdown("**🔑 Anthropic API ključ**")
        api_key = st.text_input("", placeholder="sk-ant-...", type="password", label_visibility="collapsed")
        if not api_key:
            st.warning("Vnesi API ključ ali ga dodaj v Streamlit Secrets.")

    st.divider()

    st.markdown("**💰 Bankroll**")
    br = st.number_input("", min_value=1.0, max_value=9999.0, value=float(st.session_state.bankroll), step=1.0, label_visibility="collapsed")
    st.session_state.bankroll = br

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Max stava", f"{max_stake():.2f} €")
    with col2:
        st.metric("Kelly 2%", f"{kelly_stake():.2f} €")

    st.divider()

    st.markdown("**📅 Filtriraj skupino**")
    group_filter = st.selectbox("", ["Vse"] + GROUPS, label_visibility="collapsed")

    st.divider()

    st.markdown("**📬 Telegram**")
    tg_tok = st.secrets.get("TELEGRAM_TOKEN", "") if hasattr(st, "secrets") else ""
    tg_cid = st.secrets.get("TELEGRAM_CHAT_ID", "") if hasattr(st, "secrets") else ""
    if tg_tok and tg_cid:
        st.success("📬 Telegram naložen iz Secrets", icon="✅")
        st.session_state.tg_token = tg_tok
        st.session_state.tg_chat_id = tg_cid
    else:
        tg_tok_in = st.text_input("Bot token", value=st.session_state.tg_token, placeholder="1234:ABC...", type="password")
        tg_cid_in = st.text_input("Chat ID", value=st.session_state.tg_chat_id, placeholder="8869048456")
        if tg_tok_in: st.session_state.tg_token = tg_tok_in
        if tg_cid_in: st.session_state.tg_chat_id = tg_cid_in

    st.divider()
    st.markdown("<p style='color:#3b3f4e; font-size:11px;'>⚠️ Stave so tvegane. Nikoli ne stavij več kot si pripravljen izgubiti.</p>", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 2rem;'>
  <h1 style='font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 4px;'>
    Svetovno Prvenstvo 2026
  </h1>
  <p style='color: #6b7280; font-size: 15px; margin: 0;'>
    AI analiza tekem · Value bets · Telegram obvestila
  </p>
</div>
""", unsafe_allow_html=True)

tab_tekme, tab_analiza, tab_strategija, tab_telegram = st.tabs([
    "  🗓 Tekme  ", "  🔍 Analiza  ", "  📈 Strategija  ", "  📬 Telegram bot  "
])


# ── TAB: TEKME ────────────────────────────────────────────────────────────────
with tab_tekme:
    filtered = [m for m in MATCHES if group_filter == "Vse" or m.group == group_filter]

    for match in filtered:
        analyzed = match.id in st.session_state.analyses
        is_value = analyzed and st.session_state.analyses[match.id].get("value_bet", "").upper().startswith("DA")

        with st.container():
            value_html = "&nbsp; <span style='background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:2px 8px;border-radius:20px;font-size:11px;'>✦ VALUE BET</span>" if is_value else ("&nbsp; <span style='color:#10b981;font-size:11px;'>✓ Analizirano</span>" if analyzed else "")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1.5])
            with c1:
                st.markdown(f"""
                <div style='padding: 14px 0 6px;'>
                  <div style='font-family: Syne, sans-serif; font-size: 16px; font-weight: 600; color: #e8eaf0;'>
                    {match.flag_home} {match.home} <span style='color:#3b4a6b; margin: 0 6px;'>vs</span> {match.flag_away} {match.away}
                  </div>
                  <div style='font-size: 12px; color: #6b7280; margin-top: 4px;'>
                    📅 {match.date} · {match.time} &nbsp;·&nbsp; Skupina {match.group}
                    {value_html}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.write("")
                if st.button(
                    "🔍 Analiziraj" if not analyzed else "🔄 Osveži",
                    key=f"btn_{match.id}",
                    disabled=not api_key,
                ):
                    st.session_state.selected_match = match.id
                    with st.spinner(f"Analiziram {match.home} vs {match.away}..."):
                        try:
                            result = analyze_match(match, api_key)
                            st.session_state.analyses[match.id] = result
                            st.success("✓ Analiza končana! Pojdi na zavihek 'Analiza'.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Napaka: {e}")

            st.markdown("<hr style='margin: 4px 0; border-color: #1a2035;'>", unsafe_allow_html=True)

    if not api_key:
        st.info("👈 Vnesi Anthropic API ključ v stransko ploščo za začetek analize.")


# ── TAB: ANALIZA ──────────────────────────────────────────────────────────────
with tab_analiza:
    if not st.session_state.analyses:
        st.markdown("""
        <div style='text-align:center; padding: 4rem 0; color: #4b5563;'>
          <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
          <div style='font-size: 16px; font-family: Syne, sans-serif;'>Še ni analiz</div>
          <div style='font-size: 13px; margin-top: 8px;'>Pojdi na zavihek "Tekme" in klikni Analiziraj</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        analyzed_ids = list(st.session_state.analyses.keys())
        analyzed_matches = [m for m in MATCHES if m.id in analyzed_ids]

        match_options = {f"{m.flag_home} {m.home} vs {m.flag_away} {m.away} ({m.date})": m.id for m in analyzed_matches}
        selected_label = st.selectbox("Izberi tekmo", list(match_options.keys()))
        mid = match_options[selected_label]
        match = next(m for m in MATCHES if m.id == mid)
        a = st.session_state.analyses[mid]

        is_value = a.get("value_bet", "").upper().startswith("DA")
        zaupanje = a.get("zaupanje", "").lower()

        # Header
        st.markdown(f"""
        <div style='background: #0d1828; border: 1px solid #1e3050; border-radius: 16px; padding: 24px 28px; margin: 1rem 0;'>
          <div style='font-family: Syne, sans-serif; font-size: 1.6rem; font-weight: 700; color: #e8eaf0; margin-bottom: 6px;'>
            {match.flag_home} {match.home} <span style='color: #2d4a6b; margin: 0 10px; font-weight: 400;'>vs</span> {match.flag_away} {match.away}
          </div>
          <div style='color: #6b7280; font-size: 13px; margin-bottom: 16px;'>
            {match.date} · {match.time} · Skupina {match.group}
          </div>
          <div style='color: #c9d5e8; font-size: 14px; line-height: 1.7;'>{a["analiza"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Verjetnosti + kvote
        st.markdown("#### 📊 Verjetnosti in kvote")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.metric(f"{match.flag_home} Zmaga", f"{a['ver_doma']}%", f"Kvota: {a['kvota_doma']}")
        with pc2:
            st.metric("🤝 Remi", f"{a['ver_remi']}%", f"Kvota: {a['kvota_remi']}")
        with pc3:
            st.metric(f"{match.flag_away} Zmaga", f"{a['ver_gostje']}%", f"Kvota: {a['kvota_gostje']}")

        st.divider()

        # Postave in forma
        st.markdown("#### 🧑‍🤝‍🧑 Postavi in forma")
        lc, rc = st.columns(2)
        with lc:
            st.markdown(f"**{match.flag_home} {match.home}**")
            st.markdown(f"<div class='section-label'>Trener</div><div style='color:#c9d5e8; font-size:14px; margin-bottom:10px;'>{a['trener_doma']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-label'>Postava / poškodbe</div><div style='color:#c9d5e8; font-size:14px; margin-bottom:10px;'>{a['postava_doma']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-label'>Forma (zadnjih 5)</div><div style='color:#c9d5e8; font-size:14px;'>{a['forma_doma']}</div>", unsafe_allow_html=True)
        with rc:
            st.markdown(f"**{match.flag_away} {match.away}**")
            st.markdown(f"<div class='section-label'>Trener</div><div style='color:#c9d5e8; font-size:14px; margin-bottom:10px;'>{a['trener_gostje']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-label'>Postava / poškodbe</div><div style='color:#c9d5e8; font-size:14px; margin-bottom:10px;'>{a['postava_gostje']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-label'>Forma (zadnjih 5)</div><div style='color:#c9d5e8; font-size:14px;'>{a['forma_gostje']}</div>", unsafe_allow_html=True)

        # Debug expander - shows raw AI response
        with st.expander("🔧 Surovi AI odgovor (za debug)"):
            st.code(a.get("raw", "ni podatkov"), language=None)

        st.divider()

        # Value bet
        if is_value:
            st.markdown(f"""
            <div style='background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 12px; padding: 20px 24px; margin-bottom: 1rem;'>
              <div style='color: #10b981; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;'>✦ Value Bet Zaznan</div>
              <div style='font-family: Syne, sans-serif; font-size: 18px; font-weight: 700; color: #e8eaf0; margin-bottom: 8px;'>{a["value_trg"]}</div>
              <div style='color: #9ca3af; font-size: 14px; line-height: 1.6;'>{a["razlog_value"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Ni zaznanega value beta za to tekmo.")

        # Priporočilo
        conf_color = "#10b981" if "visoko" in zaupanje else ("#f59e0b" if "srednje" in zaupanje else "#ef4444")
        conf_emoji = "🟢" if "visoko" in zaupanje else ("🟡" if "srednje" in zaupanje else "🔴")

        st.markdown(f"""
        <div style='background: #111827; border: 1px solid #1e2540; border-radius: 12px; padding: 20px 24px; margin-bottom: 1rem;'>
          <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <div style='color: #6b7280; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 500;'>Priporočilo</div>
            <div style='color: {conf_color}; font-size: 12px;'>{conf_emoji} Zaupanje: {a["zaupanje"]}</div>
          </div>
          <div style='font-size: 16px; color: #e8eaf0; font-weight: 500; line-height: 1.6;'>{a["priporocilo"]}</div>
        </div>
        """, unsafe_allow_html=True)

        if a.get("opozorilo", "—") != "—":
            st.warning(f"⚠️ {a['opozorilo']}")

        # Telegram send
        if st.session_state.tg_token and st.session_state.tg_chat_id:
            if st.button("📬 Pošlji analizo na Telegram", type="primary"):
                try:
                    import requests as req
                    msg = f"""⚽ *SP 2026 Analiza*

{match.flag_home} *{match.home}* vs {match.flag_away} *{match.away}*
📅 {match.date} · {match.time} · Skupina {match.group}

📊 *Verjetnosti:*
• {match.home}: {a['ver_doma']}% (kvota {a['kvota_doma']})
• Remi: {a['ver_remi']}% (kvota {a['kvota_remi']})
• {match.away}: {a['ver_gostje']}% (kvota {a['kvota_gostje']})

{"✦ *VALUE BET:* " + a['value_trg'] if is_value else "ℹ️ Ni value beta"}

💡 *Priporočilo:*
{a['priporocilo']}

⚠️ {a.get('opozorilo', '')}
_Zaupanje: {a['zaupanje']}_"""
                    url = f"https://api.telegram.org/bot{st.session_state.tg_token}/sendMessage"
                    r = req.post(url, json={"chat_id": st.session_state.tg_chat_id, "text": msg, "parse_mode": "Markdown"})
                    if r.status_code == 200:
                        st.success("✅ Sporočilo poslano na Telegram!")
                    else:
                        st.error(f"Napaka: {r.text}")
                except Exception as e:
                    st.error(f"Napaka pri pošiljanju: {e}")


# ── TAB: STRATEGIJA ───────────────────────────────────────────────────────────
with tab_strategija:
    st.markdown("#### 📈 Upravljanje bankrolla")

    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Začetni bankroll", f"{st.session_state.bankroll:.2f} €")
    with s2: st.metric("Max na tekmo", f"{max_stake():.2f} €")
    with s3: st.metric("Kelly 2%", f"{kelly_stake():.2f} €")
    with s4: st.metric("Analizirane tekme", len(st.session_state.analyses))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🎯 Kelly kriterij")
        st.markdown("""
        Kelly kriterij določa optimalno velikost stavka glede na prednost, ki jo imaš.

        **Formula:** `f = (b·p − q) / b`
        - `p` = tvoja ocenjena verjetnost zmage
        - `q = 1 − p`
        - `b = kvota − 1`

        Za varnost priporočamo **1/4 Kelly** (ali 2% bankrolla), ker so naše ocene verjetnosti negotove.
        """)

    with c2:
        st.markdown("#### 🔍 Kaj je value bet?")
        st.markdown("""
        Value bet nastane, ko je kvota stavnice **višja od dejanske verjetnosti**.

        **Primer:**
        - Naša ocena: 60% za zmago = poštena kvota 1.67
        - Stavnica ponuja: 2.00
        - **Vrednost = (0.60 × 2.00) − 1 = +0.20** ✓

        Pozitivna vrednost = value bet. Dolgoročno profitabilno.
        """)

    st.divider()
    st.markdown("#### ⚠️ Odgovorno stavljenje")
    st.error("Stavljenje je tvegano. Začni z majhnimi zneski. Nikoli ne stavij denarja, ki si ga ne moreš privoščiti izgubiti. Stavnice imajo dolgoročno prednost.")


# ── TAB: TELEGRAM BOT ─────────────────────────────────────────────────────────
with tab_telegram:
    st.markdown("#### 📬 Nastavitev Telegram bota")
    st.markdown("Bot ti bo vsak dan ob **09:00** poslal analizo tekem, ki se igrajo naslednji dan.")

    st.divider()

    with st.expander("Korak 1: Ustvari Telegram bota (2 min)", expanded=True):
        st.markdown("""
        1. Odpri Telegram in poišči **@BotFather**
        2. Pošlji ukaz `/newbot`
        3. Sledite navodilom — izberi ime in username za bota
        4. Dobit boš **API token** (oblika: `1234567890:ABCdef...`)
        5. Token vnesi v stransko ploščo ← levo
        """)

    with st.expander("Korak 2: Poišči svoj Chat ID"):
        st.markdown("""
        1. Poišči svojega bota po imenu in pošlji `/start`
        2. Odpri URL v brskalniku (zamenjaj TOKEN):
           `https://api.telegram.org/botTOKEN/getUpdates`
        3. V odgovoru poišči `"chat":{"id": XXXXX}` — to je tvoj Chat ID
        4. Chat ID vnesi v stransko ploščo ← levo
        """)

    with st.expander("Korak 3: Ročno pošiljanje"):
        st.markdown("""
        Ko imaš vnesen token in chat ID:
        1. Pojdi na zavihek **Tekme**
        2. Analiziraj željeno tekmo
        3. Pojdi na zavihek **Analiza**
        4. Klikni **Pošlji analizo na Telegram**
        """)

    with st.expander("Korak 4: Avtomatska dnevna sporočila (napredna nastavitev)"):
        st.markdown("""
        Za popolnoma avtomatizirano delovanje potrebuješ Python skripto na strežniku.
        Spodnja koda teče vsak dan ob 09:00 in pošlje analizo tekem naslednjega dne.

        **Brezplačne možnosti za hosting:**
        - [Render.com](https://render.com) — brezplačni cron job
        - GitHub Actions — brezplačni cron workflow
        - PythonAnywhere — brezplačni account
        """)
        st.code("""
# scheduler.py — za GitHub Actions ali Render cron
import os, anthropic, requests
from datetime import datetime, timedelta

ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
TG_TOKEN      = os.environ["TELEGRAM_TOKEN"]
TG_CHAT_ID    = os.environ["TELEGRAM_CHAT_ID"]

# Seznam tekem (datumi v formatu YYYY-MM-DD)
MATCHES = [
    {"home": "Argentina", "away": "Kanada", "date": "2026-06-12", "group": "A"},
    {"home": "Španija",   "away": "Maroko",  "date": "2026-06-13", "group": "B"},
    # ... dodaj ostale tekme
]

def get_tomorrows_matches():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return [m for m in MATCHES if m["date"] == tomorrow]

def analyze(match):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": 
            f"Analiziraj {match['home']} vs {match['away']} za SP 2026. "
            f"Preveri poškodbe, formo, value bet priložnosti. Odgovori v slovenščini."}]
    )
    return " ".join(b.text for b in resp.content if hasattr(b, "text"))

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )

if __name__ == "__main__":
    matches = get_tomorrows_matches()
    if not matches:
        send_telegram("⚽ Jutri ni SP tekem.")
    for m in matches:
        analysis = analyze(m)
        send_telegram(f"⚽ *{m['home']} vs {m['away']}*\\n\\n{analysis}")
        print(f"Poslano: {m['home']} vs {m['away']}")
""", language="python")

    # Test Telegram
    st.divider()
    st.markdown("#### 🧪 Test Telegram povezave")
    if st.button("Pošlji testno sporočilo", disabled=not (st.session_state.tg_token and st.session_state.tg_chat_id)):
        try:
            import requests as req
            r = req.post(
                f"https://api.telegram.org/bot{st.session_state.tg_token}/sendMessage",
                json={"chat_id": st.session_state.tg_chat_id, "text": "✅ SP 2026 Stavni Analizator je povezan! Pripravljeni smo na svetovno prvenstvo! ⚽🏆"}
            )
            if r.status_code == 200:
                st.success("✅ Testno sporočilo poslano!")
            else:
                st.error(f"Napaka: {r.json().get('description', r.text)}")
        except Exception as e:
            st.error(f"Napaka: {e}")