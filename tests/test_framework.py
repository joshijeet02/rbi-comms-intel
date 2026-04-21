import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.framework import assess_document


class FrameworkTests(unittest.TestCase):
    def test_assess_document_extracts_five_dimensions(self):
        text = (
            "Growth is gaining traction, but inflation remains above target. "
            "Liquidity conditions will remain calibrated while policy stays vigilant."
        )

        assessment = assess_document(text)

        self.assertEqual(assessment.growth_assessment, "growth-resilient")
        self.assertEqual(assessment.inflation_assessment, "inflation-sticky")
        self.assertEqual(assessment.liquidity_stance, "calibrated-tight")
        self.assertEqual(assessment.forward_guidance, "vigilant")
        self.assertEqual(assessment.stance_label, "hawkish")

    def test_assess_document_finds_new_focus_terms(self):
        previous_text = "Inflation and growth were the main focus."
        current_text = "Food inflation, transmission lags, and global volatility need attention."

        assessment = assess_document(current_text, previous_text=previous_text)

        self.assertIn("food inflation", assessment.new_focus_terms)
        self.assertIn("transmission lags", assessment.new_focus_terms)
        self.assertIn("global volatility", assessment.new_focus_terms)

    def test_assessment_record_serializes_focus_terms(self):
        assessment = assess_document(
            "Disinflation is broad-based and growth needs support while policy remains data dependent."
        )

        record = assessment.to_record()

        self.assertIn("stance_score", record)
        self.assertIn("new_focus_terms_json", record)
        self.assertIsInstance(json.loads(record["new_focus_terms_json"]), list)


if __name__ == "__main__":
    unittest.main()
