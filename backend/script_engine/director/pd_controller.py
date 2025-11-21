#!/usr/bin/env python3
"""
TOKNNews — PD Controller (Clean Integrated Build)
Controls:
 - Segment type (headline / breaking / show_intro)
 - Hybrid anchor selection (EpisodeBuilder suggestion + PD override)
 - Daypart intelligence
 - Bitsy/Vega cadence rules
 - Intro logic
 - Ad insertion
 - State persistence
"""

import time

# State + routing imports
from script_engine.director.director_state import load_state, save_state
from script_engine.director.segment_router import route_segment
from script_engine.director.ad_logic import should_insert_ad


# =====================================================================
# Anchor selection helpers
# =====================================================================

def select_anchors(state, headline):
    """
    Basic domain-based anchor selection.
    PD may override this depending on suggested_anchor or breaking.
    """
    h = headline.lower()

    if "regulat" in h or "sec" in h or "lawsuit" in h:
        return ["lawson"]

    if "solana" in h or "defi" in h or "liquidity" in h:
        return ["reef"]

    if "market" in h or "macro" in h or "inflation" in h:
        return ["bond"]

    if "on-chain" in h or "blockchain data" in h:
        return ["ledger"]

    if "ai" in h or "compute" in h or "model" in h:
        return ["neura"]

    if "funding" in h or "venture" in h:
        return ["cap"]

    if "retail" in h or "meme" in h or "community" in h:
        return ["penny"]

    # Fallback: rotation pool
    return ["reef", "lawson", "bond"]



# =====================================================================
# HYBRID ANCHOR OVERLAY (EpisodeBuilder + PD Override)
# =====================================================================

def apply_hybrid_anchor_logic(anchors, suggested_anchor, pd_flags):
    """
    Hybrid logic:
       - EpisodeBuilder suggests primary
       - PD overrides ONLY when breaking or override mode
       - Otherwise, suggested anchor becomes primary
    """
    if not suggested_anchor:
        return anchors

    # PD override modes always win
    if pd_flags.get("is_breaking") or pd_flags.get("allow_override"):
        return anchors

    # PB suggestion wins in normal segments
    if suggested_anchor not in anchors:
        return [suggested_anchor] + anchors

    # PB suggestion already primary or present
    return anchors



# =====================================================================
# DUO-ANCHOR MAPPING (Optional Panels)
# =====================================================================

DUO_MAP = {
    "reef": "bond",
    "lawson": "bond",
    "penny": "cash",
    "bond": "lawson",
    "cash": "penny",
    "ledger": "reef",
    "neura": "bond",
}



def apply_duo_anchor(anchors):
    """
    Enables duo segments when appropriate.
    """
    primary = anchors[0]

    if primary in DUO_MAP:
        secondary = DUO_MAP[primary]
        if secondary not in anchors:
            anchors.append(secondary)

    return anchors



# =====================================================================
# MAIN PD CONTROLLER
# =====================================================================

def run_pd(headline, suggested_anchor=None):
    state = load_state()

    # ------------------------------------------
    # 1. Determine segment type
    # ------------------------------------------
    segment_type = route_segment(headline, state)

    # ------------------------------------------
    # 2. Build PD flags
    # ------------------------------------------
    pd_flags = {
        "is_breaking": segment_type == "breaking",
        "allow_override": segment_type == "breaking",  # future expansion
    }

    # ------------------------------------------
    # 3. Select anchors + Hybrid Override
    # ------------------------------------------
    anchors = select_anchors(state, headline)
    anchors = apply_hybrid_anchor_logic(anchors, suggested_anchor, pd_flags)

    # ------------------------------------------
    # 4. Enable duo anchors (optional)
    # ------------------------------------------
    anchors = apply_duo_anchor(anchors)

    # ------------------------------------------
    # 5. Daypart intelligence (tone & pacing)
    # ------------------------------------------
    hour = time.localtime().tm_hour

    if 5 <= hour < 12:
        daypart = "morning"
    elif 12 <= hour < 17:
        daypart = "afternoon"
    elif 17 <= hour < 22:
        daypart = "evening"
    else:
        daypart = "latenight"

    pd_flags["daypart"] = daypart

    # ------------------------------------------
    # 6. Bitsy / Vega persona gating
    # ------------------------------------------
    # Vega: pacing + intros + late-night presence
    if segment_type == "breaking":
        allow_vega = False
    elif segment_type == "show_intro":
        allow_vega = True
    elif daypart == "latenight":
        allow_vega = True
    else:
        allow_vega = (state.get("cycle_index", 0) % 4 == 0)

    # Bitsy: culture, hype, chaos
    if segment_type == "breaking":
        allow_bitsy = False
    elif daypart == "morning":
        allow_bitsy = False  # too early for chaos
    elif daypart == "latenight":
        allow_bitsy = True   # late-night chaos allowed
    else:
        allow_bitsy = (state.get("cycle_index", 0) % 6 == 0)

    # ------------------------------------------
    # 7. Show Intro
    # ------------------------------------------
    show_intro = False
    if not state.get("intro_played", False):
        show_intro = True
        state["intro_played"] = True

    # ------------------------------------------
    # 8. Ad Insertion
    # ------------------------------------------
    insert_ad = should_insert_ad(state.get("cycle_index", 0))

    # ------------------------------------------
    # 9. Persist updated PD state
    # ------------------------------------------
    save_state(state)

    # ------------------------------------------
    # 10. Full PD Configuration Return Bundle
    # ------------------------------------------
    return {
        "segment_type": segment_type,
        "anchors": anchors,
        "allow_bitsy": allow_bitsy,
        "allow_vega": allow_vega,
        "daypart": daypart,
        "show_intro": show_intro,
        "insert_ad": insert_ad,
    }
