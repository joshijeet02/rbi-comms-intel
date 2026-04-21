import os

import pandas as pd
import streamlit as st

from ai.brief import generate_auto_brief
from db.store import BriefStore, DocumentStore
from engine.briefing import compare_meeting_documents


def render_briefing_view():
    st.subheader("Auto-Briefing Mode")
    store = DocumentStore()
    briefs = BriefStore()
    current = store.get_latest()
    if current is None:
        st.info("No RBI communication records yet.")
        return

    previous = store.get_previous_in_series(current["series_key"], current["published_at"])
    briefing = compare_meeting_documents(previous, current)

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Stance", current["stance_label"].title(), current["document_type"])
    col2.metric("Stance Score", current["stance_score"], current["published_at"])
    col3.metric("New Focus Terms", len(briefing["new_focus_terms"]), current.get("meeting_key") or "No meeting key")

    if previous:
        st.caption(f"Comparing against {previous['title']} ({previous['published_at']})")
    else:
        st.caption("No previous document in this series yet.")

    comparison_df = pd.DataFrame(
        [
            {"Dimension": "Growth", "Change": briefing["growth_change"]},
            {"Dimension": "Inflation", "Change": briefing["inflation_change"]},
            {"Dimension": "Risk Balance", "Change": briefing["risk_balance_change"]},
            {"Dimension": "Liquidity", "Change": briefing["liquidity_change"]},
            {"Dimension": "Forward Guidance", "Change": briefing["guidance_change"]},
        ]
    )
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.markdown("**New Variables In Focus**")
    if briefing["new_focus_terms"]:
        st.write(", ".join(briefing["new_focus_terms"]))
    else:
        st.write("None newly detected.")

    history_df = pd.DataFrame(store.tone_history(limit=12))
    if not history_df.empty:
        st.markdown("**Stance Trend**")
        st.line_chart(history_df.set_index("published_at")[["stance_score"]])

    saved_brief = briefs.get_latest(current["doc_id"])
    if saved_brief and saved_brief.get("brief_text"):
        st.markdown("**Saved Brief**")
        st.write(saved_brief["brief_text"])

    if st.button("Generate Auto Brief", use_container_width=True):
        brief_text = generate_auto_brief(current, briefing)
        briefs.save_briefing(
            meeting_key=current.get("meeting_key") or current["doc_id"],
            current_doc_id=current["doc_id"],
            previous_doc_id=previous["doc_id"] if previous else None,
            briefing=briefing,
            brief_text=brief_text,
        )
        st.success("Auto brief generated and saved.")
        st.write(brief_text)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.caption("Using built-in brief generation fallback until `ANTHROPIC_API_KEY` is set.")
