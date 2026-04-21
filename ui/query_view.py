import pandas as pd
import streamlit as st

from ai.brief import answer_query
from db.store import DocumentStore


def render_query_view():
    st.subheader("Query Mode")
    st.caption(
        "Ask about growth, inflation, liquidity, forward guidance, or how RBI language has changed across meetings."
    )
    store = DocumentStore()
    question = st.text_input(
        "Ask about RBI communications",
        placeholder="How has the MPC described transmission lags since February 2024?",
    )

    if not question:
        st.info("Try a question about inflation, liquidity stance, or changes in forward guidance.")
        return

    rows = store.search(question, limit=8)
    if not rows:
        st.info("No supporting RBI passages found.")
        return

    st.markdown("**Synthesised Answer**")
    st.write(answer_query(question, rows))

    st.markdown("**Supporting Passages**")
    dataframe = pd.DataFrame(rows)[["chunk_id", "title", "published_at", "text"]]
    st.dataframe(dataframe, use_container_width=True, hide_index=True)
