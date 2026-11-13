"""HeyGen: start an avatar video, check on it, download it when done."""

import logging
from pathlib import Path
from typing import Any, Dict, List

import httpx

from src.content_assistant import config

logger = logging.getLogger(__name__)
API = "https://api.heygen.com"
MAX_SCRIPT = 4800  # HeyGen caps one text input at 5000 characters


def _headers() -> Dict[str, str]:
    if not config.HEYGEN_API_KEY:
        raise RuntimeError("HEYGEN_API_KEY is not set in Render.")
    return {"X-Api-Key": config.HEYGEN_API_KEY, "Accept": "application/json"}


def list_avatars() -> List[Dict[str, Any]]:
    r = httpx.get(f"{API}/v2/avatars", headers=_headers(), timeout=60)
    r.raise_for_status()
    data = r.json().get("data") or {}
    out = [
        {"id": a.get("avatar_id"), "name": a.get("avatar_name"), "preview": a.get("preview_image_url"),
         "kind": "avatar", "voice": a.get("default_voice_id")}
        for a in data.get("avatars", [])
    ]
    out += [
        {"id": t.get("talking_photo_id"), "name": t.get("talking_photo_name"), "preview": t.get("preview_image_url"),
         "kind": "talking_photo", "voice": None}
        for t in data.get("talking_photos", [])
    ]
    return out


def list_voices() -> List[Dict[str, Any]]:
    r = httpx.get(f"{API}/v2/voices", headers=_headers(), timeout=60)
    r.raise_for_status()
    voices = (r.json().get("data") or {}).get("voices", [])
    return [
        {"id": v.get("voice_id"), "name": v.get("name"), "language": v.get("language"), "gender": v.get("gender")}
        for v in voices
    ]


def start_video(script: str, avatar: Dict[str, str], voice_id: str, vertical: bool,
                background: str, title: str) -> str:
    if not avatar.get("id") or not voice_id:
        raise RuntimeError("Pick your HeyGen avatar and voice in Settings first.")
    if avatar.get("kind") == "talking_photo":
        character = {"type": "talking_photo", "talking_photo_id": avatar["id"]}
    else:
        character = {"type": "avatar", "avatar_id": avatar["id"], "avatar_style": "normal"}
    body = {
        "title": title[:100],
        "video_inputs": [{
            "character": character,
            "voice": {"type": "text", "input_text": script[:MAX_SCRIPT], "voice_id": voice_id},
            "background": {"type": "color", "value": background},
        }],
        "dimension": {"width": 1080, "height": 1920} if vertical else {"width": 1920, "height": 1080},
    }
    r = httpx.post(f"{API}/v2/video/generate", headers=_headers(), json=body, timeout=60)
    payload = r.json() if r.content else {}
    if r.status_code >= 400 or payload.get("error"):
        raise RuntimeError(f"HeyGen refused the video: {payload.get('error') or r.text[:300]}")
    video_id = (payload.get("data") or {}).get("video_id")
    if not video_id:
        raise RuntimeError(f"HeyGen returned no video id: {r.text[:300]}")
    return video_id


def check_video(video_id: str) -> Dict[str, Any]:
    """Returns {'status': pending|processing|completed|failed, 'url': ..., 'error': ...}."""
    r = httpx.get(f"{API}/v1/video_status.get", params={"video_id": video_id}, headers=_headers(), timeout=60)
    if r.status_code == 404:
        r = httpx.get(f"{API}/v2/videos/{video_id}", headers=_headers(), timeout=60)
    r.raise_for_status()
    data = r.json().get("data") or {}
    err = data.get("error")
    if isinstance(err, dict):
        err = err.get("message") or err.get("detail") or str(err)
    return {"status": data.get("status", "processing"), "url": data.get("video_url"), "error": err}


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=600, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_bytes(1 << 20):
                fh.write(chunk)
    return dest
