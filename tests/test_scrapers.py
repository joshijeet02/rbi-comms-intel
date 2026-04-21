import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.schema import init_db
from db.store import DocumentStore
from scrapers.rbi_document import extract_text_from_html, extract_text_from_pdf_bytes
from scrapers.rbi_index import extract_index_records
from seed.backfill_corpus import backfill_corpus


def build_minimal_pdf_bytes(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT\n/F1 18 Tf\n50 100 Td\n({escaped}) Tj\nET\n".encode("latin-1")
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        + f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("latin-1")
        + stream
        + b"endstream\nendobj\n"
        + b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
        + b"xref\n0 6\n"
        + b"0000000000 65535 f \n"
        + b"0000000010 00000 n \n"
        + b"0000000063 00000 n \n"
        + b"0000000122 00000 n \n"
        + b"0000000248 00000 n \n"
        + b"0000000365 00000 n \n"
        + b"trailer<< /Size 6 /Root 1 0 R >>\n"
        + b"startxref\n435\n%%EOF"
    )
    return pdf


class RbiScraperTests(unittest.TestCase):
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

    def test_extract_index_records_filters_supported_links(self):
        html = """
        <ul>
          <li><a href="/Scripts/BS_PressReleaseDisplay.aspx?prid=60001">Resolution of the Monetary Policy Committee April 9, 2025</a></li>
          <li><a href="/Scripts/BS_SpeechesView.aspx?Id=1501">Speech by Governor on monetary policy transmission</a></li>
          <li><a href="/scripts/unused.aspx">Banking ombudsman notice</a></li>
        </ul>
        """
        source = {
            "series_key": "mpc-statement",
            "document_type": "Monetary Policy Statement",
            "base_url": "https://www.rbi.org.in",
            "match_terms": (
                "resolution of the monetary policy committee",
                "monetary policy",
            ),
        }

        records = extract_index_records(html, source)

        self.assertEqual(len(records), 2)
        self.assertEqual(
            records[0]["url"],
            "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60001",
        )
        self.assertEqual(records[1]["title"], "Speech by Governor on monetary policy transmission")

    def test_extract_text_from_html_strips_tags(self):
        html = """
        <html>
          <body>
            <div class="breadcrumbs">Home / Speeches</div>
            <h1>Governor's remarks</h1>
            <p>Inflation risks remain elevated.</p>
            <p>Liquidity conditions are monitored closely.</p>
          </body>
        </html>
        """

        text = extract_text_from_html(html)

        self.assertIn("Governor's remarks", text)
        self.assertIn("Inflation risks remain elevated.", text)
        self.assertIn("Liquidity conditions are monitored closely.", text)

    def test_extract_text_from_pdf_bytes(self):
        pdf_bytes = build_minimal_pdf_bytes("Inflation risks remain elevated.")

        text = extract_text_from_pdf_bytes(pdf_bytes)

        self.assertIn("Inflation risks remain elevated.", text)

    def test_backfill_corpus_builds_document_records(self):
        index_html = """
        <ul>
          <li><a href="/Scripts/BS_PressReleaseDisplay.aspx?prid=60001">Resolution of the Monetary Policy Committee April 9, 2025</a></li>
        </ul>
        """
        document_html = """
        <html>
          <body>
            <p>Inflation risks remain elevated while growth is resilient.</p>
            <p>The committee remains vigilant on liquidity conditions.</p>
          </body>
        </html>
        """
        sources = [
            {
                "series_key": "mpc-statement",
                "document_type": "Monetary Policy Statement",
                "index_url": "https://www.rbi.org.in/index",
                "base_url": "https://www.rbi.org.in",
                "match_terms": ("resolution of the monetary policy committee",),
            }
        ]

        def fake_fetch_text(url: str) -> str:
            self.assertEqual(url, "https://www.rbi.org.in/index")
            return index_html

        def fake_fetch_bytes(url: str) -> bytes:
            self.assertEqual(
                url,
                "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60001",
            )
            return document_html.encode("utf-8")

        result = backfill_corpus(
            limit_per_source=10,
            sources=sources,
            fetch_index_text=fake_fetch_text,
            fetch_document_bytes=fake_fetch_bytes,
        )

        store = DocumentStore()
        row = store.get_latest()

        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["by_source"]["mpc-statement"], 1)
        self.assertIsNotNone(row)
        self.assertEqual(row["series_key"], "mpc-statement")
        self.assertEqual(row["published_at"], "2025-04-09")
        self.assertEqual(row["meeting_key"], "2025-04")
        self.assertIn("Inflation risks remain elevated", row["summary"])
        self.assertIn("liquidity conditions", row["full_text"])


if __name__ == "__main__":
    unittest.main()
