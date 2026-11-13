"""
The assistant's workflow for one prompt:

  drafting  → writes script + all posts + Instagram graphic
  rendering → HeyGen is making the avatar video          (HeyGen mode)
  needs_video → waiting for you to upload the Meta AI video (Meta AI mode)
  review    → everything is ready; nothing posts until you tap Approve
  posting   → uploading/posting to the platforms you ticked
  done / partial / error
"""

import logging
import os
import shutil
import smtplib
import threading
import time
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List, Optional

from itsdangerous import BadSignature, URLSafeSerializer

from config.settings import Settings
from src.content_assistant import config, heygen, image_card, instagram, linkedin, store, writer, youtube

logger = logging.getLogger(__name__)
_signer = URLSafeSerializer(config.ASSISTANT_SECRET, salt="assistant-media")
_busy = set()
_busy_lock = threading.Lock()


# ---- helpers ----------------------------------------------------------------

def job_dir(job_id: str) -> Path:
    return config.MEDIA_DIR / job_id


def public_image_url(job_id: str) -> str:
    return f"{config.PUBLIC_BASE_URL}/assistant/public/{_signer.dumps(job_id)}.jpg"


def job_from_public_token(token: str) -> Optional[str]:
    try:
        return _signer.loads(token)
    except BadSignature:
        return None


def _run_once(key: str, fn, *args) -> None:
    """Run fn in a background thread unless the same job is already running."""
    with _busy_lock:
        if key in _busy:
            return
        _busy.add(key)

    def wrapper():
        try:
            fn(*args)
        except Exception as exc:  # never kill the thread silently
            logger.exception("Assistant task %s failed", key)
            store.update_job(key.split(":", 1)[1], status="error", error=str(exc)[:1000], step="")
        finally:
            with _busy_lock:
                _busy.discard(key)

    threading.Thread(target=wrapper, daemon=True).start()


def notify(job: Dict[str, Any], subject: str, line: str) -> None:
    s = Settings()
    to = config.NOTIFY_EMAIL
    if not (to and s.SMTP_HOST and s.SMTP_USERNAME and s.SMTP_PASSWORD):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = s.SMTP_FROM_EMAIL or s.SMTP_USERNAME
    msg["To"] = to
    msg.set_content(
        f"{line}\n\n{config.BRANDS[job['brand']]['name']}: {job['prompt'][:200]}\n\n"
        f"Open it: {config.PUBLIC_BASE_URL}/assistant#job={job['id']}"
    )
    try:
        with smtplib.SMTP(s.SMTP_HOST, s.SMTP_PORT, timeout=15) as smtp:
            if s.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(s.SMTP_USERNAME, s.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as exc:
        logger.warning("Assistant notify email failed: %s", exc)


# ---- settings (HeyGen avatar/voice per brand) --------------------------------

def heygen_choice(brand: str) -> Dict[str, Any]:
    saved = store.kv_get(f"heygen:{brand}") or store.kv_get("heygen:codigo") or {}
    avatar_id = saved.get("avatar_id") or os.getenv(f"HEYGEN_AVATAR_ID_{brand.upper()}", "")
    voice_id = saved.get("voice_id") or os.getenv(f"HEYGEN_VOICE_ID_{brand.upper()}", "")
    return {"avatar": {"id": avatar_id, "kind": saved.get("avatar_kind", "avatar")}, "voice_id": voice_id}


# ---- drafting ---------------------------------------------------------------

def start(brand: str, prompt: str, options: Dict[str, Any]) -> str:
    job_id = store.create_job(brand, prompt, options)
    _run_once(f"draft:{job_id}", _draft, job_id)
    return job_id


def _make_image(job: Dict[str, Any], pack: Dict[str, Any]) -> str:
    path = job_dir(job["id"]) / "instagram.jpg"
    image_card.make_card(job["brand"], pack["image_headline"], pack["image_subline"], pack["image_cta"], path)
    return str(path)


def _draft(job_id: str) -> None:
    job = store.get_job(job_id)
    pack = writer.write_pack(job["brand"], job["prompt"], job["options"])
    image_path = _make_image(job, pack)
    store.update_job(job_id, pack=pack, image_path=image_path)
    _after_writing(store.get_job(job_id))


def _after_writing(job: Dict[str, Any]) -> None:
    if job["options"].get("video_mode") == "heygen":
        _start_heygen(job)
    else:
        store.update_job(job["id"], status="needs_video",
                         step="Make the clips in Meta AI with the scene prompts, then upload the finished video.")
        notify(job, "Your Meta AI prompts are ready", "Your script and Meta AI scene prompts are ready.")


def _start_heygen(job: Dict[str, Any]) -> None:
    choice = heygen_choice(job["brand"])
    vid = heygen.start_video(
        script=job["pack"]["video_script"], avatar=choice["avatar"], voice_id=choice["voice_id"],
        vertical=job["options"].get("format", "short") == "short",
        background=config.BRANDS[job["brand"]]["colors"]["bg"], title=job["pack"]["youtube_title"],
    )
    store.update_job(job["id"], status="rendering", heygen_video_id=vid, video_path=None,
                     step="HeyGen is making your video (usually 3–15 minutes)…", error=None)


def check_rendering(job_id: str) -> None:
    key = f"render:{job_id}"
    with _busy_lock:
        if key in _busy:
            return
        _busy.add(key)
    try:
        _check_rendering(job_id)
    finally:
        with _busy_lock:
            _busy.discard(key)


def _check_rendering(job_id: str) -> None:
    job = store.get_job(job_id)
    if not job or job["status"] != "rendering" or not job["heygen_video_id"]:
        return
    st = heygen.check_video(job["heygen_video_id"])
    if st["status"] == "completed" and st["url"]:
        path = heygen.download(st["url"], job_dir(job_id) / "video.mp4")
        store.update_job(job_id, status="review", video_path=str(path), step="Ready for your review.")
        notify(store.get_job(job_id), "Your video is ready to approve", "Your video and posts are ready. Nothing posts until you approve.")
    elif st["status"] == "failed":
        store.update_job(job_id, status="error", error=f"HeyGen failed: {st['error']}", step="")


def save_uploaded_video(job_id: str, src_file, filename: str) -> None:
    suffix = Path(filename or "").suffix.lower()
    suffix = suffix if suffix in (".mp4", ".mov", ".m4v", ".webm") else ".mp4"
    for old in job_dir(job_id).glob("video.*"):
        old.unlink()
    dest = job_dir(job_id) / f"video{suffix}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as out:
        shutil.copyfileobj(src_file, out, length=1 << 20)
    store.update_job(job_id, video_path=str(dest), status="review", step="Ready for your review.", error=None)


def revise(job_id: str, feedback: str, remake_video: bool) -> None:
    def work():
        job = store.get_job(job_id)
        pack = writer.revise_pack(job["brand"], job["prompt"], job["options"], job["pack"], feedback)
        image_path = _make_image(job, pack)
        store.update_job(job_id, pack=pack, image_path=image_path)
        job = store.get_job(job_id)
        if remake_video and job["options"].get("video_mode") == "heygen":
            _start_heygen(job)
        elif remake_video:
            store.update_job(job_id, status="needs_video", video_path=None,
                             step="Script updated. Make the new clips in Meta AI and upload the video.")
        else:
            store.update_job(job_id, status="review" if job["video_path"] else job["status"],
                             step="Updated. Ready for your review.")
    store.update_job(job_id, status="drafting", step="Rewriting with your changes…", error=None)
    _run_once(f"revise:{job_id}", work)


def edit_pack(job_id: str, changes: Dict[str, Any]) -> None:
    job = store.get_job(job_id)
    pack = dict(job["pack"])
    image_changed = False
    for key, val in changes.items():
        if key in pack:
            image_changed |= key.startswith("image_") and pack[key] != val
            pack[key] = val
    store.update_job(job_id, pack=pack)
    if image_changed:
        store.update_job(job_id, image_path=_make_image(store.get_job(job_id), pack))


def retry_draft(job_id: str) -> None:
    job = store.get_job(job_id)
    if not job["pack"]:
        store.update_job(job_id, status="drafting", step="Writing your script and posts…", error=None)
        _run_once(f"draft:{job_id}", _draft, job_id)
    else:
        store.update_job(job_id, error=None)
        _run_once(f"draft:{job_id}", _after_writing, job)


# ---- posting ----------------------------------------------------------------

def approve(job_id: str, platforms: List[str], youtube_url: str = "") -> None:
    job = store.get_job(job_id)
    opts = dict(job["options"])
    opts["platforms"] = [p for p in platforms if p in config.PLATFORMS]
    store.update_job(job_id, options=opts, status="posting", step="Posting…", error=None,
                     youtube_url=youtube_url.strip() or job.get("youtube_url"))
    _run_once(f"post:{job_id}", _post, job_id)


def _post(job_id: str) -> None:
    job = store.get_job(job_id)
    pack, brand = job["pack"], job["brand"]
    wanted = job["options"].get("platforms", [])
    results = job["results"]
    yt_url = job.get("youtube_url") or (results.get("youtube") or {}).get("url")

    def done(p):
        return (results.get(p) or {}).get("ok")

    # 1) YouTube first, so the other posts can link to it.
    if "youtube" in wanted and not done("youtube"):
        if config.YOUTUBE_MODE == "api":
            store.update_job(job_id, step="Uploading to YouTube…")
            try:
                res = youtube.upload(brand, Path(job["video_path"]), pack["youtube_title"],
                                     pack["youtube_description"], pack["youtube_tags"])
                yt_url = res["url"]
                note = ""
                if res.get("privacy") == "private" and config.YOUTUBE_PRIVACY != "private":
                    note = "YouTube set it to Private — your Google API audit isn't approved yet."
                store.set_result(job_id, "youtube", {"ok": True, "url": yt_url, "note": note})
                store.update_job(job_id, youtube_url=yt_url)
            except Exception as exc:
                store.set_result(job_id, "youtube", {"ok": False, "error": str(exc)[:500]})
        elif yt_url:
            store.set_result(job_id, "youtube", {"ok": True, "url": yt_url, "note": "Uploaded by you"})
        else:
            store.set_result(job_id, "youtube", {"ok": False, "error": "Upload the video in the YouTube app, paste the link, then tap Retry."})

    # 2) LinkedIn
    if "linkedin" in wanted and not done("linkedin"):
        store.update_job(job_id, step="Posting to LinkedIn…")
        try:
            res = linkedin.post(writer.linkedin_text(pack, yt_url), Path(job["image_path"]), pack["image_headline"])
            store.set_result(job_id, "linkedin", {"ok": True, **res})
        except Exception as exc:
            store.set_result(job_id, "linkedin", {"ok": False, "error": str(exc)[:500]})

    # 3) Instagram
    if "instagram" in wanted and not done("instagram"):
        store.update_job(job_id, step="Posting to Instagram…")
        try:
            res = instagram.publish_image(brand, public_image_url(job_id), writer.instagram_caption_text(pack))
            store.set_result(job_id, "instagram", {"ok": True, **res})
        except Exception as exc:
            store.set_result(job_id, "instagram", {"ok": False, "error": str(exc)[:500]})

    job = store.get_job(job_id)
    oks = [bool((job["results"].get(p) or {}).get("ok")) for p in wanted]
    status = "done" if all(oks) else "partial"
    store.update_job(job_id, status=status, step="All posted ✓" if status == "done" else "Some posts need attention.")
    if status == "partial":
        notify(job, "Some posts need attention", "One or more platforms didn't post. Open the job to see why and tap Retry.")


# ---- background watcher -----------------------------------------------------

def _watch() -> None:
    while True:
        try:
            for job in store.list_jobs(50):
                if job["status"] == "rendering":
                    try:
                        check_rendering(job["id"])
                    except Exception as exc:
                        logger.warning("HeyGen check failed for %s: %s", job["id"], exc)
        except Exception:
            logger.exception("Assistant watcher loop error")
        time.sleep(30)


_watcher_started = False


def start_watcher() -> None:
    global _watcher_started
    if not _watcher_started:
        _watcher_started = True
        threading.Thread(target=_watch, daemon=True).start()
