from scrapers.rbi_document import (
    extract_document_text,
    fetch_bytes,
    fetch_text,
    sha256_text,
)
from scrapers.rbi_index import (
    extract_index_records,
    infer_meeting_key,
    infer_published_date,
    normalize_whitespace,
)
from scrapers.rbi_sources import RBI_SOURCES
from db.store import DocumentStore
from engine.chunker import chunk_document


def first_nonempty_paragraph(text: str) -> str:
    for paragraph in text.split("\n"):
        cleaned = normalize_whitespace(paragraph)
        if cleaned:
            return cleaned
    return ""


def slugify(value: str) -> str:
    letters = []
    for char in value.lower():
        if char.isalnum():
            letters.append(char)
        elif letters and letters[-1] != "-":
            letters.append("-")
    return "".join(letters).strip("-")


def build_doc_id(series_key: str, published_at: str, title: str) -> str:
    date_token = published_at or "undated"
    title_slug = slugify(title)[:48]
    return "-".join(part for part in (series_key, date_token, title_slug) if part)


def backfill_corpus(
    limit_per_source: int = 50,
    sources: list[dict] | None = None,
    fetch_index_text=None,
    fetch_document_bytes=None,
    store: DocumentStore | None = None,
) -> dict[str, object]:
    fetch_index_text = fetch_index_text or fetch_text
    fetch_document_bytes = fetch_document_bytes or fetch_bytes
    sources = sources or RBI_SOURCES
    store = store or DocumentStore()

    inserted = 0
    skipped = 0
    by_source: dict[str, int] = {}

    for source in sources:
        inserted_for_source = 0
        index_html = fetch_index_text(source["index_url"])
        candidates = extract_index_records(index_html, source)[:limit_per_source]

        for record in candidates:
            content = fetch_document_bytes(record["url"])
            full_text = extract_document_text(record["url"], content)
            if not full_text.strip():
                skipped += 1
                continue

            published_at = infer_published_date(record["title"])
            if not published_at:
                skipped += 1
                continue

            summary = first_nonempty_paragraph(full_text)
            payload = {
                **record,
                "doc_id": build_doc_id(record["series_key"], published_at, record["title"]),
                "meeting_key": infer_meeting_key(record["title"], record["document_type"]),
                "published_at": published_at,
                "source": "RBI",
                "summary": summary,
                "full_text": full_text,
                "content_hash": sha256_text(full_text),
                "stance_score": 0.0,
                "stance_label": "neutral",
                "growth_assessment": "",
                "inflation_assessment": "",
                "risk_balance": "",
                "liquidity_stance": "",
                "forward_guidance": "",
                "new_focus_terms_json": "[]",
            }
            store.upsert_document(payload)
            store.replace_chunks(
                payload["doc_id"],
                chunk_document(payload["doc_id"], full_text),
            )
            inserted += 1
            inserted_for_source += 1

        by_source[source["series_key"]] = inserted_for_source

    return {"inserted": inserted, "skipped": skipped, "by_source": by_source}
