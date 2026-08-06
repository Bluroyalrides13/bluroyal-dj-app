"""Single source of truth for MT360 / Código de Poder 777 offer pricing.

Both the full API router and the standalone MT360 app create Stripe checkout
sessions from this table. It lives here so the two can never disagree about
what something costs.

The slugs are Stripe-facing identifiers — renaming one breaks live checkout
links and any session already in flight. Display names are safe to change.
"""

MT360_OFFER_PRICING = {
    "quickstart-sprint": {"name": "QuickStart Sprint", "amount_cents": 4700},
    "mini-launch-kit": {"name": "Mini Launch Kit", "amount_cents": 9700},
    "diy-course": {"name": "DIY Course", "amount_cents": 19700},
    "group-mentorship": {"name": "Group Mentorship", "amount_cents": 79700},
    "vip-coaching": {"name": "VIP Coaching", "amount_cents": 349700},
    "done-with-you-business-launch": {"name": "Done-With-You Business Launch", "amount_cents": 999700},
    "signature-tools-a-la-carte": {"name": "Signature Poder 777 Tools", "amount_cents": 1297},
}
