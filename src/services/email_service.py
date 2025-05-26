# src/services/email_service.py
"""
Email notification service for the Task Manager application.
Sends task assignment notifications to employees (currently placeholder).
"""

import logging
from typing import Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

def notify_employee(employee: Dict[str, Any], task: str) -> None:
    """
    Notify an employee about a task assignment (placeholder until email is enabled).

    Args:
        employee: Dictionary with employee details (must include 'email' and 'name').
        task: Task description to include in the notification.

    Returns:
        None

    Note:
        Email sending is commented out. Uncomment and configure .env variables
        (EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT) to enable.
    """
    if not isinstance(employee, dict) or "email" not in employee or "name" not in employee:
        logger.error(f"Invalid employee data: {employee}")
        return

    email = employee["email"]
    name = employee["name"]
    message = f"Notification for {name} ({email}): Task assigned - {task}"
    logger.info(message)
    print(message)  # Placeholder until email is enabled

    # Uncomment the following to enable email notifications:
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.DEBUG)
    )
    def send_email(to_email: str, subject: str, body: str, attachment_path: str = None) -> None:
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        if not sender or not password:
            logger.error("Missing EMAIL_SENDER or EMAIL_PASSWORD in .env")
            raise ValueError("Email credentials must be set in environment variables.")

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        if attachment_path:
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                    msg.attach(part)
            except Exception as e:
                logger.warning(f"Failed to attach {attachment_path}: {e}")

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            logger.info(f"Email sent to {to_email}")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            raise

    subject = "New Task Assignment"
    body = (
        f"<p>Dear {name},</p>"
        f"<p>You have been assigned the following task: <b>{task}</b></p>"
        f"<p>Please check the Task Manager for details.</p>"
        f"<p>Best regards,<br>Task Manager Team</p>"
    )
    try:
        send_email(email, subject, body)
        logger.info(f"Notified {name} ({email}) about task '{task}'")
    except Exception as e:
        logger.error(f"Failed to notify {name} ({email}) about task '{task}': {e}")
    """
