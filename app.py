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
    Match(1,  "Argentina",    "Kanada",        "12. jun 2026", "A", "21:00", "🇦🇷", "🇨🇦"),
    Match(2,  "Španija",      "Maroko",         "13. jun 2026", "B", "18:00", "🇪🇸", "🇲🇦"),
    Match(3,  "Francija",     "Mehika",         "13. jun 2026", "C", "21:00", "🇫🇷", "🇲🇽"),
    Match(4,  "Nemčija",      "Japonska",       "14. jun 2026", "D", "18:00", "🇩🇪", "🇯🇵"),
    Match(5,  "Brazilija",    "Nigerija",       "14. jun 2026", "E", "21:00", "🇧🇷", "🇳🇬"),
    Match(6,  "Anglija",      "Senegal",        "15. jun 2026", "F", "21:00", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "🇸🇳"),
    Match(7,  "Portugalska",  "Češka",          "15. jun 2026", "G", "18:00", "🇵🇹", "🇨🇿"),
    Match(8,  "Nizozemska",   "Peru",           "16. jun 2026", "H", "21:00", "🇳🇱", "🇵🇪"),
    Match(9,  "Hrvaška",      "Maroko",         "17. jun 2026", "B", "15:00", "🇭🇷", "🇲🇦"),
    Match(10, "ZDA",          "Panama",         "17. jun 2026", "C", "21:00", "🇺🇸", "🇵🇦"),
    Match(11, "Belgija",      "Egipt",          "18. jun 2026", "D", "18:00", "🇧🇪", "🇪🇬"),
    Match(12, "Urugvaj",      "Slovenija",      "19. jun 2026", "F", "15:00", "🇺🇾", "🇸🇮"),
]

GROUPS = sorted(set(m.group for m in MATCHES))


# ── Session state ─────────────────────────────────────────────────────────────
if "bankroll"       not in st.session_state: st.session_state.bankroll       = 20.0
if "analyses"       not in st.session_state: st.session_state.analyses       = {}
if "selected_match" not in st.session_state: st.session_state.selected_match = None
if "tg_token"       not in st.session_state: st.session_state.tg_token       = ""
if "tg_chat_id"     not in st.session_state: st.session_state.tg_chat_id     = ""


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_field(text: str, key: str) -> str:
    pattern = rf"{key}:\s*(.+?)(?=\n[A-ZČŠŽ_]+:|$)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else "—"

def max_stake() -> float:
    return min(5.0, st.session_state.bankroll * 0.25)

def kelly_stake() -> float:
    return round(st.session_state.bankroll * 0.02, 2)

def analyze_match(match: Match, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    system = f"""Si vrhunski stavni analitik za SP 2026. Odgovarjaš IZKLJUČNO v slovenščini.
Bankroll: {st.session_state.bankroll:.2f} €, maksimalni priporočeni stavek: {max_stake():.2f} €.

Tvoja analiza mora biti strukturirana TOČNO v tej obliki (vsak razdelek na svoji vrstici):

ANALIZA: [2-3 stavki splošne ocene tekme]
POSTAVA_DOMA: [polna postava ali poškodbe/odsotnosti]  
POSTAVA_GOSTJE: [polna postava ali poškodbe/odsotnosti]
FORMA_DOMA: [zadnjih 5 tekem z rezultati, npr. Z Z R P Z]
FORMA_GOSTJE: [zadnjih 5 tekem z rezultati]
TRENER_DOMA: [ime trenerja in kratka ocena]
TRENER_GOSTJE: [ime trenerja in kratka ocena]
VERJETNOST_DOMA: [% npr. 55]
VERJETNOST_REMI: [% npr. 25]
VERJETNOST_GOSTJE: [% npr. 20]
KVOTA_DOMA: [pričakovana poštena kvota]
KVOTA_REMI: [pričakovana poštena kvota]
KVOTA_GOSTJE: [pričakovana poštena kvota]
VALUE_BET: [DA ali NE]
VALUE_TRG: [npr. "Zmaga Španije", "Obe ekipi dasta gol", "Nad 2.5 gola", itd.]
RAZLOG_VALUE: [zakaj je tu vrednost - konkretna razlaga]
PRIPOROČILO: [točno kaj staviti in koliko €]
ZAUPANJE: [nizko / srednje / visoko]
OPOZORILO: [morebitna tveganja ali zakaj biti previden]"""

    messages = [{
        "role": "user",
        "content": f"Analiziraj tekmo SP 2026: {match.home} vs {match.away} ({match.date}, Skupina {match.group}). Uporabi web search za najnovejše informacije o poškodbah, formi ekip, morebitnih suspenzijah in kvotah stavnic."
    }]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system=system,
        messages=messages,
    )

    raw = " ".join(b.text for b in response.content if hasattr(b, "text"))

    return {
        "raw":              raw,
        "analiza":          parse_field(raw, "ANALIZA"),
        "postava_doma":     parse_field(raw, "POSTAVA_DOMA"),
        "postava_gostje":   parse_field(raw, "POSTAVA_GOSTJE"),
        "forma_doma":       parse_field(raw, "FORMA_DOMA"),
        "forma_gostje":     parse_field(raw, "FORMA_GOSTJE"),
        "trener_doma":      parse_field(raw, "TRENER_DOMA"),
        "trener_gostje":    parse_field(raw, "TRENER_GOSTJE"),
        "ver_doma":         parse_field(raw, "VERJETNOST_DOMA"),
        "ver_remi":         parse_field(raw, "VERJETNOST_REMI"),
        "ver_gostje":       parse_field(raw, "VERJETNOST_GOSTJE"),
        "kvota_doma":       parse_field(raw, "KVOTA_DOMA"),
        "kvota_remi":       parse_field(raw, "KVOTA_REMI"),
        "kvota_gostje":     parse_field(raw, "KVOTA_GOSTJE"),
        "value_bet":        parse_field(raw, "VALUE_BET"),
        "value_trg":        parse_field(raw, "VALUE_TRG"),
        "razlog_value":     parse_field(raw, "RAZLOG_VALUE"),
        "priporocilo":      parse_field(raw, "PRIPOROCILO"),
        "zaupanje":         parse_field(raw, "ZAUPANJE"),
        "opozorilo":        parse_field(raw, "OPOZORILO"),
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
    tg_tok = st.text_input("Bot token", value=st.session_state.tg_token, placeholder="1234:ABC...", type="password")
    tg_cid = st.text_input("Chat ID", value=st.session_state.tg_chat_id, placeholder="-100...")
    if tg_tok: st.session_state.tg_token = tg_tok
    if tg_cid: st.session_state.tg_chat_id = tg_cid

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
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1.5])
            with c1:
                st.markdown(f"""
                <div style='padding: 14px 0 6px;'>
                  <div style='font-family: Syne, sans-serif; font-size: 16px; font-weight: 600; color: #e8eaf0;'>
                    {match.flag_home} {match.home} <span style='color:#3b4a6b; margin: 0 6px;'>vs</span> {match.flag_away} {match.away}
                  </div>
                  <div style='font-size: 12px; color: #6b7280; margin-top: 4px;'>
                    📅 {match.date} · {match.time} &nbsp;·&nbsp; Skupina {match.group}
                    {"&nbsp; <span class='value-badge'>✦ VALUE BET</span>" if is_value else ""}
                    {"&nbsp; <span style='color:#10b981; font-size:11px;'>✓ Analizirano</span>" if analyzed and not is_value else ""}
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
        model="claude-sonnet-4-20250514",
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