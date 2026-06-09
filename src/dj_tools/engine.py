"""
DJ Business Engine
All five tools delivered to DJs who purchase the Blu Bloods platform:
  1. Event Timeline Builder
  2. Client Questionnaire Portal
  3. Setlist & Moment Organizer
  4. Booking & Pricing Calculator
  5. Instagram Content Pack Generator
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ─────────────────────────────────────────────
# 1. EVENT TIMELINE BUILDER
# ─────────────────────────────────────────────

CEREMONY_MOMENTS = [
    ("Guest Arrival / Pre-show Music", -60),
    ("Processional", 0),
    ("Ceremony", 10),
    ("Recessional", 35),
    ("Cocktail Hour", 45),
]

RECEPTION_MOMENTS = [
    ("Guest Arrival / Cocktail", 0),
    ("Bridal Party Grand Entrance", 60),
    ("Couple's First Dance", 65),
    ("Father-Daughter Dance", 70),
    ("Mother-Son Dance", 75),
    ("Welcome / Blessing", 80),
    ("Dinner Service", 85),
    ("Toasts & Speeches", 110),
    ("Cake Cutting", 130),
    ("Open Dancing", 145),
    ("Last Dance", 230),
    ("Send-off", 240),
]


def build_event_timeline(
    event_type: str,           # "wedding" | "corporate" | "birthday" | "club"
    start_time: str,           # "18:00"
    event_date: str,           # "2026-08-15"
    venue: str = "",
    notes: str = "",
) -> Dict:
    """Generate a minute-by-minute run-of-show timeline."""

    base_hour, base_minute = map(int, start_time.split(":"))
    base_dt = datetime.strptime(f"{event_date} {start_time}", "%Y-%m-%d %H:%M")

    reception_style_events = {
        "wedding",
        "same_sex_wedding_lgbtq",
        "corporate",
        "sweet_16",
        "birthday",
        "quinceanera",
        "general_party",
        "bar_mitzvah",
        "bat_mitzvah",
        "anniversary",
        "anniversay",
        "club",
    }
    moments = RECEPTION_MOMENTS if event_type in reception_style_events else CEREMONY_MOMENTS

    timeline = []
    for label, offset in moments:
        moment_dt = base_dt + timedelta(minutes=offset)
        timeline.append({
            "time": moment_dt.strftime("%I:%M %p"),
            "moment": label,
            "notes": "",
            "song": "",
        })

    return {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_date": event_date,
        "start_time": start_time,
        "venue": venue,
        "notes": notes,
        "timeline": timeline,
        "created_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 2. CLIENT QUESTIONNAIRE PORTAL
# ─────────────────────────────────────────────

WEDDING_QUESTIONS = [
    {"id": "couple_names",       "label": "Couple's full names",             "type": "text"},
    {"id": "wedding_date",       "label": "Wedding date",                    "type": "date"},
    {"id": "venue_name",         "label": "Venue name & address",            "type": "text"},
    {"id": "guest_count",        "label": "Estimated guest count",           "type": "number"},
    {"id": "ceremony_start",     "label": "Ceremony start time",             "type": "time"},
    {"id": "reception_start",    "label": "Reception start time",            "type": "time"},
    {"id": "processional_song",  "label": "Processional song",               "type": "text"},
    {"id": "recessional_song",   "label": "Recessional song",                "type": "text"},
    {"id": "first_dance_song",   "label": "First dance song & artist",       "type": "text"},
    {"id": "father_daughter",    "label": "Father-daughter dance song",      "type": "text"},
    {"id": "mother_son",         "label": "Mother-son dance song",           "type": "text"},
    {"id": "cake_cutting_song",  "label": "Cake cutting song",               "type": "text"},
    {"id": "last_dance_song",    "label": "Last dance song",                 "type": "text"},
    {"id": "must_play",          "label": "Must-play songs (list them)",     "type": "textarea"},
    {"id": "do_not_play",        "label": "Do-NOT-play songs or genres",     "type": "textarea"},
    {"id": "vibe",               "label": "Describe the vibe you want",      "type": "textarea"},
    {"id": "announcer_name",     "label": "Who is announcing the couple?",   "type": "text"},
    {"id": "special_requests",   "label": "Anything else the DJ should know","type": "textarea"},
]

CORPORATE_QUESTIONS = [
    {"id": "company_name",    "label": "Company / event name",           "type": "text"},
    {"id": "event_date",      "label": "Event date",                     "type": "date"},
    {"id": "venue_name",      "label": "Venue name & address",           "type": "text"},
    {"id": "guest_count",     "label": "Estimated guest count",          "type": "number"},
    {"id": "start_time",      "label": "Event start time",               "type": "time"},
    {"id": "end_time",        "label": "Event end time",                 "type": "time"},
    {"id": "vibe",            "label": "Desired vibe / energy",          "type": "textarea"},
    {"id": "must_play",       "label": "Must-play tracks",               "type": "textarea"},
    {"id": "do_not_play",     "label": "Genres or songs to avoid",       "type": "textarea"},
    {"id": "special_requests","label": "Special announcements or moments","type": "textarea"},
]

PARTY_QUESTIONS = [
    {"id": "client_name",      "label": "Client / host full name",          "type": "text"},
    {"id": "event_date",       "label": "Event date",                        "type": "date"},
    {"id": "venue_name",       "label": "Venue name & address",              "type": "text"},
    {"id": "guest_count",      "label": "Estimated guest count",             "type": "number"},
    {"id": "start_time",       "label": "Event start time",                  "type": "time"},
    {"id": "end_time",         "label": "Event end time",                    "type": "time"},
    {"id": "grand_intro_song", "label": "Grand intro song (if needed)",      "type": "text"},
    {"id": "special_moments",  "label": "Special moments to announce",        "type": "textarea"},
    {"id": "must_play",        "label": "Must-play songs",                    "type": "textarea"},
    {"id": "do_not_play",      "label": "Do-NOT-play songs or genres",       "type": "textarea"},
    {"id": "vibe",             "label": "Desired vibe / energy",             "type": "textarea"},
    {"id": "special_requests", "label": "Anything else the DJ should know",  "type": "textarea"},
]

QUESTIONNAIRE_BY_EVENT = {
    "wedding": WEDDING_QUESTIONS,
    "same_sex_wedding_lgbtq": WEDDING_QUESTIONS,
    "corporate": CORPORATE_QUESTIONS,
    "sweet_16": PARTY_QUESTIONS,
    "birthday": PARTY_QUESTIONS,
    "quinceanera": PARTY_QUESTIONS,
    "general_party": PARTY_QUESTIONS,
    "bar_mitzvah": PARTY_QUESTIONS,
    "bat_mitzvah": PARTY_QUESTIONS,
    "anniversary": PARTY_QUESTIONS,
    "anniversay": PARTY_QUESTIONS,
}


def get_questionnaire_template(event_type: str) -> Dict:
    """Return the right set of questions for the event type."""
    questions = QUESTIONNAIRE_BY_EVENT.get(event_type, PARTY_QUESTIONS)
    return {
        "event_type": event_type,
        "questions": questions,
        "portal_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
    }


def save_questionnaire_answers(portal_id: str, event_type: str, answers: Dict) -> Dict:
    """Package the answers into a structured event brief."""
    return {
        "portal_id": portal_id,
        "event_type": event_type,
        "answers": answers,
        "brief_id": str(uuid.uuid4()),
        "submitted_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 3. SETLIST & MOMENT ORGANIZER
# ─────────────────────────────────────────────

DEFAULT_MOMENTS = [
    "Pre-show",
    "Processional",
    "Cocktail Hour",
    "Dinner",
    "First Dance",
    "Party / Open Floor",
    "Last Song",
]


def build_setlist(
    moments: Optional[List[str]] = None,
    songs: Optional[List[Dict]] = None,
) -> Dict:
    """
    Organize songs into event moments.
    songs = [{"title": "...", "artist": "...", "moment": "First Dance", "notes": ""}]
    """
    moment_list = moments or DEFAULT_MOMENTS
    organized: Dict[str, List] = {m: [] for m in moment_list}

    for song in (songs or []):
        moment = song.get("moment", "Party / Open Floor")
        if moment not in organized:
            organized[moment] = []
        organized[moment].append({
            "title": song.get("title", ""),
            "artist": song.get("artist", ""),
            "notes": song.get("notes", ""),
            "id": str(uuid.uuid4()),
        })

    return {
        "setlist_id": str(uuid.uuid4()),
        "moments": moment_list,
        "songs_by_moment": organized,
        "total_songs": sum(len(v) for v in organized.values()),
        "created_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 4. BOOKING & PRICING CALCULATOR
# ─────────────────────────────────────────────

BASE_RATES: Dict[str, float] = {
    "wedding":   1200.0,
    "same_sex_wedding_lgbtq": 1200.0,
    "corporate": 900.0,
    "sweet_16": 700.0,
    "birthday":  600.0,
    "quinceanera": 850.0,
    "general_party": 600.0,
    "bar_mitzvah": 950.0,
    "bat_mitzvah": 950.0,
    "anniversary": 650.0,
    "anniversay": 650.0,
    "club":      500.0,
}

EXTRAS: Dict[str, float] = {
    "ceremony_add_on":    300.0,
    "extra_hour":         150.0,
    "travel_fee_per_hr":   50.0,
    "lighting_package":   400.0,
    "photo_booth":        500.0,
    "mc_services":        200.0,
}


def calculate_booking_price(
    event_type: str,
    hours: float,
    add_ons: Optional[List[str]] = None,
    travel_hours: float = 0.0,
    discount_percent: float = 0.0,
) -> Dict:
    """Return a full price breakdown for a DJ booking."""
    base = BASE_RATES.get(event_type, 600.0)

    # Extra hours beyond 4
    standard_hours = 4.0
    extra_hours = max(0.0, hours - standard_hours)
    extra_hour_cost = extra_hours * EXTRAS["extra_hour"]

    # Add-ons
    add_on_total = 0.0
    add_on_breakdown = []
    for add_on in (add_ons or []):
        cost = EXTRAS.get(add_on, 0.0)
        add_on_total += cost
        add_on_breakdown.append({"item": add_on, "cost": cost})

    # Travel
    travel_cost = travel_hours * EXTRAS["travel_fee_per_hr"]

    subtotal = base + extra_hour_cost + add_on_total + travel_cost
    discount_amount = subtotal * (discount_percent / 100.0)
    total = subtotal - discount_amount

    return {
        "event_type": event_type,
        "hours": hours,
        "base_rate": base,
        "extra_hours": extra_hours,
        "extra_hour_cost": round(extra_hour_cost, 2),
        "add_ons": add_on_breakdown,
        "add_on_total": round(add_on_total, 2),
        "travel_cost": round(travel_cost, 2),
        "subtotal": round(subtotal, 2),
        "discount_percent": discount_percent,
        "discount_amount": round(discount_amount, 2),
        "total": round(total, 2),
        "currency": "USD",
        "quote_id": str(uuid.uuid4()),
        "valid_until": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }


# ─────────────────────────────────────────────
# 5. INSTAGRAM CONTENT PACK GENERATOR
# ─────────────────────────────────────────────

CONTENT_HOOKS = {
    "authority": [
        "Most DJs make this one mistake that costs them every high-end wedding booking.",
        "Here is the exact timeline I use for every 5-star wedding reception.",
        "3 songs that always kill the dance floor — and the one that clears it.",
    ],
    "social_proof": [
        "Just wrapped another sold-out event. Here is what made it run smooth.",
        "Client said it was the best wedding they had ever attended. Here is what I did differently.",
        "Booked 6 events this month from Instagram alone. Here is the system I used.",
    ],
    "value": [
        "Save this — the complete DJ run-of-show template for a wedding reception.",
        "Free checklist: everything you need to confirm with a client 48 hours before an event.",
        "The pricing formula that helped me stop undercharging for corporate gigs.",
    ],
    "offer": [
        "I built a tool that handles client questionnaires, timelines, and pricing for you. Link in bio.",
        "Everything inside the Blu Bloods Resource Vault — now available. Link in bio.",
        "DM me VIP if you want a done-with-you buildout for your DJ booking system.",
    ],
}

CAPTION_TEMPLATES = [
    """{hook}

Here is what I have learned after {years} years behind the decks:

The DJs who stay booked year-round are not always the most technical. They run a better system.

They show up prepared. They communicate better. They deliver an experience, not just music.

That is what the Blu Bloods platform is built to give you.

{cta}

#DJLife #WeddingDJ #EventDJ #DJBusiness #BluBloods""",

    """{hook}

No one talks about the business side of DJing.

Getting leads. Converting them. Running the event without stress. Getting paid what you are worth.

I built a platform that handles all of it.

{cta}

#DJBusiness #WeddingDJ #DJTips #BluBloods""",

    """{hook}

Drop a 🎵 below if you want the full breakdown.

{cta}

#DJLife #EventPlanning #WeddingDJ #BluBloods #DJTips""",
]

DM_SCRIPTS = {
    "warm_lead": (
        "Hey [Name] — saw you reached out about the Blu Bloods platform. "
        "Quick question before we go further: what is the one part of your DJ business "
        "that takes up the most time right now? "
        "I want to make sure what I have built actually solves the right problem for you."
    ),
    "cold_outreach": (
        "Hey [Name] — I noticed you are a DJ in [city]. "
        "I built a tool specifically for DJs that handles client questionnaires, "
        "event timelines, and pricing quotes automatically. "
        "Would it be useful if I sent you a quick look at how it works?"
    ),
    "follow_up": (
        "Hey [Name] — just following up from earlier. "
        "I know you are busy. If the timing is not right, no worries. "
        "But if you are still looking for a way to run your events more smoothly and "
        "charge more confidently, I am here. "
        "Just reply YES and I will send you the details."
    ),
    "close": (
        "Based on everything you told me, the [OFFER NAME] is the right fit. "
        "It gives you [KEY BENEFIT] without [MAIN PAIN]. "
        "Investment is [PRICE]. "
        "I only take [X] new clients per month so I can give each one proper attention. "
        "Are you ready to move forward?"
    ),
}


def generate_content_pack(
    years_experience: int = 5,
    specialty: str = "wedding",
    cta: str = "Link in bio to apply.",
) -> Dict:
    """Generate a 30-day Instagram content plan with captions and DM scripts."""

    posts = []
    categories = list(CONTENT_HOOKS.keys())

    for day in range(1, 31):
        category = categories[(day - 1) % len(categories)]
        hooks = CONTENT_HOOKS[category]
        hook = hooks[(day - 1) % len(hooks)]
        template = CAPTION_TEMPLATES[(day - 1) % len(CAPTION_TEMPLATES)]
        caption = template.format(hook=hook, years=years_experience, cta=cta)

        posts.append({
            "day": day,
            "category": category,
            "hook": hook,
            "caption": caption,
            "format": "carousel" if day % 3 == 0 else ("reel" if day % 2 == 0 else "static"),
        })

    return {
        "pack_id": str(uuid.uuid4()),
        "specialty": specialty,
        "years_experience": years_experience,
        "cta": cta,
        "posts": posts,
        "dm_scripts": DM_SCRIPTS,
        "bio_suggestions": [
            f"DJ & event specialist | {specialty.title()} expert | Helping DJs book premium events | Link below",
            f"Booked {years_experience}+ years | {specialty.title()} DJ | Resources for DJs who want more | Apply below",
            f"DJ Blu Bloods | Premium event experiences | DM for booking | Resources for DJs in bio",
        ],
        "created_at": datetime.utcnow().isoformat(),
    }
