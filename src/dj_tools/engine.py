"""
DJ Business Engine
All five tools delivered to DJs who purchase the Blu Bloods platform:
  1. Event Timeline Builder
  2. Client Questionnaire Portal
  3. Setlist & Moment Organizer
  4. Booking & Pricing Calculator
  5. Instagram Content Pack Generator
    6. DJ Profile Setup
    7. Lead Management (CRM)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import threading
from pathlib import Path

from config.settings import Settings
from src.models.database import DatabaseManager


# ─────────────────────────────────────────────
# 1. EVENT TIMELINE BUILDER
# ─────────────────────────────────────────────
# DATA PERSISTENCE HELPERS
# ─────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
LEADS_FILE = DATA_DIR / "crm_leads.json"
BRIEFS_FILE = DATA_DIR / "questionnaire_briefs.json"
QUOTES_FILE = DATA_DIR / "pricing_quotes.json"
AGREEMENTS_FILE = DATA_DIR / "service_agreements.json"
SALES_TRACKER_FILE = DATA_DIR / "sales_tracker.json"

_json_lock = threading.Lock()


def _load_json(filepath: Path) -> List[Dict]:
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _append_record(filepath: Path, record: Dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _json_lock:
        records = _load_json(filepath)
        records.append(record)
        with open(filepath, "w") as f:
            json.dump(records, f, indent=2)


def _save_json(filepath: Path, payload: Dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _json_lock:
        with open(filepath, "w") as f:
            json.dump(payload, f, indent=2)


def _load_json_object(filepath: Path) -> Dict:
    if not filepath.exists():
        return {}
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


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

WEDDING_MOMENTS = RECEPTION_MOMENTS

SWEET_16_MOMENTS = [
    ("Guest Arrival", 0),
    ("Candle Lighting Ceremony", 15),
    ("First Dance", 45),
    ("Cake Cutting", 60),
    ("Special Dances", 75),
    ("Open Dancing", 90),
    ("Speeches / Toasts", 120),
    ("Last Dance", 180),
]

BIRTHDAY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Grand Entrance / Intro", 15),
    ("Cake Cutting", 30),
    ("Special Dances", 50),
    ("Open Dancing", 70),
    ("Speeches / Toasts", 120),
    ("Last Dance", 180),
]

QUINCEANERA_MOMENTS = [
    ("Ceremony / Guest Arrival", 0),
    ("Debutante Entrance", 15),
    ("Father-Daughter Dance", 30),
    ("First Dance", 40),
    ("Welcome / Blessing", 50),
    ("Dinner Service", 60),
    ("Cake Cutting", 90),
    ("Toasts & Speeches", 110),
    ("Open Dancing", 130),
    ("Last Dance", 240),
]

BAR_MITZVAH_MOMENTS = [
    ("Service Ends / Guest Arrival", 0),
    ("Grand Entrance / Introductions", 20),
    ("Hora (Optional)", 30),
    ("Dinner Service", 55),
    ("Blessings / Speeches", 85),
    ("Candle Lighting Ceremony (Optional)", 105),
    ("Video Montage (Optional)", 125),
    ("Games / Interactive Activities (Optional)", 140),
    ("Cake Cutting", 165),
    ("Open Dancing", 180),
    ("Final Dance / Send-off", 230),
]

BAT_MITZVAH_MOMENTS = [
    ("Service Ends / Guest Arrival", 0),
    ("Grand Entrance / Introductions", 20),
    ("Hora (Optional)", 30),
    ("Dinner Service", 55),
    ("Blessings / Speeches", 85),
    ("Candle Lighting Ceremony (Optional)", 105),
    ("Video Montage (Optional)", 125),
    ("Games / Interactive Activities (Optional)", 140),
    ("Cake Cutting", 165),
    ("Open Dancing", 180),
    ("Final Dance / Send-off", 230),
]

ANNIVERSARY_MOMENTS = [
    ("Guest Arrival / Cocktail", 0),
    ("Couple's Entrance", 20),
    ("First Dance (Re-dedication)", 30),
    ("Welcome / Remarks", 40),
    ("Dinner Service", 50),
    ("Toasts & Well-wishes", 90),
    ("Cake Cutting", 120),
    ("Open Dancing", 140),
    ("Last Dance / Send-off", 200),
]

CORPORATE_MOMENTS = [
    ("Guest Check-in", 0),
    ("Welcome / Remarks", 15),
    ("Networking / Cocktails", 30),
    ("Dinner Service", 60),
    ("Awards / Announcements", 120),
    ("Dancing", 150),
    ("Closing Remarks", 210),
]

CLUB_MOMENTS = [
    ("Setup / Soundcheck", -30),
    ("Doors Open / Early Crowd", 0),
    ("Warm-up Set", 30),
    ("Building Energy", 60),
    ("Peak Hour", 90),
    ("Sustained Peak", 120),
    ("Wind Down", 150),
    ("Closing Set", 180),
]

GRADUATION_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Graduate Grand Entrance", 20),
    ("Welcome / Introductions", 30),
    ("Awards & Accomplishments", 45),
    ("Slideshow / Video", 65),
    ("Family Speeches", 85),
    ("Open Dancing", 110),
    ("Final Song", 180),
]

BABY_SHOWER_MOMENTS = [
    ("Guest Arrival / Brunch", 0),
    ("Welcome", 20),
    ("Games", 40),
    ("Family Recognitions", 70),
    ("Gift Opening", 90),
    ("Cake / Dessert", 120),
    ("Closing Music", 150),
]

GENDER_REVEAL_MOMENTS = [
    ("Guest Arrival", 0),
    ("Family Welcome", 20),
    ("Games / Activities", 35),
    ("Photographer Setup", 55),
    ("Reveal Countdown", 70),
    ("Gender Reveal Moment", 75),
    ("Family Announcements", 85),
    ("Celebration Music", 95),
]

BRIDAL_SHOWER_MOMENTS = [
    ("Guest Arrival", 0),
    ("Bride Entrance", 20),
    ("Welcome Toast", 30),
    ("Games", 50),
    ("Gift Opening", 80),
    ("Toasts", 110),
    ("Closing Celebration", 140),
]

RETIREMENT_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Honoree Entrance", 20),
    ("Recognition Ceremony", 35),
    ("Awards Presentation", 55),
    ("Video Tribute", 75),
    ("Speeches", 95),
    ("Open Celebration", 120),
]

PROM_MOMENTS = [
    ("Student Arrival", 0),
    ("Grand Entrance", 20),
    ("Opening Dance", 35),
    ("Dance Set 1", 50),
    ("Prom Court Announcement", 90),
    ("King & Queen Crowning", 105),
    ("Dance Set 2", 120),
    ("Closing Song", 200),
]

HOMECOMING_DANCE_MOMENTS = [
    ("Student Arrival", 0),
    ("Theme Welcome", 20),
    ("Dance Set 1", 35),
    ("School Announcements", 70),
    ("Dance Contest", 90),
    ("Dance Set 2", 110),
    ("Closing Song", 180),
]

SCHOOL_DANCE_MOMENTS = [
    ("Student Arrival", 0),
    ("Welcome / Rules", 15),
    ("Dance Set 1", 30),
    ("Group Activity", 60),
    ("Dance Set 2", 80),
    ("Final Requests", 110),
    ("Closing Song", 130),
]

FUNDRAISER_CHARITY_GALA_MOMENTS = [
    ("Guest Check-in", 0),
    ("Welcome / Mission Intro", 20),
    ("Dinner Service", 40),
    ("Sponsor Recognition", 70),
    ("Silent Auction Close", 95),
    ("Live Auction", 110),
    ("Donation Announcements", 140),
    ("Closing Remarks", 170),
]

COMMUNITY_FESTIVAL_MOMENTS = [
    ("Opening Announcements", 0),
    ("Stage Set 1", 20),
    ("Vendor / Sponsor Mentions", 45),
    ("Entertainment Set 2", 70),
    ("Community Announcements", 95),
    ("Entertainment Set 3", 120),
    ("Closing Announcements", 160),
]

CAR_SHOW_MOMENTS = [
    ("Registration Opens", 0),
    ("Welcome / Rules", 20),
    ("Vehicle Announcements", 40),
    ("Judging Window", 70),
    ("Sponsor Recognition", 95),
    ("Trophy Presentation", 120),
    ("Closing Music", 145),
]

GRAND_OPENING_MOMENTS = [
    ("Guest Arrival", 0),
    ("Welcome", 20),
    ("VIP Introductions", 30),
    ("Ribbon Cutting", 45),
    ("Promotions & Giveaways", 60),
    ("Networking", 80),
    ("Closing Announcements", 120),
]

NETWORKING_EVENT_MOMENTS = [
    ("Guest Check-in", 0),
    ("Welcome", 15),
    ("Company Introductions", 25),
    ("Networking Block 1", 40),
    ("Sponsor Mentions", 75),
    ("Networking Block 2", 90),
    ("Closing Remarks", 130),
]

TRADE_SHOW_EXPO_MOMENTS = [
    ("Doors Open", 0),
    ("Exhibitor Announcements", 20),
    ("Presentation Block 1", 35),
    ("Sponsor Mentions", 60),
    ("Presentation Block 2", 85),
    ("Crowd Engagement Segment", 110),
    ("Closing Announcements", 150),
]

KARAOKE_NIGHT_MOMENTS = [
    ("Check-in / Signup", 0),
    ("Host Welcome", 15),
    ("Karaoke Round 1", 25),
    ("Karaoke Round 2", 65),
    ("Contest Finals", 110),
    ("Prize Awards", 135),
    ("Closing Songs", 155),
]

MUSIC_BINGO_SINGO_MOMENTS = [
    ("Welcome / Rules", 0),
    ("Round 1", 20),
    ("Round 2", 45),
    ("Prize Break", 70),
    ("Theme Round", 85),
    ("Final Round", 110),
    ("Winners Announcement", 130),
]

TRIVIA_NIGHT_MOMENTS = [
    ("Welcome / Team Setup", 0),
    ("Round 1", 20),
    ("Round 2", 45),
    ("Break", 70),
    ("Round 3", 85),
    ("Final Round", 110),
    ("Score + Prizes", 135),
]

CHRISTMAS_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Holiday Welcome", 20),
    ("Gift Exchange", 45),
    ("Santa Arrival (Optional)", 70),
    ("Dinner / Refreshments", 90),
    ("Holiday Dance Set", 120),
    ("Closing Song", 170),
]

NEW_YEARS_EVE_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Warm-up Set", 25),
    ("Main Dance Set", 60),
    ("Champagne Toast Prep", 115),
    ("Countdown", 120),
    ("Midnight Song", 121),
    ("Balloon Drop (Optional)", 122),
    ("After-Midnight Set", 130),
]

HALLOWEEN_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Costume Showcase", 20),
    ("Dance Set 1", 35),
    ("Costume Contest", 70),
    ("Prize Announcements", 90),
    ("Dance Set 2", 110),
    ("Closing Song", 150),
]

FOURTH_OF_JULY_EVENT_MOMENTS = [
    ("Guest Arrival", 0),
    ("Family Activities", 25),
    ("Patriotic Music Set", 50),
    ("Community Announcements", 75),
    ("Fireworks Prep", 105),
    ("Fireworks", 120),
    ("Closing Song", 130),
]

GENERAL_PARTY_MOMENTS = [
    ("Guest Arrival", 0),
    ("Grand Intro", 15),
    ("Games / Activities", 30),
    ("Dinner / Snacks", 60),
    ("Open Dancing", 90),
    ("Peak Hour", 120),
    ("Cake / Celebration", 150),
    ("Last Dance", 210),
]

# Timeline moments mapping
TIMELINE_BY_EVENT = {
    "wedding": WEDDING_MOMENTS,
    "same_sex_wedding_lgbtq": WEDDING_MOMENTS,
    "corporate": CORPORATE_MOMENTS,
    "sweet_16": SWEET_16_MOMENTS,
    "birthday": BIRTHDAY_MOMENTS,
    "quinceanera": QUINCEANERA_MOMENTS,
    "general_party": GENERAL_PARTY_MOMENTS,
    "bar_mitzvah": BAR_MITZVAH_MOMENTS,
    "bat_mitzvah": BAT_MITZVAH_MOMENTS,
    "anniversary": ANNIVERSARY_MOMENTS,
    "anniversay": ANNIVERSARY_MOMENTS,
    "club": CLUB_MOMENTS,
    "graduation_party": GRADUATION_PARTY_MOMENTS,
    "baby_shower": BABY_SHOWER_MOMENTS,
    "gender_reveal": GENDER_REVEAL_MOMENTS,
    "bridal_shower": BRIDAL_SHOWER_MOMENTS,
    "retirement_party": RETIREMENT_PARTY_MOMENTS,
    "prom": PROM_MOMENTS,
    "homecoming_dance": HOMECOMING_DANCE_MOMENTS,
    "school_dance": SCHOOL_DANCE_MOMENTS,
    "fundraiser_charity_gala": FUNDRAISER_CHARITY_GALA_MOMENTS,
    "community_festival": COMMUNITY_FESTIVAL_MOMENTS,
    "car_show": CAR_SHOW_MOMENTS,
    "grand_opening": GRAND_OPENING_MOMENTS,
    "networking_event": NETWORKING_EVENT_MOMENTS,
    "trade_show_expo": TRADE_SHOW_EXPO_MOMENTS,
    "karaoke_night": KARAOKE_NIGHT_MOMENTS,
    "music_bingo_singo": MUSIC_BINGO_SINGO_MOMENTS,
    "trivia_night": TRIVIA_NIGHT_MOMENTS,
    "christmas_party": CHRISTMAS_PARTY_MOMENTS,
    "new_years_eve_party": NEW_YEARS_EVE_PARTY_MOMENTS,
    "halloween_party": HALLOWEEN_PARTY_MOMENTS,
    "fourth_of_july_event": FOURTH_OF_JULY_EVENT_MOMENTS,
}


def build_event_timeline(
    event_type: str,           # "wedding" | "corporate" | "birthday" | "club"
    start_time: str,           # "18:00"
    event_date: str,           # "2026-08-15"
    venue: str = "",
    notes: str = "",
) -> Dict:
    """Generate a minute-by-minute run-of-show timeline for the specific event type."""

    base_hour, base_minute = map(int, start_time.split(":"))
    base_dt = datetime.strptime(f"{event_date} {start_time}", "%Y-%m-%d %H:%M")

    # Get event-specific moments
    moments = TIMELINE_BY_EVENT.get(event_type, GENERAL_PARTY_MOMENTS)

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

SAME_SEX_WEDDING_QUESTIONS = [
    {"id": "couple_names",       "label": "Couple's full names",                            "type": "text"},
    {"id": "name_pronunciation", "label": "Name pronunciation for introductions",            "type": "text"},
    {"id": "event_date",         "label": "Wedding date",                                    "type": "date"},
    {"id": "venue_name",         "label": "Venue name & address",                            "type": "text"},
    {"id": "guest_count",        "label": "Estimated guest count",                           "type": "number"},
    {"id": "ceremony_start",     "label": "Ceremony start time",                             "type": "time"},
    {"id": "reception_start",    "label": "Reception start time",                            "type": "time"},
    {"id": "entrance_order",     "label": "Grand entrance order (who gets introduced and how)", "type": "textarea"},
    {"id": "first_dance_song",   "label": "First dance song & artist",                       "type": "text"},
    {"id": "special_dances",     "label": "Special dances and songs (if any)",               "type": "textarea"},
    {"id": "toasts_speeches",    "label": "Who is giving toasts/speeches and when?",         "type": "textarea"},
    {"id": "cake_cutting_song",  "label": "Cake cutting song",                               "type": "text"},
    {"id": "last_dance_song",    "label": "Last dance song",                                 "type": "text"},
    {"id": "must_play",          "label": "Must-play songs",                                  "type": "textarea"},
    {"id": "do_not_play",        "label": "Do-NOT-play songs or genres",                     "type": "textarea"},
    {"id": "clean_music_only",   "label": "Clean music only?",                                "type": "text"},
    {"id": "vibe",               "label": "Describe the vibe you want",                       "type": "textarea"},
    {"id": "special_requests",   "label": "Any announcements, pronouns, or special notes?",  "type": "textarea"},
]

CORPORATE_QUESTIONS = [
    {"id": "company_name",        "label": "Company / event name",                        "type": "text"},
    {"id": "event_date",          "label": "Event date",                                  "type": "date"},
    {"id": "venue_name",          "label": "Venue name & address",                        "type": "text"},
    {"id": "guest_count",         "label": "Estimated guest count",                       "type": "number"},
    {"id": "start_time",          "label": "Event start time",                            "type": "time"},
    {"id": "end_time",            "label": "Event end time",                              "type": "time"},
    {"id": "event_goal",          "label": "Primary event goal (networking, awards, party)", "type": "text"},
    {"id": "mc_required",         "label": "Need DJ to MC announcements?",                 "type": "text"},
    {"id": "agenda_highlights",   "label": "Key schedule moments (awards, intros, speeches)", "type": "textarea"},
    {"id": "av_needs",            "label": "Any AV/mic/projector requirements?",           "type": "textarea"},
    {"id": "dress_code_branding", "label": "Dress code or brand guidelines for DJ/MC",    "type": "text"},
    {"id": "must_play",           "label": "Must-play tracks",                              "type": "textarea"},
    {"id": "do_not_play",         "label": "Genres or songs to avoid",                     "type": "textarea"},
    {"id": "vibe",                "label": "Desired vibe / energy",                         "type": "textarea"},
    {"id": "special_requests",    "label": "Special announcements or moments",              "type": "textarea"},
]

PARTY_QUESTIONS = [
    {"id": "client_name",          "label": "Client / host full name",                  "type": "text"},
    {"id": "event_date",           "label": "Event date",                                "type": "date"},
    {"id": "venue_name",           "label": "Venue name & address",                      "type": "text"},
    {"id": "guest_count",          "label": "Estimated guest count",                     "type": "number"},
    {"id": "crowd_type",           "label": "Crowd type (adults, teens, mixed)",         "type": "text"},
    {"id": "start_time",           "label": "Event start time",                          "type": "time"},
    {"id": "end_time",             "label": "Event end time",                            "type": "time"},
    {"id": "grand_intro_song",     "label": "Grand intro song (if needed)",              "type": "text"},
    {"id": "special_moments",      "label": "Special moments to announce",                "type": "textarea"},
    {"id": "games_or_activities",  "label": "Games/activities planned?",                  "type": "textarea"},
    {"id": "must_play",            "label": "Must-play songs",                            "type": "textarea"},
    {"id": "do_not_play",          "label": "Do-NOT-play songs or genres",               "type": "textarea"},
    {"id": "clean_music_only",     "label": "Clean music only?",                          "type": "text"},
    {"id": "vibe",                 "label": "Desired vibe / energy",                      "type": "textarea"},
    {"id": "special_requests",     "label": "Anything else the DJ should know",           "type": "textarea"},
]

SWEET_16_QUESTIONS = [
    {"id": "guest_name",           "label": "Sweet 16 guest full name",        "type": "text"},
    {"id": "event_date",           "label": "Event date",                      "type": "date"},
    {"id": "venue_name",           "label": "Venue name & address",            "type": "text"},
    {"id": "guest_count",          "label": "Estimated guest count",           "type": "number"},
    {"id": "start_time",           "label": "Event start time",                "type": "time"},
    {"id": "end_time",             "label": "Event end time",                  "type": "time"},
    {"id": "candle_lighting_song", "label": "Candle lighting ceremony song",   "type": "text"},
    {"id": "first_dance_song",     "label": "Sweet 16 first dance song",       "type": "text"},
    {"id": "cake_cutting_song",    "label": "Cake cutting song",               "type": "text"},
    {"id": "special_dances",       "label": "Special dances or moments",       "type": "textarea"},
    {"id": "speeches",             "label": "Who is giving speeches/toasts?",  "type": "textarea"},
    {"id": "must_play",            "label": "Must-play songs",                 "type": "textarea"},
    {"id": "do_not_play",          "label": "Do-NOT-play songs or genres",     "type": "textarea"},
    {"id": "vibe",                 "label": "Desired vibe / energy",           "type": "textarea"},
    {"id": "special_requests",     "label": "Anything else?",                  "type": "textarea"},
]

BIRTHDAY_QUESTIONS = [
    {"id": "guest_name",       "label": "Birthday guest full name & age",     "type": "text"},
    {"id": "event_date",       "label": "Event date",                         "type": "date"},
    {"id": "venue_name",       "label": "Venue name & address",               "type": "text"},
    {"id": "guest_count",      "label": "Estimated guest count",              "type": "number"},
    {"id": "start_time",       "label": "Event start time",                   "type": "time"},
    {"id": "end_time",         "label": "Event end time",                     "type": "time"},
    {"id": "entrance_song",    "label": "Entrance / grand intro song",        "type": "text"},
    {"id": "cake_cutting_song","label": "Cake cutting song",                  "type": "text"},
    {"id": "special_moments",  "label": "Special moments or dance requests",  "type": "textarea"},
    {"id": "games_or_activities","label": "Any games/activities planned?",      "type": "textarea"},
    {"id": "clean_music_only", "label": "Clean music only?",                    "type": "text"},
    {"id": "must_play",        "label": "Must-play songs",                    "type": "textarea"},
    {"id": "do_not_play",      "label": "Do-NOT-play songs or genres",        "type": "textarea"},
    {"id": "vibe",             "label": "Desired vibe / energy",              "type": "textarea"},
    {"id": "special_requests", "label": "Anything else?",                     "type": "textarea"},
]

QUINCEANERA_QUESTIONS = [
    {"id": "debutante_name",    "label": "Quinceanera guest full name",       "type": "text"},
    {"id": "event_date",        "label": "Event date",                        "type": "date"},
    {"id": "venue_name",        "label": "Venue name & address",              "type": "text"},
    {"id": "guest_count",       "label": "Estimated guest count",             "type": "number"},
    {"id": "start_time",        "label": "Event start time",                  "type": "time"},
    {"id": "end_time",          "label": "Event end time",                    "type": "time"},
    {"id": "ceremony_start",    "label": "Ceremony start time (if separate)", "type": "time"},
    {"id": "entrance_song",     "label": "Debutante entrance song",           "type": "text"},
    {"id": "father_daughter",   "label": "Father-daughter dance song",        "type": "text"},
    {"id": "first_dance_song",  "label": "First dance song",                  "type": "text"},
    {"id": "cake_cutting_song", "label": "Cake cutting song",                 "type": "text"},
    {"id": "surprise_dance",    "label": "Surprise dance planned? Song + timing", "type": "textarea"},
    {"id": "special_traditions", "label": "Special traditions (shoe ceremony, etc)", "type": "textarea"},
    {"id": "must_play",         "label": "Must-play songs",                   "type": "textarea"},
    {"id": "do_not_play",       "label": "Do-NOT-play songs or genres",       "type": "textarea"},
    {"id": "vibe",              "label": "Desired vibe / energy",             "type": "textarea"},
    {"id": "special_requests",  "label": "Anything else?",                    "type": "textarea"},
]

BAR_MITZVAH_QUESTIONS = [
    {"id": "celebrant_name",         "label": "Bar Mitzvah celebrant full name",                        "type": "text"},
    {"id": "name_pronunciation",     "label": "Name pronunciation for introductions",                   "type": "text"},
    {"id": "parents_names",          "label": "Parents' full names",                                    "type": "text"},
    {"id": "event_date",             "label": "Event date",                                             "type": "date"},
    {"id": "venue_name",             "label": "Reception venue name & address",                         "type": "text"},
    {"id": "service_location",       "label": "Synagogue/service location (if different)",             "type": "text"},
    {"id": "guest_count",            "label": "Estimated guest count",                                  "type": "number"},
    {"id": "kids_vs_adults",         "label": "Approximate kids/teens vs adults mix",                  "type": "text"},
    {"id": "service_start",          "label": "Service/ceremony start time",                            "type": "time"},
    {"id": "service_end",            "label": "Service/ceremony end time",                              "type": "time"},
    {"id": "party_start",            "label": "Reception/party start time",                             "type": "time"},
    {"id": "party_end",              "label": "Reception/party end time",                               "type": "time"},
    {"id": "religious_customs",      "label": "Any religious customs or restrictions DJ should respect?", "type": "textarea"},
    {"id": "formal_entrance",        "label": "Formal grand entrance? If yes, who should be introduced?", "type": "textarea"},
    {"id": "entrance_song",          "label": "Celebrant grand entrance song",                          "type": "text"},
    {"id": "hora_plan",              "label": "Hora planned? If yes, when and who leads it?",          "type": "textarea"},
    {"id": "candle_lighting_plan",   "label": "Candle lighting planned? (optional) Include count + honorees", "type": "textarea"},
    {"id": "candle_lighting_song",   "label": "Candle lighting song(s) if used",                        "type": "text"},
    {"id": "speakers",               "label": "Who is speaking? (parents, grandparents, rabbi, celebrant)", "type": "textarea"},
    {"id": "video_montage",          "label": "Video montage planned? Timing + AV/audio support needed", "type": "textarea"},
    {"id": "games_interactive",      "label": "Kids activities/games planned? (dance contest, trivia, etc)", "type": "textarea"},
    {"id": "cake_cutting_song",      "label": "Cake cutting song",                                      "type": "text"},
    {"id": "must_play",              "label": "Top must-play songs (celebrant + family)",              "type": "textarea"},
    {"id": "do_not_play",            "label": "Do-NOT-play songs or genres",                            "type": "textarea"},
    {"id": "clean_music_only",       "label": "Clean music only? Any explicit content rules?",          "type": "text"},
    {"id": "special_friends",        "label": "Any special friends/family to recognize during event?", "type": "textarea"},
    {"id": "special_requests",       "label": "Any additional DJ/MC notes or announcements?",           "type": "textarea"},
]

BAT_MITZVAH_QUESTIONS = [
    {"id": "celebrant_name",         "label": "Bat Mitzvah celebrant full name",                        "type": "text"},
    {"id": "name_pronunciation",     "label": "Name pronunciation for introductions",                   "type": "text"},
    {"id": "parents_names",          "label": "Parents' full names",                                    "type": "text"},
    {"id": "event_date",             "label": "Event date",                                             "type": "date"},
    {"id": "venue_name",             "label": "Reception venue name & address",                         "type": "text"},
    {"id": "service_location",       "label": "Synagogue/service location (if different)",             "type": "text"},
    {"id": "guest_count",            "label": "Estimated guest count",                                  "type": "number"},
    {"id": "kids_vs_adults",         "label": "Approximate kids/teens vs adults mix",                  "type": "text"},
    {"id": "service_start",          "label": "Service/ceremony start time",                            "type": "time"},
    {"id": "service_end",            "label": "Service/ceremony end time",                              "type": "time"},
    {"id": "party_start",            "label": "Reception/party start time",                             "type": "time"},
    {"id": "party_end",              "label": "Reception/party end time",                               "type": "time"},
    {"id": "religious_customs",      "label": "Any religious customs or restrictions DJ should respect?", "type": "textarea"},
    {"id": "formal_entrance",        "label": "Formal grand entrance? If yes, who should be introduced?", "type": "textarea"},
    {"id": "entrance_song",          "label": "Celebrant grand entrance song",                          "type": "text"},
    {"id": "hora_plan",              "label": "Hora planned? If yes, when and who leads it?",          "type": "textarea"},
    {"id": "candle_lighting_plan",   "label": "Candle lighting planned? (optional) Include count + honorees", "type": "textarea"},
    {"id": "candle_lighting_song",   "label": "Candle lighting song(s) if used",                        "type": "text"},
    {"id": "speakers",               "label": "Who is speaking? (parents, grandparents, rabbi, celebrant)", "type": "textarea"},
    {"id": "video_montage",          "label": "Video montage planned? Timing + AV/audio support needed", "type": "textarea"},
    {"id": "games_interactive",      "label": "Kids activities/games planned? (dance contest, trivia, etc)", "type": "textarea"},
    {"id": "cake_cutting_song",      "label": "Cake cutting song",                                      "type": "text"},
    {"id": "must_play",              "label": "Top must-play songs (celebrant + family)",              "type": "textarea"},
    {"id": "do_not_play",            "label": "Do-NOT-play songs or genres",                            "type": "textarea"},
    {"id": "clean_music_only",       "label": "Clean music only? Any explicit content rules?",          "type": "text"},
    {"id": "special_friends",        "label": "Any special friends/family to recognize during event?", "type": "textarea"},
    {"id": "special_requests",       "label": "Any additional DJ/MC notes or announcements?",           "type": "textarea"},
]

ANNIVERSARY_QUESTIONS = [
    {"id": "anniversary_number", "label": "Which anniversary is being celebrated?", "type": "text"},
    {"id": "wedding_date", "label": "What was your wedding date?", "type": "date"},
    {"id": "first_dance_song", "label": "What was your first dance song?", "type": "text"},
    {"id": "anniversary_dance", "label": "Will there be an Anniversary Dance?", "type": "text"},
    {"id": "family_speeches", "label": "Will family members give speeches?", "type": "text"},
    {"id": "slideshow_video", "label": "Will there be a slideshow/video montage?", "type": "text"},
    {"id": "vow_renewal", "label": "Any vow renewal ceremony?", "type": "text"},
    {"id": "dating_years_music", "label": "Favorite music from your dating years?", "type": "textarea"},
    {"id": "family_recognition", "label": "Any family members to recognize?", "type": "textarea"},
    {"id": "top_priority_moment", "label": "What is the most important moment of the evening?", "type": "textarea"},
]

CLUB_QUESTIONS = [
    {"id": "venue_name",        "label": "Club / venue name & location",                    "type": "text"},
    {"id": "event_date",        "label": "Event date",                                      "type": "date"},
    {"id": "set_start",         "label": "Set start time",                                  "type": "time"},
    {"id": "set_end",           "label": "Set end time",                                    "type": "time"},
    {"id": "expected_crowd",    "label": "Expected crowd size",                             "type": "number"},
    {"id": "age_profile",       "label": "Expected crowd profile (age/style)",              "type": "text"},
    {"id": "opening_genres",    "label": "Opening set genres",                              "type": "textarea"},
    {"id": "peak_genres",       "label": "Peak-time genres / vibe",                         "type": "textarea"},
    {"id": "bpm_range",         "label": "Preferred BPM range",                             "type": "text"},
    {"id": "must_play",         "label": "Must-play tracks",                                "type": "textarea"},
    {"id": "do_not_play",       "label": "Do-NOT-play songs or genres",                     "type": "textarea"},
    {"id": "mic_policy",        "label": "Mic policy / shoutouts allowed?",                 "type": "text"},
    {"id": "technical_needs",   "label": "Technical requirements (CDJs, mixer, booth setup)", "type": "textarea"},
    {"id": "lighting_fx",       "label": "Lighting/FX cues needed?",                        "type": "textarea"},
    {"id": "special_requests",  "label": "Anything else?",                                  "type": "textarea"},
]

GRADUATION_PARTY_QUESTIONS = [
    {"id": "graduate_name", "label": "Graduate's name?", "type": "text"},
    {"id": "school_name", "label": "School graduating from?", "type": "text"},
    {"id": "future_plans", "label": "College or career plans?", "type": "textarea"},
    {"id": "school_colors", "label": "School colors?", "type": "text"},
    {"id": "school_mascot", "label": "School mascot?", "type": "text"},
    {"id": "speeches", "label": "Will there be speeches?", "type": "text"},
    {"id": "slideshow", "label": "Will there be a slideshow?", "type": "text"},
    {"id": "awards", "label": "Any academic awards to recognize?", "type": "textarea"},
    {"id": "favorite_songs", "label": "Favorite songs?", "type": "textarea"},
    {"id": "preferred_genres", "label": "Preferred music genres?", "type": "textarea"},
    {"id": "special_introductions", "label": "Any special introductions?", "type": "textarea"},
]

BABY_SHOWER_QUESTIONS = [
    {"id": "parents_to_be", "label": "Name of parent(s)-to-be?", "type": "text"},
    {"id": "due_date", "label": "Due date?", "type": "date"},
    {"id": "baby_gender", "label": "Boy, girl, or surprise?", "type": "text"},
    {"id": "theme", "label": "Theme of shower?", "type": "text"},
    {"id": "games", "label": "Will there be games?", "type": "text"},
    {"id": "host", "label": "Who is hosting?", "type": "text"},
    {"id": "gift_opening_schedule", "label": "Gift opening schedule?", "type": "textarea"},
    {"id": "special_announcements", "label": "Special announcements?", "type": "textarea"},
    {"id": "background_music_style", "label": "Background music style?", "type": "textarea"},
    {"id": "family_recognitions", "label": "Any family recognitions?", "type": "textarea"},
]

GENDER_REVEAL_QUESTIONS = [
    {"id": "gender_known_by", "label": "Who knows the baby's gender?", "type": "text"},
    {"id": "reveal_method", "label": "Reveal method?", "type": "textarea"},
    {"id": "reveal_time", "label": "Reveal time?", "type": "time"},
    {"id": "countdown_music", "label": "Music for countdown?", "type": "text"},
    {"id": "photographer_videographer", "label": "Photographer/videographer?", "type": "text"},
    {"id": "speeches", "label": "Any speeches?", "type": "text"},
    {"id": "special_family_members", "label": "Any special family members involved?", "type": "textarea"},
    {"id": "pre_reveal_music_style", "label": "Preferred music style before reveal?", "type": "textarea"},
    {"id": "games", "label": "Will there be games?", "type": "text"},
]

BRIDAL_SHOWER_QUESTIONS = [
    {"id": "bride_name", "label": "Bride name", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "favorite_music", "label": "Bride's favorite music", "type": "textarea"},
    {"id": "games", "label": "Games planned", "type": "textarea"},
    {"id": "gift_opening_schedule", "label": "Gift opening schedule", "type": "textarea"},
    {"id": "special_guests", "label": "Special guests to recognize", "type": "textarea"},
    {"id": "toasts", "label": "Toast schedule", "type": "textarea"},
]

RETIREMENT_PARTY_QUESTIONS = [
    {"id": "retiree_name", "label": "Retiree's name?", "type": "text"},
    {"id": "company", "label": "Company?", "type": "text"},
    {"id": "years_of_service", "label": "Years of service?", "type": "text"},
    {"id": "position_held", "label": "Position held?", "type": "text"},
    {"id": "favorite_music_era", "label": "Favorite music era?", "type": "text"},
    {"id": "awards", "label": "Will there be awards?", "type": "text"},
    {"id": "speeches", "label": "Will there be speeches?", "type": "text"},
    {"id": "surprise_guests", "label": "Any surprise guests?", "type": "text"},
    {"id": "video_tribute", "label": "Video tribute?", "type": "text"},
    {"id": "highlighted_accomplishment", "label": "What accomplishment should be highlighted?", "type": "textarea"},
]

PROM_QUESTIONS = [
    {"id": "school_name", "label": "School name?", "type": "text"},
    {"id": "theme", "label": "Theme?", "type": "text"},
    {"id": "student_count", "label": "Student count?", "type": "number"},
    {"id": "prom_court_announcement", "label": "Prom King & Queen announcement?", "type": "text"},
    {"id": "school_music_guidelines", "label": "School-approved music guidelines?", "type": "textarea"},
    {"id": "must_play_songs", "label": "Must-play songs?", "type": "textarea"},
    {"id": "trending_songs", "label": "Current trending songs?", "type": "textarea"},
    {"id": "slow_dance_preferences", "label": "Slow dance preferences?", "type": "textarea"},
    {"id": "contests", "label": "Any contests?", "type": "textarea"},
    {"id": "chaperone_contact", "label": "Chaperone contact information?", "type": "text"},
]

HOMECOMING_DANCE_QUESTIONS = [
    {"id": "school_name", "label": "School name?", "type": "text"},
    {"id": "grade_levels", "label": "Grade levels attending?", "type": "text"},
    {"id": "theme", "label": "Theme?", "type": "text"},
    {"id": "music_restrictions", "label": "Music restrictions?", "type": "textarea"},
    {"id": "requested_genres", "label": "Requested genres?", "type": "textarea"},
    {"id": "announcements", "label": "Any announcements?", "type": "textarea"},
    {"id": "dance_contests", "label": "Dance contests?", "type": "textarea"},
    {"id": "school_mascot_song", "label": "School mascot/song?", "type": "text"},
    {"id": "chaperone_contact", "label": "Chaperone contact?", "type": "text"},
]

SCHOOL_DANCE_QUESTIONS = [
    {"id": "school_name", "label": "School name?", "type": "text"},
    {"id": "grade_levels", "label": "Grade levels attending?", "type": "text"},
    {"id": "theme", "label": "Theme?", "type": "text"},
    {"id": "music_restrictions", "label": "Music restrictions?", "type": "textarea"},
    {"id": "requested_genres", "label": "Requested genres?", "type": "textarea"},
    {"id": "announcements", "label": "Any announcements?", "type": "textarea"},
    {"id": "dance_contests", "label": "Dance contests?", "type": "textarea"},
    {"id": "school_mascot_song", "label": "School mascot/song?", "type": "text"},
    {"id": "chaperone_contact", "label": "Chaperone contact?", "type": "text"},
]

FUNDRAISER_CHARITY_GALA_QUESTIONS = [
    {"id": "organization_name", "label": "Organization name?", "type": "text"},
    {"id": "supported_cause", "label": "Cause being supported?", "type": "textarea"},
    {"id": "fundraising_goal", "label": "Fundraising goal?", "type": "text"},
    {"id": "sponsors", "label": "Sponsors?", "type": "textarea"},
    {"id": "silent_auction", "label": "Silent auction?", "type": "text"},
    {"id": "live_auction", "label": "Live auction?", "type": "text"},
    {"id": "key_speakers", "label": "Key speakers?", "type": "textarea"},
    {"id": "donation_appeal_time", "label": "Donation appeal time?", "type": "text"},
    {"id": "recognition_announcements", "label": "Recognition announcements?", "type": "textarea"},
    {"id": "preferred_atmosphere", "label": "Preferred event atmosphere?", "type": "textarea"},
]

COMMUNITY_FESTIVAL_QUESTIONS = [
    {"id": "event_name", "label": "Event name?", "type": "text"},
    {"id": "organization", "label": "Organization?", "type": "text"},
    {"id": "estimated_attendance", "label": "Estimated attendance?", "type": "number"},
    {"id": "stage_schedule", "label": "Stage schedule?", "type": "textarea"},
    {"id": "sponsor_list", "label": "Sponsor list?", "type": "textarea"},
    {"id": "vendor_announcements", "label": "Vendor announcements?", "type": "textarea"},
    {"id": "entertainment_schedule", "label": "Entertainment schedule?", "type": "textarea"},
    {"id": "public_announcements", "label": "Public announcements needed?", "type": "textarea"},
    {"id": "family_friendly", "label": "Family-friendly audience?", "type": "text"},
]

CAR_SHOW_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "registration_time", "label": "Registration time", "type": "time"},
    {"id": "judging_categories", "label": "Judging categories", "type": "textarea"},
    {"id": "sponsor_recognition", "label": "Sponsor recognition", "type": "textarea"},
    {"id": "trophy_presentation", "label": "Trophy presentation timing", "type": "textarea"},
    {"id": "vehicle_announcements", "label": "Vehicle announcements", "type": "textarea"},
]

GRAND_OPENING_QUESTIONS = [
    {"id": "business_name", "label": "Business name", "type": "text"},
    {"id": "ribbon_cutting_time", "label": "Ribbon cutting time", "type": "time"},
    {"id": "vip_guests", "label": "VIP guests?", "type": "textarea"},
    {"id": "sponsors", "label": "Sponsors?", "type": "textarea"},
    {"id": "giveaways", "label": "Giveaways?", "type": "textarea"},
    {"id": "promotional_announcements", "label": "Promotional announcements?", "type": "textarea"},
    {"id": "background_music_style", "label": "Background music style?", "type": "textarea"},
    {"id": "special_offers", "label": "Special offers to announce?", "type": "textarea"},
    {"id": "photographer_present", "label": "Photographer present?", "type": "text"},
]

NETWORKING_EVENT_QUESTIONS = [
    {"id": "organization", "label": "Company/organization?", "type": "text"},
    {"id": "expected_attendance", "label": "Expected attendance?", "type": "number"},
    {"id": "networking_or_dancing", "label": "Networking only or dancing?", "type": "text"},
    {"id": "sponsor_recognition", "label": "Sponsor recognition?", "type": "textarea"},
    {"id": "speakers", "label": "Speakers?", "type": "textarea"},
    {"id": "background_music_preferences", "label": "Background music preferences?", "type": "textarea"},
    {"id": "announcements", "label": "Announcements needed?", "type": "textarea"},
    {"id": "vip_guests", "label": "VIP guests?", "type": "textarea"},
    {"id": "event_goals", "label": "Event goals?", "type": "textarea"},
]

TRADE_SHOW_EXPO_QUESTIONS = [
    {"id": "expo_name", "label": "Trade show / expo name", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "booth_announcements", "label": "Booth announcements", "type": "textarea"},
    {"id": "presentation_schedule", "label": "Presentation schedule", "type": "textarea"},
    {"id": "sponsor_mentions", "label": "Sponsor mentions", "type": "textarea"},
    {"id": "crowd_engagement", "label": "Crowd engagement plan", "type": "textarea"},
]

KARAOKE_NIGHT_QUESTIONS = [
    {"id": "public_or_private", "label": "Public or private event?", "type": "text"},
    {"id": "guest_count", "label": "Number of guests?", "type": "number"},
    {"id": "contest_format", "label": "Contest format?", "type": "textarea"},
    {"id": "prizes", "label": "Prizes?", "type": "textarea"},
    {"id": "family_friendly", "label": "Family-friendly?", "type": "text"},
    {"id": "music_restrictions", "label": "Music restrictions?", "type": "textarea"},
    {"id": "rotation_preferences", "label": "Rotation preferences?", "type": "textarea"},
    {"id": "song_request_process", "label": "Song request process?", "type": "textarea"},
    {"id": "event_timeline", "label": "Event timeline?", "type": "textarea"},
]

MUSIC_BINGO_SINGO_QUESTIONS = [
    {"id": "number_of_rounds", "label": "Number of rounds", "type": "number"},
    {"id": "theme_rounds", "label": "Theme rounds?", "type": "textarea"},
    {"id": "number_of_players", "label": "Number of players?", "type": "number"},
    {"id": "prize_structure", "label": "Prize structure?", "type": "textarea"},
    {"id": "family_friendly", "label": "Family-friendly?", "type": "text"},
    {"id": "preferred_decades", "label": "Music decades preferred?", "type": "textarea"},
    {"id": "special_announcements", "label": "Special announcements?", "type": "textarea"},
    {"id": "event_duration", "label": "Event duration?", "type": "text"},
]

TRIVIA_NIGHT_QUESTIONS = [
    {"id": "number_of_rounds", "label": "Number of rounds?", "type": "number"},
    {"id": "categories", "label": "Categories?", "type": "textarea"},
    {"id": "team_or_individual", "label": "Team or individual?", "type": "text"},
    {"id": "prizes", "label": "Prizes?", "type": "textarea"},
    {"id": "tie_breaker_format", "label": "Tie-breaker format?", "type": "textarea"},
    {"id": "audience_demographics", "label": "Audience demographics?", "type": "textarea"},
    {"id": "special_theme", "label": "Special theme?", "type": "text"},
    {"id": "sponsor_mentions", "label": "Sponsor mentions?", "type": "textarea"},
]

CHRISTMAS_PARTY_QUESTIONS = [
    {"id": "corporate_or_family", "label": "Corporate or family?", "type": "text"},
    {"id": "gift_exchange", "label": "Gift exchange?", "type": "text"},
    {"id": "santa_appearance", "label": "Santa appearance?", "type": "text"},
    {"id": "holiday_music_preferences", "label": "Holiday music preferences?", "type": "textarea"},
    {"id": "employee_recognition", "label": "Employee recognition?", "type": "text"},
    {"id": "awards", "label": "Awards?", "type": "text"},
    {"id": "theme", "label": "Theme?", "type": "text"},
]

NEW_YEARS_EVE_PARTY_QUESTIONS = [
    {"id": "countdown_timing", "label": "Countdown timing?", "type": "text"},
    {"id": "champagne_toast", "label": "Champagne toast?", "type": "text"},
    {"id": "midnight_song", "label": "Midnight song?", "type": "text"},
    {"id": "balloon_drop", "label": "Balloon drop?", "type": "text"},
    {"id": "party_favors", "label": "Party favors?", "type": "textarea"},
    {"id": "special_announcements", "label": "Special announcements?", "type": "textarea"},
]

HALLOWEEN_PARTY_QUESTIONS = [
    {"id": "costume_contest", "label": "Costume contest?", "type": "text"},
    {"id": "contest_categories", "label": "Categories?", "type": "textarea"},
    {"id": "prize_winners", "label": "Prize winners?", "type": "textarea"},
    {"id": "theme", "label": "Theme?", "type": "text"},
    {"id": "audience_type", "label": "Family-friendly or adults only?", "type": "text"},
]

FOURTH_OF_JULY_EVENT_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "fireworks_timing", "label": "Fireworks timing", "type": "text"},
    {"id": "patriotic_music", "label": "Patriotic music preferences", "type": "textarea"},
    {"id": "family_activities", "label": "Family activities", "type": "textarea"},
]

QUESTIONNAIRE_BY_EVENT = {
    "wedding": WEDDING_QUESTIONS,
    "same_sex_wedding_lgbtq": SAME_SEX_WEDDING_QUESTIONS,
    "corporate": CORPORATE_QUESTIONS,
    "sweet_16": SWEET_16_QUESTIONS,
    "birthday": BIRTHDAY_QUESTIONS,
    "quinceanera": QUINCEANERA_QUESTIONS,
    "general_party": PARTY_QUESTIONS,
    "bar_mitzvah": BAR_MITZVAH_QUESTIONS,
    "bat_mitzvah": BAT_MITZVAH_QUESTIONS,
    "anniversary": ANNIVERSARY_QUESTIONS,
    "anniversay": ANNIVERSARY_QUESTIONS,
    "club": CLUB_QUESTIONS,
    "graduation_party": GRADUATION_PARTY_QUESTIONS,
    "baby_shower": BABY_SHOWER_QUESTIONS,
    "gender_reveal": GENDER_REVEAL_QUESTIONS,
    "bridal_shower": BRIDAL_SHOWER_QUESTIONS,
    "retirement_party": RETIREMENT_PARTY_QUESTIONS,
    "prom": PROM_QUESTIONS,
    "homecoming_dance": HOMECOMING_DANCE_QUESTIONS,
    "school_dance": SCHOOL_DANCE_QUESTIONS,
    "fundraiser_charity_gala": FUNDRAISER_CHARITY_GALA_QUESTIONS,
    "community_festival": COMMUNITY_FESTIVAL_QUESTIONS,
    "car_show": CAR_SHOW_QUESTIONS,
    "grand_opening": GRAND_OPENING_QUESTIONS,
    "networking_event": NETWORKING_EVENT_QUESTIONS,
    "trade_show_expo": TRADE_SHOW_EXPO_QUESTIONS,
    "karaoke_night": KARAOKE_NIGHT_QUESTIONS,
    "music_bingo_singo": MUSIC_BINGO_SINGO_QUESTIONS,
    "trivia_night": TRIVIA_NIGHT_QUESTIONS,
    "christmas_party": CHRISTMAS_PARTY_QUESTIONS,
    "new_years_eve_party": NEW_YEARS_EVE_PARTY_QUESTIONS,
    "halloween_party": HALLOWEEN_PARTY_QUESTIONS,
    "fourth_of_july_event": FOURTH_OF_JULY_EVENT_QUESTIONS,
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
    result = {
        "portal_id": portal_id,
        "event_type": event_type,
        "answers": answers,
        "brief_id": str(uuid.uuid4()),
        "submitted_at": datetime.utcnow().isoformat(),
    }
    _append_record(BRIEFS_FILE, result)
    return result


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

    result = {
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
        "quoted_at": datetime.utcnow().isoformat(),
    }
    _append_record(QUOTES_FILE, result)
    return result


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

WEDDING_HOOKS = {
    "authority": [
        "Most DJs make this one mistake that costs them every high-end wedding booking.",
        "Here is the exact timeline I use for every 5-star wedding reception.",
        "The song sequence that keeps the dance floor packed all night long.",
        "Father-daughter dance setup: how to make it emotional and keep the energy flowing.",
    ],
    "social_proof": [
        "Client said 'It was the best wedding they had ever attended.' Here is what I did differently.",
        "Just wrapped back-to-back weddings. The couple cried during our first dance. Here is the setup.",
        "Booked this couple from a 30-second Instagram video. It showed my timeline system.",
    ],
    "value": [
        "Save this — the complete DJ run-of-show template for a wedding reception.",
        "The 5 critical songs for a wedding that guarantee a packed dance floor.",
        "Pricing breakdown: how to charge premium rates and book more weddings.",
    ],
    "offer": [
        "I built a wedding-specific tool for DJ timelines, client forms, and quotes. Link in bio.",
        "Done-with-you wedding DJ system inside the Vault. Everything templated. Link in bio.",
        "DM me if you want to book 2-3 premium weddings per month at higher rates.",
    ],
}

BIRTHDAY_HOOKS = {
    "authority": [
        "How to keep a birthday party energy high from start to finish — no dead moments.",
        "The birthday DJ mistake that makes people leave early (and how to avoid it).",
        "Cake cutting songs that get the crowd hyped, not awkward.",
    ],
    "social_proof": [
        "Just played a 50th birthday bash where everyone was dancing the whole time.",
        "Parent booked me for their kid's 16th because I made the 13th party unforgettable.",
        "Turned a small birthday into the talk of the neighborhood. Here is the timeline.",
    ],
    "value": [
        "Birthday party checklist: the moments that matter and songs that land.",
        "How to read the crowd and adapt your setlist real-time for birthdays.",
        "Pricing strategy for birthday parties that gets you booked every weekend.",
    ],
    "offer": [
        "Birthday-specific system: timelines, questionnaires, all set up. Link in bio.",
        "Book more birthday parties with the DJ system built for multi-generational crowds.",
        "Everything you need to run a birthday party from start to finish in the Vault.",
    ],
}

SWEET_16_HOOKS = {
    "authority": [
        "Sweet 16 candle lighting: the one moment that has to be perfect.",
        "How to keep a Sweet 16 dance floor packed without playing radio hits all night.",
        "Sweet 16 DJ setup: from ceremony to party — minute by minute.",
    ],
    "social_proof": [
        "Just played a Sweet 16 where the birthday girl cried happy tears during candle lighting.",
        "Parent hired me after seeing my Sweet 16 timeline posted on Instagram.",
        "Booked 3 more Sweet 16s from the one I did last month. Here is why it worked.",
    ],
    "value": [
        "Complete Sweet 16 timeline: candle ceremony to last dance.",
        "Songs for Sweet 16 that hit with both the birthday girl and her parents.",
        "How to price Sweet 16 parties and actually get booked.",
    ],
    "offer": [
        "Sweet 16 specialist system — all the templates you need. Link in bio.",
        "Book more Sweet 16s with the DJ questionnaire and timeline built for this exact event.",
        "Everything inside: candle ceremony setups, best songs, pricing formula.",
    ],
}

QUINCEANERA_HOOKS = {
    "authority": [
        "Quinceanera tradition meets modern music — how to do both perfectly.",
        "The debutante entrance song that sets the tone for the whole night.",
        "Father-daughter choreography cues: how a DJ enhances the moment.",
    ],
    "social_proof": [
        "Just played a Quinceanera with 300 guests. The traditional moments hit perfectly.",
        "Booked two more Quinceaneras after this family saw my timeline system.",
        "Parent told me this was the most well-timed Quinceanera they had attended.",
    ],
    "value": [
        "Quinceanera timeline: ceremony to reception to after-party.",
        "How to honor tradition while keeping modern guests engaged and dancing.",
        "Pricing Quinceaneras what they are actually worth.",
    ],
    "offer": [
        "Quinceanera-specific platform with ceremony timing, song cues, and pricing. Link in bio.",
        "Book premium Quinceaneras with a system built for this exact tradition.",
        "Get all the templates, questionnaires, and timelines in the Vault.",
    ],
}

CORPORATE_HOOKS = {
    "authority": [
        "Corporate event DJ: how to read the room and adapt real-time.",
        "The difference between a DJ who kills corporate events and one who does not.",
        "How to time announcements, awards, and dancing perfectly.",
    ],
    "social_proof": [
        "Just wrapped a 500-person corporate event. Seamless. No awkward moments.",
        "Company re-booked me for their quarterly events. Here is the system I use.",
        "Corporate client said 'Best event energy we have ever had.' Here is why.",
    ],
    "value": [
        "Corporate event timeline: check-in to closing remarks.",
        "How to handle technical A/V, live announcements, and dancing all at once.",
        "Corporate pricing: how to charge premium rates for these gigs.",
    ],
    "offer": [
        "Corporate event system — timelines, questionnaires, technical checklist. Link in bio.",
        "Book high-ticket corporate events with a professional system. Vault link.",
        "Everything templates and ready to go for corporate bookings.",
    ],
}

CLUB_HOOKS = {
    "authority": [
        "Club DJ energy: how to read a crowd and keep momentum all night.",
        "The BPM progression that keeps a dance floor packed for 4 hours straight.",
        "Club setup: how to soundcheck and still have time for dinner.",
    ],
    "social_proof": [
        "Just finished a 4-hour club set. Packed the whole time. Here is how I sequenced it.",
        "Booked for a club's weekend residency after one stellar night.",
        "Venue manager asked me back before I even left. Here is what I did.",
    ],
    "value": [
        "Club DJ workflow: setup to peak hour to closing.",
        "Songs that work in clubs but still feel premium and intentional.",
        "Club pricing: getting paid what this work is actually worth.",
    ],
    "offer": [
        "Club DJ playbook: technical setup, setlist strategy, timing. Link in bio.",
        "Book club residencies by running professional systems. Vault inside.",
        "Everything a club DJ needs in one platform.",
    ],
}

CONTENT_HOOKS_BY_EVENT = {
    "wedding": WEDDING_HOOKS,
    "same_sex_wedding_lgbtq": WEDDING_HOOKS,
    "corporate": CORPORATE_HOOKS,
    "sweet_16": SWEET_16_HOOKS,
    "birthday": BIRTHDAY_HOOKS,
    "quinceanera": QUINCEANERA_HOOKS,
    "general_party": BIRTHDAY_HOOKS,
    "bar_mitzvah": BIRTHDAY_HOOKS,
    "bat_mitzvah": BIRTHDAY_HOOKS,
    "anniversary": WEDDING_HOOKS,
    "anniversay": WEDDING_HOOKS,
    "club": CLUB_HOOKS,
}

CAPTION_TEMPLATES = [
    """{hook}

Here is what I have learned after {years} years behind the decks at {specialty} events:

The DJs who stay booked year-round are not always the most technical. They run a better system.

They show up prepared. They communicate better. They deliver an experience, not just music.

That is what the Blu Bloods platform is built to give you.

{cta}

#DJLife #DJ{specialty_tag} #EventDJ #DJBusiness #BluBloods""",

    """{hook}

No one talks about the business side of DJing.

Getting leads. Converting them. Running the event without stress. Getting paid what you are worth.

I built a platform that handles all of it — specifically for {specialty} DJs.

{cta}

#DJBusiness #DJ{specialty_tag} #DJTips #BluBloods""",

    """{hook}

Drop a 🎵 below if you want the full breakdown.

{cta}

#DJLife #EventPlanning #DJ{specialty_tag} #BluBloods #DJTips""",
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
    specialty: str = "general_party",
    cta: str = "Link in bio to apply.",
) -> Dict:
    """Generate a 30-day Instagram content plan with event-specific captions and DM scripts."""

    # Get event-specific hooks
    hooks_dict = CONTENT_HOOKS_BY_EVENT.get(specialty, BIRTHDAY_HOOKS)
    posts = []
    categories = list(hooks_dict.keys())

    for day in range(1, 31):
        category = categories[(day - 1) % len(categories)]
        hooks = hooks_dict[category]
        hook = hooks[(day - 1) % len(hooks)]
        template = CAPTION_TEMPLATES[(day - 1) % len(CAPTION_TEMPLATES)]
        specialty_label = specialty.replace("_", " ").title()
        specialty_tag = specialty_label.replace(" ", "")
        caption = template.format(hook=hook, years=years_experience, cta=cta, specialty=specialty_label, specialty_tag=specialty_tag)

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
            f"DJ & {specialty.replace('_', ' ').lower()} specialist | {years_experience}+ years | Helping DJs book premium events | Link below",
            f"Booked {years_experience}+ years | {specialty.replace('_', ' ').title()} expert | Resources for DJs | Apply below",
            f"DJ Blu Bloods | Premium {specialty.replace('_', ' ').lower()} experiences | DM for booking | Resources in bio",
        ],
        "created_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 6. LESSON PLAN BUILDER
# ─────────────────────────────────────────────

LESSON_PLAN_FOCUS_LIBRARY = {
    "literacy": [
        "Letter recognition and phonemic awareness",
        "Vocabulary growth with read-alouds",
        "Story sequencing and retell skills",
    ],
    "math": [
        "Counting, one-to-one correspondence, and number sense",
        "Pattern recognition and sorting",
        "Shape identification and spatial language",
    ],
    "social_emotional": [
        "Self-regulation and classroom routines",
        "Friendship, empathy, and turn-taking",
        "Emotional vocabulary and reflection",
    ],
    "science": [
        "Observation, prediction, and inquiry",
        "Life cycles, weather, and seasons",
        "Hands-on exploration with simple tools",
    ],
    "mixed": [
        "Integrated literacy and math routines",
        "Theme-based exploration across subjects",
        "Social-emotional learning through stories and play",
    ],
}

LESSON_PRINTABLE_LIBRARY = {
    "literacy": [
        "Letter tracing worksheets",
        "Beginning sound match cards",
        "Sight word pocket chart cards",
        "Story sequence cut-and-paste activity",
    ],
    "math": [
        "Number tracing sheets",
        "Counting clip cards",
        "Pattern strip printable",
        "Shape hunt checklist",
    ],
    "social_emotional": [
        "Feelings wheel printable",
        "Classroom expectations poster",
        "Conflict-resolution prompt cards",
        "Calm corner reflection sheet",
    ],
    "science": [
        "Observation journal pages",
        "Life-cycle sequencing cards",
        "Weather tracking chart",
        "Simple experiment recording sheet",
    ],
    "mixed": [
        "Theme vocabulary cards",
        "Hands-on center rotation board",
        "At-home extension activity sheet",
        "Weekly reflection page",
    ],
}

SPANISH_BLOCKS = {
    "Morning meeting": "Reunion de la manana",
    "Mini-lesson": "Mini leccion",
    "Hands-on center": "Centro practico",
    "Movement or sensory": "Movimiento o sensorial",
    "Wrap-up reflection": "Reflexion final",
}

SPANISH_PRINTABLE_LIBRARY = {
    "literacy": [
        "Hojas para trazar letras",
        "Tarjetas para relacionar sonidos iniciales",
        "Tarjetas de palabras frecuentes",
        "Actividad de secuencia de historia recortar y pegar",
    ],
    "math": [
        "Hojas para trazar numeros",
        "Tarjetas de conteo con pinzas",
        "Plantilla imprimible de patrones",
        "Lista de busqueda de figuras",
    ],
    "social_emotional": [
        "Rueda de emociones imprimible",
        "Cartel de expectativas del aula",
        "Tarjetas de resolucion de conflictos",
        "Hoja de reflexion para rincon de calma",
    ],
    "science": [
        "Paginas de diario de observacion",
        "Tarjetas de secuencia de ciclo de vida",
        "Grafica de seguimiento del clima",
        "Hoja de registro de experimento simple",
    ],
    "mixed": [
        "Tarjetas de vocabulario por tema",
        "Tablero de rotacion de centros",
        "Actividad para casa",
        "Pagina de reflexion semanal",
    ],
}


# ─────────────────────────────────────────────
# COMPREHENSIVE LESSON THEMES (with daycare classroom context)
# ─────────────────────────────────────────────

COMPREHENSIVE_LESSON_THEMES = {
    "welcome_to_school": {
        "title": "Welcome to School",
        "emoji": "🏠",
        "month": "August/September",
        "overview": "The first week of school is about comfort and community. Children learn classroom routines, where things belong, and the names of their teachers and friends. Keep activities short, predictable, and warm.",
        "learning_objectives": {
            "literacy": [
                "Recognize own first name in print",
                "Learn classroom signs and symbols",
            ],
            "math": [
                "Sort classroom items by category",
                "Match same and different",
            ],
            "science": [
                "Explore the five senses through classroom tour",
                "Notice routines and patterns",
            ],
            "social_emotional": [
                "Learn classmates' names",
                "Practice greetings and goodbyes",
                "Follow simple classroom rules",
            ],
        },
        "key_vocabulary": "school, teacher, classroom, friend, hello, goodbye, please, thank you, line up, listen, share, rule",
        "materials_needed": [
            "Name tags with photos",
            "Classroom labels (door, sink, books)",
            "Class rules poster",
            "Photos of each child",
            "Welcome circle props",
            "Attendance chart",
            "Name puzzle pieces",
            "Crayons and large paper",
            "Friendship song cards",
        ],
        "songs_and_fingerplays": [
            "Hello, Hello, Hello (greeting)",
            "The More We Get Together",
            "Where Is Friend? (to Frère Jacques)",
            "Wheels on the Bus",
        ],
        "read_alouds": [
            "The Kissing Hand — Audrey Penn",
            "First Day Jitters — Julie Danneberg",
            "We Don't Eat Our Classmates — Ryan Higgins",
            "Llama Llama Misses Mama — Anna Dewdney",
        ],
        "family_take_home_note": "This week your child practiced classroom routines and learned new friends' names! Ask: Who is your teacher? What is your favorite spot in the classroom?",
        "teacher_tip": "Keep day-one transitions short and predictable. Children who cling to parents need quiet welcomes, not crowds. A photo of family in their cubby helps tremendously.",
        "daily_activities": {
            "monday": {
                "title": "Welcome & Hello",
                "circle_time": "Greet each child by name. Sing the Hello song. Show classroom rules with simple pictures (walking feet, listening ears, kind hands).",
                "center_activity": "Small-group classroom tour — visit each center and explore one toy from each.",
                "read_aloud": "The Kissing Hand by Audrey Penn",
            },
            "tuesday": {
                "title": "What's Your Name?",
                "circle_time": "Photo name game — hold up each child's photo and the class says their name together.",
                "center_activity": "Name puzzle — children trace their first name with a finger, then a marker.",
                "read_aloud": "First Day Jitters by Julie Danneberg",
            },
            "wednesday": {
                "title": "Our Classroom",
                "circle_time": "Tour the classroom labels (door, sink, library, blocks). Children point to each one as you say its name.",
                "center_activity": "Picture-matching of classroom items (cup→cup, book→book).",
                "read_aloud": "Llama Llama Misses Mama by Anna Dewdney",
            },
            "thursday": {
                "title": "Making Friends",
                "circle_time": "Friendship song. Each child shares one thing they like to do.",
                "art_center": "Partner art — pairs draw each other on a shared paper.",
                "read_aloud": "We Don't Eat Our Classmates by Ryan Higgins",
            },
            "friday": {
                "title": "Our Class is Special",
                "group_activity": "Class handprint mural on butcher paper titled 'Our Class.' Each child adds a painted handprint and signs (or stamps) their name.",
                "circle_time": "Review songs from the week. Celebrate a successful first week!",
            },
        },
    },
    "all_about_me": {
        "title": "All About Me",
        "emoji": "👤",
        "month": "September",
        "overview": "Children explore their own identity — body, family, likes, and what makes them special. Builds self-awareness, confidence, and the language to describe themselves.",
        "learning_objectives": {
            "literacy": [
                "Recognize the first letter of own name",
                "Use 'I am' and 'I like' sentence frames",
            ],
            "math": [
                "Measure and compare height",
                "Count body parts (2 eyes, 10 fingers)",
            ],
            "science": [
                "Identify major body parts and their functions",
                "Compare physical traits",
            ],
            "social_emotional": [
                "Express personal likes and dislikes",
                "Celebrate own uniqueness",
            ],
        },
        "key_vocabulary": "me, body, head, hands, feet, eyes, hair, tall, short, favorite, special, unique",
        "materials_needed": [
            "Hand mirrors",
            "Height chart on wall",
            "Paper plates for self-portraits",
            "Yarn (hair colors)",
            "Crayons and skin-tone markers",
            "Body outline butcher paper",
            "Family photo request slip",
        ],
        "songs_and_fingerplays": [
            "Head, Shoulders, Knees and Toes",
            "If You're Happy and You Know It",
            "The Hokey Pokey",
            "This Is Me (original chant)",
        ],
        "read_alouds": [
            "I Like Myself! — Karen Beaumont",
            "The Skin You Live In — Michael Tyler",
            "All Are Welcome — Alexandra Penfold",
            "Marisol McDonald Doesn't Match — Monica Brown",
        ],
        "family_take_home_note": "Help your child feel proud of who they are! Ask: What is your favorite thing about yourself? Send in a family photo for our class display.",
        "teacher_tip": "Use skin-tone crayons and markers for self-portraits — and make sure the package shows the full range. Children notice when their actual color is missing from the box.",
        "daily_activities": {
            "monday": {
                "title": "My Body",
                "circle_time": "Sing Head, Shoulders, Knees and Toes — fast, then slow, then silly.",
                "center_activity": "Trace child-sized body outlines on butcher paper. Children label parts.",
                "read_aloud": "The Skin You Live In by Michael Tyler",
            },
            "tuesday": {
                "title": "My Face",
                "circle_time": "Mirror exploration — children describe their own face (eye color, hair color).",
                "art_center": "Paper plate self-portraits with yarn for hair.",
                "read_aloud": "I Like Myself! by Karen Beaumont",
            },
            "wednesday": {
                "title": "How Tall Am I?",
                "math_activity": "Measure each child against a class height chart. Compare 'taller' and 'shorter.'",
                "center_activity": "Trace each child's hand and count fingers. Whose hand is biggest?",
                "read_aloud": "All Are Welcome by Alexandra Penfold",
            },
            "thursday": {
                "title": "My Favorites",
                "circle_time": "Each child shares a favorite color, food, and toy.",
                "math_center": "Class graph: favorite ice cream flavor (chocolate, vanilla, strawberry).",
                "read_aloud": "Marisol McDonald Doesn't Match by Monica Brown",
            },
            "friday": {
                "title": "I Am Special",
                "group_project": "Make 'All About Me' mini-books — each child completes pages: My name is ___, I am ___ years old, My favorite color is ___.",
                "circle_time": "Children share their books with the class.",
            },
        },
    },
}


def _format_comprehensive_theme(theme_data: Dict, language_mode: str, weeks: int = 1) -> Dict:
    """Format comprehensive theme data into a structured lesson plan with professional formatting."""
    
    # Build learning objectives by category
    formatted_objectives = {}
    for subject, objectives in theme_data.get("learning_objectives", {}).items():
        formatted_objectives[subject.replace("_", "-").title()] = objectives
    
    # Format daily activities with proper structure
    daily_activities_list = []
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for idx, (day_key, day_name) in enumerate(zip(weekdays, weekday_names)):
        day_data = theme_data.get("daily_activities", {}).get(day_key, {})
        if day_data:
            activity_obj = {
                "day": day_name,
                "title": day_data.get("title", ""),
                "activities": {},
            }
            
            # Map different activity keys to standardized labels
            for key in day_data:
                if key != "title":
                    label = key.replace("_", " ").title()
                    activity_obj["activities"][label] = day_data[key]
            
            daily_activities_list.append(activity_obj)
    
    return {
        "title": theme_data.get("title", "Untitled Theme"),
        "emoji": theme_data.get("emoji", "📚"),
        "month": theme_data.get("month", ""),
        "overview": theme_data.get("overview", ""),
        "learning_objectives": formatted_objectives,
        "key_vocabulary": theme_data.get("key_vocabulary", ""),
        "materials_needed": theme_data.get("materials_needed", []),
        "songs_and_fingerplays": theme_data.get("songs_and_fingerplays", []),
        "read_alouds": theme_data.get("read_alouds", []),
        "family_take_home_note": theme_data.get("family_take_home_note", ""),
        "teacher_tip": theme_data.get("teacher_tip", ""),
        "daily_activities": daily_activities_list,
    }


def _build_theme_printables(theme_data: Dict, language_mode: str, printable_count: int = 4) -> List[Dict[str, str]]:
    """Generate printable worksheets based on theme learning objectives."""
    documents: List[Dict[str, str]] = []
    theme_title = theme_data.get("title", "Theme")
    learning_objectives = theme_data.get("learning_objectives", {})
    
    subjects = list(learning_objectives.keys())
    
    for idx in range(printable_count):
        subject = subjects[idx % len(subjects)] if subjects else "Learning"
        objective = learning_objectives.get(subject, [""])[0] if learning_objectives.get(subject) else ""
        
        title = f"Worksheet {idx + 1}: {theme_title} - {subject}"
        
        instructions = _bilingual(
            "Instructions: Complete the activity with your learner. Review answers together and celebrate progress!",
            "Instrucciones: Completa la actividad con tu estudiante. ¡Revisen las respuestas juntas y celebren el progreso!",
            language_mode,
        )
        
        focus = _bilingual(
            f"Learning Focus: {objective}",
            f"Enfoque de aprendizaje: {objective}",
            language_mode,
        )
        
        content = "\n".join(
            [
                title,
                "=" * len(title),
                "",
                focus,
                instructions,
                "",
                _bilingual("Name: ____________________", "Nombre: ____________________", language_mode),
                _bilingual("Date: ____________________", "Fecha: ____________________", language_mode),
                "",
                _bilingual("Activity:", "Actividad:", language_mode),
                "_" * 50,
                "_" * 50,
                "_" * 50,
                "",
                _bilingual("Draw or write your answer:", "Dibuja o escribe tu respuesta:", language_mode),
                "_" * 50,
                "_" * 50,
                "",
                _bilingual("Circle the best answer:", "Encierra la mejor respuesta:", language_mode),
                "☐ A          ☐ B          ☐ C",
                "",
                _bilingual("Teacher/Parent Notes:", "Notas del maestro/padre:", language_mode),
                "_" * 50,
            ]
        )
        
        documents.append(
            {
                "id": f"printable_{idx + 1}",
                "title": title,
                "content": content,
                "format": "txt",
            }
        )
    
    return documents


def _normalize_focus(value: str) -> str:
    focus = (value or "mixed").strip().lower()
    return focus if focus in LESSON_PLAN_FOCUS_LIBRARY else "mixed"


def _normalize_audience(value: str) -> str:
    audience = (value or "preschool").strip().lower()
    if audience in {"preschool", "homeschool", "mixed"}:
        return audience
    return "preschool"


def _normalize_language_mode(value: str) -> str:
    language_mode = (value or "english").strip().lower()
    if language_mode in {"english", "spanish", "bilingual"}:
        return language_mode
    return "english"


def _bilingual(english_text: str, spanish_text: str, language_mode: str) -> str:
    if language_mode == "spanish":
        return spanish_text
    if language_mode == "bilingual":
        return f"{english_text} / {spanish_text}"
    return english_text


def _build_printable_documents(
    theme: str,
    audience_type: str,
    focus_area: str,
    language_mode: str,
    printable_resources: List[str],
) -> List[Dict[str, str]]:
    """Create worksheet-ready printable document payloads for UI download/printing."""
    documents: List[Dict[str, str]] = []

    for idx, title in enumerate(printable_resources, start=1):
        if language_mode == "bilingual" and " / " in title:
            worksheet_title = f"Worksheet {idx}: {title}"
        else:
            worksheet_title = _bilingual(
                f"Worksheet {idx}: {title}",
                f"Hoja de trabajo {idx}: {title}",
                language_mode,
            )
        instructions = _bilingual(
            "Instructions: Complete the activity with your learner and review answers together.",
            "Instrucciones: Completa la actividad con tu estudiante y revisen las respuestas juntos.",
            language_mode,
        )
        skill_focus = _bilingual(
            f"Skill focus: {focus_area.replace('_', ' ')}",
            f"Enfoque: {focus_area.replace('_', ' ')}",
            language_mode,
        )
        audience_line = _bilingual(
            f"Audience: {audience_type}",
            f"Audiencia: {audience_type}",
            language_mode,
        )
        prompt_line = _bilingual(
            f"Prompt: Use the {theme.lower()} theme to guide this worksheet task.",
            f"Actividad: Usa el tema de {theme.lower()} para guiar esta hoja.",
            language_mode,
        )

        content = "\n".join(
            [
                worksheet_title,
                "=" * len(worksheet_title),
                audience_line,
                skill_focus,
                instructions,
                prompt_line,
                "",
                _bilingual("Student Name: ____________________", "Nombre del estudiante: ____________________", language_mode),
                _bilingual("Date: ____________________", "Fecha: ____________________", language_mode),
                "",
                _bilingual("1. Draw or write your response below:", "1. Dibuja o escribe tu respuesta abajo:", language_mode),
                "__________________________________________",
                "__________________________________________",
                "",
                _bilingual("2. Circle or mark the best answer.", "2. Encierra o marca la mejor respuesta.", language_mode),
                "A) ____    B) ____    C) ____",
                "",
                _bilingual("Teacher/Parent Notes:", "Notas del maestro/padre:", language_mode),
                "__________________________________________",
                "__________________________________________",
            ]
        )

        documents.append(
            {
                "id": f"printable_{idx}",
                "title": worksheet_title,
                "content": content,
                "format": "txt",
            }
        )

    return documents


def generate_lesson_plan(
    theme: str,
    audience_type: str = "preschool",
    duration_weeks: int = 4,
    focus_area: str = "mixed",
    session_length_minutes: int = 45,
    language_mode: str = "english",
    include_printables: bool = True,
) -> Dict:
    """Generate a multi-week lesson plan framework with daily activities and printable suggestions.
    
    Supports both predefined comprehensive themes and custom theme generation.
    """

    normalized_theme = (theme or "Seasonal Learning").strip() or "Seasonal Learning"
    normalized_audience = _normalize_audience(audience_type)
    normalized_focus = _normalize_focus(focus_area)
    normalized_language = _normalize_language_mode(language_mode)
    weeks = max(1, min(duration_weeks, 12))
    minutes = max(20, min(session_length_minutes, 120))

    # Check if this is a comprehensive theme
    theme_key = normalized_theme.lower().replace(" ", "_")
    is_comprehensive_theme = theme_key in COMPREHENSIVE_LESSON_THEMES
    
    if is_comprehensive_theme:
        theme_data = COMPREHENSIVE_LESSON_THEMES[theme_key]
        formatted_theme = _format_comprehensive_theme(theme_data, normalized_language, weeks)
        
        # Build printables if requested
        printable_documents = []
        if include_printables:
            printable_documents = _build_theme_printables(
                theme_data,
                language_mode=normalized_language,
                printable_count=4
            )
        
        return {
            "plan_id": str(uuid.uuid4()),
            "theme": formatted_theme.get("title", normalized_theme),
            "emoji": formatted_theme.get("emoji", "📚"),
            "month": formatted_theme.get("month", ""),
            "audience_type": normalized_audience,
            "focus_area": normalized_focus,
            "language_mode": normalized_language,
            "duration_weeks": weeks,
            "session_length_minutes": minutes,
            "overview": formatted_theme.get("overview", ""),
            "learning_objectives": formatted_theme.get("learning_objectives", {}),
            "key_vocabulary": formatted_theme.get("key_vocabulary", ""),
            "materials_needed": formatted_theme.get("materials_needed", []),
            "songs_and_fingerplays": formatted_theme.get("songs_and_fingerplays", []),
            "read_alouds": formatted_theme.get("read_alouds", []),
            "family_take_home_note": formatted_theme.get("family_take_home_note", ""),
            "teacher_tip": formatted_theme.get("teacher_tip", ""),
            "daily_activities": formatted_theme.get("daily_activities", []),
            "printable_resources": [doc["title"] for doc in printable_documents] if printable_documents else [],
            "printable_documents": printable_documents,
            "is_comprehensive": True,
            "created_at": datetime.utcnow().isoformat(),
        }
    
    # Fallback to legacy custom theme generation
    focus_targets = LESSON_PLAN_FOCUS_LIBRARY[normalized_focus]
    printable_pool = LESSON_PRINTABLE_LIBRARY[normalized_focus]
    spanish_printable_pool = SPANISH_PRINTABLE_LIBRARY[normalized_focus]
    daily_blocks = [
        "Morning meeting",
        "Mini-lesson",
        "Hands-on center",
        "Movement or sensory",
        "Wrap-up reflection",
    ]

    weekly_plans = []
    for week in range(1, weeks + 1):
        week_title = f"Week {week}: {normalized_theme}"
        week_objectives = [
            _bilingual(
                focus_targets[(week - 1) % len(focus_targets)],
                focus_targets[(week - 1) % len(focus_targets)],
                normalized_language,
            ),
            _bilingual(
                focus_targets[week % len(focus_targets)],
                focus_targets[week % len(focus_targets)],
                normalized_language,
            ),
            _bilingual(
                f"Apply {normalized_theme.lower()} vocabulary through guided play and discussion",
                f"Aplicar vocabulario de {normalized_theme.lower()} mediante juego guiado y conversacion",
                normalized_language,
            ),
        ]

        daily_plan = []
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for idx, day in enumerate(weekdays):
            daily_plan.append(
                {
                    "day": day,
                    "objective": week_objectives[idx % len(week_objectives)],
                    "schedule": [
                        {
                            "block": _bilingual(daily_blocks[0], SPANISH_BLOCKS[daily_blocks[0]], normalized_language),
                            "minutes": max(8, round(minutes * 0.2)),
                            "activity": _bilingual(
                                f"Introduce {normalized_theme.lower()} question of the day and preview goals.",
                                f"Presenta la pregunta del dia sobre {normalized_theme.lower()} y los objetivos.",
                                normalized_language,
                            ),
                        },
                        {
                            "block": _bilingual(daily_blocks[1], SPANISH_BLOCKS[daily_blocks[1]], normalized_language),
                            "minutes": max(10, round(minutes * 0.25)),
                            "activity": _bilingual(
                                f"Teach mini concept on {normalized_focus.replace('_', ' ')} using visuals and modeling.",
                                f"Ensena un mini concepto de {normalized_focus.replace('_', ' ')} con apoyos visuales.",
                                normalized_language,
                            ),
                        },
                        {
                            "block": _bilingual(daily_blocks[2], SPANISH_BLOCKS[daily_blocks[2]], normalized_language),
                            "minutes": max(10, round(minutes * 0.25)),
                            "activity": _bilingual(
                                f"Center task: {printable_pool[(idx + week) % len(printable_pool)]}.",
                                f"Actividad de centro: {spanish_printable_pool[(idx + week) % len(spanish_printable_pool)]}.",
                                normalized_language,
                            ),
                        },
                        {
                            "block": _bilingual(daily_blocks[3], SPANISH_BLOCKS[daily_blocks[3]], normalized_language),
                            "minutes": max(8, round(minutes * 0.2)),
                            "activity": _bilingual(
                                f"Movement game tied to {normalized_theme.lower()} and collaborative play.",
                                f"Juego de movimiento relacionado con {normalized_theme.lower()} y trabajo colaborativo.",
                                normalized_language,
                            ),
                        },
                        {
                            "block": _bilingual(daily_blocks[4], SPANISH_BLOCKS[daily_blocks[4]], normalized_language),
                            "minutes": max(6, round(minutes * 0.1)),
                            "activity": _bilingual(
                                "Quick check for understanding and send-home prompt.",
                                "Verificacion rapida de comprension y actividad para casa.",
                                normalized_language,
                            ),
                        },
                    ],
                    "home_extension": _bilingual(
                        f"Family prompt: practice one {normalized_theme.lower()} activity at home for 10 minutes.",
                        f"Actividad en familia: practiquen una actividad de {normalized_theme.lower()} por 10 minutos en casa.",
                        normalized_language,
                    ),
                }
            )

        weekly_plans.append(
            {
                "week": week,
                "title": week_title,
                "objectives": week_objectives,
                "daily_plan": daily_plan,
                "assessment": _bilingual(
                    "Use observation checklist and student work samples to track progress.",
                    "Use una lista de observacion y muestras de trabajo para medir el progreso.",
                    normalized_language,
                ),
            }
        )

    printable_resources = printable_pool
    if normalized_language == "spanish":
        printable_resources = spanish_printable_pool
    elif normalized_language == "bilingual":
        printable_resources = [
            f"{eng} / {spa}" for eng, spa in zip(printable_pool, spanish_printable_pool)
        ]

    active_printables = printable_resources if include_printables else []
    printable_documents = _build_printable_documents(
        theme=normalized_theme,
        audience_type=normalized_audience,
        focus_area=normalized_focus,
        language_mode=normalized_language,
        printable_resources=active_printables,
    )

    return {
        "plan_id": str(uuid.uuid4()),
        "theme": normalized_theme,
        "audience_type": normalized_audience,
        "focus_area": normalized_focus,
        "language_mode": normalized_language,
        "duration_weeks": weeks,
        "session_length_minutes": minutes,
        "weekly_plans": weekly_plans,
        "printable_resources": active_printables,
        "printable_documents": printable_documents,
        "is_comprehensive": False,
        "instagram_promo_hooks": [
            _bilingual(
                f"Parents asked for done-for-you {normalized_theme.lower()} lesson plans, so we built them.",
                f"Las familias pidieron planes de {normalized_theme.lower()} listos para usar, y por eso los creamos.",
                normalized_language,
            ),
            _bilingual(
                f"Stop planning from scratch: this {weeks}-week {normalized_theme.lower()} kit is classroom-ready.",
                f"Deja de planear desde cero: este kit de {weeks} semanas sobre {normalized_theme.lower()} esta listo para clase.",
                normalized_language,
            ),
            _bilingual(
                "Comment LESSONS and we will send the tier that fits your school-year goals.",
                "Comenta LECCIONES y te enviamos el nivel que mejor se adapta a tus metas escolares.",
                normalized_language,
            ),
        ],
        "created_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 7. DJ PROFILE SETUP
# ─────────────────────────────────────────────

DJ_PROFILE_TEMPLATE = {
    "business_information": [
        {"id": "business_name", "label": "Business Name", "type": "text"},
        {"id": "owner_name", "label": "Owner Name", "type": "text"},
        {"id": "logo", "label": "Logo", "type": "text"},
        {"id": "website", "label": "Website", "type": "text"},
        {"id": "phone", "label": "Phone", "type": "text"},
        {"id": "email", "label": "Email", "type": "text"},
        {"id": "social_media_links", "label": "Social Media Links", "type": "textarea"},
    ],
    "services_offered": [
        "Weddings",
        "Quinceaneras",
        "Sweet 16s",
        "Corporate Events",
        "Bar/Bat Mitzvahs",
        "School Events",
        "Karaoke",
        "Trivia",
        "Singo/Music Bingo",
        "Holiday Parties",
        "Birthday Parties",
    ],
    "coverage_area": [
        {"id": "cities_served", "label": "Cities Served", "type": "textarea"},
        {"id": "travel_radius", "label": "Travel Radius", "type": "text"},
        {"id": "destination_events", "label": "Destination Events", "type": "text"},
    ],
    "equipment": [
        "Sound Systems",
        "Wireless Mics",
        "Ceremony Audio",
        "Uplighting",
        "Photo Booth",
        "Dancing on Clouds",
        "Cold Sparks",
        "Monogram",
        "Projector/Screen",
    ],
    "pricing": [
        {"id": "starting_price", "label": "Starting Price", "type": "number"},
        {"id": "ceremony_add_on", "label": "Ceremony Add-On", "type": "number"},
        {"id": "cocktail_hour_add_on", "label": "Cocktail Hour Add-On", "type": "number"},
        {"id": "travel_fees", "label": "Travel Fees", "type": "number"},
        {"id": "overtime_rate", "label": "Overtime Rate", "type": "number"},
    ],
}


def get_dj_profile_template() -> Dict:
    """Return the DJ profile setup template."""
    return {
        "profile_id": str(uuid.uuid4()),
        "template": DJ_PROFILE_TEMPLATE,
        "created_at": datetime.utcnow().isoformat(),
    }


def save_dj_profile(profile_id: str, profile: Dict) -> Dict:
    """Package DJ profile answers into a structured setup record."""
    return {
        "profile_id": profile_id,
        "profile": profile,
        "saved_id": str(uuid.uuid4()),
        "saved_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# 7. LEAD MANAGEMENT (CRM)
# ─────────────────────────────────────────────

LEAD_STATUS_OPTIONS = [
    "New Lead",
    "Contacted",
    "Consultation Scheduled",
    "Proposal Sent",
    "Follow Up Needed",
    "Booked",
    "Lost",
]

LEAD_CRM_TEMPLATE = {
    "lead_information": [
        {"id": "name", "label": "Name", "type": "text"},
        {"id": "phone", "label": "Phone", "type": "text"},
        {"id": "email", "label": "Email", "type": "text"},
        {"id": "event_date", "label": "Event Date", "type": "date"},
        {"id": "venue", "label": "Venue", "type": "text"},
        {"id": "event_type", "label": "Event Type", "type": "text"},
        {"id": "budget", "label": "Budget", "type": "text"},
        {"id": "referral_source", "label": "Referral Source", "type": "text"},
    ],
    "lead_status": LEAD_STATUS_OPTIONS,
    "notes_section": [
        {"id": "special_requests", "label": "Special requests", "type": "textarea"},
        {"id": "concerns", "label": "Concerns", "type": "textarea"},
        {"id": "follow_up_history", "label": "Follow-up history", "type": "textarea"},
    ],
}


def get_lead_crm_template() -> Dict:
    """Return the lead management CRM template."""
    return {
        "lead_id": str(uuid.uuid4()),
        "template": LEAD_CRM_TEMPLATE,
        "created_at": datetime.utcnow().isoformat(),
    }


def save_lead_crm_record(lead_id: str, lead: Dict) -> Dict:
    """Package lead details into a structured CRM record."""
    result = {
        "lead_id": lead_id,
        "lead": lead,
        "record_id": str(uuid.uuid4()),
        "saved_at": datetime.utcnow().isoformat(),
    }
    _append_record(LEADS_FILE, result)
    return result


# ─────────────────────────────────────────────
# 8. DJ SERVICE AGREEMENTS
# ─────────────────────────────────────────────

SERVICE_AGREEMENT_TEMPLATE = {
    "main_contract": {
        "client_information": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
            {"id": "phone", "label": "Phone", "type": "text"},
            {"id": "email", "label": "Email", "type": "text"},
            {"id": "address", "label": "Address", "type": "text"},
        ],
        "event_information": [
            {"id": "event_type", "label": "Event Type", "type": "text"},
            {"id": "event_date", "label": "Event Date", "type": "date"},
            {"id": "venue_name", "label": "Venue Name", "type": "text"},
            {"id": "venue_address", "label": "Venue Address", "type": "text"},
            {"id": "start_time", "label": "Start Time", "type": "time"},
            {"id": "end_time", "label": "End Time", "type": "time"},
        ],
        "services_included": [
            "DJ Service",
            "MC Service",
            "Ceremony Audio",
            "Cocktail Hour",
            "Reception",
            "Uplighting",
            "Photo Booth",
            "Cold Sparks",
            "Dancing on Clouds",
            "Monogram",
            "Karaoke",
            "Other",
        ],
        "financial_information": [
            {"id": "total_package_price", "label": "Total Package Price", "type": "number"},
            {"id": "retainer_amount", "label": "Retainer Amount", "type": "number"},
            {"id": "retainer_due_date", "label": "Retainer Due Date", "type": "date"},
            {"id": "balance_due_date", "label": "Balance Due Date", "type": "date"},
            {"id": "overtime_rate", "label": "Overtime Rate", "type": "number"},
        ],
        "terms_conditions": [
            "Retainer is non-refundable",
            "Client responsible for venue permissions",
            "DJ not responsible for power failures",
            "Force majeure clause",
            "Cancellation policy",
            "Overtime policy",
            "Equipment damage clause",
        ],
        "electronic_signatures": [
            {"id": "client_signature", "label": "Client Signature", "type": "text"},
            {"id": "dj_signature", "label": "DJ Signature", "type": "text"},
            {"id": "signature_date", "label": "Date", "type": "date"},
        ],
    },
    "payment_authorization_form": {
        "client_information": [
            {"id": "name", "label": "Name", "type": "text"},
            {"id": "email", "label": "Email", "type": "text"},
            {"id": "phone", "label": "Phone", "type": "text"},
        ],
        "payment_details": [
            {"id": "retainer_amount", "label": "Retainer Amount", "type": "number"},
            {"id": "remaining_balance", "label": "Remaining Balance", "type": "number"},
            {"id": "payment_schedule", "label": "Payment Schedule", "type": "textarea"},
        ],
        "payment_methods": ["Credit Card", "ACH", "Cash", "Check", "Venmo", "Zelle", "PayPal"],
        "agreement_text": "I authorize payment according to the contract terms.",
        "signature": [
            {"id": "signature", "label": "Signature", "type": "text"},
            {"id": "date", "label": "Date", "type": "date"},
        ],
    },
    "event_change_request_form": {
        "client_information": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
            {"id": "event_date", "label": "Event Date", "type": "date"},
        ],
        "requested_changes": [
            "Time Change",
            "Venue Change",
            "Additional Hours",
            "Added Services",
            "Removed Services",
        ],
        "details": [
            {"id": "reason_for_change", "label": "Reason for Change", "type": "textarea"},
            {"id": "additional_charges", "label": "Additional Charges", "type": "text"},
            {"id": "approval_signature", "label": "Approval Signature", "type": "text"},
        ],
    },
    "cancellation_request_form": {
        "client_information": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
            {"id": "event_information", "label": "Event Information", "type": "textarea"},
        ],
        "reason_for_cancellation": ["Illness", "Venue Issue", "Budget", "Personal", "Other"],
        "details": [
            {"id": "cancellation_date", "label": "Cancellation Date", "type": "date"},
            {
                "id": "acknowledgement_of_contract_terms",
                "label": "Acknowledgement of Contract Terms",
                "type": "textarea",
            },
            {"id": "signature", "label": "Signature", "type": "text"},
        ],
    },
    "final_payment_confirmation_form": {
        "fields": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
            {"id": "event_date", "label": "Event Date", "type": "date"},
            {"id": "contract_total", "label": "Contract Total", "type": "number"},
            {"id": "payments_received", "label": "Payments Received", "type": "number"},
            {"id": "remaining_balance", "label": "Remaining Balance", "type": "number"},
            {"id": "date_paid", "label": "Date Paid", "type": "date"},
            {"id": "payment_method", "label": "Payment Method", "type": "text"},
        ],
        "balance_paid_in_full": ["Yes", "No"],
    },
    "event_liability_waiver": {
        "fields": [
            {"id": "venue_information", "label": "Venue Information", "type": "textarea"},
            {"id": "equipment_placement", "label": "Equipment Placement", "type": "textarea"},
        ],
        "client_acknowledges": [
            "DJ equipment requires dedicated power",
            "Guests should not handle equipment",
            "Client responsible for damage caused by guests",
        ],
        "signature": [
            {"id": "signature", "label": "Signature", "type": "text"},
            {"id": "date", "label": "Date", "type": "date"},
        ],
    },
    "venue_information_form": {
        "fields": [
            {"id": "venue_name", "label": "Venue Name", "type": "text"},
            {"id": "venue_address", "label": "Venue Address", "type": "text"},
            {"id": "venue_contact", "label": "Venue Contact", "type": "text"},
            {"id": "venue_phone", "label": "Venue Phone", "type": "text"},
            {"id": "load_in_time", "label": "Load-In Time", "type": "time"},
            {"id": "load_out_time", "label": "Load-Out Time", "type": "time"},
            {"id": "parking_instructions", "label": "Parking Instructions", "type": "textarea"},
            {"id": "vendor_rules", "label": "Vendor Rules", "type": "textarea"},
            {"id": "insurance_requirements", "label": "Insurance Requirements", "type": "textarea"},
            {"id": "sound_restrictions", "label": "Sound Restrictions", "type": "textarea"},
            {"id": "curfew", "label": "Curfew", "type": "text"},
        ]
    },
    "music_licensing_content_agreement": {
        "fields": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
        ],
        "client_understands": [
            "Clean music may be required",
            "Requested songs may not be available",
            "DJ reserves right to decline offensive requests",
        ],
        "signature": [
            {"id": "signature", "label": "Signature", "type": "text"},
            {"id": "date", "label": "Date", "type": "date"},
        ],
    },
    "testimonial_media_release_form": {
        "fields": [
            {"id": "client_name", "label": "Client Name", "type": "text"},
        ],
        "may_use_for_marketing": [
            "Photos",
            "Videos",
            "Testimonials",
            "Social Media Content",
        ],
        "marketing_permission": ["Yes", "No"],
        "signature": [
            {"id": "signature", "label": "Signature", "type": "text"},
            {"id": "date", "label": "Date", "type": "date"},
        ],
    },
}


def get_service_agreement_template() -> Dict:
    """Return the full DJ service agreement forms template."""
    return {
        "agreement_id": str(uuid.uuid4()),
        "template": SERVICE_AGREEMENT_TEMPLATE,
        "created_at": datetime.utcnow().isoformat(),
    }


def save_service_agreement_pack(agreement_id: str, agreement_pack: Dict) -> Dict:
    """Save completed agreement forms as a single contract pack record."""
    result = {
        "agreement_id": agreement_id,
        "agreement_pack": agreement_pack,
        "record_id": str(uuid.uuid4()),
        "saved_at": datetime.utcnow().isoformat(),
    }
    _append_record(AGREEMENTS_FILE, result)
    return result


def save_sales_event(event: Dict) -> Dict:
    """Persist sales tracker events by offer slug (clicks, sold, revenue)."""
    slug = str(event.get("offer_slug") or "offer")
    price = float(event.get("price") or 0)
    event_type = str(event.get("event_type") or "click")

    tracker = _load_json_object(SALES_TRACKER_FILE)
    offers = tracker.get("offers", {})
    if slug not in offers:
        offers[slug] = {"clicks": 0, "sold": 0, "revenue": 0.0, "price": price}

    if event_type == "click":
        offers[slug]["clicks"] = int(offers[slug].get("clicks", 0)) + 1
    elif event_type == "sold":
        offers[slug]["sold"] = int(offers[slug].get("sold", 0)) + 1
        offers[slug]["revenue"] = float(offers[slug].get("revenue", 0.0)) + price

    tracker["offers"] = offers
    tracker["updated_at"] = datetime.utcnow().isoformat()
    _save_json(SALES_TRACKER_FILE, tracker)

    return {
        "success": True,
        "offer_slug": slug,
        "event_type": event_type,
        "tracker": tracker,
    }


def get_sales_tracker() -> Dict:
    """Return current sales tracker object."""
    tracker = _load_json_object(SALES_TRACKER_FILE)
    if "offers" not in tracker:
        tracker["offers"] = {}
    return tracker


# ─────────────────────────────────────────────
# 9. ADMIN DASHBOARD STATS
# ─────────────────────────────────────────────

def get_admin_stats() -> Dict:
    """Aggregate data from all saved records for the admin dashboard."""
    leads = _load_json(LEADS_FILE)
    quotes = _load_json(QUOTES_FILE)
    now = datetime.utcnow()
    current_month = now.strftime("%Y-%m")
    app_db = DatabaseManager(Settings().DATABASE_URL)

    # Monthly revenue — sum quotes generated this calendar month
    monthly_revenue = sum(
        q.get("total", 0) for q in quotes
        if q.get("quoted_at", "").startswith(current_month)
    )

    # Aggregate lead data
    upcoming_events: List[Dict] = []
    new_leads_count = 0
    contracts_outstanding = 0
    payments_due = 0
    event_type_counts: Dict[str, int] = {}
    referral_counts: Dict[str, int] = {}

    for record in leads:
        data = record.get("lead", {})
        status = data.get("lead_status", "").strip()
        event_date_str = data.get("event_date", "")
        event_type = data.get("event_type", "").strip() or "Unknown"
        referral = data.get("referral_source", "").strip() or "Unknown"

        if status == "New Lead":
            new_leads_count += 1
        if status == "Proposal Sent":
            contracts_outstanding += 1
        if status == "Booked":
            payments_due += 1

        # Upcoming booked events with a future date
        if status == "Booked" and event_date_str:
            try:
                evt_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                if evt_date >= now:
                    upcoming_events.append({
                        "name": data.get("name", "—"),
                        "event_type": event_type,
                        "event_date": event_date_str,
                        "venue": data.get("venue", "—"),
                    })
            except ValueError:
                pass

        # Tally event types and referral sources for all leads
        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        referral_counts[referral] = referral_counts.get(referral, 0) + 1

    upcoming_events.sort(key=lambda x: x["event_date"])

    top_referrals = sorted(referral_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    sales_tracker = get_sales_tracker()
    sales_offers = sales_tracker.get("offers", {})
    sales_clicks = sum(int(v.get("clicks", 0)) for v in sales_offers.values())
    sales_closed = sum(int(v.get("sold", 0)) for v in sales_offers.values())
    sales_revenue = sum(float(v.get("revenue", 0.0)) for v in sales_offers.values())

    return {
        "monthly_revenue": round(monthly_revenue, 2),
        "upcoming_events_count": len(upcoming_events),
        "upcoming_events": upcoming_events[:5],
        "multitasking360_applications": app_db.count_info_product_applications(),
        "new_leads": new_leads_count,
        "contracts_outstanding": contracts_outstanding,
        "payments_due": payments_due,
        "total_quotes": len(quotes),
        "total_leads": len(leads),
        "sales_clicks": sales_clicks,
        "sales_closed": sales_closed,
        "sales_revenue": round(sales_revenue, 2),
        "event_types_booked": event_type_counts,
        "top_referral_sources": [{"source": s, "count": c} for s, c in top_referrals],
    }
