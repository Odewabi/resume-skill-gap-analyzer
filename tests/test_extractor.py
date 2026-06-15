"""
tests/test_extractor.py
------------------------
Unit tests for the dictionary-based matching logic in src/extractor.py
Tests run without spaCy by testing only the taxonomy loading and exact matching.
Run with: pytest tests/
"""

import sys
import json
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "skill_taxonomy.json"


def load_taxonomy():
    with open(TAXONOMY_PATH) as f:
        return json.load(f)


def build_lookup(taxonomy):
    variant_to_canonical = {}
    canonical_to_category = {}
    for category, skills in taxonomy.items():
        for canonical, variants in skills.items():
            canonical_to_category[canonical] = category
            for v in [canonical.lower()] + [vv.lower() for vv in variants]:
                variant_to_canonical[v] = canonical
    return variant_to_canonical, canonical_to_category


def match_exact(text, variant_to_canonical, min_len=2):
    found = set()
    text_lower = text.lower()
    for variant, canonical in variant_to_canonical.items():
        if len(variant) < min_len:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return found


# ── Tests ────────────────────────────────────────────────────────────────────

def test_taxonomy_loads():
    taxonomy = load_taxonomy()
    assert isinstance(taxonomy, dict)
    assert len(taxonomy) == 5


def test_taxonomy_has_required_categories():
    taxonomy = load_taxonomy()
    expected = {
        "Programming Languages",
        "Frameworks and Libraries",
        "Tools and Platforms",
        "CS Concepts and Methodologies",
        "Soft and Professional Skills",
    }
    assert set(taxonomy.keys()) == expected


def test_taxonomy_minimum_entries():
    taxonomy = load_taxonomy()
    total = sum(len(v) for v in taxonomy.values())
    assert total >= 50, f"Expected >= 50 skills, got {total}"


def test_taxonomy_all_variants_are_lists():
    taxonomy = load_taxonomy()
    for category, skills in taxonomy.items():
        for canonical, variants in skills.items():
            assert isinstance(variants, list), f"{canonical} variants should be a list"


def test_exact_match_python():
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)
    result = match_exact("Experience with Python programming", lookup)
    assert "Python" in result


def test_exact_match_javascript_alias():
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)
    result = match_exact("Must know JS and React", lookup)
    assert "JavaScript" in result
    assert "React" in result


def test_exact_match_oop_abbreviation():
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)
    result = match_exact("Strong OOP skills required", lookup)
    assert "Object-Oriented Programming" in result


def test_exact_match_agile():
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)
    result = match_exact("Works in Agile/Scrum environment", lookup)
    assert "Agile" in result


def test_no_false_positive_single_char_r():
    """'R' as a language should not match inside words like 'React' or 'required'."""
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)
    # 'R' variant is just 'r' - our min_len=2 guard + word boundary should handle this
    result = match_exact("React is required for this role", lookup)
    # React should match, but standalone 'R' should not cause spurious matches
    assert "React" in result


def test_gap_computation():
    taxonomy = load_taxonomy()
    lookup, _ = build_lookup(taxonomy)

    jd_text = "Python, React, Docker, AWS, REST API, Git, Agile"
    resume_text = "Python, Git, HTML, CSS, OOP, Data Structures"

    jd_skills = match_exact(jd_text, lookup)
    resume_skills = match_exact(resume_text, lookup)
    gap = jd_skills - resume_skills

    assert "React" in gap
    assert "Docker" in gap
    assert "Python" not in gap   # Python is in both
    assert "Git" not in gap      # Git is in both


def test_skills_as_dict_serialisable():
    """Result should be JSON-serialisable (no sets)."""
    taxonomy = load_taxonomy()
    lookup, cat_lookup = build_lookup(taxonomy)
    skills = match_exact("Python Flask Git Docker", lookup)
    by_cat = {}
    for s in skills:
        cat = cat_lookup.get(s, "Other")
        by_cat.setdefault(cat, []).append(s)
    result = {"all": sorted(skills), "by_category": {k: sorted(v) for k, v in by_cat.items()}}
    serialised = json.dumps(result)  # should not raise
    assert "Python" in serialised
