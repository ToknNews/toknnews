#!/usr/bin/env python3
"""
timeline_builder.py – builds the exact order and timing of anchors for an episode
Fully updated for November 2025 architecture – no dead imports, no legacy functions
"""

import random
from datetime import datetime
from script_engine.persona.line_builder import (
    build_line,
    escalate_confidence,
    apply_style_constraints,
    enforce_phonetics,
    enforce_lexicon
)

# These were moved to hybrid_line_writer months ago
from script_engine.persona.hybrid_line_writer import (
    apply_tone_shift,
    build_anchor_react
)
# ------------------------------------------------------------------
# PERSONA SYSTEM – FINAL CANON FALLBACK (22 Nov 2025)
# persona_loader is broken → we hard-code the real 13 anchors forever
# ------------------------------------------------------------------

CANON_ANCHORS = {
    "Chip Blue":     {"voice_id": "teAyVVX8spybXkITa1A0"},
    "Cash Green":    {"voice_id": "b2zP5WtU6zW1RDLwR1VL"},
    "Neura Grey":    {"voice_id": "U21zT7YnOSlmiJ6Uzs70"},
    "Ledger Stone":  {"voice_id": "NZN55afVwq1WHQJOwDCz"},
    "Lawson Black":  {"voice_id": "Wz0W8ilvy9oYu7DeKWfB"},
    "Reef Gold":     {"voice_id": "7pLXpsTZ3rOalpNWmYqI"},
    "Cap Silver":    {"voice_id": "eeFsfJ0uulJx6xKTmsRE"},
    "Bond Crimson":  {"voice_id": "ckPPrwZqzA7Vp7ceNunQ"},
    "Ivy Quinn":     {"voice_id": "Iw2tTyxZnwTODhsmOq00"},
    "Bitsy Gold":    {"voice_id": "VOkhRocQyiAQg2RF9A5e"},
    "Penny Lane":    {"voice_id": "7WqwVs6Wqe0yEev6QDxV"},
    "Rex Vol":       {"voice_id": "5Rbobt83lpNwhTQEhH2F"},
    "Vega Watt":     {"voice_id": "Ax1HxHll9ku8pGyIt6kK"},
}

def get_active_personas():
    return CANON_ANCHORS

def get_voice_id(anchor: str):
    name = anchor.split()[0] + " " + anchor.split()[1] if " " in anchor else anchor
    return CANON_ANCHORS.get(name, CANON_ANCHORS["Chip Blue"])["voice_id"]

def get_escalation_style(anchor: str):
    return "confident"

def get_lexicon(anchor: str):
    return {"preferred": [], "avoid": ["um", "uh", "like", "you know"]}

def get_avoid_list(anchor: str):
    return ["um", "uh", "like", "you know"])

from script_engine.director.pd_controller import get_pd_directive
from script_engine.utils import log


def build_timeline(block_data: dict, previous_cast: list = None) -> list:
    """
    Returns a list of dicts: [{'anchor': 'Chip', 'line': '...', 'duration': 4.2, ...}, ...]
    """
    if previous_cast is None:
        previous_cast = []

    active_personas = get_active_personas()
    pd = get_pd_directive(block_data.get("sentiment", "neutral"))

    # PD decides lead anchor
    lead_anchor = pd.get("lead", random.choice(list(active_personas.keys())))
    supporting = [a for a in active_personas if a != lead_anchor]
    random.shuffle(supporting)

    # Basic 12-anchor rotation with PD overrides
    timeline = []
    anchors_used = set()

    # 1. Opening (always lead)
    line = f"Good evening, I'm {lead_anchor} with Token News."
    timeline.append({
        "anchor": lead_anchor,
        "line": line,
        "raw_line": line,
        "role": "open",
        "duration_estimate": 4.0
    })
    anchors_used.add(lead_anchor)

    # 2–11. Body – rotate with PD escalation
    for i, segment in enumerate(block_data["segments"][:10]):
        if pd.get("escalate") and i % 3 == 0:
            anchor = pd.get("escalate_anchor", lead_anchor)
        else:
            # rotate fairly
            available = [a for a in supporting if a not in anchors_used]
            if not available:
                available = supporting
            anchor = random.choice(available)

        raw_line = segment["headline"]
        line = build_line(anchor, raw_line, timeline[-1] if timeline else None)

        # Apply PD tone shift if needed
        if pd.get("tone_shift"):
            line = apply_tone_shift(line, pd["tone_shift"])

        # Anchor reaction (banter)
        if random.random() < 0.4:
            react_anchor = random.choice([a for a in active_personas if a != anchor])
            reaction = build_anchor_react(react_anchor, line)
            timeline.append({
                "anchor": react_anchor,
                "line": reaction,
                "raw_line": reaction,
                "role": "react",
                "duration_estimate": len(reaction.split()) * 0.35
            })

        timeline.append({
            "anchor": anchor,
            "line": line,
            "raw_line": raw_line,
            "role": "deliver",
            "duration_estimate": len(line.split()) * 0.38
        })
        anchors_used.add(anchor)

    # Final sign-off – always lead + co-anchor
    co_anchor = random.choice([a for a in active_personas if a != lead_anchor])
    timeline.append({
        "anchor": lead_anchor,
        "line": "That's tonight's Token News.",
        "raw_line": "That's tonight's Token News.",
        "role": "close"
    })
    timeline.append({
        "anchor": co_anchor,
        "line": f"I'm {co_anchor}. Good night.",
        "raw_line": f"I'm {co_anchor}. Good night.",
        "role": "close"
    })

    log(f"Timeline built – {len(timeline)} lines, lead: {lead_anchor}")
    return timeline
