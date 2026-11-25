# AI Study & Grade Advisor (Module 05 Mini Project)

An AI-powered upgrade to the Student Grade Calculator! Enter student subject scores to get grade analytics (average, letter grade, GPA, strongest/weakest subjects) and a personalized study plan powered by the **Gemini API** (with an automatic built-in offline smart advisor fallback).

## Features

- **Python CLI (`main.py` & `ai_advisor.py`)** — Zero external dependencies; works offline or with `GEMINI_API_KEY`
- **Web UI (`index.html`, `styles.css`, `app.js`)** — GitHub Pages ready interactive interface
- **Unit Tests (`tests/test_ai_advisor.py`)** — Automated `unittest` coverage
- **LinkedIn Post Draft (`LINKEDIN_POST.md`)** — Ready-to-share post for the Module 05 deliverable

## Run Locally

```bash
# Run the Python CLI
python main.py

# Optional: enable live Gemini API responses
set GEMINI_API_KEY=your_api_key_here
python main.py

# Run unit tests
python -m unittest discover -s tests -v
```
