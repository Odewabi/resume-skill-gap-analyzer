"""
tests/test_preprocessor.py
---------------------------
Unit tests for src/preprocessor.py
Run with: pytest tests/
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# We mock spaCy so tests run without the model installed
import unittest.mock as mock

# Create a minimal spaCy mock
mock_token = lambda text, is_stop, is_punct, is_space: mock.MagicMock(
    text=text, is_stop=is_stop, is_punct=is_punct, is_space=is_space
)

def make_mock_nlp():
    nlp = mock.MagicMock()
    def side_effect(text):
        words = text.split()
        tokens = []
        stop_words = {"the", "a", "an", "is", "are", "with", "and", "or", "for", "in", "of", "to"}
        for w in words:
            clean = w.strip(".,;:!?()")
            t = mock.MagicMock()
            t.text = clean
            t.is_stop = clean.lower() in stop_words
            t.is_punct = w in {".", ",", ";", ":", "!", "?", "(", ")"}
            t.is_space = clean == ""
            tokens.append(t)
        doc = mock.MagicMock()
        doc.__iter__ = mock.Mock(return_value=iter(tokens))
        return doc
    nlp.side_effect = side_effect
    return nlp


with mock.patch("spacy.load", return_value=make_mock_nlp()):
    import preprocessor


def test_clean_text_removes_html():
    result = preprocessor.clean_text("<p>Hello <b>World</b></p>")
    assert "<" not in result
    assert "Hello" in result
    assert "World" in result


def test_clean_text_removes_bullets():
    result = preprocessor.clean_text("• Python • React • AWS")
    assert "•" not in result
    assert "Python" in result


def test_clean_text_collapses_whitespace():
    result = preprocessor.clean_text("Hello    \n\n  World")
    assert "  " not in result
    assert result == "Hello World"


def test_normalize_lowercases():
    assert preprocessor.normalize("Python Flask AWS") == "python flask aws"


def test_normalize_strips_whitespace():
    assert preprocessor.normalize("  hello  ") == "hello"


def test_tokenize_returns_list():
    with mock.patch("preprocessor.nlp", make_mock_nlp()):
        result = preprocessor.tokenize("Python and Flask are great")
        assert isinstance(result, list)
        assert "python" in result or "Python" in result


def test_tokenize_removes_stopwords_by_default():
    with mock.patch("preprocessor.nlp", make_mock_nlp()):
        result = preprocessor.tokenize("Python and the Flask framework")
        # "and" and "the" should be removed
        lower = [t.lower() for t in result]
        assert "and" not in lower
        assert "the" not in lower


def test_preprocess_returns_string():
    with mock.patch("preprocessor.nlp", make_mock_nlp()):
        result = preprocessor.preprocess("Python developer with React experience")
        assert isinstance(result, str)
        assert len(result) > 0


def test_preprocess_for_ner_keeps_case_structure():
    """preprocess_for_ner should lowercase but not remove stop words."""
    result = preprocessor.preprocess_for_ner("Seeking a Python and React developer")
    assert result == result.lower()
    # Should be a plain string, not tokenized
    assert isinstance(result, str)
