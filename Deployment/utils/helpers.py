"""
helpers.py — Utility functions for category detection and lookups.

Provides keyword-based category fallback detection and simple lookup
functions that retrieve authority, document type, and tone for a given category.
"""

from utils.constants import CATEGORY_AUTHORITY_MAP


from utils.constants import ALL_CATEGORIES

def validate_llm_json(parsed_json: dict) -> dict:
    """
    Validates the structured JSON parsed from the LLM.
    Ensures safe fallbacks for UI consumption if the model hallucinates keys.
    """
    category = parsed_json.get("category", "")
    if category not in ALL_CATEGORIES:
        category = "Other"
        
    severity = str(parsed_json.get("severity", "LOW")).strip().upper()
    if severity not in ["LOW", "MEDIUM", "HIGH"]:
        severity = "LOW"
        
    confidence = parsed_json.get("confidence", 0.0)
    try:
        confidence = float(confidence)
        if confidence < 0.0 or confidence > 1.0:
            confidence = 0.5
    except (ValueError, TypeError):
        confidence = 0.5
        
    return {
        "category": category,
        "subcategory": str(parsed_json.get("subcategory", "None")),
        "severity": severity,
        "confidence": confidence,
        "reason": str(parsed_json.get("reason", "No reason provided by AI.")),
        "recommended_authority": str(parsed_json.get("recommended_authority", "")),
        "response": str(parsed_json.get("response", ""))
    }


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

from typing import Optional

def get_authority_details(issue_type: str, location: str) -> Optional[dict]:
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
