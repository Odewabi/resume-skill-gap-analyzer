"""
src/gap_engine.py
-----------------
Computes the skill gap between a resume and job description,
and formats the result for display in the web interface.
"""

from scorer import compute_similarity, interpret_score


# Plain-language improvement tips keyed by skill category
TIPS = {
    "Programming Languages": (
        "Add any missing languages to your Skills section. "
        "Even a small personal project using that language demonstrates initiative."
    ),
    "Frameworks and Libraries": (
        "List frameworks in a dedicated Skills or Technologies section. "
        "If you've used them in coursework or projects, name the project explicitly."
    ),
    "Tools and Platforms": (
        "Mention tools you've used in project descriptions — e.g., "
        "'Deployed using Docker' or 'Version control with Git/GitHub'."
    ),
    "CS Concepts and Methodologies": (
        "Highlight relevant concepts in your coursework section or project summaries. "
        "For example, 'Applied OOP principles in a Java-based inventory system'."
    ),
    "Soft and Professional Skills": (
        "Weave soft skills into your experience bullets — e.g., "
        "'Collaborated with a team of 4 to deliver...' instead of just listing 'Teamwork'."
    ),
    "Other": (
        "Review the job description for any additional keywords and ensure "
        "your resume uses similar language where accurate."
    ),
}


def compute_gap(resume_skills: dict, jd_skills: dict) -> dict:
    """
    Compute the skill gap between resume and job description skill sets.

    Args:
        resume_skills: result dict from extractor.extract_skills() on the resume
        jd_skills:     result dict from extractor.extract_skills() on the JD

    Returns a dict with:
        - missing_skills: { category: [skill, ...] }   skills in JD but not resume
        - matched_skills: { category: [skill, ...] }   skills in both
        - missing_count: int
        - matched_count: int
        - total_jd_skills: int
        - coverage_pct: float  (0–100)
    """
    resume_all = resume_skills.get("all", set())
    jd_all = jd_skills.get("all", set())
    jd_by_cat = jd_skills.get("by_category", {})

    missing_all = jd_all - resume_all
    matched_all = jd_all & resume_all

    # Organise missing skills by category
    missing_by_cat: dict[str, list[str]] = {}
    for cat, skills in jd_by_cat.items():
        missing = sorted(s for s in skills if s in missing_all)
        if missing:
            missing_by_cat[cat] = missing

    # Organise matched skills by category
    matched_by_cat: dict[str, list[str]] = {}
    for cat, skills in jd_by_cat.items():
        matched = sorted(s for s in skills if s in matched_all)
        if matched:
            matched_by_cat[cat] = matched

    total_jd = len(jd_all)
    coverage = round((len(matched_all) / total_jd * 100), 1) if total_jd > 0 else 0.0

    return {
        "missing_skills": missing_by_cat,
        "matched_skills": matched_by_cat,
        "missing_count": len(missing_all),
        "matched_count": len(matched_all),
        "total_jd_skills": total_jd,
        "coverage_pct": coverage,
    }


def generate_tips(missing_by_category: dict[str, list[str]]) -> list[str]:
    """
    Generate plain-language improvement tips based on which
    skill categories have gaps.
    """
    tips = []
    for cat in missing_by_category:
        tip = TIPS.get(cat, TIPS["Other"])
        tips.append(f"**{cat}:** {tip}")
    return tips


def build_report(
    resume_text: str,
    jd_text: str,
    resume_skills: dict,
    jd_skills: dict,
) -> dict:
    """
    Build the complete gap report combining similarity score,
    skill gap, and improvement tips.

    Returns a single report dict ready to pass to the Flask template.
    """
    # Similarity score
    raw_score = compute_similarity(resume_text, jd_text)
    similarity = interpret_score(raw_score)

    # Skill gap
    gap = compute_gap(resume_skills, jd_skills)

    # Tips (only for categories with missing skills)
    tips = generate_tips(gap["missing_skills"])

    return {
        "similarity": similarity,
        "missing_skills": gap["missing_skills"],
        "matched_skills": gap["matched_skills"],
        "missing_count": gap["missing_count"],
        "matched_count": gap["matched_count"],
        "total_jd_skills": gap["total_jd_skills"],
        "coverage_pct": gap["coverage_pct"],
        "tips": tips,
    }


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    # Simulate extractor output for a quick smoke test
    resume_skills = {
        "all": {"Python", "Git", "HTML", "CSS", "Object-Oriented Programming",
                "Data Structures", "MySQL", "JavaScript"},
        "by_category": {
            "Programming Languages": {"Python", "JavaScript", "HTML", "CSS"},
            "Tools and Platforms":   {"Git", "MySQL"},
            "CS Concepts and Methodologies": {"Object-Oriented Programming", "Data Structures"},
        }
    }

    jd_skills = {
        "all": {"Python", "JavaScript", "React", "Flask", "Git", "Docker",
                "AWS", "Object-Oriented Programming", "Algorithms", "Agile", "REST API"},
        "by_category": {
            "Programming Languages":        {"Python", "JavaScript"},
            "Frameworks and Libraries":     {"React", "Flask", "REST API"},
            "Tools and Platforms":          {"Git", "Docker", "AWS"},
            "CS Concepts and Methodologies":{"Object-Oriented Programming", "Algorithms"},
            "Soft and Professional Skills": {"Agile"},
        }
    }

    resume_text = "Python Java HTML CSS Git GitHub MySQL OOP Data Structures JavaScript jQuery"
    jd_text = ("Python JavaScript React Flask REST APIs Git Docker AWS "
               "OOP data structures algorithms Agile Scrum communication teamwork")

    report = build_report(resume_text, jd_text, resume_skills, jd_skills)

    print(f"Similarity     : {report['similarity']['score']} — {report['similarity']['label']}")
    print(f"Coverage       : {report['coverage_pct']}% ({report['matched_count']}/{report['total_jd_skills']} JD skills matched)")
    print(f"Missing skills : {report['missing_count']}")
    for cat, skills in report["missing_skills"].items():
        print(f"  {cat}: {skills}")
    print(f"\nMatched skills : {report['matched_count']}")
    for cat, skills in report["matched_skills"].items():
        print(f"  {cat}: {skills}")
    print(f"\nTips:")
    for tip in report["tips"]:
        print(f"  - {tip}")
