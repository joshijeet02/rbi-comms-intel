import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from db.schema import init_db
from db.store import CommunicationStore
from seed.sample_data import seed
from ui.briefing_view import render_briefing_view
from ui.corpus_view import render_corpus_view
from ui.explainer_view import render_explainer_view
from ui.ingestion_view import render_ingestion_view
from ui.query_view import render_query_view


st.set_page_config(
    page_title="RBI Communication Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Header */
    h1 { font-weight: 800 !important; letter-spacing: -0.5px !important; margin-bottom: 0.25rem !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 44px; background-color: #1e2130; border-radius: 8px 8px 0 0;
        padding: 10px 20px; color: #aab; font-weight: 600; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #1F4B99 !important; color: white !important; }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; font-weight: 700 !important; color: #5b9cf6 !important;
    }

    /* Suggested question buttons */
    button[kind="secondary"] {
        background: #1a2038 !important;
        border: 1px solid #2d3561 !important;
        color: #c9d1e0 !important;
        font-size: 0.82rem !important;
        border-radius: 8px !important;
        text-align: left !important;
    }
    button[kind="secondary"]:hover {
        background: #1F4B99 !important;
        color: white !important;
        border-color: #1F4B99 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1523 0%, #141b2d 100%);
        border-right: 1px solid #2d3561;
    }
    [data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 RBI Intelligence")
    st.divider()

    st.markdown("### ⚙️ Mode")
    layman_mode = st.toggle(
        "Simple / Layman Mode",
        value=st.session_state.get("layman_mode", False),
        help="Switch to plain-English explanations focused on everyday impact — EMIs, prices, jobs.",
    )
    st.session_state["layman_mode"] = layman_mode

    if layman_mode:
        st.success("🗣️ **Plain-English Mode ON**\nAnswers avoid jargon and explain real-world impact.")
    else:
        st.info("📊 **Analyst Mode**\nFull economist-grade output with citation and stance scores.")

    st.divider()
    st.markdown("### 📌 About")
    st.caption(
        "This app indexes official RBI communications — MPC statements, "
        "Governor speeches, and policy minutes — and lets you query them "
        "in plain English or expert analyst mode."
    )
    st.markdown("[RBI Official Site](https://www.rbi.org.in)", unsafe_allow_html=False)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()
if CommunicationStore().count() == 0:
    seed()

# ── Header ────────────────────────────────────────────────────────────────────
if layman_mode:
    st.title("🏦 What is the RBI Saying?")
    st.caption(
        "A plain-English guide to India's central bank — what they decide, why it matters, "
        "and how it affects your everyday life."
    )
else:
    st.title("RBI Communication Intelligence")
    st.caption(
        "Query the RBI corpus, compare each meeting to the last one, "
        "and track how policy language is evolving."
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
if layman_mode:
    tab_query, tab_explainer, tab_briefing, tab_corpus = st.tabs(
        ["💬 Ask the RBI", "📖 Jargon Guide", "📋 Meeting Comparisons", "📂 Documents"]
    )
else:
    tab_query, tab_explainer, tab_briefing, tab_corpus, tab_ingestion = st.tabs(
        ["Query Mode", "Explainer / Glossary", "Auto-Briefing Mode", "Corpus", "Ingestion"]
    )

with tab_query:
    render_query_view()

with tab_explainer:
    render_explainer_view()

with tab_briefing:
    render_briefing_view()

with tab_corpus:
    render_corpus_view()

if not layman_mode:
    with tab_ingestion:
        render_ingestion_view()
