import os

try:
    import anthropic
except ImportError:  # pragma: no cover - optional dependency
    anthropic = None

from engine.retrieval import build_context_window


_SYSTEM = (
    "You are a senior India economist writing an RBI communication note for a rates strategist. "
    "Explain the communication tone, policy bias, and the rates-market implication. "
    "Write three short paragraphs, plain prose, no headers, no throat-clearing."
)

_LAYMAN_SYSTEM = (
    "You are a friendly guide explaining India's central bank (RBI) to a curious person with no economics background. "
    "Avoid all jargon — never use terms like 'hawkish', 'basis points', or 'transmission' without explaining them first. "
    "Focus on what the RBI's decisions mean for everyday people: home loan EMIs, grocery prices, savings rates, and jobs. "
    "Write in short, simple paragraphs. Be warm, clear, and direct."
)


def _client() -> anthropic.Anthropic:
    if anthropic is None:
        raise EnvironmentError("anthropic package not installed")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


def build_query_prompt(question: str, context_window: str) -> str:
    return f"""You are answering a question about RBI communications.

Question:
{question}

Use only the cited context below.
Every factual claim must cite chunk IDs in square brackets.

Context:
{context_window}
"""


def _fallback_cited_answer(question: str, context_rows: list[dict]) -> str:
    del question
    opening = "Relevant RBI passages point to the following pattern:"
    points = []
    for row in context_rows[:3]:
        snippet = row["text"].strip().split(". ")[0].strip()
        if not snippet.endswith("."):
            snippet = f"{snippet}."
        points.append(f"{snippet} [{row['chunk_id']}]")
    return "\n\n".join([opening, *points])


def _fallback_layman_answer(question: str, context_rows: list[dict]) -> str:
    del question
    lines = [
        "Based on recent RBI documents, here's what we found:\n"
    ]
    for row in context_rows[:3]:
        snippet = row["text"].strip().split(". ")[0].strip()
        if not snippet.endswith("."):
            snippet = f"{snippet}."
        date = row.get("published_at", "")
        title = row.get("title", "RBI Document")
        lines.append(f"📄 *{title}* ({date}): {snippet}")
    lines.append(
        "\n*Note: Add an Anthropic API key via Streamlit Secrets to get a full plain-English summary.*"
    )
    return "\n\n".join(lines)


def answer_query(question: str, context_rows: list[dict]) -> str:
    context_window = build_context_window(context_rows)
    try:
        client = _client()
    except EnvironmentError:
        return _fallback_cited_answer(question, context_rows)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system="You are a senior India rates economist. Be concise, analytical, and citation-heavy.",
        messages=[
            {
                "role": "user",
                "content": build_query_prompt(question, context_window),
            }
        ],
    )
    return message.content[0].text


def answer_query_layman(question: str, context_rows: list[dict]) -> str:
    """Like answer_query but uses plain-English prompts suitable for non-economists."""
    context_window = build_context_window(context_rows)
    try:
        client = _client()
    except EnvironmentError:
        return _fallback_layman_answer(question, context_rows)

    prompt = (
        f"A person with no economics background has asked the following question about the RBI:\n\n"
        f"{question}\n\n"
        f"Use the RBI document excerpts below to answer. Explain in simple terms what this means "
        f"for everyday life — home loans, prices, jobs, savings. Avoid abbreviations and jargon."
        f"\n\nContext from RBI documents:\n{context_window}"
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=_LAYMAN_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def build_auto_brief_prompt(current_doc: dict, briefing: dict) -> str:
    return f"""Write an RBI MPC meeting brief.

Current document: {current_doc['title']} ({current_doc['published_at']})
Growth change: {briefing['growth_change']}
Inflation change: {briefing['inflation_change']}
Risk balance change: {briefing['risk_balance_change']}
Liquidity change: {briefing['liquidity_change']}
Guidance change: {briefing['guidance_change']}
New focus terms: {', '.join(briefing['new_focus_terms']) or 'none'}
Stance score: {briefing['stance_score']} ({briefing['stance_label']})
"""


def _fallback_auto_brief(current_doc: dict, briefing: dict) -> str:
    return (
        f"{current_doc['title']} leaves the growth assessment at {briefing['growth_change']} "
        f"and the inflation assessment at {briefing['inflation_change']}. "
        f"Liquidity reads as {briefing['liquidity_change']}, while guidance shifts through "
        f"{briefing['guidance_change']}.\n\n"
        f"The overall stance score is {briefing['stance_score']} "
        f"({briefing['stance_label']}). New variables in focus: "
        f"{', '.join(briefing['new_focus_terms']) or 'none'}."
    )


def generate_auto_brief(current_doc: dict, briefing: dict) -> str:
    try:
        client = _client()
    except EnvironmentError:
        return _fallback_auto_brief(current_doc, briefing)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=_SYSTEM,
        messages=[{"role": "user", "content": build_auto_brief_prompt(current_doc, briefing)}],
    )
    return message.content[0].text


def generate_communication_brief(document: dict) -> str:
    prompt = f"""RBI Communication Intelligence

TITLE: {document['title']}
TYPE: {document['document_type']}
DATE: {document['published_at']}
SPEAKER: {document.get('speaker') or 'Unknown'}

MODEL SIGNALS:
- Tone label: {document['tone_label']}
- Policy bias: {document['policy_bias']}
- Net score: {document['net_score']}
- Inflation mentions: {document['inflation_mentions']}
- Growth mentions: {document['growth_mentions']}
- Liquidity mentions: {document['liquidity_mentions']}

SUMMARY:
{document.get('summary') or 'No summary provided.'}

TEXT:
{document['full_text'][:4000]}

Write:
1. What changed in the communication stance.
2. What the document implies for the next RBI reaction function.
3. What bond markets should infer from the tone.
"""

    try:
        client = _client()
    except EnvironmentError:
        return (
            f"{document['title']} reads as {document['tone_label']} with a "
            f"{document['policy_bias']} signal. Inflation references total "
            f"{document['inflation_mentions']}, growth references total {document['growth_mentions']}, "
            f"and liquidity references total {document['liquidity_mentions']}.\n\n"
            f"The communication implies the RBI is leaning {document['tone_label']} for now, "
            f"with rates-market implications driven by the document's emphasis on "
            f"{document['policy_bias']}."
        )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
