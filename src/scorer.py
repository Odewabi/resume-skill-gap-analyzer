"""
src/scorer.py
-------------
TF-IDF vectorization and cosine similarity scoring for the Resume Skill Gap Analyzer.
Computes an overall similarity score between resume and job description text.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute cosine similarity between resume and job description
    using TF-IDF vectorization.

    Returns a float between 0.0 (no overlap) and 1.0 (identical).
    """
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # unigrams and bigrams
        stop_words="english",
        min_df=1,
    )
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score), 4)


def interpret_score(score: float) -> dict:
    """
    Convert a raw cosine similarity score into a human-readable label,
    color class, and plain-language description for the UI.
    """
    if score >= 0.70:
        return {
            "score": score,
            "label": "Strong Match",
            "css_class": "strong",
            "description": (
                "Your resume aligns well with this job description. "
                "Focus on addressing any specific skill gaps listed below."
            ),
        }
    elif score >= 0.45:
        return {
            "score": score,
            "label": "Moderate Match",
            "css_class": "moderate",
            "description": (
                "Your resume partially matches this job description. "
                "Adding the missing skills below could significantly improve your fit."
            ),
        }
    elif score >= 0.20:
        return {
            "score": score,
            "label": "Low Match",
            "css_class": "low",
            "description": (
                "Your resume has limited overlap with this job description. "
                "Consider tailoring your resume language to better reflect the role's requirements."
            ),
        }
    else:
        return {
            "score": score,
            "label": "Very Low Match",
            "css_class": "very-low",
            "description": (
                "Your resume and this job description share very little common language. "
                "Review the job description carefully and update your resume to address "
                "the specific skills and tools listed."
            ),
        }


if __name__ == "__main__":
    resume = """
    Skills: Python, Java, HTML, CSS, Git, GitHub, MySQL, OOP, Data Structures.
    Coursework: Software Engineering, Operating Systems, Database Design.
    Projects: Built a client-side web app using JavaScript and jQuery.
    Experience with unit testing and debugging.
    """

    jd = """
    We are seeking a Software Engineer Intern with strong Python and JavaScript skills.
    Experience with React, Flask, and REST APIs is preferred. Familiarity with Git,
    Docker, and AWS is a plus. You should understand OOP, data structures, and algorithms,
    and be comfortable working in an Agile/Scrum environment. Good communication and
    teamwork skills are essential.
    """

    score = compute_similarity(resume, jd)
    result = interpret_score(score)
    print(f"Similarity score : {score}")
    print(f"Label            : {result['label']}")
    print(f"Description      : {result['description']}")
