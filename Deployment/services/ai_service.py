"""
ai_service.py — Handles all Groq API interactions.

Contains two main functions:
1. analyze_legal_issue() — Sends the user's problem to the AI for analysis,
   category detection, and authority recommendation.
2. generate_complaint_draft() — Sends a prompt to the AI to draft a formal
   legal document based on the user's case details.
"""

import requests
import json

from utils.constants import ALL_CATEGORIES
from utils.helpers import get_authority_for_category, validate_llm_json, STEP_GUIDES


# Groq API endpoint (OpenAI-compatible)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"


def analyze_legal_issue(user_input: str, selected_language: str, manual_category: str, groq_api_key: str, user_location: str = "") -> dict:
    """
    Analyze the user's legal issue using the Groq AI.

    Args:
        user_input: The user's description of their problem.
        selected_language: Language the response should be in (English/Hindi/Marathi).
        manual_category: User-selected category or "Auto-Detect".
        groq_api_key: API key for Groq.
        user_location: User's city/location for India-specific context.

    Returns:
        A dict with keys: "success", "category", "recommended_authority", "response", "error"
    """
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }

    # Build category list for the AI prompt
    category_list_str = ", ".join([f'"{c}"' for c in ALL_CATEGORIES])

    # If user manually selected a category, hint that to the AI
    category_hint = ""
    if manual_category != "Auto-Detect":
        category_hint = f'\nIMPORTANT HINT: The user has pre-selected the category "{manual_category}". Use this as the category unless the problem clearly belongs to a different category.'

    # Build step guide reference for the LLM
    step_guide_ref = ""
    for cat, steps in STEP_GUIDES.items():
        step_guide_ref += f"\n{cat}:\n"
        for i, (title, desc) in enumerate(steps, 1):
            step_guide_ref += f"  {i}. {title}: {desc}\n"

    # Build the smart language enforcement block
    lang_instruction = ""
    if selected_language != "English":
        lang_instruction = f"""
            CRITICAL LANGUAGE RULE:
            ALL user-facing text MUST be in {selected_language}.
            Do NOT generate in English first and translate. Think and write directly in {selected_language}.
            Do NOT mix English randomly into sentences.
            
            EXCEPTION — Keep these official/legal terms in English when they appear:
            FIR, RTI, Consumer Forum, National Consumer Helpline, POSH Act, CrPC, IPC, BNS,
            Cyber Crime Cell, Labour Court, E-Daakhil, PIL, NCW, ICC, Lok Adalat, CPGRAMS.
            
            TRANSLATION QUALITY:
            - Do NOT translate word-by-word. Use natural, human-like phrasing.
            - The output must sound like a native {selected_language} speaker wrote it.
            - Step titles MUST also be in {selected_language} (not English titles).
            
            Example (Marathi): "तक्रार National Consumer Helpline वर नोंदवा"
            Example (Hindi): "FIR दर्ज करें और Investigating Officer से संपर्क करें"
            
            TONE: Practical, action-oriented, clear, simple. NOT emotional.
            """
    else:
        lang_instruction = """
            LANGUAGE: Generate all text fields in clear, professional English.
            Avoid emotional or dramatic language. Keep tone neutral and professional.
            """

    prompt = f"""System Instructions:
            You are a highly intelligent Indian Legal Assistant extracting structured legal metadata.
            
            {lang_instruction}
            
            STEP 1 — CATEGORY DETECTION:
            Carefully analyze the user's problem and classify it into EXACTLY ONE of these categories:
            {category_list_str}, or "Not a Legal Issue".
            
            Use meaning and intent to determine the category, not just keywords. Examples:
            - Writing an application, request, email, permission → "Administrative / Requests"
            - Asking what they should do, seeking legal advice, procedural inquiry → "Legal Guidance / Inquiry"
            - Physical violence, theft, cybercrime, fraud, murder → "Criminal Issues" (Subcategories: Cyber Fraud, Assault, etc.)
            - Abuse, stalking, bullying, domestic violence → "Harassment / Abuse"
            - Defective product, refund, e-commerce issue → "Consumer Issues"
            - HR issues, salary, termination, workplace bullying → "Workplace Issues"
            - Potholes, garbage, sewage, streetlights → "Civic / Public Issues"
            
            {category_hint}
            
            STEP 2 — SEVERITY DETECTION:
            Define severity based on REAL impact:
            - HIGH: Physical harm, threats to life/safety, serious fraud, repeated/escalating crime.
            - MEDIUM: Harassment, consumer issues, civic problems affecting daily life, moderate urgency.
            - LOW: General queries, writing emails, legal guidance without conflict, no immediate harm.
            DO NOT overestimate severity. If no immediate harm, default to LOW. If unsure, default to MEDIUM.
            
            STEP 3 — LLM RULES:
            - DO NOT assume facts not provided.
            - DO NOT invent people, actions, or events.
            - Stick ONLY to user input. If unclear, set lower confidence.
            - Keep reasoning short and factual.
            - Use professional, neutral legal tone. NO emotional or dramatic phrasing.
            
            STEP 4 — RESPONSE MAPPING & RESPONSE TEXT:
            Based on the detected category, assign the correct recommended authority.
            Your "response" key output MUST be detailed markdown format answering the user:
            ### 1. Issue Understanding
            ### 2. Legal Explanation
            ### 3. What You Should Do Next
            
            STEP 5 — STEP-BY-STEP ACTION PLAN (MANDATORY):
            You MUST generate exactly 6 steps for the user's situation.
            ALL step titles and descriptions MUST be in {selected_language}.
            Do NOT keep step titles in English when language is not English.
            Do NOT translate word-by-word. Use natural, human-like phrasing that sounds native.
            Keep official legal terms (FIR, RTI, Consumer Forum, etc.) in English within the text.
            Include realistic timelines (e.g., 7–15 days) and India-specific context.
            User location: {user_location if user_location else 'Not specified'}
            
            The 6 steps MUST follow this structure:
            1. Immediate Action — What to do RIGHT NOW for safety or evidence
            2. Primary Step — The main formal action (file complaint, send notice, etc.)
            3. Waiting Period — How long to wait, what to track
            4. Escalation — What to do if the primary step fails or is ignored
            5. Evidence Required — What documents/proof to collect and preserve
            6. Optional Legal Action — Court or legal recourse if everything else fails
            
            Use the following REFERENCE for content guidance (rewrite naturally in {selected_language}):
            {step_guide_ref}
            
            STEP 6 — RESPONSE OUTPUT (STRICT JSON):
            You MUST return your response as a strict JSON object with NO OTHER TEXT outside the JSON braces.
            {{
              "category": "exact match from the category list (ALWAYS in English)",
              "subcategory": "short string (ALWAYS in English, e.g. Cyber Fraud, Leave Request)",
              "severity": "LOW" | "MEDIUM" | "HIGH",
              "confidence": 0.85,
              "reason": "short explanation in {selected_language}",
              "recommended_authority": "authority name or 'N/A'",
              "response": "Detailed markdown explanation in {selected_language}.",
              "step_by_step_plan": [
                {{"title": "step title in {selected_language}", "description": "step description in {selected_language}"}},
                ...
              ]
            }}
            
            IMPORTANT: "category" and "subcategory" keys must ALWAYS be in English for backend processing.
            ALL other text fields (reason, response, step_by_step_plan) must be in {selected_language}.
            Keep official legal terms (FIR, RTI, Consumer Forum, etc.) in English within the {selected_language} text.
            
            Problem: {user_input}
            """

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            raw_reply = result["choices"][0]["message"]["content"]
            try:
                parsed_reply = json.loads(raw_reply)

                validated_json = validate_llm_json(parsed_reply)
                
                # If user manually selected a category, prefer that
                final_category = manual_category if manual_category != "Auto-Detect" else validated_json["category"]
                
                # Set authority: use AI's if available, otherwise derive from mapping
                final_authority = validated_json["recommended_authority"]
                if not final_authority or final_authority == "N/A":
                    final_authority = get_authority_for_category(final_category)

                return {
                    "success": True,
                    "category": final_category,
                    "subcategory": validated_json["subcategory"],
                    "severity": validated_json["severity"],
                    "confidence": validated_json["confidence"],
                    "reason": validated_json["reason"],
                    "recommended_authority": final_authority,
                    "response": validated_json["response"] if validated_json["response"] else "Analysis completed but no advice provided.",
                    "step_by_step_plan": validated_json["step_by_step_plan"],
                    "error": None,
                }

            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "The AI returned an invalid response structure.",
                }
        else:
            return {"success": False, "error": "API returned an unexpected format."}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network or API Error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {e}"}


def generate_complaint_draft(
    category: str,
    custom_authority: str,
    custom_doc_type: str,
    default_tone: str,
    severity_tone_line: str,
    language: str,
    user_problem: str,
    personal_details: str,
    dynamic_fields: dict,
    groq_api_key: str,
) -> dict:
    """
    Generate a formal legal complaint draft using the Groq AI.

    Args:
        category: Detected complaint category.
        custom_authority: Authority the document is addressed to.
        custom_doc_type: Type of document (FIR, complaint, etc.).
        default_tone: Writing tone for the document.
        language: Language for the document.
        user_problem: The user's original problem description.
        personal_details: Formatted string of personal details.
        groq_api_key: API key for Groq.

    Returns:
        A dict with keys: "success", "draft", "error"
    """
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }

    dynamic_fields_text = ""
    if dynamic_fields:
        provided_fields = {k: v for k, v in dynamic_fields.items() if v.strip()}
        if provided_fields:
            dynamic_fields_text = "\\nInclude the following details if available:\\n"
            for k, v in provided_fields.items():
                dynamic_fields_text += f"{k}: {v}\\n"

    # Build smart language enforcement for the draft
    if language != "English":
        draft_lang_rule = f"""CRITICAL LANGUAGE RULE:
                Generate the ENTIRE document natively in {language}.
                Do NOT write in English first and translate. Think and write directly in {language}.
                
                SMART LANGUAGE HANDLING:
                - Write all paragraphs, explanations, and formal text in {language}.
                - KEEP official legal terms, organization names, and proper nouns in English.
                  Examples: FIR, RTI, Consumer Forum, POSH Act, CrPC, IPC, Cyber Crime Cell, PIL, NCW.
                - Translate ONLY the surrounding text into {language}.
                
                TONE: Formal, practical, non-emotional, legally appropriate.
                Do NOT use dramatic phrases. Keep language clear and professional."""
    else:
        draft_lang_rule = """LANGUAGE: Generate the entire document in clear, professional English.
                Avoid emotional or dramatic language. Keep tone neutral and legally appropriate."""

    draft_prompt = f"""
                You are an expert Indian Legal Assistant and an experienced advocate.
                
                {draft_lang_rule}
                
                DETECTED CATEGORY: {category}
                RECOMMENDED AUTHORITY: {custom_authority}
                
                Your task is to draft a highly professional, specific, and detailed {custom_doc_type} based ONLY on the user's situation. 
                The document MUST be explicitly addressed to: {custom_authority}.
                
                CRITICAL INSTRUCTIONS:
                1. DO NOT output a generic template. You MUST write a detailed complaint using ONLY the specific facts provided in the "User's Specific Problem" section below. Extract all possible facts (dates, amounts, actions) from the problem.
                2. Adapt the facts logically into formal Indian legal language. The tone should be: {default_tone}.
                3. Include a precise and professional Subject Line reflecting the severity of the issue.
                4. At the very TOP of the document, include the line:
                   "Recommended Authority: {custom_authority}"
                5. Structure the draft into clear paragraphs:
                   - Introduction (Who is complaining and against whom/what).
                   - Detailed Account of Incident (Chronological narrative based STRICTLY on the user's problem).
                   - Legal Grounds / Impact (The harm or consequences faced by the complainant).
                   - Prayer/Relief Requested (Specific action demanded). You MUST naturally weave the following exact phrase into this section: "{severity_tone_line}"
                   
                STRICT FACTUAL RULES:
                - Do NOT add or assume any facts that are not explicitly mentioned in the input.
                - Do NOT create imaginary events, people, or actions.
                - If details like number of people, exact actions, or severity are missing, write in a neutral and general way.
                - Do NOT exaggerate or dramatize the situation. Ensure factual accuracy over storytelling.
                - Use professional, neutral language. NO emotional phrases like "great sadness" or "unbearable pain".
                
                Please seamlessly and naturally integrate the following personal details into the body and the signature block of the draft:
                {personal_details}
                {dynamic_fields_text}
                
                *IMPORTANT*: If any of the personal details above are enclosed in brackets like [Your Name] or [Location], keep them EXACTLY as bracketed placeholders in the text so the user can fill them in later. Do not invent details for placeholders.
                
                Category: {category}
                User's Specific Problem: {user_problem}
                
                Output ONLY the formal document itself. Do NOT include any conversational text, explanations, or introductory remarks like "Here is your draft".
                """

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": draft_prompt}],
        "temperature": 0.4,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            draft_text = result["choices"][0]["message"]["content"]
            return {"success": True, "draft": draft_text, "error": None}
        else:
            return {"success": False, "draft": None, "error": "Failed to generate draft."}

    except Exception as e:
        return {"success": False, "draft": None, "error": f"Drafting error: {e}"}
