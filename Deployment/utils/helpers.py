"""
helpers.py — Utility functions for category detection, lookups, and UI localization.

Provides LLM JSON validation, authority/document/tone lookups,
step-by-step guidance, and multilingual UI text mapping.
"""

# ═══════════════════════════════════════════════════════════════
# MULTILINGUAL UI TEXT MAPPING
# ═══════════════════════════════════════════════════════════════

UI_TRANSLATIONS = {
    "English": {
        "app_title": "🏛️ Lawyer's Up : Legal AI Assistant",
        "app_subtitle": "Describe your issue below to instantly receive professional legal guidance. 🚀",
        "select_category": "📂 Select Complaint Category",
        "auto_detect": "Auto-Detect",
        "recommended_authority_label": "🏢 Recommended Authority (auto-filled)",
        "recommended_authority_placeholder": "Will be detected from your description",
        "enter_problem": "✍️ **Enter your problem:**",
        "enter_location": "📍 **Your Location (City):**",
        "location_placeholder": "E.g., Pune, Mumbai (Helps us find the exact authority)",
        "get_help_btn": "✨ Get Legal Help",
        "analyzing": "Analyzing your issue...",
        "analysis_header": "📊 Legal Analysis & Strategy",
        "analysis_complete": "✅ Analysis Complete!",
        "severity_high": "🚨 High Severity: Immediate action required",
        "severity_medium": "⚠️ Medium Severity: Action needed soon",
        "severity_low": "ℹ️ Low Severity",
        "severity_label": "Severity Level",
        "confidence_label": "Confidence",
        "reason_label": "Reason",
        "subcategory_label": "Subcategory",
        "detected_category": "📌 Detected Category",
        "recommended_authority": "🏢 Recommended Authority",
        "smart_authority_header": "🎯 Smart Authority Mapping",
        "email_label": "📧 Email",
        "visit_website": "🌐 Visit Official Website",
        "action_plan_header": "🧭 Step-by-Step Action Plan",
        "action_plan_subtitle": "Follow these real-world steps for",
        "legal_explanation_header": "📘 Detailed Legal Explanation",
        "generate_complaint_header": "📄 Generate Complaint",
        "generate_complaint_btn": "Generate Complaint",
        "draft_subtitle": "Generate a meticulously formatted legal document ready for submission.",
        "personalize_header": "📝 Personalize Document (Optional)",
        "personalize_hint": "Fill in the details below to automatically include them in your draft. Leave blank to keep placeholders.",
        "complaint_type": "Complaint Type",
        "addressing_authority": "Addressing Authority (To:)",
        "core_details": "Core Details",
        "case_specific": "Case-Specific Details",
        "full_name": "Full Name",
        "phone": "Phone Number",
        "email_address": "Email Address",
        "age": "Age",
        "date": "Date",
        "address": "Your Address",
        "generate_draft_btn": "🖋️ Generate Draft",
        "drafting": "Drafting your document...",
        "draft_success": "✨ Draft generated successfully!",
        "review_complaint": "Review Your Complaint",
        "review_hint": "Review your draft below. Use the copy button in the top-right of the box.",
        "copy_text": "📋 Copy Text",
        "download_pdf": "📥 Download as PDF",
        "send_email_header": "Send Complaint via Email",
        "send_email_hint": "Enter authority email (police, principal, company, etc.)",
        "email_autofilled": "✅ Email auto-filled based on authority",
        "email_override": "Override automatically detected email",
        "recipient_email": "Recipient Email Address",
        "email_subject": "Email Subject",
        "email_subject_default": "Official Legal Complaint Draft",
        "send_email_btn": "🚀 Send Complaint via Email",
        "tone_high": "This matter requires urgent attention and immediate action.",
        "tone_medium": "This matter requires timely attention.",
        "tone_low": "This matter is submitted for your consideration.",
    },
    "Hindi": {
        "app_title": "🏛️ लॉयर्स अप : AI कानूनी सहायक",
        "app_subtitle": "अपनी समस्या नीचे लिखें और तुरंत पेशेवर कानूनी मार्गदर्शन प्राप्त करें। 🚀",
        "select_category": "📂 शिकायत श्रेणी चुनें",
        "auto_detect": "स्वचालित पहचान",
        "recommended_authority_label": "🏢 अनुशंसित प्राधिकरण (स्वचालित)",
        "recommended_authority_placeholder": "आपके विवरण से पहचाना जाएगा",
        "enter_problem": "✍️ **अपनी समस्या लिखें:**",
        "enter_location": "📍 **आपका स्थान (शहर):**",
        "location_placeholder": "उदा., पुणे, मुंबई (सही प्राधिकरण खोजने में सहायक)",
        "get_help_btn": "✨ कानूनी सहायता प्राप्त करें",
        "analyzing": "आपकी समस्या का विश्लेषण हो रहा है...",
        "analysis_header": "📊 कानूनी विश्लेषण और रणनीति",
        "analysis_complete": "✅ विश्लेषण पूर्ण!",
        "severity_high": "🚨 उच्च गंभीरता: तत्काल कार्रवाई आवश्यक",
        "severity_medium": "⚠️ मध्यम गंभीरता: शीघ्र कार्रवाई आवश्यक",
        "severity_low": "ℹ️ कम गंभीरता",
        "severity_label": "गंभीरता स्तर",
        "confidence_label": "विश्वसनीयता",
        "reason_label": "कारण",
        "subcategory_label": "उपश्रेणी",
        "detected_category": "📌 पहचानी गई श्रेणी",
        "recommended_authority": "🏢 अनुशंसित प्राधिकरण",
        "smart_authority_header": "🎯 स्मार्ट प्राधिकरण मैपिंग",
        "email_label": "📧 ईमेल",
        "visit_website": "🌐 आधिकारिक वेबसाइट पर जाएं",
        "action_plan_header": "🧭 चरण-दर-चरण कार्य योजना",
        "action_plan_subtitle": "इन व्यावहारिक चरणों का पालन करें",
        "legal_explanation_header": "📘 विस्तृत कानूनी विवरण",
        "generate_complaint_header": "📄 शिकायत तैयार करें",
        "generate_complaint_btn": "शिकायत तैयार करें",
        "draft_subtitle": "प्रस्तुति के लिए तैयार एक पेशेवर कानूनी दस्तावेज़ बनाएं।",
        "personalize_header": "📝 दस्तावेज़ को अनुकूलित करें (वैकल्पिक)",
        "personalize_hint": "नीचे विवरण भरें। खाली छोड़ने पर प्लेसहोल्डर रहेंगे।",
        "complaint_type": "शिकायत प्रकार",
        "addressing_authority": "प्राधिकरण को संबोधित (सेवा में:)",
        "core_details": "मूल विवरण",
        "case_specific": "मामले से संबंधित विवरण",
        "full_name": "पूरा नाम",
        "phone": "फ़ोन नंबर",
        "email_address": "ईमेल पता",
        "age": "आयु",
        "date": "दिनांक",
        "address": "आपका पता",
        "generate_draft_btn": "🖋️ ड्राफ्ट तैयार करें",
        "drafting": "आपका दस्तावेज़ तैयार हो रहा है...",
        "draft_success": "✨ ड्राफ्ट सफलतापूर्वक तैयार!",
        "review_complaint": "अपनी शिकायत की समीक्षा करें",
        "review_hint": "नीचे अपना ड्राफ्ट देखें। बॉक्स के ऊपरी दाएं कोने में कॉपी बटन का उपयोग करें।",
        "copy_text": "📋 कॉपी करें",
        "download_pdf": "📥 PDF डाउनलोड करें",
        "send_email_header": "ईमेल द्वारा शिकायत भेजें",
        "send_email_hint": "प्राधिकरण का ईमेल दर्ज करें (पुलिस, प्रधानाचार्य, कंपनी आदि)",
        "email_autofilled": "✅ प्राधिकरण के आधार पर ईमेल स्वचालित भरा गया",
        "email_override": "स्वचालित ईमेल बदलें",
        "recipient_email": "प्राप्तकर्ता ईमेल पता",
        "email_subject": "ईमेल विषय",
        "email_subject_default": "आधिकारिक कानूनी शिकायत ड्राफ्ट",
        "send_email_btn": "🚀 ईमेल द्वारा शिकायत भेजें",
        "tone_high": "इस मामले में तत्काल ध्यान और कार्रवाई आवश्यक है।",
        "tone_medium": "इस मामले में समय पर ध्यान देने की आवश्यकता है।",
        "tone_low": "यह मामला आपके विचारार्थ प्रस्तुत किया जाता है।",
    },
    "Marathi": {
        "app_title": "🏛️ लॉयर्स अप : AI कायदेशीर सहाय्यक",
        "app_subtitle": "तुमची समस्या खाली लिहा आणि त्वरित व्यावसायिक कायदेशीर मार्गदर्शन मिळवा. 🚀",
        "select_category": "📂 तक्रार श्रेणी निवडा",
        "auto_detect": "स्वयंचलित ओळख",
        "recommended_authority_label": "🏢 शिफारस केलेले प्राधिकरण (स्वयंचलित)",
        "recommended_authority_placeholder": "तुमच्या वर्णनावरून ओळखले जाईल",
        "enter_problem": "✍️ **तुमची समस्या लिहा:**",
        "enter_location": "📍 **तुमचे ठिकाण (शहर):**",
        "location_placeholder": "उदा., पुणे, मुंबई (योग्य प्राधिकरण शोधण्यासाठी)",
        "get_help_btn": "✨ कायदेशीर मदत मिळवा",
        "analyzing": "तुमच्या समस्येचे विश्लेषण सुरू आहे...",
        "analysis_header": "📊 कायदेशीर विश्लेषण आणि रणनीती",
        "analysis_complete": "✅ विश्लेषण पूर्ण!",
        "severity_high": "🚨 उच्च तीव्रता: तात्काळ कारवाई आवश्यक",
        "severity_medium": "⚠️ मध्यम तीव्रता: लवकर कारवाई आवश्यक",
        "severity_low": "ℹ️ कमी तीव्रता",
        "severity_label": "तीव्रता स्तर",
        "confidence_label": "विश्वासार्हता",
        "reason_label": "कारण",
        "subcategory_label": "उपश्रेणी",
        "detected_category": "📌 ओळखलेली श्रेणी",
        "recommended_authority": "🏢 शिफारस केलेले प्राधिकरण",
        "smart_authority_header": "🎯 स्मार्ट प्राधिकरण मॅपिंग",
        "email_label": "📧 ईमेल",
        "visit_website": "🌐 अधिकृत वेबसाइटला भेट द्या",
        "action_plan_header": "🧭 टप्प्याटप्प्याने कृती योजना",
        "action_plan_subtitle": "या व्यावहारिक पायऱ्यांचे अनुसरण करा",
        "legal_explanation_header": "📘 सविस्तर कायदेशीर स्पष्टीकरण",
        "generate_complaint_header": "📄 तक्रार तयार करा",
        "generate_complaint_btn": "तक्रार तयार करा",
        "draft_subtitle": "सादर करण्यासाठी तयार असलेला व्यावसायिक कायदेशीर दस्तऐवज तयार करा.",
        "personalize_header": "📝 दस्तऐवज सानुकूलित करा (पर्यायी)",
        "personalize_hint": "खालील तपशील भरा. रिकामे ठेवल्यास प्लेसहोल्डर राहतील.",
        "complaint_type": "तक्रार प्रकार",
        "addressing_authority": "प्राधिकरणास संबोधित (प्रति:)",
        "core_details": "मूळ तपशील",
        "case_specific": "प्रकरणाशी संबंधित तपशील",
        "full_name": "पूर्ण नाव",
        "phone": "फोन नंबर",
        "email_address": "ईमेल पत्ता",
        "age": "वय",
        "date": "दिनांक",
        "address": "तुमचा पत्ता",
        "generate_draft_btn": "🖋️ मसुदा तयार करा",
        "drafting": "तुमचा दस्तऐवज तयार होत आहे...",
        "draft_success": "✨ मसुदा यशस्वीरित्या तयार!",
        "review_complaint": "तुमच्या तक्रारीचे पुनरावलोकन करा",
        "review_hint": "खाली तुमचा मसुदा पहा. बॉक्सच्या वरच्या उजव्या कोपऱ्यातील कॉपी बटन वापरा.",
        "copy_text": "📋 कॉपी करा",
        "download_pdf": "📥 PDF डाउनलोड करा",
        "send_email_header": "ईमेलद्वारे तक्रार पाठवा",
        "send_email_hint": "प्राधिकरणाचा ईमेल प्रविष्ट करा (पोलीस, मुख्याध्यापक, कंपनी इ.)",
        "email_autofilled": "✅ प्राधिकरणावर आधारित ईमेल स्वयंचलित भरला",
        "email_override": "स्वयंचलित ईमेल बदला",
        "recipient_email": "प्राप्तकर्ता ईमेल पत्ता",
        "email_subject": "ईमेल विषय",
        "email_subject_default": "अधिकृत कायदेशीर तक्रार मसुदा",
        "send_email_btn": "🚀 ईमेलद्वारे तक्रार पाठवा",
        "tone_high": "या प्रकरणात तात्काळ लक्ष आणि कारवाई आवश्यक आहे.",
        "tone_medium": "या प्रकरणात वेळेवर लक्ष देणे आवश्यक आहे.",
        "tone_low": "हे प्रकरण आपल्या विचारार्थ सादर केले जात आहे.",
    }
}


def get_ui_text(language: str, key: str) -> str:
    """
    Fetch a localized UI string for the given language and key.
    Falls back to English if the language or key is not found.
    """
    lang_dict = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["English"])
    return lang_dict.get(key, UI_TRANSLATIONS["English"].get(key, key))

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
        
    # Validate step_by_step_plan: must be a list of dicts with title+description
    raw_steps = parsed_json.get("step_by_step_plan", [])
    validated_steps = []
    if isinstance(raw_steps, list):
        for step in raw_steps:
            if isinstance(step, dict) and "title" in step and "description" in step:
                validated_steps.append({
                    "title": str(step["title"]),
                    "description": str(step["description"])
                })
        
    return {
        "category": category,
        "subcategory": str(parsed_json.get("subcategory", "None")),
        "severity": severity,
        "confidence": confidence,
        "reason": str(parsed_json.get("reason", "No reason provided by AI.")),
        "recommended_authority": str(parsed_json.get("recommended_authority", "")),
        "response": str(parsed_json.get("response", "")),
        "step_by_step_plan": validated_steps
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
