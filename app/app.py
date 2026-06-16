"""
app/app.py
----------
Flask web application for the Resume Skill Gap Analyzer.
Routes:
  GET  /          → input form (index.html)
  POST /analyze   → run analysis, render results (results.html)
  GET  /about     → brief project info page
"""

import sys
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

# Add src/ to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessor import preprocess_for_ner
from extractor import extract_skills
from gap_engine import build_report

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    resume_text = request.form.get("resume", "").strip()
    jd_text = request.form.get("jd", "").strip()

    # Basic validation
    errors = []
    if len(resume_text) < 50:
        errors.append("Please paste your full resume text (at least 50 characters).")
    if len(jd_text) < 50:
        errors.append("Please paste the full job description (at least 50 characters).")

    if errors:
        return render_template("index.html", errors=errors,
                               resume=resume_text, jd=jd_text)

    # Run the analysis pipeline
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    report = build_report(resume_text, jd_text, resume_skills, jd_skills)

    return render_template("results.html", report=report,
                           resume=resume_text, jd=jd_text)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
