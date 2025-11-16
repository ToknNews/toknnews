# backend/script_engine/director/segment_router.py

def route_next_segment(state, story_queue, energy, daypart) -> str:
    """
    Stage 3 routing:
    1. Recovery from vega_pad → force news
    2. Breaking
    3. News
    4. Banter
    5. Expose
    6. Fallback banter
    """

    # 👇 NEW: if last segment was vega_pad, ALWAYS recover with news
    if state.last_segment == "vega_pad":
        state.last_segment = "news"  # reset state
        return "news"

    # Bitsy meta recovery
    if state.last_segment == "bitsy_meta":
        state.last_segment = "news"
        return "news"

    # Breaking news
    if state.breaking_queue:
        return "breaking"

    # News queue
    if story_queue:
        return "news"

    # High-energy filler
    if energy in ["high", "medium_high"]:
        return "banter"

    # Low energy → exposé mode
    if energy == "low":
        return "expose"

    # Fallback
    return "banter"
