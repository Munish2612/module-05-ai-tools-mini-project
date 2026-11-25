"""AI Study & Grade Advisor core logic (Module 05 Mini Project).

Combines student grade analysis with optional live Gemini API feedback
and a built-in offline smart advisor fallback (zero external dependencies).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


GRADE_SCALE: list[tuple[float, str, float]] = [
    (90.0, "A", 4.0),
    (80.0, "B", 3.0),
    (70.0, "C", 2.0),
    (60.0, "D", 1.0),
    (0.0, "F", 0.0),
]


def get_letter_and_gpa(average: float) -> tuple[str, float]:
    """Return (letter_grade, gpa) for a numeric average."""
    for threshold, letter, gpa in GRADE_SCALE:
        if average >= threshold:
            return letter, gpa
    return "F", 0.0


def analyze_performance(name: str, scores: dict[str, float]) -> dict[str, Any]:
    """Analyze a student's scores and identify strengths and focus areas."""
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Student name cannot be empty.")
    if not scores:
        raise ValueError("At least one subject score is required.")

    validated: dict[str, float] = {}
    for subject, raw_score in scores.items():
        subj = subject.strip()
        if not subj:
            raise ValueError("Subject name cannot be empty.")
        val = float(raw_score)
        if val < 0 or val > 100:
            raise ValueError(f"Score for '{subj}' must be between 0 and 100.")
        validated[subj] = val

    avg = round(sum(validated.values()) / len(validated), 2)
    letter, gpa = get_letter_and_gpa(avg)
    strongest = max(validated.items(), key=lambda item: item[1])
    weakest = min(validated.items(), key=lambda item: item[1])

    return {
        "name": clean_name,
        "scores": validated,
        "average": avg,
        "letter_grade": letter,
        "gpa": gpa,
        "strongest": {"subject": strongest[0], "score": strongest[1]},
        "weakest": {"subject": weakest[0], "score": weakest[1]},
    }


def generate_offline_advice(analysis: dict[str, Any]) -> str:
    """Generate structured, personalized study advice without an API key."""
    name = analysis["name"]
    avg = analysis["average"]
    letter = analysis["letter_grade"]
    strong = analysis["strongest"]
    weak = analysis["weakest"]

    if avg >= 90:
        standing = "Excellent work! You are performing at an honors level."
    elif avg >= 80:
        standing = "Strong performance! You have a solid grasp of the material."
    elif avg >= 70:
        standing = "Good progress, with clear room to push into the B/A range."
    elif avg >= 60:
        standing = "You are passing, but consistent review will make a big difference."
    else:
        standing = "Needs immediate focus—let's build a structured recovery plan."

    tips = [
        f"1. Prioritize {weak['subject']} ({weak['score']:.1f}/100) with 30–45 minutes of active recall daily.",
        f"2. Leverage your momentum in {strong['subject']} ({strong['score']:.1f}/100) to keep confidence high.",
        "3. Practice past problems under timed conditions and summarize mistakes in a short error log.",
    ]

    return (
        f"AI Study Coach Report for {name}\n"
        f"Overall: {avg:.2f} ({letter}, GPA {analysis['gpa']:.1f}) — {standing}\n\n"
        f"Recommended Action Plan:\n" + "\n".join(tips)
    )


def generate_ai_advice(
    analysis: dict[str, Any], api_key: str | None = None
) -> tuple[str, str]:
    """Return (advice_text, source) using Gemini API if key is set, else offline fallback."""
    key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return generate_offline_advice(analysis), "offline-advisor"

    prompt = (
        f"You are a supportive academic coach. Give a concise 4-line study plan for "
        f"{analysis['name']} based on these scores: {analysis['scores']}. "
        f"Average: {analysis['average']} ({analysis['letter_grade']}). "
        f"Strongest: {analysis['strongest']}. Weakest: {analysis['weakest']}."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={key}"
    )
    payload = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text, "gemini-api"
    except (urllib.error.URLError, KeyError, IndexError, TimeoutError):
        return generate_offline_advice(analysis), "offline-fallback"
