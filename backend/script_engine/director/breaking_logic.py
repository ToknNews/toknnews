# backend/script_engine/director/breaking_logic.py

# -------- Escalation Level Engine (Stage 6/7) --------

def compute_escalation_level(story_queue, state, daypart, energy):
    """
    Compute escalation (0–3) based on importance, sentiment, keywords, etc.
    This version aligns with your enriched story format.
    """

    if not story_queue:
        return 0

    story = story_queue[0]

    # Pull fields with safe defaults
    importance = story.get("importance", 5)  # 1–10 scale
    sentiment = story.get("sentiment", "neutral")
    headline = story.get("headline", "").lower()

    # Start baseline
    level = 0

    # Strong importance
    if importance >= 8:
        level = max(level, 2)
    if importance >= 9:
        level = max(level, 3)

    # Negative sentiment elevates
    if sentiment == "negative":
        level = max(level, 2)

    # Keyword triggers
    critical_terms = ["hack", "exploit", "liquidation", "crash", "attack", "breach", "emergency"]
    if any(term in headline for term in critical_terms):
        level = max(level, 3)

    # Breaking → direct escalation
    if state.breaking_queue:
        level = max(level, 3)

    return level

def check_breaking_interrupt(state):
    """
    Minimal version:
    If anything is in state.breaking_queue, treat it as breaking news.
    Later this will check severity, age, domain, etc.
    """
    if not state.breaking_queue:
        return None

    return state.breaking_queue[0]  # top of queue

# -------- Show Reset Helper (Stage 6/7) --------

from datetime import datetime, timedelta

def should_reset_show(state, story_queue):
    print("\n--- DEBUG: should_reset_show ---")
    print("last_intro_age_minutes      =", (datetime.utcnow() - state.last_intro_time).total_seconds() / 60)
    print("intro_interval_minutes      =", state.intro_interval_minutes)
    print("last_reset_age_minutes      =", (datetime.utcnow() - state.last_reset_time).total_seconds() / 60)
    print("reset_interval_minutes      =", state.reset_interval_minutes)
    print("story_queue_length          =", len(story_queue))
    print("segment_history_last        =", state.segment_history[-1] if state.segment_history else None)
    print("breaking_queue_empty        =", not state.breaking_queue)
    """
    Returns True if Chip should perform a mid-show reset.
    Very lightweight conditions — full tuning comes later.
    """

    now = datetime.utcnow()

    # 1. Hard reset: too long since last Intro
    if now - state.last_intro_time > timedelta(minutes=state.intro_interval_minutes):
        return True

    # 2. Soft reset interval
    if now - state.last_reset_time > timedelta(minutes=state.reset_interval_minutes):
        return True

    # 3. Many fresh headlines (e.g., RSS/API flood)
    if len(story_queue) >= 3:
        return True

    # 4. Breaking news just ended
    if (
        state.segment_history 
        and state.segment_history[-1] == "breaking" 
        and not state.breaking_queue
    ):
        return True

    return False

def reset_allowed(state):
    print("\n--- DEBUG: reset_allowed ---")
    print("escalation_level            =", getattr(state, "escalation_level", None))
    print("last_reset_age_seconds      =", (datetime.utcnow() - state.last_reset_time).total_seconds())
    print("reset_cooldown_seconds      =", state.reset_cooldown_seconds)
    """
    Returns True if Chip Reset is eligible based on:
    - cooldown timing
    - escalation level
    """

    now = datetime.utcnow()

    # cooldown check
    since_last_reset = (now - state.last_reset_time).total_seconds()
    if since_last_reset < state.reset_cooldown_seconds:
        return False

    # require moderate or higher escalation
    if getattr(state, "escalation_level", 0) < 2:
        return False

    return True
