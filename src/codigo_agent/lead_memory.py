"""
Lead Memory (Phase 2, MVP)
--------------------------
Tracks a profile per lead, keyed by their ManyChat subscriber_id (or any
stable identifier ManyChat passes through — IG handle also works).

This is a JSON-file store, intentionally simple: fine for the first weeks
of traffic. Swap for a real DatabaseManager table (same pattern as
src/models/database.py) once volume justifies it — the LeadMemory
interface below (get/update) won't need to change if you do.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "codigo_leads.json"
_LOCK = threading.Lock()

_DEFAULT_PROFILE = {
    "name": None,
    "ig_handle": None,
    "goal": None,
    "blocker": None,
    "product_idea": None,
    "ideal_customer": None,
    "budget_signal": None,
    "objections": [],
    "recommended_product": None,
    "lead_status": "NEW",
    "last_message_at": None,
    "messages": [],  # short rolling history, trimmed in _trim()
}

_MAX_HISTORY = 20  # keep prompts small; trim older turns


class LeadMemory:
    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or _STORE_PATH
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write({})

    def _read(self) -> dict:
        with _LOCK:
            if not self.store_path.exists():
                return {}
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, data: dict) -> None:
        with _LOCK:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, lead_id: str) -> dict:
        data = self._read()
        return data.get(lead_id, dict(_DEFAULT_PROFILE))

    def append_message(self, lead_id: str, role: str, content: str) -> dict:
        """Add a turn to history and bump last_message_at. Returns updated profile."""
        data = self._read()
        profile = data.get(lead_id, dict(_DEFAULT_PROFILE))
        profile["messages"].append({"role": role, "content": content})
        profile["messages"] = profile["messages"][-_MAX_HISTORY:]
        profile["last_message_at"] = datetime.now(timezone.utc).isoformat()
        data[lead_id] = profile
        self._write(data)
        return profile

    def update_fields(self, lead_id: str, **fields) -> dict:
        """Update known profile fields (goal, blocker, lead_status, etc)."""
        data = self._read()
        profile = data.get(lead_id, dict(_DEFAULT_PROFILE))
        for key, value in fields.items():
            if key == "objections" and value:
                profile.setdefault("objections", [])
                if value not in profile["objections"]:
                    profile["objections"].append(value)
            else:
                profile[key] = value
        data[lead_id] = profile
        self._write(data)
        return profile

    def all_by_status(self, status: str) -> dict:
        """For the future follow-up job (Phase 6): leads stuck in a given status."""
        data = self._read()
        return {lid: p for lid, p in data.items() if p.get("lead_status") == status}

