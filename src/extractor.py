"""
src/extractor.py
----------------
Skill extraction for the Resume Skill Gap Analyzer.
Combines spaCy Named Entity Recognition with dictionary-based matching
(exact + fuzzy via rapidfuzz) against the curated skill taxonomy.
"""

import json
import re
from pathlib import Path

import spacy
from rapidfuzz import fuzz

from preprocessor import preprocess_for_ner

# ── Configuration ────────────────────────────────────────────────────────────

TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "skill_taxonomy.json"
FUZZY_THRESHOLD = 85          # rapidfuzz partial_ratio threshold (0–100)
MIN_SKILL_LENGTH = 2          # ignore single-character matches

# ── Load resources ───────────────────────────────────────────────────────────

nlp = spacy.load("en_core_web_sm")

with open(TAXONOMY_PATH, "r") as f:
    TAXONOMY: dict[str, dict[str, list[str]]] = json.load(f)

# Build a flat lookup: variant (lowercase) → canonical name
VARIANT_TO_CANONICAL: dict[str, str] = {}
CANONICAL_TO_CATEGORY: dict[str, str] = {}

for category, skills in TAXONOMY.items():
    for canonical, variants in skills.items():
        CANONICAL_TO_CATEGORY[canonical] = category
        # Include the canonical name itself as a variant
        for variant in [canonical.lower()] + [v.lower() for v in variants]:
            VARIANT_TO_CANONICAL[variant] = canonical


# ── Helpers ──────────────────────────────────────────────────────────────────

def _match_exact(text: str) -> set[str]:
    """Return canonical skill names found via exact substring match."""
    found = set()
    text_lower = text.lower()
    for variant, canonical in VARIANT_TO_CANONICAL.items():
        if len(variant) < MIN_SKILL_LENGTH:
            continue
        # Use word-boundary-aware search to avoid matching 'R' inside 'React'
        pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return found


def _match_fuzzy(tokens: list[str]) -> set[str]:
    """
    Return canonical skill names found via fuzzy matching of individual
    tokens and bigrams against taxonomy variants.
    Only runs on tokens >= 4 characters to reduce false positives.
    """
    found = set()
    candidates = tokens + [
        f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)
    ]
    for candidate in candidates:
        if len(candidate) < 4:
            continue
        for variant, canonical in VARIANT_TO_CANONICAL.items():
            if len(variant) < 4:
                continue
            score = fuzz.partial_ratio(candidate.lower(), variant.lower())
            if score >= FUZZY_THRESHOLD:
                found.add(canonical)
    return found


def _ner_candidates(text: str) -> list[str]:
    """
    Run spaCy NER and return a list of entity and noun-chunk strings
    that may contain skill names.
    """
    doc = nlp(text)
    candidates = []
    # Named entities (ORG, PRODUCT often capture tech names)
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "GPE", "WORK_OF_ART"}:
            candidates.append(ent.text)
    # Noun chunks as additional candidates
    for chunk in doc.noun_chunks:
        candidates.append(chunk.text)
    return candidates


# ── Main extraction function ─────────────────────────────────────────────────

def extract_skills(text: str) -> dict[str, set[str]]:
    """
    Extract skills from text using three complementary methods:
      1. Exact dictionary matching (highest precision)
      2. Fuzzy matching on tokens and bigrams (catches abbreviations)
      3. spaCy NER + noun chunk matching (catches unlisted tech names)

    Returns a dict:
      {
        "all": set of all canonical skill names found,
        "by_category": { category: set of canonical names }
      }
    """
    clean = preprocess_for_ner(text)
    tokens = clean.lower().split()

    # Layer 1: exact match
    exact = _match_exact(clean)

    # Layer 2: fuzzy match
    fuzzy = _match_fuzzy(tokens)

    # Layer 3: NER candidates → exact match those too
    ner_texts = _ner_candidates(clean)
    ner_found = set()
    for candidate in ner_texts:
        ner_found |= _match_exact(candidate)

    all_skills = exact | fuzzy | ner_found

    # Organise by category
    by_category: dict[str, set[str]] = {}
    for skill in all_skills:
        cat = CANONICAL_TO_CATEGORY.get(skill, "Other")
        by_category.setdefault(cat, set()).add(skill)

    return {"all": all_skills, "by_category": by_category}


def skills_as_dict(extraction_result: dict) -> dict:
    """
    Convert sets to sorted lists for JSON serialisation.
    """
    return {
        "all": sorted(extraction_result["all"]),
        "by_category": {
            cat: sorted(skills)
            for cat, skills in extraction_result["by_category"].items()
        }
    }


# ── CLI smoke test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_jd = """
    We are seeking a Software Engineer Intern with strong Python and JavaScript skills.
    Experience with React, Flask, and REST APIs is preferred. Familiarity with Git,
    Docker, and AWS is a plus. You should understand OOP, data structures, and algorithms,
    and be comfortable working in an Agile/Scrum environment. Good communication and
    teamwork skills are essential.
    """

    sample_resume = """
    Skills: Python, Java, HTML, CSS, Git, GitHub, MySQL, OOP, Data Structures.
    Coursework: Software Engineering, Operating Systems, Database Design.
    Projects: Built a client-side web app using JavaScript and jQuery.
    """

    print("=== JD Skills ===")
    jd_result = extract_skills(sample_jd)
    import json as _json
    print(_json.dumps(skills_as_dict(jd_result), indent=2))

    print("\n=== Resume Skills ===")
    resume_result = extract_skills(sample_resume)
    print(_json.dumps(skills_as_dict(resume_result), indent=2))

    print("\n=== Gap (JD - Resume) ===")
    gap = jd_result["all"] - resume_result["all"]
    print(sorted(gap))
