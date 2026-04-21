import pandas as pd
import streamlit as st

from db.store import DocumentStore
from scrapers.rbi_sources import RBI_SOURCES
from seed.backfill_corpus import backfill_corpus
from seed.sample_data import seed


def render_ingestion_view():
    st.subheader("Ingestion")
    store = DocumentStore()
    latest = store.get_latest()

    col1, col2 = st.columns(2)
    col1.metric("Documents", store.count())
    col2.metric("Latest Document", latest["published_at"] if latest else "None")

    limit_per_source = st.slider("Documents per source", min_value=1, max_value=20, value=5)

    left, right = st.columns(2)
    if left.button("Seed Sample Corpus", use_container_width=True):
        seed()
        st.success("Sample corpus seeded.")

    if right.button("Backfill From RBI", use_container_width=True):
        try:
            result = backfill_corpus(limit_per_source=limit_per_source)
        except Exception as exc:  # pragma: no cover - UI/runtime path
            st.error(f"Ingestion failed: {exc}")
        else:
            st.success(f"Inserted {result['inserted']} documents.")
            st.write(result)

    st.markdown("**Configured Sources**")
    st.dataframe(
        pd.DataFrame(RBI_SOURCES)[["series_key", "document_type", "index_url"]],
        use_container_width=True,
        hide_index=True,
    )
