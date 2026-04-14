#TO RUN Locally --> streamlit run "Deployment\app.py"
"""To Deploy Updated --> 
git add .
git commit -m "Tested and working update"
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
from utils.helpers import get_authority_for_category, get_doc_type_for_category, get_tone_for_category, get_authority_details, get_step_guidance
from services.ai_service import analyze_legal_issue, generate_complaint_draft
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
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

selected_language = render_sidebar()

# ═══════════════════════════════════════════════════════════════
# MAIN UI — Input Section
# ═══════════════════════════════════════════════════════════════

st.title("🏛️ Lawyer's Up : Legal AI Assistant")
st.markdown("Describe your issue below to instantly receive professional legal guidance. 🚀")

# Category selector dropdown
cat_col1, cat_col2 = st.columns([1.5, 3.5])
with cat_col1:
    manual_category = st.selectbox(
        "📂 Select Complaint Category",
        ["Auto-Detect"] + ALL_CATEGORIES,
        help="Choose a category or let AI auto-detect from your description.",
    )
with cat_col2:
    # Show auto-filled authority based on category selection
    if manual_category != "Auto-Detect":
        auto_authority = get_authority_for_category(manual_category)
        st.text_input(
            "🏢 Recommended Authority (auto-filled)",
            value=auto_authority,
            disabled=True,
            help="This authority is auto-filled based on your selected category.",
        )
    else:
        st.text_input(
            "🏢 Recommended Authority",
            value="Will be detected from your description",
            disabled=True,
            help="Select a category or let AI determine the appropriate authority.",
        )

# User input text area
user_input = st.text_area(
    "✍️ **Enter your problem:**",
    height=150,
    placeholder="E.g., I was defrauded of money online by a fake e-commerce website...",
)

# User location input
user_location = st.text_input(
    "📍 **Your Location (City):**",
    placeholder="E.g., Pune, Mumbai (Helps us find the exact authority)",
    help="We use this to fetch regional contact information."
)

col1, col2 = st.columns([1, 4])
with col1:
    get_help_btn = st.button("✨ Get Legal Help", use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# HANDLE "Get Legal Help" BUTTON
# ═══════════════════════════════════════════════════════════════

if get_help_btn:
    if not user_input.strip():
        st.warning("Please enter your problem before submitting.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing. Please ensure it is set in your .env file.")
    else:
        with st.spinner("Analyzing your issue..."):
            result = analyze_legal_issue(user_input, selected_language, manual_category, GROQ_API_KEY)

            if result["success"]:
                st.session_state.category = result["category"]
                st.session_state.recommended_authority = result["recommended_authority"]
                st.session_state.llm_response = result["response"]
                st.session_state.user_problem = user_input
                st.session_state.severity = result.get("severity", "LOW")
                st.session_state.subcategory = result.get("subcategory", "None")
                st.session_state.confidence = result.get("confidence", 0.0)
                st.session_state.reason = result.get("reason", "No reason provided by AI.")
                st.session_state.user_location = user_location
                st.session_state.language = selected_language
                st.session_state.complaint_draft = None  # Reset previous drafts
            else:
                st.error(result["error"])

# ═══════════════════════════════════════════════════════════════
# DISPLAY — Analysis Results & Complaint Generator
# ═══════════════════════════════════════════════════════════════

if "llm_response" in st.session_state and st.session_state.llm_response:
    st.markdown("---")
    st.subheader("📊 Legal Analysis & Strategy")
    st.success("✅ Analysis Complete!")
    
    category = st.session_state.category
    subcategory = st.session_state.get("subcategory", "None")
    severity = st.session_state.get("severity", "LOW")
    confidence = st.session_state.get("confidence", 0.0)
    reason = st.session_state.get("reason", "")
    
    if severity == "HIGH":
        st.error("🚨 High Severity: Immediate action required")
    elif severity == "MEDIUM":
        st.warning("⚠️ Medium Severity: Action needed soon")
    else:
        st.info("ℹ️ Low Severity")
        
    st.markdown(f"**Severity Level:** {severity} (Confidence: {confidence:.0%})")
    st.markdown(f"**Reason:** {reason}")
    if subcategory and subcategory.lower() not in ["none", ""]:
        st.markdown(f"**Subcategory:** {subcategory}")

    recommended_authority = st.session_state.get("recommended_authority", get_authority_for_category(category))
    stored_location = st.session_state.get("user_location", "")
    smart_authority = get_authority_details(category, stored_location)

    cat_col, auth_col = st.columns([1.5, 3.5])
    with cat_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.success(f"📌 **Detected Category:** {category}")
        else:
            st.warning(f"⚠️ **Detected Category:** {category}")
    with auth_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.info(f"🏢 **Recommended Authority:** {recommended_authority}")

    if smart_authority:
        st.markdown("---")
        st.markdown("### 🎯 Smart Authority Mapping")
        st.success(f"**{smart_authority['name']}**")
        
        st.markdown(f"**📧 Email:** `{smart_authority['email']}`")
        st.link_button("🌐 Visit Official Website", smart_authority['website'], use_container_width=True)


    # ═══════════════════════════════════════════════════════════════
    # STEP-BY-STEP GUIDANCE SECTION
    # ═══════════════════════════════════════════════════════════════
    
    step_guide = get_step_guidance(category)
    if step_guide:
        st.markdown("---")
        st.subheader("🧭 Step-by-Step Action Plan")
        st.markdown(f"Follow these real-world steps for **{category}**:")
        
        for idx, (title, description) in enumerate(step_guide, 1):
            st.markdown(f"**{idx}. {title}**\n\n{description}")

    # ═══════════════════════════════════════════════════════════════
    # COLLAPSIBLE EXPLANATION SECTION
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📘 Detailed Legal Explanation"):
        st.markdown(st.session_state.llm_response)

    # ═══════════════════════════════════════════════════════════════
    # COMPLAINT GENERATOR SECTION
    # ═══════════════════════════════════════════════════════════════

    if category not in ["Not a Legal Issue", "Unknown Category"]:
        st.markdown("---")
        st.header("📄 Generate Complaint")
        
        if "show_complaint_form" not in st.session_state:
            st.session_state.show_complaint_form = False
            
        if not st.session_state.show_complaint_form:
            if st.button("Generate Complaint", type="primary"):
                st.session_state.show_complaint_form = True
                st.rerun()
                
        if st.session_state.show_complaint_form:
            default_type = get_doc_type_for_category(category)
            default_auth = recommended_authority
            default_tone = get_tone_for_category(category)

            st.markdown("Generate a meticulously formatted legal document ready for submission.")

            with st.expander("📝 Personalize Document (Optional)", expanded=True):
                st.markdown("Fill in the details below to automatically include them in your draft. Leave blank to keep placeholders.")

                c_type_col1, c_type_col2 = st.columns(2)
                with c_type_col1:
                    custom_doc_type = st.text_input("Complaint Type", value=default_type, help="E.g., FIR, Consumer Complaint, College Application")
                with c_type_col2:
                    custom_authority = st.text_input("Addressing Authority (To:)", value=default_auth, help="You can override the auto-filled authority here.")

                st.markdown("#### Core Details")
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    p_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
                    p_phone = st.text_input("Phone Number", placeholder="e.g. +91 9876543210")
                    p_email = st.text_input("Email Address", placeholder="e.g. rahul@example.com")
                with f_col2:
                    p_age = st.text_input("Age", placeholder="e.g. 30")
                    p_date = st.date_input("Date", value=datetime.today())
                    p_address = st.text_area("Your Address", height=68, placeholder="e.g. 123, Main Street, Mumbai")

                st.markdown("#### Case-Specific Details")
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
                    gen_btn = st.button("🖋️ Generate Draft", use_container_width=True)

                if gen_btn:
                    with st.spinner(f"Drafting your {category} document..."):
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
                            tone_line = "This matter requires urgent attention and immediate action."
                        elif severity_val == "MEDIUM":
                            tone_line = "This matter requires timely attention."
                        else:
                            tone_line = "This matter is submitted for your consideration."

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
                        else:
                            st.error(draft_result["error"])

        # ═══════════════════════════════════════════════════════════════
        # DISPLAY — Draft, PDF Download & Email
        # ═══════════════════════════════════════════════════════════════

        if st.session_state.get("complaint_draft"):
            st.success("✨ Draft generated successfully!")

            col_header, col_copy = st.columns([5, 1])
            with col_header:
                st.markdown("### Step 1: Review Your Complaint")
                st.caption("Review your draft below. Use the copy button in the top-right of the box.")
            with col_copy:
                st.write("")  # Spacing alignment
                if st.button("📋 Copy Text", use_container_width=True):
                    st.toast("Copied to clipboard ✅")

            # Using st.code() which provides a stable built-in copy button
            st.code(st.session_state.complaint_draft, language="text", wrap_lines=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # PDF Download
            pdf_buffer = generate_pdf(st.session_state.complaint_draft)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="legal_complaint_draft.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.divider()

            # Email Section
            st.markdown("### Step 2: Send Complaint via Email")
            st.caption("Enter authority email (police, principal, company, etc.)")

            default_email = smart_authority["email"] if smart_authority and "email" in smart_authority else ""

            if default_email:
                st.success("✅ Email auto-filled based on authority")
                use_custom_email = st.checkbox("Override automatically detected email")
                recipient_email = st.text_input(
                    "Recipient Email Address", 
                    value=default_email, 
                    disabled=not use_custom_email
                )
            else:
                st.warning("⚠️ Email not available, please enter manually")
                recipient_email = st.text_input(
                    "Recipient Email Address", 
                    placeholder="e.g. support@company.com"
                )

            subject = st.text_input("Email Subject", value="Official Legal Complaint Draft")

            st.markdown("<br>", unsafe_allow_html=True)
            send_email_clicked = st.button("🚀 Send Complaint via Email", type="primary", use_container_width=True)

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
# FOOTER
# ═══════════════════════════════════════════════════════════════

render_footer()
