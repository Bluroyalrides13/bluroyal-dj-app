"""
The writer: turns your one-line prompt into everything each platform needs,
in one Claude call with a fixed output shape (so nothing comes back missing).
"""

import json
import logging
from typing import Any, Dict, Optional

from anthropic import Anthropic

from src.content_assistant import config

logger = logging.getLogger(__name__)

YOUTUBE_LINK_PLACEHOLDER = "{YOUTUBE_LINK}"

_PACK_TOOL = {
    "name": "save_content_pack",
    "description": "Save the finished content pack for every platform.",
    "input_schema": {
        "type": "object",
        "properties": {
            "hook": {"type": "string", "description": "The opening line, spoken in the first 2 seconds."},
            "video_script": {
                "type": "string",
                "description": "Full spoken narration, start to finish, no stage directions, no emojis.",
            },
            "meta_ai_scenes": {
                "type": "array",
                "description": "Scene-by-scene plan for making the video by hand in Meta AI. One entry per clip.",
                "items": {
                    "type": "object",
                    "properties": {
                        "scene": {"type": "integer"},
                        "prompt": {
                            "type": "string",
                            "description": "Copy-paste prompt for Meta AI, in English, visual only: subject, setting, camera move, lighting, style, vertical 9:16.",
                        },
                        "voiceover": {"type": "string", "description": "The narration line that plays over this clip."},
                    },
                    "required": ["scene", "prompt", "voiceover"],
                },
            },
            "youtube_title": {"type": "string", "description": "Max 90 characters. Shorts end with #Shorts."},
            "youtube_description": {"type": "string"},
            "youtube_tags": {"type": "array", "items": {"type": "string"}},
            "linkedin_post": {
                "type": "string",
                "description": f"Professional LinkedIn post promoting the video. Must contain {YOUTUBE_LINK_PLACEHOLDER} exactly once where the video link goes.",
            },
            "instagram_caption": {"type": "string", "description": "Caption without hashtags."},
            "instagram_hashtags": {"type": "array", "items": {"type": "string"}},
            "image_headline": {"type": "string", "description": "Max 7 words, for the Instagram graphic."},
            "image_subline": {"type": "string", "description": "Max 14 words, for the Instagram graphic."},
            "image_cta": {"type": "string", "description": "Max 5 words, for the bottom of the graphic."},
        },
        "required": [
            "hook", "video_script", "meta_ai_scenes", "youtube_title", "youtube_description",
            "youtube_tags", "linkedin_post", "instagram_caption", "instagram_hashtags",
            "image_headline", "image_subline", "image_cta",
        ],
    },
}

_LANG = {
    "es": "Write everything in Spanish (neutral Latin American), except the Meta AI scene prompts, which stay in English.",
    "en": "Write everything in English.",
    "bilingual": (
        "Video script, YouTube title and Instagram graphic in Spanish. YouTube description, "
        "LinkedIn post and Instagram caption in Spanish first, then a short English version underneath. "
        "Meta AI scene prompts in English."
    ),
}


def _system(brand_key: str, opts: Dict[str, Any]) -> str:
    brand = config.BRANDS[brand_key]
    fmt = opts.get("format", "short")
    seconds = int(opts.get("seconds") or (50 if fmt == "short" else 300))
    words = int(seconds * 2.4)
    shape = (
        f"YouTube Short: vertical 9:16, about {seconds} seconds (~{words} spoken words). Title ends with #Shorts."
        if fmt == "short"
        else f"Regular horizontal YouTube video, about {seconds // 60} minutes (~{words} spoken words)."
    )
    mode = opts.get("video_mode", brand["default_video_mode"])
    who = (
        "The script will be read by Cindy's HeyGen avatar speaking straight to camera."
        if mode == "heygen"
        else "The video is faceless: Cindy builds it clip by clip in Meta AI with the scene prompts, with narration over the top."
    )
    site = f" Mention {brand['website']} where it fits." if brand["website"] else ""
    keyword = (
        f" Instagram call to action: comment the word {brand['instagram_keyword']}."
        if brand["instagram_keyword"] else ""
    )
    return (
        f"You are the content producer for {brand['name']}.\n{brand['voice']}\n\n"
        f"FORMAT: {shape} {who}\n"
        f"LANGUAGE: {_LANG.get(opts.get('language', brand['default_language']), _LANG['es'])}\n\n"
        "RULES:\n"
        "- The hook must stop the scroll in the first 2 seconds.\n"
        "- One idea per video. Short sentences that sound natural out loud.\n"
        "- Meta AI scenes: 5 to 8 clips, each a self-contained visual prompt (no text on screen, "
        "no real living people, no logos), consistent style across clips.\n"
        "- YouTube description: 2 short paragraphs, a call to action, then 3 to 5 hashtags.\n"
        "- LinkedIn post: 80 to 180 words, value first, line breaks for readability, max 3 hashtags, "
        f"includes {YOUTUBE_LINK_PLACEHOLDER} once.\n"
        "- Instagram caption: hook line, 2 to 4 short lines, call to action, say the full video is on "
        f"YouTube (link in bio).{keyword}\n"
        "- 8 to 15 Instagram hashtags, mixing broad and niche, no # symbol needed.\n"
        f"- Never promise income results or make medical/legal claims.{site}\n"
        "Return the result by calling the save_content_pack tool (always call it, never answer in plain text)."
    )


def _call(system: str, user: str) -> Dict[str, Any]:
    """Ask Claude for the pack. Some models refuse a forced tool call, so we
    let it choose the tool, and fall back to plain JSON if it answers in text."""
    client = Anthropic()
    attempts = [
        {"tool_choice": {"type": "auto"}},
        {"tool_choice": {"type": "auto"}, "nudge": True},
    ]
    last_text = ""
    for attempt in attempts:
        content = user
        if attempt.get("nudge"):
            content += ("\n\nIMPORTANT: respond ONLY by calling the save_content_pack tool. "
                        "If you cannot call tools, reply with a single JSON object with exactly its fields.")
        resp = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=8000,
            system=system,
            tools=[_PACK_TOOL],
            tool_choice=attempt["tool_choice"],
            messages=[{"role": "user", "content": content}],
        )
        texts = []
        for block in resp.content:
            if getattr(block, "type", "") == "tool_use" and block.name == "save_content_pack":
                return _clean(dict(block.input))
            if getattr(block, "type", "") == "text":
                texts.append(block.text)
        last_text = "\n".join(texts)
        parsed = _json_from_text(last_text)
        if parsed and "video_script" in parsed:
            return _clean(parsed)
    raise RuntimeError(f"The writer didn't return a content pack. Tap Try again. ({last_text[:200]})")


def _json_from_text(text: str) -> Optional[Dict[str, Any]]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _clean(pack: Dict[str, Any]) -> Dict[str, Any]:
    pack["youtube_title"] = pack.get("youtube_title", "")[:100]
    pack["youtube_tags"] = [t.lstrip("#").strip() for t in pack.get("youtube_tags", []) if t.strip()][:20]
    pack["instagram_hashtags"] = [
        "#" + t.lstrip("#").strip().replace(" ", "") for t in pack.get("instagram_hashtags", []) if t.strip()
    ][:20]
    if YOUTUBE_LINK_PLACEHOLDER not in pack.get("linkedin_post", ""):
        pack["linkedin_post"] = pack.get("linkedin_post", "").rstrip() + f"\n\n▶ {YOUTUBE_LINK_PLACEHOLDER}"
    return pack


def write_pack(brand_key: str, prompt: str, opts: Dict[str, Any]) -> Dict[str, Any]:
    return _call(_system(brand_key, opts), f"Today's video idea from Cindy:\n{prompt}")


def revise_pack(brand_key: str, prompt: str, opts: Dict[str, Any],
                current: Dict[str, Any], feedback: str) -> Dict[str, Any]:
    user = (
        f"Original idea from Cindy:\n{prompt}\n\n"
        f"Current draft (JSON):\n{json.dumps(current, ensure_ascii=False)}\n\n"
        f"Cindy's changes:\n{feedback}\n\n"
        "Apply her changes. Keep everything she didn't mention as close to the draft as possible."
    )
    return _call(_system(brand_key, opts), user)


def instagram_caption_text(pack: Dict[str, Any]) -> str:
    tags = " ".join(pack.get("instagram_hashtags", []))
    return f"{pack.get('instagram_caption', '').strip()}\n\n{tags}".strip()[:2200]


def linkedin_text(pack: Dict[str, Any], youtube_url: Optional[str]) -> str:
    text = pack.get("linkedin_post", "")
    if youtube_url:
        return text.replace(YOUTUBE_LINK_PLACEHOLDER, youtube_url)
    # No link yet: drop the placeholder and any line left with just an arrow.
    lines = [ln.replace(YOUTUBE_LINK_PLACEHOLDER, "").rstrip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln.strip() not in ("▶", "👉", "→")).strip()
