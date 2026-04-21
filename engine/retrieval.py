import re


STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "since",
    "the",
    "their",
    "to",
    "what",
}


def prepare_search_query(query: str) -> str:
    tokens = [
        token
        for token in re.findall(r"[a-zA-Z0-9]+", query.lower())
        if len(token) > 2 and token not in STOPWORDS
    ]
    if not tokens:
        return ""
    return " OR ".join(tokens)


def build_context_window(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        blocks.append(
            f"[{row['chunk_id']}] {row['title']} ({row['published_at']})\n{row['text']}"
        )
    return "\n\n".join(blocks)
