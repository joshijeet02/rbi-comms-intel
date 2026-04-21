import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from db.schema import init_db
from db.store import CommunicationStore
from seed.sample_data import seed
from ui.briefing_view import render_briefing_view
from ui.corpus_view import render_corpus_view
from ui.ingestion_view import render_ingestion_view
from ui.query_view import render_query_view


st.set_page_config(
    page_title="RBI Communication Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-weight: 800 !important; color: #1C1E21 !important;
         letter-spacing: -0.5px !important; margin-bottom: 0.5rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 44px; background-color: #F0F2F6; border-radius: 8px 8px 0px 0px;
        padding: 10px 20px; color: #555; font-weight: 600; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #1F4B99 !important; color: white !important; }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; font-weight: 700 !important; color: #1F4B99 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

init_db()
if CommunicationStore().count() == 0:
    seed()

st.title("RBI Communication Intelligence")
st.caption(
    "Query the RBI corpus, compare each meeting to the last one, and track how policy language is evolving."
)

tab_query, tab_briefing, tab_corpus, tab_ingestion = st.tabs(
    ["Query Mode", "Auto-Briefing Mode", "Corpus", "Ingestion"]
)

with tab_query:
    render_query_view()

with tab_briefing:
    render_briefing_view()

with tab_corpus:
    render_corpus_view()

with tab_ingestion:
    render_ingestion_view()
