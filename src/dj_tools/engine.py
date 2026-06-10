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
    {"id": "couple_names",      "label": "Couple's full names",                         "type": "text"},
    {"id": "anniversary_year",  "label": "Which anniversary? (e.g. 25th)",              "type": "text"},
    {"id": "event_date",        "label": "Event date",                                  "type": "date"},
    {"id": "venue_name",        "label": "Venue name & address",                        "type": "text"},
    {"id": "guest_count",       "label": "Estimated guest count",                       "type": "number"},
    {"id": "start_time",        "label": "Event start time",                            "type": "time"},
    {"id": "end_time",          "label": "Event end time",                              "type": "time"},
    {"id": "couple_intro_song", "label": "Couple entrance/introduction song",            "type": "text"},
    {"id": "first_dance_song",  "label": "First dance song (original or cover?)",        "type": "text"},
    {"id": "vow_renewal",       "label": "Any vow-renewal segment planned?",             "type": "text"},
    {"id": "toasts_speakers",   "label": "Who is speaking and when?",                    "type": "textarea"},
    {"id": "cake_cutting_song", "label": "Cake cutting song",                            "type": "text"},
    {"id": "must_play",         "label": "Songs from your era / must-play",              "type": "textarea"},
    {"id": "do_not_play",       "label": "Do-NOT-play songs or genres",                  "type": "textarea"},
    {"id": "vibe",              "label": "Desired vibe / energy",                        "type": "textarea"},
    {"id": "special_requests",  "label": "Anything else?",                               "type": "textarea"},
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
    {"id": "graduate_name", "label": "Graduate full name", "type": "text"},
    {"id": "school_name", "label": "School name", "type": "text"},
    {"id": "future_plans", "label": "Graduate's future plans", "type": "textarea"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "awards", "label": "Awards/accomplishments to announce", "type": "textarea"},
    {"id": "special_intros", "label": "Special introductions", "type": "textarea"},
    {"id": "slideshow", "label": "Slide show planned? Timing details", "type": "textarea"},
    {"id": "favorite_music", "label": "Graduate's favorite music", "type": "textarea"},
    {"id": "must_play", "label": "Must-play songs", "type": "textarea"},
    {"id": "do_not_play", "label": "Do-NOT-play songs", "type": "textarea"},
]

BABY_SHOWER_QUESTIONS = [
    {"id": "mom_name", "label": "Mom's name", "type": "text"},
    {"id": "theme", "label": "Shower theme", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "games_planned", "label": "Games planned", "type": "textarea"},
    {"id": "gift_opening", "label": "Gift opening time", "type": "time"},
    {"id": "family_recognitions", "label": "Family recognitions", "type": "textarea"},
    {"id": "music_preferences", "label": "Background music preferences", "type": "textarea"},
]

GENDER_REVEAL_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "reveal_method", "label": "Reveal method", "type": "textarea"},
    {"id": "countdown_timing", "label": "Countdown timing", "type": "text"},
    {"id": "photographer_coordination", "label": "Photographer coordination", "type": "textarea"},
    {"id": "special_music", "label": "Special music for reveal", "type": "textarea"},
    {"id": "family_announcements", "label": "Family announcements", "type": "textarea"},
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
    {"id": "honoree_name", "label": "Retiree full name", "type": "text"},
    {"id": "years_of_service", "label": "Years of service", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "favorite_music_era", "label": "Favorite music era", "type": "text"},
    {"id": "awards", "label": "Awards to present", "type": "textarea"},
    {"id": "speeches", "label": "Speech order", "type": "textarea"},
    {"id": "recognition_ceremony", "label": "Recognition ceremony details", "type": "textarea"},
    {"id": "video_tribute", "label": "Video tribute timing", "type": "textarea"},
]

PROM_QUESTIONS = [
    {"id": "school_name", "label": "School name", "type": "text"},
    {"id": "theme", "label": "Prom theme", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "song_requests", "label": "Song requests", "type": "textarea"},
    {"id": "prom_court", "label": "Prom King & Queen timing", "type": "textarea"},
    {"id": "school_rules", "label": "School rules", "type": "textarea"},
    {"id": "clean_music", "label": "Clean music requirements", "type": "textarea"},
]

HOMECOMING_DANCE_QUESTIONS = [
    {"id": "school_name", "label": "School name", "type": "text"},
    {"id": "theme", "label": "Theme", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "student_age_group", "label": "Student age group", "type": "text"},
    {"id": "announcement_requirements", "label": "Announcement requirements", "type": "textarea"},
    {"id": "dance_contests", "label": "Dance contests", "type": "textarea"},
    {"id": "school_restrictions", "label": "School restrictions", "type": "textarea"},
]

SCHOOL_DANCE_QUESTIONS = [
    {"id": "school_name", "label": "School name", "type": "text"},
    {"id": "grade_levels", "label": "Grade levels", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "clean_edit_requirements", "label": "Clean edit requirements", "type": "textarea"},
    {"id": "school_rules", "label": "School rules", "type": "textarea"},
    {"id": "chaperone_contact", "label": "Chaperone contact", "type": "text"},
    {"id": "trending_music", "label": "Current trending music", "type": "textarea"},
]

FUNDRAISER_CHARITY_GALA_QUESTIONS = [
    {"id": "organization", "label": "Organization", "type": "text"},
    {"id": "mission", "label": "Mission", "type": "textarea"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "silent_auction", "label": "Silent auction details", "type": "textarea"},
    {"id": "live_auction", "label": "Live auction details", "type": "textarea"},
    {"id": "sponsors", "label": "Sponsors", "type": "textarea"},
    {"id": "donation_announcements", "label": "Donation announcements", "type": "textarea"},
]

COMMUNITY_FESTIVAL_QUESTIONS = [
    {"id": "event_name", "label": "Festival name", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "audience_demographics", "label": "Audience demographics", "type": "textarea"},
    {"id": "stage_schedule", "label": "Stage schedule", "type": "textarea"},
    {"id": "sponsors", "label": "Sponsors", "type": "textarea"},
    {"id": "vendors", "label": "Vendors", "type": "textarea"},
    {"id": "announcements", "label": "Announcements", "type": "textarea"},
    {"id": "entertainment_schedule", "label": "Entertainment schedule", "type": "textarea"},
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
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "venue_name", "label": "Venue name & address", "type": "text"},
    {"id": "ribbon_cutting_time", "label": "Ribbon cutting time", "type": "time"},
    {"id": "vip_guests", "label": "VIP guests", "type": "textarea"},
    {"id": "sponsor_recognition", "label": "Sponsor recognition", "type": "textarea"},
    {"id": "promotions", "label": "Promotions", "type": "textarea"},
    {"id": "giveaways", "label": "Giveaways", "type": "textarea"},
]

NETWORKING_EVENT_QUESTIONS = [
    {"id": "event_name", "label": "Event name", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "background_music_only", "label": "Background music only?", "type": "text"},
    {"id": "company_introductions", "label": "Company introductions", "type": "textarea"},
    {"id": "sponsor_recognition", "label": "Sponsor recognition", "type": "textarea"},
    {"id": "announcements", "label": "Announcements", "type": "textarea"},
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
    {"id": "age_group", "label": "Age group", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "contest_prizes", "label": "Contest prizes", "type": "textarea"},
    {"id": "rotation_preferences", "label": "Rotation preferences", "type": "textarea"},
    {"id": "clean_music", "label": "Clean music required?", "type": "text"},
]

MUSIC_BINGO_SINGO_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "number_of_rounds", "label": "Number of rounds", "type": "number"},
    {"id": "prize_structure", "label": "Prize structure", "type": "textarea"},
    {"id": "theme_rounds", "label": "Theme rounds", "type": "textarea"},
    {"id": "audience_demographics", "label": "Audience demographics", "type": "textarea"},
]

TRIVIA_NIGHT_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "categories", "label": "Categories", "type": "textarea"},
    {"id": "number_of_rounds", "label": "Number of rounds", "type": "number"},
    {"id": "prizes", "label": "Prizes", "type": "textarea"},
    {"id": "team_or_individual", "label": "Team or individual play", "type": "text"},
]

CHRISTMAS_PARTY_QUESTIONS = [
    {"id": "event_type", "label": "Family or corporate event?", "type": "text"},
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "gift_exchange", "label": "Gift exchange details", "type": "textarea"},
    {"id": "santa_arrival", "label": "Santa arrival planned?", "type": "text"},
    {"id": "holiday_music_preferences", "label": "Holiday music preferences", "type": "textarea"},
]

NEW_YEARS_EVE_PARTY_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "countdown_timing", "label": "Countdown timing", "type": "text"},
    {"id": "champagne_toast", "label": "Champagne toast details", "type": "textarea"},
    {"id": "midnight_song", "label": "Midnight song", "type": "text"},
    {"id": "balloon_drop", "label": "Balloon drop planned?", "type": "text"},
]

HALLOWEEN_PARTY_QUESTIONS = [
    {"id": "event_date", "label": "Event date", "type": "date"},
    {"id": "costume_contest", "label": "Costume contest planned?", "type": "text"},
    {"id": "contest_categories", "label": "Contest categories", "type": "textarea"},
    {"id": "prize_announcements", "label": "Prize announcements", "type": "textarea"},
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

#DJLife #DJ {specialty.replace(' ', '')} #EventDJ #DJBusiness #BluBloods""",

    """{hook}

No one talks about the business side of DJing.

Getting leads. Converting them. Running the event without stress. Getting paid what you are worth.

I built a platform that handles all of it — specifically for {specialty} DJs.

{cta}

#DJBusiness #DJ {specialty.replace(' ', '')} #DJTips #BluBloods""",

    """{hook}

Drop a 🎵 below if you want the full breakdown.

{cta}

#DJLife #EventPlanning #DJ {specialty.replace(' ', '')} #BluBloods #DJTips""",
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
        caption = template.format(hook=hook, years=years_experience, cta=cta, specialty=specialty.replace("_", " ").title())

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
