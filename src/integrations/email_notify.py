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


def send_checkout_failure_alert(offer_slug: str, reason: str) -> bool:
    """Alert when a buy button fails to produce a checkout session.

    Stripe only ever hears about attempts that reach it, so a failure here is
    invisible everywhere else: the shopper sees an error and leaves, the
    dashboard stays empty, and it reads as 'nobody is buying' rather than
    'nobody can buy'. Worth an email every time.
    """
    if not _is_configured():
        return False

    message = EmailMessage()
    message["Subject"] = f"ALERTA: falló el checkout — {offer_slug}"
    message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    message["To"] = settings.SMTP_TO_EMAIL
    message.set_content(
        "\n".join(
            [
                "Un cliente intentó comprar y el checkout falló.",
                "",
                f"Producto: {offer_slug}",
                f"Motivo técnico: {reason}",
                "",
                "Esto significa que la persona vio un error y probablemente se fue.",
                "Stripe no registra estos intentos, así que este correo es el único aviso.",
                "",
                "Revisa STRIPE_SECRET_KEY en Render y los logs del servicio.",
            ]
        )
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        logger.info("Checkout failure alert sent for %s", offer_slug)
        return True
    except Exception as exc:
        logger.error("Checkout failure alert FAILED for %s: %s", offer_slug, exc)
        return False


def send_vault_delivery_email(buyer_email: str, product_name: str, download_url: str) -> bool:
    """Send the buyer their download link right after a successful payment.

    This is the entire "fulfillment" step for a digital product — there is
    no order dashboard, so if this send fails the buyer paid and got
    nothing, with no other system that will ever notice. Log failures
    loudly; the caller alerts the business side separately.
    """
    if not _is_configured():
        logger.error("Vault delivery email NOT sent (SMTP not configured): %s -> %s", product_name, buyer_email)
        return False

    message = EmailMessage()
    message["Subject"] = f"Tu descarga: {product_name} — Código de Poder 777"
    message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    message["To"] = buyer_email
    message.set_content(
        "\n".join(
            [
                "¡Gracias por tu compra!",
                "",
                f"Aquí está tu descarga de: {product_name}",
                "",
                download_url,
                "",
                "Este enlace es válido por 14 días. Guarda una copia del archivo",
                "en tu computadora o Google Drive apenas lo descargues.",
                "",
                f"¿Problemas con el enlace? Responde a este correo o escribe a {settings.SUPPORT_EMAIL or settings.SMTP_TO_EMAIL}.",
                "",
                "— Código de Poder 777",
            ]
        )
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        logger.info("Vault delivery email sent: %s -> %s", product_name, buyer_email)
        return True
    except Exception as exc:
        logger.error("Vault delivery email FAILED: %s -> %s (%s)", product_name, buyer_email, exc)
        return False


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
