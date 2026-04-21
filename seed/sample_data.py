from engine.framework import assess_document
from engine.chunker import chunk_document
from db.store import CommunicationStore
from engine.signal_engine import analyze_communication


SAMPLE_COMMUNICATIONS = [
    {
        "doc_id": "sample-mps-2025-04",
        "published_at": "2025-04-09",
        "document_type": "Monetary Policy Statement",
        "title": "Resolution of the Monetary Policy Committee",
        "speaker": "MPC",
        "url": "https://rbi.example/statement/sample-mps-2025-04",
        "source": "RBI",
        "summary": "Synthetic sample statement with a clearly hawkish policy tone.",
        "full_text": (
            "Inflation risks remain elevated and upside risks require vigilance. "
            "The stance remains focused on withdrawal of accommodation to secure durable "
            "alignment with the target and preserve price stability."
        ),
    },
    {
        "doc_id": "sample-minutes-2025-02",
        "published_at": "2025-02-21",
        "document_type": "MPC Minutes",
        "title": "Minutes of the Monetary Policy Committee Meeting",
        "speaker": "MPC",
        "url": "https://rbi.example/minutes/sample-minutes-2025-02",
        "source": "RBI",
        "summary": "Synthetic sample minutes showing a balanced committee debate.",
        "full_text": (
            "Members noted that inflation is easing, but the committee must remain vigilant. "
            "Growth is steady and policy should remain data dependent while transmission continues."
        ),
    },
    {
        "doc_id": "sample-speech-2025-03",
        "published_at": "2025-03-18",
        "document_type": "Governor Speech",
        "title": "Speech on the evolving macro outlook",
        "speaker": "Governor",
        "url": "https://rbi.example/speeches/sample-speech-2025-03",
        "source": "RBI",
        "summary": "Synthetic sample speech with a more dovish growth-support signal.",
        "full_text": (
            "Disinflation is broad-based and growth needs support. Space is opening to support "
            "activity as price pressures soften and financial conditions remain orderly."
        ),
    },
]


def seed():
    store = CommunicationStore()
    previous_by_series = {}
    for document in SAMPLE_COMMUNICATIONS:
        previous_text = previous_by_series.get(document["document_type"], "")
        signal = analyze_communication(document["full_text"])
        assessment = assess_document(document["full_text"], previous_text=previous_text)
        store.upsert(
            {
                **document,
                **signal.to_record(),
                **assessment.to_record(),
                "series_key": document["document_type"].lower().replace(" ", "-"),
            }
        )
        store.replace_chunks(
            document["doc_id"],
            chunk_document(document["doc_id"], document["full_text"], max_chars=280),
        )
        previous_by_series[document["document_type"]] = document["full_text"]
