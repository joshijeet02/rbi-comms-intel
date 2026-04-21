import re


STOPWORDS = {
    "a", "about", "an", "and", "any", "are", "as", "at",
    "been", "can", "did", "does", "do", "for", "from",
    "has", "have", "how", "in", "is", "it", "its",
    "last", "me", "my", "of", "on", "or", "since",
    "tell", "the", "their", "think", "thinking", "this",
    "to", "us", "was", "what", "when", "which", "who", "will",
    "with", "years", "year",
}

# Map natural-language concepts to RBI domain keywords
# This allows broad questions to still hit the FTS index.
INTENT_KEYWORDS: dict[str, list[str]] = {
    "evolve": ["inflation", "growth", "stance", "guidance", "liquidity"],
    "evolution": ["inflation", "growth", "stance", "guidance", "liquidity"],
    "change": ["inflation", "growth", "stance", "guidance"],
    "changed": ["inflation", "growth", "stance", "guidance"],
    "thinking": ["inflation", "growth", "stance", "policy"],
    "view": ["inflation", "growth", "stance"],
    "views": ["inflation", "growth", "stance"],
    "stance": ["stance", "hawkish", "dovish", "accommodation"],
    "emi": ["repo", "transmission", "rate", "lending"],
    "loan": ["repo", "transmission", "credit", "lending"],
    "homeloan": ["repo", "transmission", "credit"],
    "savings": ["repo", "liquidity", "deposit"],
    "prices": ["inflation", "food", "core", "supply"],
    "food": ["food", "inflation", "supply", "monsoon"],
    "economy": ["growth", "gdp", "demand", "output"],
    "jobs": ["growth", "demand", "output", "employment"],
    "rbi": ["inflation", "growth", "stance", "guidance", "liquidity"],
}


def prepare_search_query(query: str) -> str:
    """
    Builds an FTS OR-query from the user's natural language input.
    For broad/layperson queries that have no specific domain tokens, expands
    intent keywords to domain concepts so FTS always has something to match.
    """
    raw_tokens = re.findall(r"[a-zA-Z0-9]+", query.lower())

    # Collect expansion terms from intent keywords present in this query.
    expansions: list[str] = []
    for token in raw_tokens:
        if token in INTENT_KEYWORDS:
            expansions.extend(INTENT_KEYWORDS[token])

    # Keep non-stopword, meaningful tokens from the original query.
    direct_tokens = [
        t for t in raw_tokens if len(t) > 2 and t not in STOPWORDS
    ]

    # Merge direct tokens + expansions, deduplicate, remove blanks.
    combined = list(dict.fromkeys(direct_tokens + expansions))
    if not combined:
        return ""
    return " OR ".join(combined)


def build_context_window(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        blocks.append(
            f"[{row['chunk_id']}] {row['title']} ({row['published_at']})\n{row['text']}"
        )
    return "\n\n".join(blocks)
