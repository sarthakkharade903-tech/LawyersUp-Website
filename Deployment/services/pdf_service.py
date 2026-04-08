"""
pdf_service.py — Handles PDF generation using ReportLab.

Converts a plain-text complaint draft into a properly formatted PDF document
that can be downloaded by the user.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(text: str) -> io.BytesIO:
    """
    Generate a PDF file from the given text.

    Args:
        text: The complaint draft text to convert to PDF.

    Returns:
        A BytesIO buffer containing the PDF data, ready for download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    styles = getSampleStyleSheet()
    story = []

    for p_text in text.split("\n"):
        if p_text.strip() == "":
            story.append(Spacer(1, 12))
            continue

        # Escape XML characters for ReportLab
        safe_text = p_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Remove bold markdown since we aren't parsing complex tags here
        safe_text = safe_text.replace("**", "")

        p = Paragraph(safe_text, styles["Normal"])
        story.append(p)
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer
