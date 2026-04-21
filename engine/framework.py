import json
from dataclasses import dataclass


GROWTH_RULES = {
    "growth-resilient": (
        "growth is gaining traction",
        "growth remains resilient",
        "resilient domestic activity",
        "investment demand remains strong",
        "growth holds up",
        "growth is steady",
    ),
    "growth-softening": (
        "growth needs support",
        "slowdown",
        "weak demand",
        "support activity",
        "growth moderation",
        "growth is slowing",
    ),
}

INFLATION_RULES = {
    "inflation-sticky": (
        "inflation remains above target",
        "inflation risks remain elevated",
        "price pressures persist",
        "upside inflation risks",
        "inflation remains elevated",
    ),
    "inflation-easing": (
        "disinflation is broad-based",
        "inflation is easing",
        "price pressures soften",
        "inflation is moderating",
        "disinflation continues",
    ),
}

RISK_RULES = {
    "upside-inflation-risks": (
        "upside risks",
        "inflation risks remain elevated",
        "upside inflation risks",
        "uncertainty remains high",
        "global volatility",
    ),
    "downside-growth-risks": (
        "downside risks to growth",
        "growth needs support",
        "weak demand",
        "global slowdown",
    ),
}

LIQUIDITY_RULES = {
    "tight-liquidity": (
        "withdrawal of accommodation",
        "liquidity conditions remain tight",
        "absorption of liquidity",
        "tight liquidity conditions",
    ),
    "calibrated-tight": (
        "liquidity conditions will remain calibrated",
        "remain calibrated",
        "calibrated liquidity",
        "nimble liquidity management",
    ),
    "durable-liquidity": (
        "orderly liquidity",
        "adequate liquidity",
        "durable liquidity",
        "system liquidity remains supportive",
    ),
}

GUIDANCE_RULES = {
    "vigilant": (
        "remain vigilant",
        "stays vigilant",
        "policy stays vigilant",
        "durable alignment",
        "watchful on inflation",
    ),
    "data-dependent": (
        "data dependent",
        "data-dependent",
        "incoming data",
        "meeting by meeting",
    ),
    "supportive": (
        "growth needs support",
        "support activity",
        "accommodative",
        "space is opening",
    ),
}

FOCUS_TERMS = (
    "food inflation",
    "transmission lags",
    "global volatility",
    "financial conditions",
    "liquidity conditions",
    "core inflation",
    "rural demand",
    "credit growth",
    "monsoon",
    "supply shocks",
    "exchange rate",
    "durable alignment",
    "uncertainty",
)

STANCE_WEIGHTS = {
    "growth-resilient": 0.5,
    "growth-balanced": 0.0,
    "growth-softening": -0.5,
    "inflation-sticky": 1.0,
    "inflation-balanced": 0.0,
    "inflation-easing": -1.0,
    "upside-inflation-risks": 0.75,
    "balanced-risks": 0.0,
    "downside-growth-risks": -0.5,
    "tight-liquidity": 1.0,
    "calibrated-tight": 0.5,
    "durable-liquidity": -0.25,
    "neutral-liquidity": 0.0,
    "vigilant": 0.75,
    "data-dependent": 0.0,
    "supportive": -0.75,
    "neutral-guidance": 0.0,
}


@dataclass
class FrameworkAssessment:
    growth_assessment: str
    inflation_assessment: str
    risk_balance: str
    liquidity_stance: str
    forward_guidance: str
    stance_score: float
    stance_label: str
    new_focus_terms: list[str]

    def to_record(self) -> dict:
        return {
            "growth_assessment": self.growth_assessment,
            "inflation_assessment": self.inflation_assessment,
            "risk_balance": self.risk_balance,
            "liquidity_stance": self.liquidity_stance,
            "forward_guidance": self.forward_guidance,
            "stance_score": self.stance_score,
            "stance_label": self.stance_label,
            "new_focus_terms_json": json.dumps(self.new_focus_terms),
        }


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def first_matching_label(text: str, rules: dict[str, tuple[str, ...]], fallback: str) -> str:
    for label, phrases in rules.items():
        if any(phrase in text for phrase in phrases):
            return label
    return fallback


def infer_risk_balance(text: str) -> str:
    return first_matching_label(text, RISK_RULES, fallback="balanced-risks")


def infer_liquidity_stance(text: str) -> str:
    return first_matching_label(text, LIQUIDITY_RULES, fallback="neutral-liquidity")


def infer_forward_guidance(text: str) -> str:
    return first_matching_label(text, GUIDANCE_RULES, fallback="neutral-guidance")


def compute_stance_score(
    growth_assessment: str,
    inflation_assessment: str,
    risk_balance: str,
    liquidity_stance: str,
    forward_guidance: str,
) -> float:
    return round(
        STANCE_WEIGHTS[growth_assessment]
        + STANCE_WEIGHTS[inflation_assessment]
        + STANCE_WEIGHTS[risk_balance]
        + STANCE_WEIGHTS[liquidity_stance]
        + STANCE_WEIGHTS[forward_guidance],
        2,
    )


def extract_new_focus_terms(text: str, previous_text: str) -> list[str]:
    previous_normalized = normalize_text(previous_text)
    return [
        term
        for term in FOCUS_TERMS
        if term in text and term not in previous_normalized
    ]


def assess_document(text: str, previous_text: str | None = None) -> FrameworkAssessment:
    normalized = normalize_text(text)
    growth_assessment = first_matching_label(
        normalized,
        GROWTH_RULES,
        fallback="growth-balanced",
    )
    inflation_assessment = first_matching_label(
        normalized,
        INFLATION_RULES,
        fallback="inflation-balanced",
    )
    risk_balance = infer_risk_balance(normalized)
    liquidity_stance = infer_liquidity_stance(normalized)
    forward_guidance = infer_forward_guidance(normalized)
    stance_score = compute_stance_score(
        growth_assessment,
        inflation_assessment,
        risk_balance,
        liquidity_stance,
        forward_guidance,
    )
    if stance_score >= 1.0:
        stance_label = "hawkish"
    elif stance_score <= -1.0:
        stance_label = "dovish"
    else:
        stance_label = "neutral"

    return FrameworkAssessment(
        growth_assessment=growth_assessment,
        inflation_assessment=inflation_assessment,
        risk_balance=risk_balance,
        liquidity_stance=liquidity_stance,
        forward_guidance=forward_guidance,
        stance_score=stance_score,
        stance_label=stance_label,
        new_focus_terms=extract_new_focus_terms(normalized, previous_text or ""),
    )
