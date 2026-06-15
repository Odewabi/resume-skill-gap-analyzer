# Resume Skill Gap Analyzer

An interactive web-based NLP tool that helps Computer Science students identify
skill gaps between their resume and a target internship or entry-level job description.

**Course:** CS 4850 – Faculty Directed Research, Weber State University  
**Student:** Oluwatomisin Adetoye Odewabi (Tomisin)  
**Mentor:** Dr. Amani Shatnawi  
**Term:** Summer 2026

---

## What It Does

1. You paste your resume text and a job description into the web form.
2. The tool extracts skills from both documents using spaCy NER and dictionary matching.
3. It computes a TF-IDF cosine similarity score between the two documents.
4. It returns a structured **skill gap report** showing:
   - Skills in the job description missing from your resume (by category)
   - Skills you already have that match
   - An overall similarity score with plain-language interpretation
   - Improvement tips

---

## Project Structure

```
resume-skill-gap-analyzer/
├── src/
│   ├── preprocessor.py     # Text cleaning, tokenization, normalization
│   ├── extractor.py        # spaCy NER + dictionary-based skill extraction
│   ├── scorer.py           # TF-IDF vectorization and cosine similarity
│   └── gap_engine.py       # Gap computation and output formatting
├── app/
│   ├── app.py              # Flask web application
│   └── templates/
│       ├── index.html      # Input form
│       └── results.html    # Gap report output page
├── data/
│   ├── skill_taxonomy.json # Curated CS skill dictionary (73 entries, 5 categories)
│   └── eval_set/           # Anonymized resume + JD pairs for evaluation
├── tests/
│   ├── test_preprocessor.py
│   └── test_extractor.py
├── notebooks/              # Jupyter notebooks for exploratory analysis
├── docs/                   # Submission reports
├── requirements.txt
└── README.md
```

---

## Setup and Installation

### Prerequisites
- Python 3.11 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/resume-skill-gap-analyzer
cd resume-skill-gap-analyzer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy language model
python -m spacy download en_core_web_sm

# 5. Run the web application
python app/app.py
# Open http://localhost:5000 in your browser
```

### Running Tests

```bash
pytest tests/ -v
```

---

## Dependencies

See `requirements.txt` for pinned versions. Key libraries:

| Library | Purpose |
|---------|---------|
| spaCy | Named Entity Recognition for skill extraction |
| rapidfuzz | Fuzzy string matching for skill aliases |
| scikit-learn | TF-IDF vectorization and cosine similarity |
| Flask | Lightweight web framework |
| pandas | Skill taxonomy and evaluation data handling |
| pytest | Unit testing |

---

## Skill Taxonomy

The file `data/skill_taxonomy.json` contains 73 canonical CS skills organized into
5 categories: Programming Languages, Frameworks and Libraries, Tools and Platforms,
CS Concepts and Methodologies, and Soft and Professional Skills.

Each entry maps a canonical name to a list of recognized aliases and abbreviations
(e.g., `"JavaScript": ["js", "ecmascript"]`).

---

## Evaluation

The skill extraction component is evaluated against a manually labeled ground truth
of 10 anonymized resume-JD pairs. Target metrics:

- Precision ≥ 0.70
- Recall ≥ 0.65
- F1 ≥ 0.67

See `docs/` for full evaluation methodology and results.

---

## Ethics and Privacy

- No personally identifiable information (PII) is stored or committed to this repository.
- All resume samples in `data/eval_set/` are either synthetic or voluntarily
  contributed with written consent and fully anonymized.
- This tool is designed to inform and empower students; it does not make automated
  hiring decisions.

---

## License

MIT License. See LICENSE for details.
