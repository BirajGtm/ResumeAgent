import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer


def extract_keywords(text):
    # Normalize and tokenize
    tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\+\#\.\-]{1,}\b', text.lower())
    return tokens

def score_ats_match(resume_text, jd_text):
    """
    Scores keyword overlap between job description and resume.
    Returns match score and missing keywords.
    """
    resume_tokens = extract_keywords(resume_text)
    jd_tokens = extract_keywords(jd_text)

    resume_counts = Counter(resume_tokens)
    jd_counts = Counter(jd_tokens)

    jd_unique = set(jd_tokens)
    resume_unique = set(resume_tokens)

    matched = jd_unique & resume_unique
    missing = jd_unique - resume_unique

    if len(jd_unique) == 0:
        score = 0
    else:
        score = round((len(matched) / len(jd_unique)) * 100, 2)

    return {
        "ats_score": score,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }
