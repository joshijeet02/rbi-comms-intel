import re
from html.parser import HTMLParser
from urllib.parse import urljoin


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

MONTH_PATTERN = (
    r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag != "a":
            return
        attrs_map = dict(attrs)
        href = attrs_map.get("href")
        if href:
            self._current_href = href
            self._chunks = []

    def handle_data(self, data: str):
        if self._current_href:
            self._chunks.append(data)

    def handle_endtag(self, tag: str):
        if tag != "a" or not self._current_href:
            return
        title = normalize_whitespace("".join(self._chunks))
        self.links.append((self._current_href, title))
        self._current_href = None
        self._chunks = []


def extract_index_records(html: str, source: dict) -> list[dict]:
    parser = _LinkParser()
    parser.feed(html)

    records: list[dict] = []
    seen_urls: set[str] = set()
    match_terms = tuple(term.lower() for term in source.get("match_terms", ()))
    base_url = source["base_url"]

    for href, title in parser.links:
        lowered = title.lower()
        if match_terms and not any(term in lowered for term in match_terms):
            continue
        url = urljoin(base_url, href)
        if not title or url in seen_urls:
            continue
        seen_urls.add(url)
        records.append(
            {
                "series_key": source["series_key"],
                "document_type": source["document_type"],
                "title": title,
                "url": url,
            }
        )
    return records


def infer_published_date(text: str) -> str | None:
    normalized = normalize_whitespace(text)
    match = re.search(
        rf"\b{MONTH_PATTERN}\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+(\d{{4}})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if match:
        month = MONTHS[match.group(1).lower()]
        day = int(match.group(2))
        year = int(match.group(3))
        return f"{year:04d}-{month:02d}-{day:02d}"

    match = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{MONTH_PATTERN}(?:,)?\s+(\d{{4}})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if match:
        day = int(match.group(1))
        month = MONTHS[match.group(2).lower()]
        year = int(match.group(3))
        return f"{year:04d}-{month:02d}-{day:02d}"

    match = re.search(r"\b(20\d{2})[-/](\d{2})[-/](\d{2})\b", normalized)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

    match = re.search(rf"\b{MONTH_PATTERN}\s+(20\d{{2}})\b", normalized, flags=re.IGNORECASE)
    if match:
        month = MONTHS[match.group(1).lower()]
        year = int(match.group(2))
        return f"{year:04d}-{month:02d}-01"

    return None


def infer_meeting_key(title: str, document_type: str) -> str | None:
    published_at = infer_published_date(title)
    if not published_at:
        return None

    year, month, _ = published_at.split("-")
    if "annual report" in document_type.lower():
        return year
    return f"{year}-{month}"
