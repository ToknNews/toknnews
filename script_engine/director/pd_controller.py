#!/usr/bin/env python3
"""
TOKNNews — PD Controller (Master Orchestrator)
Module C-7
"""

import time

# === Correct LIVE imports (no backend.* paths) ===
from script_engine.director.director_state import load_state, save_state
from script_engine.director.segment_router import route_segment
from script_engine.director.ad_logic import should_insert_ad


# =====================================================================
# Entry point called by Script Engine V3
# =====================================================================

def run_pd(headline: str):
    """
    The Programming Director (PD) orchestrates:
      - segment type
      - anchor selection
      - Bitsy/Vega allowances
      - show intro logic
      - ad insertion
    """

    state = load_state()

    # -----------------------------------------------------
    # Determine segment type from the router
    # -----------------------------------------------------
    segment_type = route_segment(headline, state)

    # -----------------------------------------------------
    # Anchor selection rules (fallback if none)
    # NOTE: In PD 2.0 this will be domain → anchor scoring
    # -----------------------------------------------------
    anchors = state.get("next_anchors", ["reef", "lawson", "bond"])

    # -----------------------------------------------------
    # Simple Bitsy / Vega rules (pre-integration stage)
    # -----------------------------------------------------
    allow_bitsy = False
    allow_vega = False

    if segment_type == "headline":
        allow_bitsy = True
        allow_vega = True

    if segment_type == "breaking":
        allow_bitsy = False
        allow_vega = False

    # -----------------------------------------------------
    # Determine if we need to run show intro
    # -----------------------------------------------------
    show_intro = False
    if not state.get("intro_played", False):
        show_intro = True
        state["intro_played"] = True

    # -----------------------------------------------------
    # Ad break logic
    # -----------------------------------------------------
    insert_ad = should_insert_ad(state.get("cycle_index", 0))

    # -----------------------------------------------------
    # Save state back out
    # -----------------------------------------------------
    save_state(state)

    # -----------------------------------------------------
    # PD return bundle
    # -----------------------------------------------------
    return {
        "segment_type": segment_type,
        "anchors": anchors,
        "allow_bitsy": allow_bitsy,
        "allow_vega": allow_vega,
        "show_intro": show_intro,
        "insert_ad": insert_ad
    }


# ---------------------------------------------------------
# Anchor logic
# ---------------------------------------------------------

def select_anchors(state, headline):
    h = headline.lower()
    if "regulat" in h or "sec" in h:
        return ["lawson"]
    if "solana" in h or "defi" in h:
        return ["reef"]
    if "market" in h or "macro" in h or "inflation" in h:
        return ["bond"]
    # fallback: choose from last used rotation
    return ["reef", "lawson", "bond"]


# ---------------------------------------------------------
# Bitsy / Vega PD control
# ---------------------------------------------------------

def allow_bitsy_pd(state, segment_type):
    if segment_type in ["breaking", "show_intro"]:
        return False
    # cooldown: once per 10 segments
    return state["cycle_index"] % 10 == 0


def allow_vega_pd(state, segment_type):
    if segment_type == "show_intro":
        return True  # Vega intro voice-over only
    if segment_type == "breaking":
        return False
    # cooldown: once per 4 segments
    return state["cycle_index"] % 4 == 0
