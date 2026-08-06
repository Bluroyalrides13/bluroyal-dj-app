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


def _first_name(full_name: str) -> str:
    return (full_name or "").strip().split(" ")[0] or "Hola"


def send_applicant_confirmation(application: Dict) -> bool:
    """Acknowledge the applicant so they aren't left wondering.

    Separate from the internal notification: this one goes to the person who
    filled in the form. Also best-effort — a failure here must not affect the
    submission or the internal notification.
    """
    to_address = (application.get("email") or "").strip()
    if not _is_configured() or not to_address:
        return False

    name = _first_name(application.get("name"))
    offer = application.get("interested_offer")

    body = [
        f"Hola {name},",
        "",
        "Gracias por tu solicitud. Ya la recibimos y la estamos revisando.",
        "",
    ]
    if offer:
        body += [f"Programa de interés: {offer}", ""]
    body += [
        "Qué sigue:",
        "  1. Revisamos tu situación y tus metas.",
        "  2. Te contactamos con la recomendación del mejor camino para ti.",
        "  3. Si encaja, agendamos una conversación.",
        "",
        "Normalmente respondemos en 1 o 2 días hábiles.",
        "",
        "Si tienes alguna pregunta, simplemente responde a este correo.",
        "",
        "Un abrazo,",
        "Código de Poder 777",
        "https://codigodepoder777.com",
    ]

    message = EmailMessage()
    message["Subject"] = "Recibimos tu solicitud — Código de Poder 777"
    message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    message["To"] = to_address
    if settings.SMTP_TO_EMAIL:
        message["Reply-To"] = settings.SMTP_TO_EMAIL
    message.set_content("\n".join(body))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        logger.info("Applicant confirmation sent to %s", to_address)
        return True
    except Exception as exc:
        logger.error("Applicant confirmation FAILED for %s: %s", to_address, exc)
        return False


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
        # Diagnostics without ever logging the secret itself. A length of 16
        # with no spaces is what Google expects; anything else is the bug.
        pwd = settings.SMTP_PASSWORD
        logger.error(
            "SMTP diagnostics -> host=%s port=%s username=%r from=%r to=%r "
            "password_length=%d has_spaces=%s tls=%s",
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.SMTP_USERNAME,
            settings.SMTP_FROM_EMAIL,
            settings.SMTP_TO_EMAIL,
            len(pwd),
            " " in pwd,
            settings.SMTP_USE_TLS,
        )
        return False
