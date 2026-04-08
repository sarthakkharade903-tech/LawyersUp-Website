"""
email_service.py — Handles sending emails via SMTP (Gmail).

Sends the complaint draft as a plain-text email to the specified
recipient (e.g., authority, company support, police email).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(sender: str, password: str, recipient: str, subject: str, body: str) -> tuple:
    """
    Send an email using Gmail's SMTP server.

    Args:
        sender: Sender's email address.
        password: Sender's app password (not regular password).
        recipient: Recipient's email address.
        subject: Email subject line.
        body: Email body text (the complaint draft).

    Returns:
        A tuple of (success: bool, error_message: str).
        If successful, error_message is an empty string.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)
