#streamlit run "Deployment\app.py"
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
from utils.helpers import get_authority_for_category, get_doc_type_for_category, get_tone_for_category
from services.ai_service import analyze_legal_issue, generate_complaint_draft
from services.pdf_service import generate_pdf
from services.email_service import send_email

# ═══════════════════════════════════════════════════════════════
# LOAD ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════

load_dotenv()
GROQ_API_KEY = st.secrets("GROQ_API_KEY")
EMAIL_USER = st.secrets("EMAIL_USER")
EMAIL_PASS = st.secrets("EMAIL_PASS")

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
    recommended_authority = st.session_state.get("recommended_authority", get_authority_for_category(category))

    cat_col, auth_col = st.columns([1.5, 3.5])
    with cat_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.success(f"📌 **Detected Category:** {category}")
        else:
            st.warning(f"⚠️ **Detected Category:** {category}")
    with auth_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.info(f"🏢 **Recommended Authority:** {recommended_authority}")

    st.markdown(st.session_state.llm_response)

    # ═══════════════════════════════════════════════════════════════
    # COMPLAINT GENERATOR SECTION
    # ═══════════════════════════════════════════════════════════════

    if category not in ["Not a Legal Issue", "Unknown Category"]:
        default_type = get_doc_type_for_category(category)
        default_auth = recommended_authority
        default_tone = get_tone_for_category(category)

        st.markdown("---")
        st.subheader("📄 Auto-Draft Formal Document")
        st.markdown("Generate a meticulously formatted legal document ready for submission.")

        with st.expander("📝 Personalize Document (Optional)", expanded=True):
            st.markdown("Fill in the details below to automatically include them in your draft. Leave blank to keep placeholders.")

            c_type_col1, c_type_col2 = st.columns(2)
            with c_type_col1:
                custom_doc_type = st.text_input("Complaint Type", value=default_type, help="E.g., FIR, Consumer Complaint, College Application")
            with c_type_col2:
                custom_authority = st.text_input("Addressing Authority (To:)", value=default_auth, help="You can override the auto-filled authority here.")

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                p_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
                p_age = st.text_input("Age", placeholder="e.g. 30")
                p_phone = st.text_input("Phone Number", placeholder="e.g. +91 9876543210")
                p_email = st.text_input("Email Address", placeholder="e.g. rahul@example.com")
            with f_col2:
                p_date = st.date_input("Date", value=datetime.today())
                p_address = st.text_area("Your Address", height=68, placeholder="e.g. 123, Main Street, Mumbai")
                p_location = st.text_input("Incident Location", placeholder="e.g. Mumbai, Maharashtra")
                p_police = st.text_input("Police Station Name", placeholder="e.g. Andheri Police Station")

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
                Incident Location: {p_location.strip() if p_location.strip() else '[Location]'}
                Police Station Name: {p_police.strip() if p_police.strip() else '[Police Station Name]'}
                """

                draft_result = generate_complaint_draft(
                    category=category,
                    custom_authority=custom_authority,
                    custom_doc_type=custom_doc_type,
                    default_tone=default_tone,
                    language=st.session_state.language,
                    user_problem=st.session_state.user_problem,
                    personal_details=personal_details,
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

            recipient_email = st.text_input("Recipient Email Address", placeholder="e.g. support@company.com")
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
