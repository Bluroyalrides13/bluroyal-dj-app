"""
Small SQLite store for jobs, account logins and settings.

Kept separate from the site's main database on purpose: nothing here can
affect leads, the vault or Blu Royal Rides.
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from src.content_assistant import config

_lock = threading.Lock()


def _conn() -> sqlite3.Connection:
    config.ensure_dirs()
    conn = sqlite3.connect(str(config.DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    with _lock, _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                created REAL,
                updated REAL,
                brand TEXT,
                prompt TEXT,
                options TEXT,
                status TEXT,
                step TEXT,
                pack TEXT,
                heygen_video_id TEXT,
                video_path TEXT,
                image_path TEXT,
                youtube_url TEXT,
                results TEXT,
                error TEXT
            );
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated REAL
            );
            """
        )


# ---- key/value (logins + settings) ------------------------------------------

def kv_get(key: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else None


def kv_set(key: str, value: Dict[str, Any]) -> None:
    with _lock, _conn() as c:
        c.execute(
            "INSERT INTO kv(key,value,updated) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=excluded.updated",
            (key, json.dumps(value), time.time()),
        )


def kv_delete(key: str) -> None:
    with _lock, _conn() as c:
        c.execute("DELETE FROM kv WHERE key=?", (key,))


def token(key: str, env_fallback: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Saved login for `key`, else values from Render env vars, else None."""
    saved = kv_get(f"token:{key}")
    if saved:
        return saved
    if env_fallback:
        vals = {k: os.getenv(v, "").strip() for k, v in env_fallback.items()}
        if all(vals.values()):
            vals["source"] = "env"
            return vals
    return None


def save_token(key: str, value: Dict[str, Any]) -> None:
    value = dict(value)
    value["saved_at"] = time.time()
    kv_set(f"token:{key}", value)


# ---- jobs -------------------------------------------------------------------

_JSON_COLS = ("options", "pack", "results")


def _row_to_job(row: sqlite3.Row) -> Dict[str, Any]:
    job = dict(row)
    for col in _JSON_COLS:
        job[col] = json.loads(job[col]) if job.get(col) else {}
    return job


def create_job(brand: str, prompt: str, options: Dict[str, Any]) -> str:
    job_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    now = time.time()
    with _lock, _conn() as c:
        c.execute(
            "INSERT INTO jobs(id,created,updated,brand,prompt,options,status,step,results) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (job_id, now, now, brand, prompt, json.dumps(options), "drafting",
             "Writing your script and posts…", json.dumps({})),
        )
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return _row_to_job(row) if row else None


def list_jobs(limit: int = 30) -> List[Dict[str, Any]]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM jobs ORDER BY created DESC LIMIT ?", (limit,)).fetchall()
    return [_row_to_job(r) for r in rows]


def update_job(job_id: str, **fields: Any) -> None:
    if not fields:
        return
    for col in _JSON_COLS:
        if col in fields and not isinstance(fields[col], str):
            fields[col] = json.dumps(fields[col])
    fields["updated"] = time.time()
    cols = ", ".join(f"{k}=?" for k in fields)
    with _lock, _conn() as c:
        c.execute(f"UPDATE jobs SET {cols} WHERE id=?", (*fields.values(), job_id))


def set_result(job_id: str, platform: str, result: Dict[str, Any]) -> None:
    with _lock, _conn() as c:
        row = c.execute("SELECT results FROM jobs WHERE id=?", (job_id,)).fetchone()
        results = json.loads(row["results"]) if row and row["results"] else {}
        results[platform] = result
        c.execute("UPDATE jobs SET results=?, updated=? WHERE id=?",
                  (json.dumps(results), time.time(), job_id))


def delete_job(job_id: str) -> None:
    with _lock, _conn() as c:
        c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
