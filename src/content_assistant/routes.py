"""
/assistant — your private content assistant page and its API.

Everything except the Instagram image link and the OAuth return pages
requires your password.
"""

import hmac
import logging
import mimetypes
import os
import secrets
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel, Field

from src.content_assistant import config, heygen, instagram, linkedin, pipeline, store, writer, youtube

logger = logging.getLogger(__name__)
router = APIRouter()

PAGE = Path(__file__).resolve().parents[2] / "static" / "assistant" / "index.html"
COOKIE = "ca_session"
SESSION_DAYS = 30
_sessions = URLSafeTimedSerializer(config.ASSISTANT_SECRET, salt="assistant-session")
_oauth = URLSafeTimedSerializer(config.ASSISTANT_SECRET, salt="assistant-oauth")
_fails: Dict[str, List[float]] = defaultdict(list)

store.init()
pipeline.start_watcher()


# ---- auth -------------------------------------------------------------------

def _logged_in(request: Request) -> bool:
    raw = request.cookies.get(COOKIE)
    if not raw:
        return False
    try:
        _sessions.loads(raw, max_age=SESSION_DAYS * 86400)
        return True
    except (BadSignature, SignatureExpired):
        return False


def require_login(request: Request) -> None:
    if not _logged_in(request):
        raise HTTPException(status_code=401, detail="Please log in.")


class LoginIn(BaseModel):
    password: str


@router.post("/assistant/api/login")
async def login(body: LoginIn, request: Request, response: Response):
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0]
    now = time.time()
    _fails[ip] = [t for t in _fails[ip] if now - t < 900]
    if len(_fails[ip]) >= 6:
        raise HTTPException(429, "Too many tries. Wait 15 minutes.")
    if not config.ASSISTANT_PASSWORD:
        raise HTTPException(500, "ASSISTANT_PASSWORD is not set in Render yet.")
    if not hmac.compare_digest(body.password.encode(), config.ASSISTANT_PASSWORD.encode()):
        _fails[ip].append(now)
        raise HTTPException(401, "Wrong password.")
    response.set_cookie(COOKIE, _sessions.dumps({"t": now}), max_age=SESSION_DAYS * 86400,
                        httponly=True, secure=config.PUBLIC_BASE_URL.startswith("https"), samesite="lax")
    return {"ok": True}


@router.post("/assistant/api/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE)
    return {"ok": True}


@router.get("/assistant", include_in_schema=False)
async def page():
    return HTMLResponse(PAGE.read_text(encoding="utf-8"), headers={"Cache-Control": "no-store"})


@router.get("/assistant/api/me")
async def me(request: Request):
    return {"logged_in": _logged_in(request)}


# ---- overview & accounts ----------------------------------------------------

def _days_left(tok: Optional[Dict[str, Any]]) -> Optional[int]:
    if tok and tok.get("expires_at"):
        return max(0, int((tok["expires_at"] - time.time()) // 86400))
    return None


def _accounts() -> Dict[str, Any]:
    out: Dict[str, Any] = {"youtube": {}, "instagram": {}, "heygen": {}}
    for b in config.BRANDS:
        yt = store.token(f"youtube:{b}", {"refresh_token": f"YOUTUBE_REFRESH_TOKEN_{b.upper()}"})
        out["youtube"][b] = {"connected": bool(yt), "label": (yt or {}).get("channel_title", "")}
        ig = store.kv_get(f"token:instagram:{b}")
        out["instagram"][b] = {"connected": bool(ig), "label": (ig or {}).get("username", ""),
                               "days_left": _days_left(ig)}
        hg = pipeline.heygen_choice(b)
        out["heygen"][b] = {"avatar_id": hg["avatar"]["id"], "voice_id": hg["voice_id"]}
    li = store.token("linkedin", {"access_token": "LINKEDIN_ACCESS_TOKEN", "person_urn": "LINKEDIN_PERSON_URN"})
    out["linkedin"] = {"connected": bool(li), "label": (li or {}).get("name", ""), "days_left": _days_left(li)}
    out["setup"] = {
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "heygen": bool(config.HEYGEN_API_KEY),
        "google": bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET),
        "linkedin": bool(config.LINKEDIN_CLIENT_ID and config.LINKEDIN_CLIENT_SECRET),
        "instagram": bool(config.INSTAGRAM_APP_ID and config.INSTAGRAM_APP_SECRET),
        "email": bool(config.NOTIFY_EMAIL),
    }
    return out


def _summary(job: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": job["id"], "brand": job["brand"], "prompt": job["prompt"][:140], "status": job["status"],
        "step": job["step"], "created": job["created"], "updated": job["updated"],
        "title": (job["pack"] or {}).get("youtube_title", ""),
    }


@router.get("/assistant/api/overview", dependencies=[Depends(require_login)])
async def overview():
    return {
        "brands": {k: {"name": v["name"], "default_video_mode": v["default_video_mode"],
                       "default_language": v["default_language"]} for k, v in config.BRANDS.items()},
        "accounts": _accounts(),
        "youtube_mode": config.YOUTUBE_MODE,
        "persistent_storage": config.PERSISTENT,
        "jobs": [_summary(j) for j in store.list_jobs(30)],
    }


# ---- jobs -------------------------------------------------------------------

class JobIn(BaseModel):
    brand: str
    prompt: str = Field(min_length=3, max_length=4000)
    video_mode: str = "heygen"
    format: str = "short"
    language: str = "es"
    seconds: Optional[int] = None


def _job_or_404(job_id: str) -> Dict[str, Any]:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job


def _full(job: Dict[str, Any]) -> Dict[str, Any]:
    pack = job["pack"] or {}
    stale = job["status"] in ("drafting", "posting") and time.time() - job["updated"] > 300
    return {
        **_summary(job),
        "options": job["options"],
        "pack": pack,
        "error": job["error"],
        "results": job["results"],
        "youtube_url": job["youtube_url"],
        "has_video": bool(job["video_path"] and Path(job["video_path"]).exists()),
        "has_image": bool(job["image_path"] and Path(job["image_path"]).exists()),
        "image_v": int(job["updated"]),
        "linkedin_preview": writer.linkedin_text(pack, job["youtube_url"] or "https://youtu.be/…") if pack else "",
        "instagram_preview": writer.instagram_caption_text(pack) if pack else "",
        "stale": stale,
    }


@router.post("/assistant/api/jobs", dependencies=[Depends(require_login)])
async def create_job(body: JobIn):
    if body.brand not in config.BRANDS:
        raise HTTPException(400, "Unknown brand.")
    opts = body.model_dump(exclude={"brand", "prompt"})
    if opts["video_mode"] not in ("heygen", "meta"):
        opts["video_mode"] = config.BRANDS[body.brand]["default_video_mode"]
    job_id = pipeline.start(body.brand, body.prompt.strip(), opts)
    return {"id": job_id}


@router.get("/assistant/api/jobs/{job_id}", dependencies=[Depends(require_login)])
async def get_job(job_id: str):
    return _full(_job_or_404(job_id))


@router.post("/assistant/api/jobs/{job_id}/video", dependencies=[Depends(require_login)])
def upload_video(job_id: str, file: UploadFile = File(...)):
    job = _job_or_404(job_id)
    if job["status"] in ("posting", "done"):
        raise HTTPException(400, "This job already posted.")
    pipeline.save_uploaded_video(job_id, file.file, file.filename or "video.mp4")
    return _full(store.get_job(job_id))


class ReviseIn(BaseModel):
    feedback: str = Field(min_length=2, max_length=3000)
    remake_video: bool = False


@router.post("/assistant/api/jobs/{job_id}/revise", dependencies=[Depends(require_login)])
async def revise(job_id: str, body: ReviseIn):
    job = _job_or_404(job_id)
    if job["status"] in ("posting", "done", "drafting"):
        raise HTTPException(400, "Can't change this job right now.")
    pipeline.revise(job_id, body.feedback, body.remake_video)
    return {"ok": True}


class EditIn(BaseModel):
    fields: Dict[str, Any]


@router.post("/assistant/api/jobs/{job_id}/edit", dependencies=[Depends(require_login)])
async def edit(job_id: str, body: EditIn):
    _job_or_404(job_id)
    pipeline.edit_pack(job_id, body.fields)
    return _full(store.get_job(job_id))


class ApproveIn(BaseModel):
    platforms: List[str]
    youtube_url: str = ""


@router.post("/assistant/api/jobs/{job_id}/approve", dependencies=[Depends(require_login)])
async def approve(job_id: str, body: ApproveIn):
    job = _job_or_404(job_id)
    if job["status"] not in ("review", "partial") and not (job["status"] == "posting" and _full(job)["stale"]):
        raise HTTPException(400, "This job isn't ready to post.")
    if "youtube" in body.platforms and config.YOUTUBE_MODE == "api" and not job["video_path"]:
        raise HTTPException(400, "There's no video to upload yet.")
    if not body.platforms:
        raise HTTPException(400, "Tick at least one platform.")
    pipeline.approve(job_id, body.platforms, body.youtube_url)
    return {"ok": True}


@router.post("/assistant/api/jobs/{job_id}/retry", dependencies=[Depends(require_login)])
def retry(job_id: str):
    job = _job_or_404(job_id)
    if job["status"] == "error" or (job["status"] == "drafting" and _full(job)["stale"]):
        pipeline.retry_draft(job_id)
    elif job["status"] == "rendering":
        pipeline.check_rendering(job_id)
    else:
        raise HTTPException(400, "Nothing to retry here.")
    return {"ok": True}


@router.post("/assistant/api/jobs/{job_id}/check", dependencies=[Depends(require_login)])
def check(job_id: str):
    _job_or_404(job_id)
    pipeline.check_rendering(job_id)
    return _full(store.get_job(job_id))


@router.delete("/assistant/api/jobs/{job_id}", dependencies=[Depends(require_login)])
def delete(job_id: str):
    _job_or_404(job_id)
    store.delete_job(job_id)
    d = pipeline.job_dir(job_id)
    if d.exists():
        for f in d.iterdir():
            f.unlink()
        d.rmdir()
    return {"ok": True}


@router.get("/assistant/api/jobs/{job_id}/image", dependencies=[Depends(require_login)])
async def job_image(job_id: str):
    job = _job_or_404(job_id)
    if not job["image_path"] or not Path(job["image_path"]).exists():
        raise HTTPException(404)
    return FileResponse(job["image_path"], media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@router.get("/assistant/api/jobs/{job_id}/video", dependencies=[Depends(require_login)])
async def job_video(job_id: str, download: int = 0):
    job = _job_or_404(job_id)
    if not job["video_path"] or not Path(job["video_path"]).exists():
        raise HTTPException(404)
    p = Path(job["video_path"])
    name = f"{job_id}{p.suffix}"
    return FileResponse(p, media_type=mimetypes.guess_type(p.name)[0] or "video/mp4",
                        filename=name if download else None)


@router.get("/assistant/public/{token}.jpg", include_in_schema=False)
async def public_image(token: str):
    """The one public link: Instagram's servers download the graphic from here."""
    job_id = pipeline.job_from_public_token(token)
    job = store.get_job(job_id) if job_id else None
    if not job or not job["image_path"] or not Path(job["image_path"]).exists():
        raise HTTPException(404)
    return FileResponse(job["image_path"], media_type="image/jpeg")


# ---- HeyGen settings --------------------------------------------------------

@router.get("/assistant/api/heygen/options", dependencies=[Depends(require_login)])
def heygen_options():
    try:
        return {"avatars": heygen.list_avatars(), "voices": heygen.list_voices()}
    except Exception as exc:
        raise HTTPException(400, f"Couldn't reach HeyGen: {exc}")


class HeygenChoice(BaseModel):
    brand: str
    avatar_id: str
    avatar_kind: str = "avatar"
    voice_id: str


@router.post("/assistant/api/heygen/choice", dependencies=[Depends(require_login)])
async def heygen_choice(body: HeygenChoice):
    if body.brand not in config.BRANDS:
        raise HTTPException(400, "Unknown brand.")
    store.kv_set(f"heygen:{body.brand}", body.model_dump(exclude={"brand"}))
    return {"ok": True}


# ---- connect accounts (OAuth) -----------------------------------------------

@router.get("/assistant/connect/{platform}", include_in_schema=False)
async def connect(platform: str, request: Request, brand: str = "codigo"):
    if not _logged_in(request):
        return RedirectResponse("/assistant")
    state = _oauth.dumps({"p": platform, "b": brand, "n": secrets.token_hex(8)})
    try:
        if platform == "youtube":
            url = youtube.auth_link(state)
        elif platform == "linkedin":
            url = linkedin.auth_link(state)
        elif platform == "instagram":
            url = instagram.auth_link(state)
        else:
            raise HTTPException(404)
    except RuntimeError as exc:
        return _connect_result(False, str(exc))
    return RedirectResponse(url)


def _connect_result(ok: bool, message: str) -> HTMLResponse:
    color = "#2e7d32" if ok else "#b3261e"
    return HTMLResponse(
        f"""<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
        <body style="font-family:-apple-system,system-ui,sans-serif;background:#0a1628;color:#fff;padding:32px;text-align:center">
        <h2 style="color:{color}">{'Connected ✓' if ok else 'Not connected'}</h2>
        <p style="font-size:17px;line-height:1.5">{message}</p>
        <p><a href="/assistant#accounts" style="color:#d4af37;font-size:18px">Back to your assistant</a></p></body>"""
    )


@router.get("/assistant/connect/{platform}/callback", include_in_schema=False)
def connect_callback(platform: str, request: Request, code: str = "", state: str = "",
                           error: str = "", error_description: str = ""):
    if not _logged_in(request):
        return RedirectResponse("/assistant")
    if error:
        return _connect_result(False, f"{error_description or error}")
    try:
        info = _oauth.loads(state, max_age=900)
    except (BadSignature, SignatureExpired):
        return _connect_result(False, "That link expired. Please tap Connect again.")
    if info.get("p") != platform:
        return _connect_result(False, "Mismatched login. Please tap Connect again.")
    brand = info.get("b") if info.get("b") in config.BRANDS else "codigo"
    try:
        if platform == "youtube":
            saved = youtube.finish_login(brand, code)
            msg = f"YouTube channel <b>{saved.get('channel_title') or 'connected'}</b> is linked to {config.BRANDS[brand]['name']}."
        elif platform == "linkedin":
            saved = linkedin.finish_login(code)
            msg = f"LinkedIn <b>{saved.get('name', '')}</b> is linked. LinkedIn asks you to reconnect every 60 days."
        elif platform == "instagram":
            saved = instagram.finish_login(brand, code)
            msg = f"Instagram <b>@{saved.get('username', '')}</b> is linked to {config.BRANDS[brand]['name']}."
        else:
            raise HTTPException(404)
    except Exception as exc:
        logger.exception("Connect %s failed", platform)
        return _connect_result(False, str(exc)[:400])
    if not config.PERSISTENT:
        msg += ("<br><br><small>Heads-up: your server has no saved disk, so this login resets on the next "
                "deploy. The setup guide shows the 1-minute fix.</small>")
    return _connect_result(True, msg)


class DisconnectIn(BaseModel):
    key: str


@router.post("/assistant/api/disconnect", dependencies=[Depends(require_login)])
async def disconnect(body: DisconnectIn):
    allowed = {"linkedin"} | {f"{p}:{b}" for p in ("youtube", "instagram") for b in config.BRANDS}
    if body.key not in allowed:
        raise HTTPException(400, "Unknown account.")
    store.kv_delete(f"token:{body.key}")
    return {"ok": True}
