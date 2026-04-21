import json


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    if len(paragraph) <= max_chars:
        return [paragraph]

    words = paragraph.split()
    parts: list[str] = []
    buffer = ""
    for word in words:
        candidate = word if not buffer else f"{buffer} {word}"
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            parts.append(buffer)
        buffer = word
    if buffer:
        parts.append(buffer)
    return parts


def chunk_document(doc_id: str, text: str, max_chars: int = 1400) -> list[dict]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[dict] = []
    buffer = ""
    chunk_index = 0

    def flush(current_text: str):
        nonlocal chunk_index
        cleaned = current_text.strip()
        if not cleaned:
            return
        chunk_id = f"{doc_id}::{chunk_index}"
        chunks.append(
            {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_index": chunk_index,
                "section_label": None,
                "page_label": None,
                "tokens_estimate": max(1, len(cleaned) // 4),
                "text": cleaned,
                "citations_json": json.dumps([chunk_id]),
            }
        )
        chunk_index += 1

    for paragraph in paragraphs:
        for piece in _split_long_paragraph(paragraph, max_chars):
            candidate = piece if not buffer else f"{buffer}\n\n{piece}"
            if len(candidate) <= max_chars:
                buffer = candidate
                continue
            flush(buffer)
            buffer = piece

    flush(buffer)
    return chunks
