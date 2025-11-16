# backend/script_engine/director/ad_logic.py

from datetime import datetime, timedelta


def should_run_ad(state, daypart) -> bool:
    """
    Minimal ad/promo check.

    Rules:
    - Must be at least 4 minutes since last promo block.
    - During morning/day: ads allowed but less frequent.
    - During evening/late-night: ads/promo more allowed.
    """

    now = datetime.utcnow()
    since_last = (now - state.last_promo_time).total_seconds()

    # Require 4-minute buffer between promos
    if since_last < 240:
        return False

    # Professional daytime → ads allowed but stricter
    if daypart in ["day", "morning"]:
        # Only allow if > 6 minutes
        return since_last > 360

    # Evening or late-night → more flexible
    return True
