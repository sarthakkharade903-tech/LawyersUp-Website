#TO RUN Locally --> streamlit run "Deployment\app.py"
"""To Deploy Updated --> 
git add .
git commit -m "Case followup button 1.0"
git push
"""
#This file handles ONLY the UI flow and orchestrates calls to service modules.
#No heavy logic lives here — just layout, inputs, buttons, and function calls.

import streamlit as st

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="Lawyer's Up - AI Legal Assistant", page_icon="⚖️", layout="wide")

import os
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from components.ui_components import render_sidebar, render_footer
from utils.constants import ALL_CATEGORIES
from utils.helpers import (
    get_authority_for_category, get_doc_type_for_category,
    get_tone_for_category, get_authority_details,
    get_step_guidance, get_ui_text
)
from services.ai_service import analyze_legal_issue, generate_complaint_draft, generate_followup
from services.pdf_service import generate_pdf
from services.email_service import send_email

# ═══════════════════════════════════════════════════════════════
# LOAD ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════

load_dotenv()
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
EMAIL_USER = st.secrets["EMAIL_USER"]
EMAIL_PASS = st.secrets["EMAIL_PASS"]

# ═══════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

if "case_history" not in st.session_state:
    st.session_state.case_history = []
if "last_case" not in st.session_state:
    st.session_state.last_case = None
if "followup_response" not in st.session_state:
    st.session_state.followup_response = None
if "show_followup_input" not in st.session_state:
    st.session_state.show_followup_input = False

def save_to_history():
    """Helper to save or update the current case in session state history."""
    if "user_problem" not in st.session_state or not st.session_state.user_problem:
        return
        
    case_data = {
        "problem": st.session_state.user_problem,
        "category": st.session_state.category,
        "severity": st.session_state.severity,
        "recommended_authority": st.session_state.recommended_authority,
        "complaint": st.session_state.get("complaint_draft"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # Extra state for full reload
        "llm_response": st.session_state.get("llm_response"),
        "subcategory": st.session_state.get("subcategory"),
        "confidence": st.session_state.get("confidence"),
        "reason": st.session_state.get("reason"),
        "step_plan": st.session_state.get("step_plan"),
        "user_location": st.session_state.get("user_location"),
        "language": st.session_state.get("language"),
        "manual_category_saved": st.session_state.get("manual_category_input")
    }
    
    # Update latest if it's the same problem during same active session
    # or append as new if different.
    found = False
    if st.session_state.case_history:
        # Check if the last case in history is the same problem (likely updating with complaint)
        if st.session_state.case_history[-1]["problem"] == case_data["problem"]:
            st.session_state.case_history[-1] = case_data
            found = True
            
    if not found:
        st.session_state.case_history.append(case_data)
        # Limit to 10 cases
        if len(st.session_state.case_history) > 10:
            st.session_state.case_history.pop(0)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

selected_language = render_sidebar()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR — CASE HISTORY (NEW)
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("---")
    st.subheader("📁 Case History")

    if not st.session_state.case_history:
        st.info("No cases saved yet. Your generated cases will appear here.")
    else:
        # Clear History button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.case_history = []
            st.rerun()

        # Iterate through history (newest first)
        for i, case in enumerate(reversed(st.session_state.case_history)):
            # Problem preview text
            preview = case["problem"][:50] + "..." if len(case["problem"]) > 50 else case["problem"]
            
            with st.expander(f"📌 {preview}"):
                st.markdown(f"**Category:** {case['category']}")
                st.markdown(f"**Severity:** {case['severity']}")
                st.markdown(f"**Date:** {case['timestamp']}")

                # Load Case Button
                if st.button("🔄 Load Case", key=f"load_btn_{i}", use_container_width=True):
                    # Restore Result UI state
                    st.session_state.user_problem = case["problem"]
                    st.session_state.category = case["category"]
                    st.session_state.severity = case["severity"]
                    st.session_state.recommended_authority = case["recommended_authority"]
                    st.session_state.complaint_draft = case["complaint"]
                    st.session_state.llm_response = case.get("llm_response")
                    st.session_state.subcategory = case.get("subcategory")
                    st.session_state.confidence = case.get("confidence", 0.0)
                    st.session_state.reason = case.get("reason")
                    st.session_state.step_plan = case.get("step_plan")
                    st.session_state.user_location = case.get("user_location", "")
                    st.session_state.language = case.get("language", "English")
                    
                    # Also Restore Last Case for Follow-up feature
                    st.session_state.last_case = {
                        "problem": case["problem"],
                        "category": case["category"],
                        "severity": case["severity"],
                        "steps": case.get("step_plan", []),
                        "complaint": case.get("complaint")
                    }
                    st.session_state.followup_response = None
                    st.session_state.show_followup_input = False
                    
                    # Restore Input Widget state
                    st.session_state.user_problem_input = case["problem"]
                    st.session_state.user_location_input = case.get("user_location", "")
                    if "manual_category_saved" in case:
                        st.session_state.manual_category_input = case["manual_category_saved"]
                    
                    st.rerun()

                # Download Complaint Button (if available)
                if case.get("complaint"):
                    st.download_button(
                        label="📥 Download Complaint",
                        data=case["complaint"],
                        file_name=f"legal_complaint_{i+1}.txt",
                        mime="text/plain",
                        key=f"dl_btn_{i}",
                        use_container_width=True
                    )

# Helper shortcut for UI text
def t(key):
    return get_ui_text(selected_language, key)

# ═══════════════════════════════════════════════════════════════
# MAIN UI — Input Section
# ═══════════════════════════════════════════════════════════════

st.title(t("app_title"))
st.markdown(t("app_subtitle"))

# Category selector dropdown
cat_col1, cat_col2 = st.columns([1.5, 3.5])
with cat_col1:
    manual_category = st.selectbox(
        t("select_category"),
        [t("auto_detect")] + ALL_CATEGORIES,
        help=t("select_category"),
        key="manual_category_input"
    )
with cat_col2:
    # Normalize auto-detect check for all languages
    is_auto = manual_category in [t("auto_detect"), "Auto-Detect", "स्वचालित पहचान", "स्वयंचलित ओळख"]
    if not is_auto:
        auto_authority = get_authority_for_category(manual_category)
        st.text_input(
            t("recommended_authority_label"),
            value=auto_authority,
            disabled=True,
            help=t("recommended_authority_label"),
        )
    else:
        st.text_input(
            t("recommended_authority"),
            value=t("recommended_authority_placeholder"),
            disabled=True,
            help=t("recommended_authority"),
        )

# User input text area
user_input = st.text_area(
    t("enter_problem"),
    height=150,
    placeholder="E.g., I was defrauded of money online by a fake e-commerce website...",
    key="user_problem_input"
)

# User location input
user_location = st.text_input(
    t("enter_location"),
    placeholder=t("location_placeholder"),
    help=t("enter_location"),
    key="user_location_input"
)

col1, col2 = st.columns([1, 4])
with col1:
    get_help_btn = st.button(t("get_help_btn"), use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# HANDLE "Get Legal Help" BUTTON
# ═══════════════════════════════════════════════════════════════

if get_help_btn:
    if not user_input.strip():
        st.warning("Please enter your problem before submitting.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing. Please ensure it is set in your .env file.")
    else:
        # Normalize manual_category back to English for backend
        api_category = manual_category if not is_auto else "Auto-Detect"
        
        with st.spinner(t("analyzing")):
            result = analyze_legal_issue(user_input, selected_language, api_category, GROQ_API_KEY, user_location)

            if result["success"]:
                st.session_state.category = result["category"]
                st.session_state.recommended_authority = result["recommended_authority"]
                st.session_state.llm_response = result["response"]
                st.session_state.user_problem = user_input
                st.session_state.severity = result.get("severity", "LOW")
                st.session_state.subcategory = result.get("subcategory", "None")
                st.session_state.confidence = result.get("confidence", 0.0)
                st.session_state.reason = result.get("reason", "")
                st.session_state.step_plan = result.get("step_by_step_plan", [])
                st.session_state.user_location = user_location
                st.session_state.language = selected_language
                st.session_state.complaint_draft = None  # Reset previous drafts
                st.session_state.show_complaint_form = False
                
                # STORE LAST CASE for Follow-up feature
                st.session_state.last_case = {
                    "problem": user_input,
                    "category": result["category"],
                    "severity": result.get("severity", "LOW"),
                    "steps": result.get("step_by_step_plan", []),
                    "complaint": None
                }
                st.session_state.followup_response = None
                st.session_state.show_followup_input = False
                
                # Save to history after successful analysis
                save_to_history()
            else:
                st.error(result["error"])

# ═══════════════════════════════════════════════════════════════
# DISPLAY — Analysis Results & Complaint Generator
# ═══════════════════════════════════════════════════════════════

if "llm_response" in st.session_state and st.session_state.llm_response:
    # Use stored language for display consistency
    lang = st.session_state.get("language", "English")
    def tl(key):
        return get_ui_text(lang, key)
    
    st.markdown("---")
    st.subheader(tl("analysis_header"))
    st.success(tl("analysis_complete"))
    
    category = st.session_state.category
    subcategory = st.session_state.get("subcategory", "None")
    severity = st.session_state.get("severity", "LOW")
    confidence = st.session_state.get("confidence", 0.0)
    reason = st.session_state.get("reason", "")
    
    if severity == "HIGH":
        st.error(tl("severity_high"))
    elif severity == "MEDIUM":
        st.warning(tl("severity_medium"))
    else:
        st.info(tl("severity_low"))
        
    st.markdown(f"**{tl('severity_label')}:** {severity} ({tl('confidence_label')}: {confidence:.0%})")
    st.markdown(f"**{tl('reason_label')}:** {reason}")
    if subcategory and subcategory.lower() not in ["none", ""]:
        st.markdown(f"**{tl('subcategory_label')}:** {subcategory}")

    recommended_authority = st.session_state.get("recommended_authority", get_authority_for_category(category))
    stored_location = st.session_state.get("user_location", "")
    smart_authority = get_authority_details(category, stored_location)

    cat_col, auth_col = st.columns([1.5, 3.5])
    with cat_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.success(f"**{tl('detected_category')}:** {category}")
        else:
            st.warning(f"⚠️ **{tl('detected_category')}:** {category}")
    with auth_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.info(f"**{tl('recommended_authority')}:** {recommended_authority}")

    if smart_authority:
        st.markdown("---")
        st.markdown(f"### {tl('smart_authority_header')}")
        st.success(f"**{smart_authority['name']}**")
        
        st.markdown(f"**{tl('email_label')}:** `{smart_authority['email']}`")
        st.link_button(tl("visit_website"), smart_authority['website'], use_container_width=True)

    # ═══════════════════════════════════════════════════════════════
    # STEP-BY-STEP GUIDANCE SECTION (LLM-generated localized steps)
    # ═══════════════════════════════════════════════════════════════
    
    # Use LLM-generated localized steps first, fallback to static English steps
    llm_steps = st.session_state.get("step_plan", [])
    static_steps = get_step_guidance(category)
    
    if llm_steps:
        st.markdown("---")
        st.subheader(tl("action_plan_header"))
        st.markdown(f"{tl('action_plan_subtitle')} **{category}**:")
        
        for idx, step in enumerate(llm_steps, 1):
            st.markdown(f"**{idx}. {step['title']}**\n\n{step['description']}")
    elif static_steps:
        # Fallback: use English static steps if LLM didn't return any
        st.markdown("---")
        st.subheader(tl("action_plan_header"))
        st.markdown(f"{tl('action_plan_subtitle')} **{category}**:")
        
        for idx, (title, description) in enumerate(static_steps, 1):
            st.markdown(f"**{idx}. {title}**\n\n{description}")

    # ═══════════════════════════════════════════════════════════════
    # COLLAPSIBLE EXPLANATION SECTION
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(tl("legal_explanation_header")):
        st.markdown(st.session_state.llm_response)

    # ═══════════════════════════════════════════════════════════════
    # COMPLAINT GENERATOR SECTION
    # ═══════════════════════════════════════════════════════════════

    if category not in ["Not a Legal Issue", "Unknown Category"]:
        st.markdown("---")
        st.header(tl("generate_complaint_header"))
        
        if "show_complaint_form" not in st.session_state:
            st.session_state.show_complaint_form = False
            
        if not st.session_state.show_complaint_form:
            if st.button(tl("generate_complaint_btn"), type="primary"):
                st.session_state.show_complaint_form = True
                st.rerun()
                
        if st.session_state.show_complaint_form:
            default_type = get_doc_type_for_category(category)
            default_auth = recommended_authority
            default_tone = get_tone_for_category(category)

            st.markdown(tl("draft_subtitle"))

            with st.expander(tl("personalize_header"), expanded=True):
                st.markdown(tl("personalize_hint"))

                c_type_col1, c_type_col2 = st.columns(2)
                with c_type_col1:
                    custom_doc_type = st.text_input(tl("complaint_type"), value=default_type)
                with c_type_col2:
                    custom_authority = st.text_input(tl("addressing_authority"), value=default_auth)

                st.markdown(f"#### {tl('core_details')}")
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    p_name = st.text_input(tl("full_name"), placeholder="e.g. Rahul Sharma")
                    p_phone = st.text_input(tl("phone"), placeholder="e.g. +91 9876543210")
                    p_email = st.text_input(tl("email_address"), placeholder="e.g. rahul@example.com")
                with f_col2:
                    p_age = st.text_input(tl("age"), placeholder="e.g. 30")
                    p_date = st.date_input(tl("date"), value=datetime.today())
                    p_address = st.text_area(tl("address"), height=68, placeholder="e.g. 123, Main Street, Mumbai")

                st.markdown(f"#### {tl('case_specific')}")
                DYNAMIC_FIELDS = {
                    "Cybercrime": ["Transaction ID", "Amount Lost", "Platform (UPI, Bank, App, etc.)"],
                    "Fraud": ["Amount Lost", "Incident Location", "Date/Time of Incident"],
                    "Harassment (College)": ["Person Name (if known)", "Platform/Location (College, online, etc.)"],
                    "Harassment (General)": ["Person Name (if known)", "Platform/Location", "Frequency of Harassment"],
                    "Consumer Issues": ["Product/Service Name", "Company Name", "Amount Paid"],
                    "Banking / Financial Issues": ["Bank Name", "Account Number (Last 4 digits)", "Amount Disputed"],
                    "Workplace Complaints": ["Company Name", "Manager/HR/Perpetrator Name", "Duration of Issue"],
                    "Women Safety": ["Incident Location", "Date/Time of Incident", "Accused Details (if known)"]
                }
                
                fields_to_show = DYNAMIC_FIELDS.get(category, ["Incident Location", "Specific Details"])
                
                dynamic_inputs = {}
                dyn_cols = st.columns(2)
                for i, field in enumerate(fields_to_show):
                    with dyn_cols[i % 2]:
                        dynamic_inputs[field] = st.text_input(field, key=f"dyn_{field}")

                btn_col, empty_col2 = st.columns([1.5, 3.5])
                with btn_col:
                    gen_btn = st.button(tl("generate_draft_btn"), use_container_width=True)

                if gen_btn:
                    with st.spinner(tl("drafting")):
                        # Build personal details string
                        personal_details = f"""
                        Name: {p_name.strip() if p_name.strip() else '[Your Name]'}
                        Age: {p_age.strip() if p_age.strip() else '[Your Age]'}
                        Address: {p_address.strip() if p_address.strip() else '[Your Address]'}
                        Phone Number: {p_phone.strip() if p_phone.strip() else '[Your Phone Number]'}
                        Email: {p_email.strip() if p_email.strip() else '[Your Email]'}
                        Date: {p_date.strftime('%d-%m-%Y')}
                        """

                        severity_val = st.session_state.get("severity", "LOW")
                        if severity_val == "HIGH":
                            tone_line = tl("tone_high")
                        elif severity_val == "MEDIUM":
                            tone_line = tl("tone_medium")
                        else:
                            tone_line = tl("tone_low")

                        draft_result = generate_complaint_draft(
                            category=category,
                            custom_authority=custom_authority,
                            custom_doc_type=custom_doc_type,
                            default_tone=default_tone,
                            severity_tone_line=tone_line,
                            language=st.session_state.language,
                            user_problem=st.session_state.user_problem,
                            personal_details=personal_details,
                            dynamic_fields=dynamic_inputs,
                            groq_api_key=GROQ_API_KEY,
                        )

                        if draft_result["success"]:
                            st.session_state.complaint_draft = draft_result["draft"]
                            # Update history with the complaint draft
                            save_to_history()
                            # Update last_case with complaint
                            if st.session_state.last_case:
                                st.session_state.last_case["complaint"] = draft_result["draft"]
                        else:
                            st.error(draft_result["error"])

        # ═══════════════════════════════════════════════════════════════
        # DISPLAY — Draft, PDF Download & Email
        # ═══════════════════════════════════════════════════════════════

        if st.session_state.get("complaint_draft"):
            st.success(tl("draft_success"))

            col_header, col_copy = st.columns([5, 1])
            with col_header:
                st.markdown(f"### {tl('review_complaint')}")
                st.caption(tl("review_hint"))
            with col_copy:
                st.write("")  # Spacing alignment
                if st.button(tl("copy_text"), use_container_width=True):
                    st.toast("✅")

            # Using st.code() which provides a stable built-in copy button
            st.code(st.session_state.complaint_draft, language="text", wrap_lines=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # PDF Download
            pdf_buffer = generate_pdf(st.session_state.complaint_draft)
            st.download_button(
                label=tl("download_pdf"),
                data=pdf_buffer,
                file_name="legal_complaint_draft.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.divider()

            # Email Section
            st.markdown(f"### {tl('send_email_header')}")
            st.caption(tl("send_email_hint"))

            default_email = smart_authority["email"] if smart_authority and "email" in smart_authority else ""

            if default_email:
                st.success(tl("email_autofilled"))
                use_custom_email = st.checkbox(tl("email_override"))
                recipient_email = st.text_input(
                    tl("recipient_email"), 
                    value=default_email, 
                    disabled=not use_custom_email
                )
            else:
                st.warning("⚠️ Email not available")
                recipient_email = st.text_input(
                    tl("recipient_email"), 
                    placeholder="e.g. support@company.com"
                )

            subject = st.text_input(tl("email_subject"), value=tl("email_subject_default"))

            st.markdown("<br>", unsafe_allow_html=True)
            send_email_clicked = st.button(tl("send_email_btn"), type="primary", use_container_width=True)

            if send_email_clicked:
                if not EMAIL_USER or not EMAIL_PASS:
                    st.error("Sender credentials (EMAIL_USER, EMAIL_PASS) not found in .env file. Please configure them.")
                elif not recipient_email.strip():
                    st.warning("Please provide a recipient email address.")
                else:
                    with st.spinner("Sending email..."):
                        success, error_msg = send_email(EMAIL_USER, EMAIL_PASS, recipient_email, subject, st.session_state.complaint_draft)
                        if success:
                            st.success("Email sent successfully! ✅")
                        else:
                            st.error(f"Failed to send email: {error_msg}")

    # ═══════════════════════════════════════════════════════════════
    # FOLLOW-UP / CONTINUE CASE SECTION (Enhanced & Repositioned)
    # ═══════════════════════════════════════════════════════════════
    
    # Show only if analysis is complete AND complaint is generated (at the end of flow)
    if st.session_state.get("last_case") and st.session_state.get("complaint_draft"):
        st.divider()
        
        if not st.session_state.show_followup_input:
            col_fup1, col_fup2, col_fup3 = st.columns([1, 2, 1])
            with col_fup2:
                if st.button(tl("continue_case_btn"), use_container_width=True, type="secondary"):
                    st.session_state.show_followup_input = True
                    st.rerun()
                st.caption(f"<center>{tl('continue_case_hint')}</center>", unsafe_allow_html=True)
        
        if st.session_state.show_followup_input:
            st.markdown(f"### {tl('followup_header')}")
            user_followup = st.text_area(tl("followup_input_label"), placeholder=tl("followup_placeholder"), key="followup_input_text")
            
            f_btn_col1, f_btn_col2 = st.columns([1.5, 3.5])
            with f_btn_col1:
                if st.button(tl("generate_followup_btn"), type="primary", use_container_width=True):
                    if user_followup.strip():
                        with st.spinner(tl("followup_thinking")):
                            f_result = generate_followup(
                                st.session_state.last_case,
                                user_followup,
                                st.session_state.language,
                                GROQ_API_KEY
                            )
                            if f_result["success"]:
                                st.session_state.followup_response = f_result
                                st.rerun()
                            else:
                                st.error(f_result["error"])
                    else:
                        st.warning("Please enter what happened next.")

        if st.session_state.get("followup_response"):
            st.markdown("---")
            st.markdown(f"#### {tl('followup_header')}")
            st.info(st.session_state.followup_response["explanation"])
            
            for f_step in st.session_state.followup_response["next_steps"]:
                st.markdown(f"- {f_step}")

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

render_footer()
