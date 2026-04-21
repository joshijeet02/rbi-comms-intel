import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.schema import init_db
from db.store import DocumentStore
from engine.chunker import chunk_document
from engine.retrieval import build_context_window


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.test_db = Path(self.tmpdir.name) / "test.db"
        self.schema_patch = mock.patch("db.schema.DB_PATH", self.test_db)
        self.store_patch = mock.patch("db.store.DB_PATH", self.test_db)
        self.schema_patch.start()
        self.store_patch.start()
        init_db()

    def tearDown(self):
        self.store_patch.stop()
        self.schema_patch.stop()
        self.tmpdir.cleanup()

    def test_chunk_document_preserves_source_metadata(self):
        chunks = chunk_document(
            doc_id="mpc-minutes-2025-04",
            text=(
                "Paragraph one.\n\n"
                "Paragraph two mentions transmission lags.\n\n"
                "Paragraph three mentions food inflation."
            ),
            max_chars=60,
        )

        self.assertEqual(chunks[0]["doc_id"], "mpc-minutes-2025-04")
        self.assertEqual(chunks[0]["chunk_index"], 0)
        self.assertIn("Paragraph one.", chunks[0]["text"])
        self.assertGreaterEqual(chunks[0]["tokens_estimate"], 1)

    def test_format_cited_answer_context_includes_chunk_ids(self):
        context = build_context_window(
            [
                {
                    "chunk_id": "mpc-minutes-2025-04::1",
                    "doc_id": "mpc-minutes-2025-04",
                    "title": "Minutes April 2025",
                    "published_at": "2025-04-23",
                    "text": "Transmission lags remain relevant.",
                }
            ]
        )

        self.assertIn("[mpc-minutes-2025-04::1]", context)
        self.assertIn("Transmission lags remain relevant.", context)

    def test_document_store_search_returns_chunk_context(self):
        store = DocumentStore()
        store.upsert_document(
            {
                "doc_id": "mpc-minutes-2025-04",
                "series_key": "mpc-minutes",
                "meeting_key": "2025-04",
                "published_at": "2025-04-23",
                "document_type": "MPC Minutes",
                "title": "Minutes April 2025",
                "speaker": "MPC",
                "url": "https://rbi.example/minutes-april-2025",
                "summary": "Minutes with discussion of transmission lags.",
                "full_text": "Transmission lags remain relevant for policy calibration.",
                "content_hash": "minutes-april-2025",
            }
        )
        store.replace_chunks(
            "mpc-minutes-2025-04",
            chunk_document(
                doc_id="mpc-minutes-2025-04",
                text=(
                    "Paragraph one.\n\n"
                    "Transmission lags remain relevant for policy calibration.\n\n"
                    "Food inflation is still a concern."
                ),
                max_chars=80,
            ),
        )

        rows = store.search("transmission lags", limit=5)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doc_id"], "mpc-minutes-2025-04")
        self.assertEqual(rows[0]["title"], "Minutes April 2025")
        self.assertIn("Transmission lags remain relevant", rows[0]["text"])


if __name__ == "__main__":
    unittest.main()
