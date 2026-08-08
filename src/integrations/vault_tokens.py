"""Signed download tokens for the Código de Poder 777 vault.

A buyer's download link must work without a login system, but must not be
guessable or reusable by someone who never paid. itsdangerous gives us a
signed, tamper-proof, time-limited token instead of building session/auth
infrastructure for a one-time-purchase catalog.

The token embeds the product slug so a single link can never be edited to
fetch a different (possibly pricier) product, and it expires so a leaked
link in an old email eventually stops working.
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from config.settings import Settings

settings = Settings()

_DOWNLOAD_LINK_MAX_AGE_SECONDS = 60 * 60 * 24 * 14  # 14 days


def _serializer() -> URLSafeTimedSerializer:
    secret = settings.STRIPE_SECRET_KEY or settings.SUPPORT_EMAIL or "codigodepoder777-fallback"
    return URLSafeTimedSerializer(secret, salt="vault-download")


def make_download_token(slug: str) -> str:
    """Create a signed token for one product slug."""
    return _serializer().dumps({"slug": slug})


def read_download_token(token: str) -> str:
    """Return the product slug for a valid, unexpired token.

    Raises ValueError with a user-safe message on any failure — expired,
    tampered, or malformed — so callers can 403 without leaking why.
    """
    try:
        data = _serializer().loads(token, max_age=_DOWNLOAD_LINK_MAX_AGE_SECONDS)
    except SignatureExpired:
        raise ValueError("This download link has expired.")
    except BadSignature:
        raise ValueError("This download link is invalid.")

    slug = data.get("slug")
    if not slug:
        raise ValueError("This download link is invalid.")
    return slug
