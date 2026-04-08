"""
helpers.py — Utility functions for category detection and lookups.

Provides keyword-based category fallback detection and simple lookup
functions that retrieve authority, document type, and tone for a given category.
"""

from utils.constants import CATEGORY_AUTHORITY_MAP


def keyword_detect_category(text: str) -> str:
    """
    Simple keyword-based fallback to detect category from user input text.
    Counts how many keywords from each category appear in the text,
    and returns the best-matching category name, or 'Other' if nothing matches.
    """
    text_lower = text.lower()
    scores = {}
    for cat, info in CATEGORY_AUTHORITY_MAP.items():
        score = sum(1 for kw in info["keywords"] if kw in text_lower)
        if score > 0:
            scores[cat] = score

    if scores:
        return max(scores, key=scores.get)
    return "Other"


def get_authority_for_category(category: str) -> str:
    """Get the default authority for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["default_authority"]
    return "The Respective Authority"


def get_doc_type_for_category(category: str) -> str:
    """Get the default document type for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["doc_type"]
    return "Formal Legal Complaint"


def get_tone_for_category(category: str) -> str:
    """Get the default tone for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["tone"]
    return "Formal and professional"
