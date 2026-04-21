import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.briefing import compare_meeting_documents


class BriefingTests(unittest.TestCase):
    def test_compare_meeting_documents_returns_five_dimension_changes(self):
        previous = {
            "growth_assessment": "growth-balanced",
            "inflation_assessment": "inflation-sticky",
            "risk_balance": "balanced-risks",
            "liquidity_stance": "calibrated-tight",
            "forward_guidance": "vigilant",
            "stance_score": 1.0,
            "stance_label": "hawkish",
            "new_focus_terms_json": "[\"food inflation\"]",
        }
        current = {
            "growth_assessment": "growth-softening",
            "inflation_assessment": "inflation-easing",
            "risk_balance": "two-sided-risks",
            "liquidity_stance": "neutral-liquidity",
            "forward_guidance": "data-dependent",
            "stance_score": -0.5,
            "stance_label": "neutral",
            "new_focus_terms_json": "[\"transmission lags\", \"global volatility\"]",
        }

        brief = compare_meeting_documents(previous, current)

        self.assertIn("growth-softening", brief["growth_change"])
        self.assertIn("inflation-easing", brief["inflation_change"])
        self.assertIn("transmission lags", brief["new_focus_terms"])

    def test_compare_meeting_documents_handles_first_observation(self):
        current = {
            "growth_assessment": "growth-balanced",
            "inflation_assessment": "inflation-sticky",
            "risk_balance": "balanced-risks",
            "liquidity_stance": "calibrated-tight",
            "forward_guidance": "vigilant",
            "stance_score": 1.0,
            "stance_label": "hawkish",
            "new_focus_terms_json": "[\"food inflation\"]",
        }

        brief = compare_meeting_documents(None, current)

        self.assertIn("First observation", brief["growth_change"])
        self.assertEqual(brief["new_focus_terms"], ["food inflation"])


if __name__ == "__main__":
    unittest.main()
