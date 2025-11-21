#!/usr/bin/env python3
"""
TOKNNews — Chip Opening Line Engine
Hybrid deterministic + GPT-enhanced system.
"""

import random
import time

# ---------------------------------------------------------
# Deterministic greeting templates
# ---------------------------------------------------------

TIME_OF_DAY_GREETS = {
    "morning": [
        "Good morning — here’s what you need to know.",
        "Good morning — let's get into the top stories.",
        "Good morning — markets are coming online, so let’s dive in."
    ],
    "afternoon": [
        "Good afternoon — here's what’s shaping the session.",
        "Good afternoon — let’s dig into today’s developments.",
        "Good afternoon — lots to cover, so let’s get started."
    ],
    "evening": [
        "Good evening — here’s what’s moving markets.",
        "Good evening — let's break down the biggest stories.",
        "Good evening — there’s plenty to unpack tonight."
    ],
    "latenight": [
        "Good evening — welcome to Token News LateNight.",
        "Good evening — it’s a wild one tonight.",
        "Good evening — let’s recap the chaos of the day."
    ]
}

HOLIDAY_GREETS = {
    "new_year": "Good evening — as we kick off a new year, here’s what matters.",
    "christmas": "Good evening — holiday markets are thin, but news never sleeps.",
    "thanksgiving": "Good evening — on a quiet holiday session, here’s what’s moving.",
    "independence_day": "Good evening — holiday volatility is in play, so let’s zoom out."
}

SEASONAL_GREETS = {
    "q1": "Good morning — Q1 flow is picking up.",
    "q2": "Good morning — Q2 rotation is underway.",
    "q3": "Good morning — mid-year markets are getting interesting.",
    "q4": "Good morning — year-end positioning is taking shape."
}

# ---------------------------------------------------------
# Market-aware inject (ONLY for Option C: rare + severe mood)
# ---------------------------------------------------------

MARKET_MOOD_LINES = {
    "volatility": [
        "Volatility is spiking — let's break it down.",
        "Markets are under pressure — here’s what to watch.",
        "It’s a tense session — here’s the signal beneath the noise."
    ],
    "fear": [
        "Sentiment is rattled — let's get into why.",
        "Risk-off energy is dominating the day.",
        "There’s real caution in the air — here’s what’s happening."
    ],
    "euphoria": [
        "Momentum is running hot — here’s what matters.",
        "Markets are ripping — let’s unpack the drivers.",
        "Risk-on everywhere — let’s walk through it."
    ]
}

# ---------------------------------------------------------
# Hybrid Open Engine
# ---------------------------------------------------------

def chip_open_line(time_of_day: str = "morning",
                   holiday: str = None,
                   season: str = None,
                   market_mood: str = "calm",
                   gpt_func=None,
                   headlines=None):
    """
    Builds Chip's opening line.
    - Deterministic templates first
    - GPT enhancement optional
    """

    # -------------------------------------------------
    # 1. Holiday override
    # -------------------------------------------------
    if holiday and holiday in HOLIDAY_GREETS:
        line = HOLIDAY_GREETS[holiday]

    # -------------------------------------------------
    # 2. Time-of-day default
    # -------------------------------------------------
    else:
        pool = TIME_OF_DAY_GREETS.get(time_of_day, TIME_OF_DAY_GREETS["morning"])
        line = random.choice(pool)

    # -------------------------------------------------
    # 3. Seasonal add-on (optional flavor)
    # -------------------------------------------------
    if season in SEASONAL_GREETS:
        line = f"{line} {SEASONAL_GREETS[season]}"

    # -------------------------------------------------
    # 4. Market mood inject (OPTION C: severe moods only)
    # -------------------------------------------------
    if market_mood in ("volatility", "fear", "euphoria"):
        mood_pool = MARKET_MOOD_LINES.get(market_mood, [])
        if mood_pool:
            mood_line = random.choice(mood_pool)
            line = f"{line} {mood_line}"

    # -------------------------------------------------
    # 5. GPT Enhancement (optional)
    # -------------------------------------------------
    if gpt_func:
        try:
            # Provide GPT with context to refine Chip’s line
            gpt_prompt = (
                "You are Chip, the rational host of Token News. "
                "Rewrite this greeting to be crisp, calm, and time-appropriate. "
                "Do not add hype. Do not repeat the headline. "
                f"Opening line: {line}"
            )
            enhanced = gpt_func(gpt_prompt)
            if enhanced:
                line = enhanced
        except Exception:
            pass

    return line.strip()
