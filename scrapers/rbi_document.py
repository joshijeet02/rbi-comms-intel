import hashlib
import io
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from pypdf import PdfReader


USER_AGENT = "Mozilla/5.0 (compatible; RBICommsBot/1.0; +https://www.rbi.org.in)"


class _HtmlTextParser(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "p",
        "section",
        "td",
        "th",
        "tr",
    }
    SKIP_TAGS = {"script", "style"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        stripped = " ".join(data.split())
        if stripped:
            self._parts.append(stripped)

    def text(self) -> str:
        lines = [" ".join(line.split()) for line in "".join(self._parts).splitlines()]
        return "\n".join(line for line in lines if line)


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    return fetch_bytes(url, timeout=timeout).decode("utf-8", errors="ignore")


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(part for part in parts if part).strip()


def extract_text_from_html(html: str | bytes) -> str:
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="ignore")
    parser = _HtmlTextParser()
    parser.feed(html)
    return parser.text()


def extract_document_text(url: str, content: bytes) -> str:
    lowered_url = url.lower()
    if content.lstrip().startswith(b"%PDF") or lowered_url.endswith(".pdf"):
        return extract_text_from_pdf_bytes(content)
    return extract_text_from_html(content)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
