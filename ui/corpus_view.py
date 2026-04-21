import streamlit as st

from db.store import DocumentStore


def render_corpus_view():
    st.subheader("Corpus")
    store = DocumentStore()
    documents = store.list_documents(limit=100)
    if not documents:
        st.info("No documents in the corpus yet.")
        return

    options = {
        f"{row['published_at']} · {row['document_type']} · {row['title']}": row
        for row in documents
    }
    selected_label = st.selectbox("Select a document", list(options.keys()))
    document = options[selected_label]
    chunks = store.get_chunks(document["doc_id"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Document Type", document["document_type"])
    col2.metric("Chunks", len(chunks))
    col3.metric("Stance", document["stance_label"].title(), document["stance_score"])

    st.markdown("**Framework Read**")
    st.write(
        f"Growth: {document['growth_assessment']} | Inflation: {document['inflation_assessment']} | "
        f"Risk: {document['risk_balance']} | Liquidity: {document['liquidity_stance']} | "
        f"Guidance: {document['forward_guidance']}"
    )
    st.write(document.get("summary") or "No summary available.")
    st.text_area("Document Text", document["full_text"], height=240)

    if chunks:
        st.markdown("**Stored Chunks**")
        for chunk in chunks:
            with st.container(border=True):
                st.caption(chunk["chunk_id"])
                st.write(chunk["text"])
