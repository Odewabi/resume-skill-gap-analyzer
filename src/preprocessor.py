"""
src/preprocessor.py
-------------------
Text cleaning and normalization for the Resume Skill Gap Analyzer.
Handles tokenization, lowercasing, stop word removal, and punctuation stripping.
"""

import re
import spacy

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")


def clean_text(text: str) -> str:
    """
    Remove HTML tags, extra whitespace, and non-ASCII characters.
    Returns a cleaned plain-text string.
    """
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Replace bullet characters and special dashes with spaces
    text = re.sub(r"[•·–—●▪◦]", " ", text)
    # Remove non-ASCII characters
    text = text.encode("ascii", errors="ignore").decode()
    # Collapse multiple whitespace/newlines into a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize(text: str) -> str:
    """
    Lowercase and strip leading/trailing whitespace.
    """
    return text.lower().strip()


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """
    Tokenize text using spaCy. Optionally removes stop words.
    Returns a list of token strings (lowercased, no punctuation).
    """
    doc = nlp(text.lower())
    tokens = [
        token.text
        for token in doc
        if not token.is_punct
        and not token.is_space
        and (not token.is_stop if remove_stopwords else True)
    ]
    return tokens


def preprocess(text: str, remove_stopwords: bool = True) -> str:
    """
    Full preprocessing pipeline: clean → normalize → tokenize → rejoin.
    Returns a single preprocessed string suitable for TF-IDF or NER input.
    """
    text = clean_text(text)
    text = normalize(text)
    tokens = tokenize(text, remove_stopwords=remove_stopwords)
    return " ".join(tokens)


def preprocess_for_ner(text: str) -> str:
    """
    Lighter preprocessing for NER: clean and normalize but do NOT remove
    stop words, as spaCy NER relies on full sentence context.
    """
    text = clean_text(text)
    text = normalize(text)
    return text


if __name__ == "__main__":
    sample = """
    <p>We are looking for a Software Engineer with experience in Python,
    React, and AWS. Strong communication skills required. Must be comfortable
    with Agile/Scrum methodologies and CI/CD pipelines.</p>
    """
    print("=== clean_text ===")
    print(clean_text(sample))
    print("\n=== preprocess (stopwords removed) ===")
    print(preprocess(sample))
    print("\n=== preprocess_for_ner ===")
    print(preprocess_for_ner(sample))
