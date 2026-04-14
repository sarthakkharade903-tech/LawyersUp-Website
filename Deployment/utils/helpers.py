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

STEP_GUIDES = {
    "Criminal Issues": [
        ("Immediate Action", "Ensure your physical safety and seek immediate medical attention if injured. Call the police emergency number (112) if the situation is ongoing."),
        ("Primary Step", "File an FIR (First Information Report) at the local police station under whose jurisdiction the crime occurred. For cyber crimes, register a complaint on cybercrime.gov.in."),
        ("Waiting Period", "Wait for the police to assign an Investigating Officer (IO) and obtain a copy of the FIR. The police have 24 hours to present the accused before a magistrate if arrested."),
        ("Escalation", "If the police refuse to register an FIR, approach the Superintendent of Police (SP) in writing. If still unaddressed, file a private complaint with a Magistrate under Section 156(3) of CrPC."),
        ("Evidence Required", "Preserve all physical evidence, medical reports, photographs of the incident scene, CCTV footage, and eyewitness contact details."),
        ("Optional Legal Action", "Consult a criminal defense lawyer to track the investigation, assist in opposing bail, or file an application for compensation if applicable.")
    ],
    "Consumer Issues": [
        ("Immediate Action", "Stop using the defective product or service immediately. Take clear photographs or screenshots of the defect, billing details, and marketing claims."),
        ("Primary Step", "Send a formal written notice (via registered post or email) to the company's grievance officer or customer support stating the issue and demanding a refund or replacement within 15 days."),
        ("Waiting Period", "Wait the stipulated 15-30 days for the company to reply or resolve the grievance internally. Keep written records of all follow-up communications."),
        ("Escalation", "If unresolved, file a complaint on the National Consumer Helpline (NCH) portal (consumerhelpline.gov.in) or call 1915."),
        ("Evidence Required", "Original invoices, warranty cards, screenshots of payments, email trails with customer care, and proof of defect (photos/videos)."),
        ("Optional Legal Action", "File a formal consumer case in the District Consumer Disputes Redressal Commission if the claim value is under ₹50 Lakhs. You can file this online via the E-Daakhil portal.")
    ],
    "Workplace Issues": [
        ("Immediate Action", "Do not resign impulsively. Review your employment contract, HR policies, and any non-disclosure/non-compete agreements. Temporarily secure personal data from work devices."),
        ("Primary Step", "File a formal written complaint with your HR department or internal grievance committee via your official company email to create a paper trail."),
        ("Waiting Period", "Allow HR 15-30 days to conduct an internal investigation. Cooperate with their inquiries but insist on written minutes of any meetings."),
        ("Escalation", "If HR ignores the issue or retaliates, send a formal legal notice through an advocate to the company directors/management for violation of contract or labor laws."),
        ("Evidence Required", "Employment contract, salary slips, email trails, chat screenshots, witness statements from colleagues (if willing), and formal termination/warning letters."),
        ("Optional Legal Action", "Approach the Labour Commissioner for mediation, or file a case in the Labour Court/Industrial Tribunal for wrongful termination or unpaid dues.")
    ],
    "Harassment / Abuse": [
        ("Immediate Action", "Prioritize your safety and mental health. Remove yourself from the situation. Confide in a trusted friend or family member. Do not delete any abusive messages or call logs."),
        ("Primary Step", "Block the abuser on all platforms. If it's workplace sexual harassment, immediately file a complaint with the Internal Complaints Committee (ICC) under the POSH Act."),
        ("Waiting Period", "For ICC complaints, the committee must complete its inquiry within 90 days. For general police complaints or NC (Non-Cognizable) reports, monitor the abuser's behavior."),
        ("Escalation", "If it's domestic violence, contact the National Commission for Women (NCW) or file an FIR under Section 498A. If online harassment, report it to the Cyber Police."),
        ("Evidence Required", "Screenshots of chats (with exact timestamps and numbers visible), call recordings, emails, CCTV footage, and witness testimonies."),
        ("Optional Legal Action", "File a petition for an injunction or a restraining order in civil court, or claim maintenance and protection orders under the Protection of Women from Domestic Violence Act.")
    ],
    "Civic / Public Issues": [
        ("Immediate Action", "Document the issue clearly. Take timestamped photographs or videos showing the extent of the civic problem (e.g., potholes, garbage dumps, broken streetlights)."),
        ("Primary Step", "Register a complaint on your local Municipal Corporation's grievance portal or mobile app (e.g., MCGM 24x7, Swachhata-MoHUA). Note the complaint reference number."),
        ("Waiting Period", "Wait 7 to 14 working days for the municipal authorities to assign a contractor or inspector to the site. Track the ticket status online."),
        ("Escalation", "If the ticket is closed without resolution, file a grievance on your state's centralized Public Grievance portal (e.g., CPGRAMS at pgportal.gov.in) addressed to the specific department head."),
        ("Evidence Required", "Clear photos with visible landmarks, GPS coordinates, the complaint ticket number, and signatures/petitions from affected neighbors."),
        ("Optional Legal Action", "If the issue causes accidents or severe public nuisance, you may file a Public Interest Litigation (PIL) in the High Court or a citizen suit in the Lok Adalat.")
    ],
    "Administrative / Requests": [
        ("Immediate Action", "Clearly define what you are requesting (e.g., leave application, NOC, license renewal). Identify the exact department and the name/designation of the recipient."),
        ("Primary Step", "Draft a formal application or letter. Ensure it is polite, concise, and references any old application numbers. Submit it online or physically."),
        ("Waiting Period", "Wait for the standard processing time of the respective department (usually 7-30 days). Do not submit duplicate requests immediately."),
        ("Escalation", "If there is undue delay, file an RTI (Right to Information) application asking for the daily progress report of your specific file/application."),
        ("Evidence Required", "Acknowledgment receipt (stamped copy if physical, tracking ID if online), old reference numbers, and identity proofs attached to the request."),
        ("Optional Legal Action", "Send a formal legal notice for dereliction of duty, or file a writ of Mandamus in the High Court compelling the public authority to perform its statutory duty.")
    ],
    "Legal Guidance / Inquiry": [
        ("Immediate Action", "Organize your thoughts and write a chronological summary of your legal situation. Avoid contacting the opposing party until you have a clear strategy."),
        ("Primary Step", "Consult with a qualified advocate specializing in the relevant field (civil, criminal, family, corporate). Prepare a list of specific questions before the meeting."),
        ("Waiting Period", "Allow your lawyer time to review documents, draft notices, or conduct legal research on precedents. Respond promptly to their requests for clarifications."),
        ("Escalation", "If you require a second opinion, seek out another lawyer or consult a legal aid clinic if you cannot afford private counsel."),
        ("Evidence Required", "Assemble a master file containing chronologically arranged copies of all relevant contracts, notices, emails, property documents, and identity proofs."),
        ("Optional Legal Action", "Proceed with filing or replying to a legal notice under the guidance of your counsel, ensuring all statutory deadlines (limitation periods) are strictly met.")
    ]
}

def get_step_guidance(category: str) -> list:
    """
    Returns an ordered list of step guiding tuples (Title, Description) 
    based on the input category. Returns empty list if not found.
    """
    return STEP_GUIDES.get(category, [])
