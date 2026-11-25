"""Unit tests for the AI Study & Grade Advisor."""

from __future__ import annotations

import unittest

from ai_advisor import (
    analyze_performance,
    generate_ai_advice,
    generate_offline_advice,
    get_letter_and_gpa,
)


class TestAIAdvisor(unittest.TestCase):
    def test_letter_and_gpa(self) -> None:
        self.assertEqual(get_letter_and_gpa(92), ("A", 4.0))
        self.assertEqual(get_letter_and_gpa(83), ("B", 3.0))
        self.assertEqual(get_letter_and_gpa(74), ("C", 2.0))
        self.assertEqual(get_letter_and_gpa(61), ("D", 1.0))
        self.assertEqual(get_letter_and_gpa(45), ("F", 0.0))

    def test_analyze_performance(self) -> None:
        result = analyze_performance("Alex", {"Math": 80, "Python": 96, "Stats": 70})
        self.assertEqual(result["average"], 82.0)
        self.assertEqual(result["letter_grade"], "B")
        self.assertEqual(result["strongest"]["subject"], "Python")
        self.assertEqual(result["weakest"]["subject"], "Stats")

    def test_analyze_performance_invalid(self) -> None:
        with self.assertRaises(ValueError):
            analyze_performance("", {"Math": 90})
        with self.assertRaises(ValueError):
            analyze_performance("Alex", {})
        with self.assertRaises(ValueError):
            analyze_performance("Alex", {"Math": 105})

    def test_generate_offline_and_fallback_advice(self) -> None:
        analysis = analyze_performance("Alex", {"Math": 65, "Python": 92})
        offline = generate_offline_advice(analysis)
        self.assertIn("Alex", offline)
        self.assertIn("Math", offline)
        self.assertIn("Python", offline)

        advice, source = generate_ai_advice(analysis, api_key="")
        self.assertEqual(source, "offline-advisor")
        self.assertIn("Recommended Action Plan", advice)


if __name__ == "__main__":
    unittest.main()
