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

import json
import os

def get_authority_details(issue_type: str, location: str) -> dict | None:
    """
    Fetch smart authority details based on issue_type and user's location.
    Looks up categories in data/authorities.json and falls back to default.
    """
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "authorities.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            authorities_data = json.load(f)
    except FileNotFoundError:
        return None
        
    if issue_type not in authorities_data:
        return None
        
    category_data = authorities_data[issue_type]
    
    norm_location = location.lower().strip() if location else ""
    
    # Try exact match for location
    if norm_location in category_data:
        return category_data[norm_location]
    
    # Check if a partial match can be found (e.g. user types "Pune, Maharashtra")
    for city_key in category_data.keys():
        if city_key != "default" and city_key in norm_location:
            return category_data[city_key]
            
    # Fallback to default
    if "default" in category_data:
        return category_data["default"]
        
    return None
