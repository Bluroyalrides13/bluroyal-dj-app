"""LinkedIn: post to your personal profile (text + image + video link).

LinkedIn logins last about 60 days and self-serve apps get no refresh token,
so the Accounts screen shows when it's time to tap Connect again.
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode

import httpx

from src.content_assistant import config, store

logger = logging.getLogger(__name__)
API = "https://api.linkedin.com"


def redirect_uri() -> str:
    return f"{config.PUBLIC_BASE_URL}/assistant/connect/linkedin/callback"


def auth_link(state: str) -> str:
    if not config.LINKEDIN_CLIENT_ID:
        raise RuntimeError("LINKEDIN_CLIENT_ID is not set in Render.")
    return "https://www.linkedin.com/oauth/v2/authorization?" + urlencode({
        "response_type": "code",
        "client_id": config.LINKEDIN_CLIENT_ID,
        "redirect_uri": redirect_uri(),
        "state": state,
        "scope": "openid profile w_member_social",
    })


def finish_login(code: str) -> Dict[str, Any]:
    r = httpx.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri(),
        "client_id": config.LINKEDIN_CLIENT_ID,
        "client_secret": config.LINKEDIN_CLIENT_SECRET,
    }, timeout=30)
    data = r.json()
    if r.status_code >= 400 or "access_token" not in data:
        raise RuntimeError(f"LinkedIn login failed: {data.get('error_description') or data}")
    me = httpx.get(f"{API}/v2/userinfo", headers={"Authorization": f"Bearer {data['access_token']}"}, timeout=30).json()
    saved = {
        "access_token": data["access_token"],
        "person_urn": f"urn:li:person:{me['sub']}",
        "name": me.get("name", ""),
        "expires_at": time.time() + int(data.get("expires_in", 5184000)),
    }
    store.save_token("linkedin", saved)
    return saved


def login() -> Dict[str, Any]:
    tok = store.token("linkedin", {"access_token": "LINKEDIN_ACCESS_TOKEN", "person_urn": "LINKEDIN_PERSON_URN"})
    if not tok:
        raise RuntimeError("LinkedIn isn't connected. Tap Accounts → Connect LinkedIn.")
    if tok.get("expires_at") and tok["expires_at"] < time.time():
        raise RuntimeError("Your LinkedIn login expired (they last 60 days). Tap Accounts → Connect LinkedIn.")
    return tok


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Linkedin-Version": config.LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def _upload_image(token: str, owner: str, image_path: Path) -> str:
    init = httpx.post(f"{API}/rest/images?action=initializeUpload", headers=_headers(token),
                      json={"initializeUploadRequest": {"owner": owner}}, timeout=30)
    if init.status_code >= 400:
        raise RuntimeError(f"LinkedIn image upload refused: {init.text[:300]}")
    value = init.json()["value"]
    with open(image_path, "rb") as fh:
        put = httpx.put(value["uploadUrl"], content=fh.read(),
                        headers={"Authorization": f"Bearer {token}"}, timeout=120)
    if put.status_code >= 400:
        raise RuntimeError(f"LinkedIn image upload failed: {put.text[:300]}")
    return value["image"]


def post(text: str, image_path: Path = None, image_alt: str = "") -> Dict[str, str]:
    tok = login()
    token, author = tok["access_token"], tok["person_urn"]
    body: Dict[str, Any] = {
        "author": author,
        "commentary": _escape(text)[:2900],
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if image_path and Path(image_path).exists():
        body["content"] = {"media": {"id": _upload_image(token, author, Path(image_path)), "altText": image_alt[:400]}}
    r = httpx.post(f"{API}/rest/posts", headers=_headers(token), json=body, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"LinkedIn refused the post: {r.text[:400]}")
    urn = r.headers.get("x-restli-id", "")
    return {"id": urn, "url": f"https://www.linkedin.com/feed/update/{urn}/" if urn else ""}


def _escape_plain(text: str) -> str:
    for ch in "\\|{}@[]()<>#*_~":
        text = text.replace(ch, "\\" + ch)
    return text


def _escape(text: str) -> str:
    """LinkedIn's 'little text' format treats some characters as markup.
    Escape them, but keep #hashtags working as real hashtags."""
    out, pos = [], 0
    for m in re.finditer(r"#(\w+)", text):
        out.append(_escape_plain(text[pos:m.start()]))
        out.append("{hashtag|\\#|" + m.group(1) + "}")
        pos = m.end()
    out.append(_escape_plain(text[pos:]))
    return "".join(out)
