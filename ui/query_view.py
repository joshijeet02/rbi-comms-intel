import pandas as pd
import streamlit as st

from ai.brief import answer_query, answer_query_layman
from db.store import DocumentStore
from ui.stance_gauge import render_stance_gauge


_SUGGESTED_QUESTIONS = [
    "Will my home loan EMI go up?",
    "Is the RBI worried about rising food prices?",
    "How has the RBI's stance changed over the last 5 years?",
    "Is the RBI trying to control inflation or support growth?",
    "What does the latest MPC meeting say about interest rates?",
    "Are interest rates likely to be cut soon?",
]


def render_query_view():
    layman_mode = st.session_state.get("layman_mode", False)

    if layman_mode:
        st.subheader("💬 Ask the RBI Anything")
        st.caption(
            "Type your question in plain English — no economics degree needed. "
            "We'll search through official RBI documents and explain what they say."
        )
    else:
        st.subheader("Query Mode")
        st.caption(
            "Ask about growth, inflation, liquidity, forward guidance, or "
            "how RBI language has changed across meetings."
        )

    store = DocumentStore()

    # Suggested questions
    st.markdown("**💡 Try one of these:**")
    cols = st.columns(3)
    clicked_question = None
    for i, q in enumerate(_SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                clicked_question = q

    if layman_mode:
        placeholder = "e.g. Will my home loan EMI go up? Is the RBI worried about prices?"
        label = "Ask your question"
    else:
        placeholder = "How has the MPC described transmission lags since February 2024?"
        label = "Ask about RBI communications"

    question = st.text_input(label, value=clicked_question or "", placeholder=placeholder)

    if not question:
        if layman_mode:
            st.info("Ask anything about the RBI — about rates, prices, growth, or how policy has changed.")
        else:
            st.info("Try a question about inflation, liquidity stance, or changes in forward guidance.")
        return

    with st.spinner("Searching RBI documents…"):
        rows = store.search(question, limit=8)

        # Smart fallback: if FTS returns nothing, use document summaries
        if not rows:
            fallback_docs = store.list_recent(limit=12)
            if fallback_docs:
                st.warning(
                    "No exact passages matched your question, so I'm drawing from "
                    "recent meeting summaries instead."
                )
                # Convert document-level records to a chunk-compatible shape
                rows = [
                    {
                        "chunk_id": d["doc_id"],
                        "title": d["title"],
                        "published_at": d["published_at"],
                        "text": d.get("summary") or d.get("full_text", "")[:600],
                    }
                    for d in fallback_docs
                    if d.get("summary") or d.get("full_text")
                ]

    if not rows:
        st.error("No RBI documents found in the corpus. Please add documents via the Ingestion tab.")
        return

    st.markdown("---")
    if layman_mode:
        st.markdown("### 🗣️ Plain-English Answer")
    else:
        st.markdown("**Synthesised Answer**")

    answer_fn = answer_query_layman if layman_mode else answer_query
    answer = answer_fn(question, rows)
    st.write(answer)

    # Show stance gauge if docs have stance info
    docs_with_stance = store.list_recent(limit=1)
    if docs_with_stance and docs_with_stance[0].get("stance_score") is not None:
        latest = docs_with_stance[0]
        st.markdown("### 📊 Current RBI Stance")
        render_stance_gauge(latest["stance_score"], latest.get("stance_label", "neutral"))

    st.markdown("---")
    if layman_mode:
        st.markdown("#### 📄 Where We Found This (Source Passages)")
        st.caption("These are the actual RBI document excerpts we used to answer your question.")
        display_df = pd.DataFrame(rows)
        display_df = display_df.rename(columns={
            "title": "Document",
            "published_at": "Date",
            "text": "RBI Passage",
        })
        show_cols = [c for c in ["Document", "Date", "RBI Passage"] if c in display_df.columns]
    else:
        st.markdown("**Supporting Passages**")
        display_df = pd.DataFrame(rows)
        show_cols = [c for c in ["chunk_id", "title", "published_at", "text"] if c in display_df.columns]

    st.dataframe(display_df[show_cols], use_container_width=True, hide_index=True)
