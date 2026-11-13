"""
Content Assistant — configuration.

Everything secret comes from Render environment variables. Nothing here
touches Blu Royal Rides code or settings.
"""

import os
from pathlib import Path


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# ---- Access -----------------------------------------------------------------
# The password you type on your phone to open /assistant.
ASSISTANT_PASSWORD = env("ASSISTANT_PASSWORD")
# Random long string used to sign your login cookie. Any 40+ characters.
ASSISTANT_SECRET = env("ASSISTANT_SECRET") or env("VAULT_TOKEN_SECRET") or "change-me-please"

# Public address of the site. Used for OAuth return links and for the image
# link Instagram downloads from.
PUBLIC_BASE_URL = env("ASSISTANT_PUBLIC_URL", "https://codigodepoder777.com").rstrip("/")

# ---- Storage ----------------------------------------------------------------
# On Render, /var/data only exists if a persistent disk is attached. Without
# it, everything still works but saved logins reset on each deploy.
_DEFAULT_DIR = "/var/data/content_assistant" if Path("/var/data").exists() else "./content_assistant_data"
DATA_DIR = Path(env("ASSISTANT_DATA_DIR", _DEFAULT_DIR))
MEDIA_DIR = DATA_DIR / "media"
DB_PATH = DATA_DIR / "assistant.db"
PERSISTENT = str(DATA_DIR).startswith("/var/data")

# ---- AI writer --------------------------------------------------------------
ANTHROPIC_MODEL = env("ASSISTANT_MODEL", "claude-sonnet-5-5")

# ---- HeyGen -----------------------------------------------------------------
HEYGEN_API_KEY = env("HEYGEN_API_KEY")

# ---- YouTube (Google Cloud OAuth client) -------------------------------------
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")
# "api"    = assistant uploads the video for you (needs Google's API audit
#            approved, otherwise YouTube locks the upload as private)
# "manual" = assistant gives you the video + copy buttons, you upload in the
#            YouTube app and paste the link back
YOUTUBE_MODE = env("YOUTUBE_MODE", "manual").lower()
YOUTUBE_PRIVACY = env("YOUTUBE_PRIVACY", "public").lower()

# ---- LinkedIn ---------------------------------------------------------------
LINKEDIN_CLIENT_ID = env("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = env("LINKEDIN_CLIENT_SECRET")
LINKEDIN_VERSION = env("LINKEDIN_VERSION", "202609")

# ---- Instagram (Instagram API with Instagram Login) --------------------------
INSTAGRAM_APP_ID = env("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = env("INSTAGRAM_APP_SECRET")
INSTAGRAM_API_VERSION = env("INSTAGRAM_API_VERSION", "v25.0")

# ---- Ready notification (optional) ------------------------------------------
# Uses the same SMTP_* variables your site already has for lead emails.
NOTIFY_EMAIL = env("ASSISTANT_NOTIFY_EMAIL") or env("SMTP_TO_EMAIL")

# ---- Brands -----------------------------------------------------------------
BRANDS = {
    "codigo": {
        "name": "Código de Poder 777",
        "default_video_mode": "heygen",
        "default_language": "es",
        "website": "codigodepoder777.com",
        "colors": {"bg": "#0a1628", "accent": "#d4af37", "text": "#ffffff"},
        "voice": (
            "Código de Poder 777 is Cindy Murphy's Spanish-first brand for women "
            "and entrepreneurs who want to build digital income with AI. Tone: "
            "confident, warm, empowering, direct, a little mystical (777 = "
            "alignment and power). Speak to the viewer as 'tú'. Every piece "
            "ends with a clear call to action (follow, comment a keyword, or "
            "visit codigodepoder777.com)."
        ),
        "instagram_keyword": "PODER",
    },
    "imperios": {
        "name": "Imperios Caídos",
        "default_video_mode": "meta",
        "default_language": "es",
        "website": "",
        "colors": {"bg": "#120d08", "accent": "#c9a227", "text": "#f5efe3"},
        "voice": (
            "Imperios Caídos is a faceless Spanish YouTube channel of short, "
            "dramatic history stories about fallen empires, lost civilizations "
            "and the people who ruled them. Tone: cinematic, suspenseful, "
            "documentary narrator. Open with a hook in the first 2 seconds. "
            "Stay historically accurate; never invent dates or quotes. End "
            "with 'Suscríbete para más historias de Imperios Caídos'."
        ),
        "instagram_keyword": "",
    },
}

PLATFORMS = ("youtube", "linkedin", "instagram")


def ensure_dirs() -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
