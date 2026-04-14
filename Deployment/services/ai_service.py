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
from utils.helpers import get_authority_for_category, validate_llm_json


# Groq API endpoint (OpenAI-compatible)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"


def analyze_legal_issue(user_input: str, selected_language: str, manual_category: str, groq_api_key: str) -> dict:
    """
    Analyze the user's legal issue using the Groq AI.

    Args:
        user_input: The user's description of their problem.
        selected_language: Language the response should be in (English/Hindi/Marathi).
        manual_category: User-selected category or "Auto-Detect".
        groq_api_key: API key for Groq.

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

    prompt = f"""System Instructions:
            You are a highly intelligent Indian Legal Assistant extracting structured legal metadata.
            
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
            
            STEP 4 — RESPONSE MAPPING & RESPONSE TEXT:
            Based on the detected category, assign the correct recommended authority.
            Your "response" key output MUST be detailed markdown format IN {selected_language} answering the user:
            ### 1. Issue Understanding
            ### 2. Legal Explanation
            ### 3. What You Should Do Next
            
            STEP 5 — RESPONSE OUTPUT (STRICT JSON):
            You MUST return your response as a strict JSON object with NO OTHER TEXT outside the JSON braces.
            {{
              "category": "exact match to the list above",
              "subcategory": "short string preserving specific detail (e.g. Cyber Fraud, Leave Request)",
              "severity": "LOW" | "MEDIUM" | "HIGH",
              "confidence": 0.85,
              "reason": "short explanation of severity and category mapping",
              "recommended_authority": "authority name or 'N/A'",
              "response": "Detailed markdown explanation in {selected_language}."
            }}
            
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

    draft_prompt = f"""
                You are an expert Indian Legal Assistant and an experienced advocate.
                
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
                
                Please seamlessly and naturally integrate the following personal details into the body and the signature block of the draft:
                {personal_details}
                {dynamic_fields_text}
                
                *IMPORTANT*: If any of the personal details above are enclosed in brackets like [Your Name] or [Location], keep them EXACTLY as bracketed placeholders in the text so the user can fill them in later. Do not invent details for placeholders.
                
                The entire generated draft MUST be written fluently in {language}.
                
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
