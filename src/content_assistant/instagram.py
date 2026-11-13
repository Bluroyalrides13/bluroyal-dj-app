"""Instagram: publish an image post to a Business/Creator account.

Uses "Instagram API with Instagram Login" (no Facebook Page needed). Logins
last 60 days; the assistant renews them automatically whenever you post, so
as long as you post at least once every ~50 days you never reconnect.
"""

import logging
import time
from typing import Any, Dict
from urllib.parse import urlencode

import httpx

from src.content_assistant import config, store

logger = logging.getLogger(__name__)
GRAPH = "https://graph.instagram.com"


def redirect_uri() -> str:
    return f"{config.PUBLIC_BASE_URL}/assistant/connect/instagram/callback"


def auth_link(state: str) -> str:
    if not config.INSTAGRAM_APP_ID:
        raise RuntimeError("INSTAGRAM_APP_ID is not set in Render.")
    return "https://www.instagram.com/oauth/authorize?" + urlencode({
        "client_id": config.INSTAGRAM_APP_ID,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "instagram_business_basic,instagram_business_content_publish",
        "state": state,
        "enable_fb_login": "0",
        "force_authentication": "1",
    })


def finish_login(brand: str, code: str) -> Dict[str, Any]:
    code = code.split("#_")[0]
    r = httpx.post("https://api.instagram.com/oauth/access_token", data={
        "client_id": config.INSTAGRAM_APP_ID,
        "client_secret": config.INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri(),
        "code": code,
    }, timeout=30)
    data = r.json()
    if isinstance(data.get("data"), list) and data["data"]:
        data = data["data"][0]
    if r.status_code >= 400 or "access_token" not in data:
        raise RuntimeError(f"Instagram login failed: {data.get('error_message') or data}")
    long = httpx.get(f"{GRAPH}/access_token", params={
        "grant_type": "ig_exchange_token",
        "client_secret": config.INSTAGRAM_APP_SECRET,
        "access_token": data["access_token"],
    }, timeout=30).json()
    if "access_token" not in long:
        raise RuntimeError(f"Instagram long-lived login failed: {long}")
    me = httpx.get(f"{GRAPH}/{config.INSTAGRAM_API_VERSION}/me",
                   params={"fields": "user_id,username", "access_token": long["access_token"]}, timeout=30).json()
    saved = {
        "access_token": long["access_token"],
        "ig_user_id": str(me.get("user_id") or me.get("id") or data.get("user_id")),
        "username": me.get("username", ""),
        "expires_at": time.time() + int(long.get("expires_in", 5184000)),
        "refreshed_at": time.time(),
    }
    store.save_token(f"instagram:{brand}", saved)
    return saved


def login_for(brand: str) -> Dict[str, Any]:
    """This brand's Instagram, or fall back to the Código account."""
    for key in (f"instagram:{brand}", "instagram:codigo"):
        tok = store.kv_get(f"token:{key}")
        if tok:
            return {**tok, "_key": key}
    env = store.token("instagram:env", {"access_token": "INSTAGRAM_ACCESS_TOKEN", "ig_user_id": "INSTAGRAM_USER_ID"})
    if env:
        return {**env, "_key": None}
    raise RuntimeError("Instagram isn't connected. Tap Accounts → Connect Instagram.")


def _maybe_refresh(tok: Dict[str, Any]) -> Dict[str, Any]:
    if not tok.get("_key") or time.time() - tok.get("refreshed_at", 0) < 3 * 86400:
        return tok
    r = httpx.get(f"{GRAPH}/refresh_access_token",
                  params={"grant_type": "ig_refresh_token", "access_token": tok["access_token"]}, timeout=30)
    if r.status_code < 400 and "access_token" in r.json():
        data = r.json()
        key = tok.pop("_key")
        tok.update(access_token=data["access_token"], refreshed_at=time.time(),
                   expires_at=time.time() + int(data.get("expires_in", 5184000)))
        store.save_token(key, tok)
        tok["_key"] = key
    else:
        logger.warning("Instagram token refresh failed: %s", r.text[:200])
    return tok


def publish_image(brand: str, image_url: str, caption: str) -> Dict[str, str]:
    tok = _maybe_refresh(login_for(brand))
    if tok.get("expires_at") and tok["expires_at"] < time.time():
        raise RuntimeError("Your Instagram login expired. Tap Accounts → Connect Instagram.")
    base = f"{GRAPH}/{config.INSTAGRAM_API_VERSION}/{tok['ig_user_id']}"
    auth = {"Authorization": f"Bearer {tok['access_token']}"}

    c = httpx.post(f"{base}/media", headers=auth, json={"image_url": image_url, "caption": caption}, timeout=60)
    if c.status_code >= 400 or "id" not in c.json():
        raise RuntimeError(f"Instagram refused the image: {c.text[:400]}")
    container = c.json()["id"]

    for _ in range(30):  # wait up to ~60s for Instagram to fetch the image
        s = httpx.get(f"{GRAPH}/{config.INSTAGRAM_API_VERSION}/{container}",
                      params={"fields": "status_code,status"}, headers=auth, timeout=30).json()
        code = s.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram couldn't process the image: {s.get('status')}")
        time.sleep(2)

    p = httpx.post(f"{base}/media_publish", headers=auth, json={"creation_id": container}, timeout=60)
    if p.status_code >= 400 or "id" not in p.json():
        raise RuntimeError(f"Instagram refused to publish: {p.text[:400]}")
    media_id = p.json()["id"]
    link = httpx.get(f"{GRAPH}/{config.INSTAGRAM_API_VERSION}/{media_id}",
                     params={"fields": "permalink"}, headers=auth, timeout=30).json().get("permalink", "")
    return {"id": media_id, "url": link}
