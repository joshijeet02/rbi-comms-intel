import json
import sqlite3
from typing import Optional

from db.schema import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class DocumentStore:
    @staticmethod
    def _with_legacy_aliases(row: sqlite3.Row | dict) -> dict:
        data = dict(row)
        data["net_score"] = data.get("stance_score")
        data["tone_label"] = data.get("stance_label")
        data["policy_bias"] = data.get("forward_guidance")
        try:
            data["new_focus_terms"] = json.loads(data.get("new_focus_terms_json") or "[]")
        except json.JSONDecodeError:
            data["new_focus_terms"] = []
        return data

    def _document_payload(self, record: dict) -> dict:
        doc_id = record["doc_id"]
        published_at = record["published_at"]
        series_key = (
            record.get("series_key")
            or record.get("meeting_key")
            or record.get("document_type")
            or doc_id
        )
        content_hash = record.get("content_hash") or f"{doc_id}:{published_at}"

        return {
            "doc_id": doc_id,
            "series_key": series_key,
            "meeting_key": record.get("meeting_key"),
            "published_at": published_at,
            "document_type": record["document_type"],
            "title": record["title"],
            "speaker": record.get("speaker"),
            "url": record["url"],
            "source": record.get("source") or "RBI",
            "summary": record.get("summary"),
            "full_text": record["full_text"],
            "hawkish_score": record.get("hawkish_score", 0) or 0,
            "dovish_score": record.get("dovish_score", 0) or 0,
            "inflation_mentions": record.get("inflation_mentions", 0) or 0,
            "growth_mentions": record.get("growth_mentions", 0) or 0,
            "liquidity_mentions": record.get("liquidity_mentions", 0) or 0,
            "content_hash": content_hash,
            "stance_score": record.get("stance_score")
            if record.get("stance_score") is not None
            else record.get("net_score", 0),
            "stance_label": record.get("stance_label")
            or record.get("tone_label")
            or "neutral",
            "growth_assessment": record.get("growth_assessment"),
            "inflation_assessment": record.get("inflation_assessment"),
            "risk_balance": record.get("risk_balance"),
            "liquidity_stance": record.get("liquidity_stance"),
            "forward_guidance": record.get("forward_guidance")
            or record.get("policy_bias"),
            "new_focus_terms_json": record.get("new_focus_terms_json") or "[]",
        }

    def upsert_document(self, record: dict):
        payload = self._document_payload(record)
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO documents (
                    doc_id,
                    series_key,
                    meeting_key,
                    published_at,
                    document_type,
                    title,
                    speaker,
                    url,
                    source,
                    summary,
                    full_text,
                    hawkish_score,
                    dovish_score,
                    inflation_mentions,
                    growth_mentions,
                    liquidity_mentions,
                    content_hash,
                    stance_score,
                    stance_label,
                    growth_assessment,
                    inflation_assessment,
                    risk_balance,
                    liquidity_stance,
                    forward_guidance,
                    new_focus_terms_json
                ) VALUES (
                    :doc_id,
                    :series_key,
                    :meeting_key,
                    :published_at,
                    :document_type,
                    :title,
                    :speaker,
                    :url,
                    :source,
                    :summary,
                    :full_text,
                    :hawkish_score,
                    :dovish_score,
                    :inflation_mentions,
                    :growth_mentions,
                    :liquidity_mentions,
                    :content_hash,
                    :stance_score,
                    :stance_label,
                    :growth_assessment,
                    :inflation_assessment,
                    :risk_balance,
                    :liquidity_stance,
                    :forward_guidance,
                    :new_focus_terms_json
                )
                ON CONFLICT(doc_id) DO UPDATE SET
                    series_key = excluded.series_key,
                    meeting_key = excluded.meeting_key,
                    published_at = excluded.published_at,
                    document_type = excluded.document_type,
                    title = excluded.title,
                    speaker = excluded.speaker,
                    url = excluded.url,
                    source = excluded.source,
                    summary = excluded.summary,
                    full_text = excluded.full_text,
                    hawkish_score = excluded.hawkish_score,
                    dovish_score = excluded.dovish_score,
                    inflation_mentions = excluded.inflation_mentions,
                    growth_mentions = excluded.growth_mentions,
                    liquidity_mentions = excluded.liquidity_mentions,
                    content_hash = excluded.content_hash,
                    stance_score = excluded.stance_score,
                    stance_label = excluded.stance_label,
                    growth_assessment = excluded.growth_assessment,
                    inflation_assessment = excluded.inflation_assessment,
                    risk_balance = excluded.risk_balance,
                    liquidity_stance = excluded.liquidity_stance,
                    forward_guidance = excluded.forward_guidance,
                    new_focus_terms_json = excluded.new_focus_terms_json
                """,
                payload,
            )
            conn.commit()
        finally:
            conn.close()

    def upsert(self, record: dict):
        self.upsert_document(record)

    def get_document(self, doc_id: str) -> Optional[dict]:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT *
                FROM documents
                WHERE doc_id = ?
                LIMIT 1
                """,
                (doc_id,),
            ).fetchone()
            return self._with_legacy_aliases(row) if row else None
        finally:
            conn.close()

    def get_previous_in_series(self, series_key: str, published_at: str) -> Optional[dict]:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT *
                FROM documents
                WHERE series_key = ?
                  AND published_at < ?
                ORDER BY published_at DESC, id DESC
                LIMIT 1
                """,
                (series_key, published_at),
            ).fetchone()
            return self._with_legacy_aliases(row) if row else None
        finally:
            conn.close()

    def get_latest(self) -> Optional[dict]:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT *
                FROM documents
                ORDER BY published_at DESC, created_at DESC
                LIMIT 1
                """
            ).fetchone()
            return self._with_legacy_aliases(row) if row else None
        finally:
            conn.close()

    def list_recent(self, limit: int = 10) -> list[dict]:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT *
                FROM documents
                ORDER BY published_at DESC, created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [self._with_legacy_aliases(row) for row in rows]
        finally:
            conn.close()

    def list_documents(self, limit: int = 100) -> list[dict]:
        return self.list_recent(limit=limit)

    def tone_history(self, limit: int = 12) -> list[dict]:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT *
                FROM documents
                ORDER BY published_at DESC, created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            history = [self._with_legacy_aliases(row) for row in rows]
            return list(reversed(history))
        finally:
            conn.close()

    def replace_chunks(self, doc_id: str, chunks: list[dict]):
        conn = _connect()
        try:
            conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
            for chunk in chunks:
                conn.execute(
                    """
                    INSERT INTO document_chunks (
                        chunk_id,
                        doc_id,
                        chunk_index,
                        section_label,
                        page_label,
                        tokens_estimate,
                        text,
                        citations_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk["chunk_id"],
                        chunk["doc_id"],
                        chunk["chunk_index"],
                        chunk.get("section_label"),
                        chunk.get("page_label"),
                        chunk["tokens_estimate"],
                        chunk["text"],
                        chunk.get("citations_json") or "[]",
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def get_chunks(self, doc_id: str) -> list[dict]:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT *
                FROM document_chunks
                WHERE doc_id = ?
                ORDER BY chunk_index ASC
                """,
                (doc_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def search(self, query: str, limit: int = 8) -> list[dict]:
        from engine.retrieval import prepare_search_query

        prepared_query = prepare_search_query(query)
        if not prepared_query:
            return []

        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT
                    c.chunk_id,
                    c.doc_id,
                    c.chunk_index,
                    c.section_label,
                    c.page_label,
                    c.tokens_estimate,
                    c.text,
                    c.citations_json,
                    d.title,
                    d.published_at,
                    d.document_type,
                    d.meeting_key
                FROM document_chunks_fts f
                JOIN document_chunks c ON c.id = f.rowid
                JOIN documents d ON d.doc_id = c.doc_id
                WHERE document_chunks_fts MATCH ?
                ORDER BY bm25(document_chunks_fts), d.published_at DESC
                LIMIT ?
                """,
                (prepared_query, limit),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def count(self) -> int:
        conn = _connect()
        try:
            return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        finally:
            conn.close()


CommunicationStore = DocumentStore


class BriefStore:
    def save_briefing(
        self,
        meeting_key: str,
        current_doc_id: str,
        previous_doc_id: str | None,
        briefing: dict,
        brief_text: str | None = None,
    ):
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO auto_briefs (
                    meeting_key,
                    current_doc_id,
                    previous_doc_id,
                    growth_change,
                    inflation_change,
                    risk_balance_change,
                    liquidity_change,
                    guidance_change,
                    new_focus_terms_json,
                    stance_score,
                    stance_label,
                    brief_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meeting_key,
                    current_doc_id,
                    previous_doc_id,
                    briefing["growth_change"],
                    briefing["inflation_change"],
                    briefing["risk_balance_change"],
                    briefing["liquidity_change"],
                    briefing["guidance_change"],
                    json.dumps(briefing.get("new_focus_terms", [])),
                    briefing["stance_score"],
                    briefing["stance_label"],
                    brief_text,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save(self, doc_id: str, brief_text: str, model: str | None = None):
        del model
        self.save_briefing(
            meeting_key=doc_id,
            current_doc_id=doc_id,
            previous_doc_id=None,
            briefing={
                "growth_change": "unchanged",
                "inflation_change": "unchanged",
                "risk_balance_change": "unchanged",
                "liquidity_change": "unchanged",
                "guidance_change": "unchanged",
                "new_focus_terms": [],
                "stance_score": 0,
                "stance_label": "neutral",
            },
            brief_text=brief_text,
        )

    def get_latest(self, doc_id: str) -> Optional[dict]:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT *
                FROM auto_briefs
                WHERE current_doc_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (doc_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
