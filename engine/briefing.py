import json


def _load_focus_terms(record: dict | None) -> list[str]:
    if not record:
        return []
    if isinstance(record.get("new_focus_terms"), list):
        return record["new_focus_terms"]
    raw_value = record.get("new_focus_terms_json") or "[]"
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return []


def compare_meeting_documents(previous: dict | None, current: dict) -> dict:
    current_focus_terms = _load_focus_terms(current)
    if previous is None:
        return {
            "growth_change": f"First observation: {current['growth_assessment']}",
            "inflation_change": f"First observation: {current['inflation_assessment']}",
            "risk_balance_change": f"First observation: {current['risk_balance']}",
            "liquidity_change": f"First observation: {current['liquidity_stance']}",
            "guidance_change": f"First observation: {current['forward_guidance']}",
            "new_focus_terms": current_focus_terms,
            "stance_score": current["stance_score"],
            "stance_label": current["stance_label"],
        }

    previous_focus_terms = _load_focus_terms(previous)
    return {
        "growth_change": f"{previous['growth_assessment']} -> {current['growth_assessment']}",
        "inflation_change": f"{previous['inflation_assessment']} -> {current['inflation_assessment']}",
        "risk_balance_change": f"{previous['risk_balance']} -> {current['risk_balance']}",
        "liquidity_change": f"{previous['liquidity_stance']} -> {current['liquidity_stance']}",
        "guidance_change": f"{previous['forward_guidance']} -> {current['forward_guidance']}",
        "new_focus_terms": sorted(set(current_focus_terms) - set(previous_focus_terms)),
        "stance_score": current["stance_score"],
        "stance_label": current["stance_label"],
    }
