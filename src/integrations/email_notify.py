"""Lead notification email.

Applications are written to SQLite, which on Render lives on an ephemeral
filesystem and does not survive a redeploy. Until that is fixed, this email
is the only durable copy of a lead, so send failures are logged loudly but
never raised — a broken mailbox must not cost us the form submission.
"""

import logging
import smtplib
from email.message import EmailMessage
from typing import Dict

from config.settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()


def _is_configured() -> bool:
    return bool(
        settings.SMTP_HOST
        and settings.SMTP_USERNAME
        and settings.SMTP_PASSWORD
        and settings.SMTP_TO_EMAIL
    )


def _format_body(application: Dict, scoring: Dict) -> str:
    def field(label: str, value) -> str:
        return f"{label}: {value if value not in (None, '') else '—'}"

    lines = [
        "Nueva solicitud desde codigodepoder777.com",
        "",
        field("Nombre", application.get("name")),
        field("Email", application.get("email")),
        field("Instagram", application.get("instagram_handle")),
        field("Programa de interés", application.get("interested_offer")),
        "",
        "Meta:",
        f"  {application.get('biggest_goal') or '—'}",
        "",
        "Industria / obstáculo:",
        f"  {application.get('biggest_block') or '—'}",
        "",
        "--- Puntuación automática ---",
        field("Score", scoring.get("overall_score")),
        field("Oferta recomendada", scoring.get("recommended_offer")),
        field("Estado", scoring.get("status")),
        field("Siguiente paso", scoring.get("next_step")),
        "",
        field("ID", scoring.get("application_id")),
    ]
    return "\n".join(lines)


def send_application_notification(application: Dict, scoring: Dict) -> bool:
    """Email a new application. Returns True if sent, False otherwise."""
    if not _is_configured():
        logger.warning(
            "Lead notification skipped: SMTP is not configured. "
            "Set SMTP_USERNAME, SMTP_PASSWORD and SMTP_TO_EMAIL."
        )
        return False

    name = application.get("name") or "Solicitante"
    offer = application.get("interested_offer") or "sin programa"

    message = EmailMessage()
    message["Subject"] = f"Nueva solicitud: {name} — {offer}"
    message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    message["To"] = settings.SMTP_TO_EMAIL
    reply_to = application.get("email")
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(_format_body(application, scoring))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        logger.info("Lead notification sent for %s", application.get("email"))
        return True
    except Exception as exc:
        logger.error("Lead notification FAILED for %s: %s", application.get("email"), exc)
        return False
