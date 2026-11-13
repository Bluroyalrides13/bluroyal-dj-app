"""YouTube: one-time Google login per channel, then resumable video uploads."""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode

import httpx

from src.content_assistant import config, store

logger = logging.getLogger(__name__)

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def redirect_uri() -> str:
    return f"{config.PUBLIC_BASE_URL}/assistant/connect/youtube/callback"


def auth_link(state: str) -> str:
    if not config.GOOGLE_CLIENT_ID:
        raise RuntimeError("GOOGLE_CLIENT_ID is not set in Render.")
    return AUTH_URL + "?" + urlencode({
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent select_account",
        "include_granted_scopes": "true",
        "state": state,
    })


def finish_login(brand: str, code: str) -> Dict[str, Any]:
    r = httpx.post(TOKEN_URL, data={
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri(),
        "grant_type": "authorization_code",
    }, timeout=30)
    data = r.json()
    if r.status_code >= 400 or "refresh_token" not in data:
        raise RuntimeError(f"Google login failed: {data.get('error_description') or data}")
    channel = _channel(data["access_token"])
    saved = {"refresh_token": data["refresh_token"], "channel_id": channel.get("id", ""),
             "channel_title": channel.get("title", "")}
    store.save_token(f"youtube:{brand}", saved)
    return saved


def _channel(access_token: str) -> Dict[str, str]:
    r = httpx.get("https://www.googleapis.com/youtube/v3/channels",
                  params={"part": "snippet", "mine": "true"},
                  headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    items = r.json().get("items") or [] if r.status_code < 400 else []
    if not items:
        return {}
    return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]}


def login_for(brand: str) -> Dict[str, Any]:
    tok = store.token(f"youtube:{brand}", {"refresh_token": f"YOUTUBE_REFRESH_TOKEN_{brand.upper()}"})
    if not tok:
        raise RuntimeError(f"YouTube isn't connected for {config.BRANDS[brand]['name']}. Tap Accounts → Connect YouTube.")
    return tok


def _access_token(brand: str) -> str:
    tok = login_for(brand)
    r = httpx.post(TOKEN_URL, data={
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }, timeout=30)
    data = r.json()
    if r.status_code >= 400:
        raise RuntimeError(
            f"YouTube login expired ({data.get('error')}). Tap Accounts → Connect YouTube again."
        )
    return data["access_token"]


def upload(brand: str, video_path: Path, title: str, description: str, tags: List[str]) -> Dict[str, str]:
    token = _access_token(brand)
    size = os.path.getsize(video_path)
    mime = mimetypes.guess_type(str(video_path))[0] or "video/mp4"
    meta = {
        "snippet": {"title": title[:100], "description": description[:4900],
                    "tags": tags[:20], "categoryId": "22"},
        "status": {"privacyStatus": config.YOUTUBE_PRIVACY, "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    start = httpx.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": mime, "X-Upload-Content-Length": str(size)},
        json=meta, timeout=60,
    )
    if start.status_code >= 400 or "location" not in start.headers:
        raise RuntimeError(f"YouTube refused the upload: {start.text[:400]}")

    def chunks():
        with open(video_path, "rb") as fh:
            while True:
                block = fh.read(4 << 20)
                if not block:
                    break
                yield block

    put = httpx.put(start.headers["location"], content=chunks(),
                    headers={"Content-Type": mime, "Content-Length": str(size)},
                    timeout=httpx.Timeout(1800, connect=60))
    if put.status_code >= 400:
        raise RuntimeError(f"YouTube upload failed: {put.text[:400]}")
    data = put.json()
    vid = data["id"]
    privacy = (data.get("status") or {}).get("privacyStatus", "")
    return {"id": vid, "url": f"https://youtu.be/{vid}", "privacy": privacy}
