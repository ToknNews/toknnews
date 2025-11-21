#!/usr/bin/env python3
"""
TOKNNews — Timeline Builder (Final PD-Integrated Build)
Module C-8
"""

import random
import time

# Absolute imports for stability
from script_engine.persona.line_builder import (
    build_analysis_line,
    build_transition_line,
    build_vega_line,
    build_bitsy_interrupt,
    build_reaction_line
)

from script_engine.openai_writer import (
    gpt_analysis,
    gpt_reaction,
    gpt_duo_line
)
from script_engine.openai_writer import gpt_story_transition
from script_engine.character_brain.persona_loader import get_voice
from script_engine.persona.chip_open_engine import chip_open_line

# ---------------------------------------------------------
# HYBRID TOSS ENGINE — Domain + Identity Driven
# ---------------------------------------------------------

TOSS_MAP = {
    "reef": [
        "Reef, what’s your read on this?",
        "Reef, where’s the liquidity pressure here?",
        "Reef, help us understand the on-chain angle."
    ],
    "lawson": [
        "Lawson, walk us through the compliance angle.",
        "Lawson, legally speaking — what does this mean?",
        "Lawson, I know you watch this sector closely."
    ],
    "bond": [
        "Bond, give us the macro perspective.",
        "Bond, you’ve been tracking this; jump in here.",
        "Bond, how do global flows factor in?"
    ],
    "ivy": [
        "Ivy, talk sentiment and behavior.",
        "Ivy, frame this through incentives.",
        "Ivy, how does crowd psychology play into this?"
    ],
    "cash": [
        "Cash, break down the trader psychology.",
        "Cash, what’s retail thinking right now?",
        "Cash, how does sentiment shift here?"
    ],
    "ledger": [
        "Ledger, what are you seeing on-chain?",
        "Ledger, help us understand the security implications.",
        "Ledger, how do the flows look?"
    ],
    "penny": [
        "Penny, bring this back to the human side.",
        "Penny, what does this mean for everyday users?",
        "Penny, simplify this for our broad audience."
    ]
}

DOMAIN_MAP = {
    "defi": ["reef"],
    "onchain": ["ledger", "reef"],
    "security": ["ledger", "lawson"],
    "regulation": ["lawson"],
    "macro": ["bond"],
    "sentiment": ["ivy", "cash"],
    "retail": ["cash", "penny"],
    "lifestyle": ["penny"],
    "general": ["chip"]
}

def get_toss_line(anchor_id: str, domain: str = "general", used_lines=None):
    """
    Hybrid toss logic:
    - If domain matches → choose best anchor for domain
    - Else → fall back to anchor identity toss
    - No repeat tosses in same segment
    """
    if used_lines is None:
        used_lines = set()

    # Domain-first
    if domain in DOMAIN_MAP:
        candidates = DOMAIN_MAP[domain]
        if anchor_id in candidates:
            pool = TOSS_MAP.get(anchor_id, [])
        else:
            # mismatch: pick first domain anchor
            domain_anchor = candidates[0]
            pool = TOSS_MAP.get(domain_anchor, [])
    else:
        # Identity fallback
        pool = TOSS_MAP.get(anchor_id, [])

    # Remove lines already used
    pool = [line for line in pool if line not in used_lines]

    if not pool:
        # fallback if all lines used
        pool = TOSS_MAP.get(anchor_id, []) or ["Let's bring in another perspective."]

    line = random.choice(pool)
    used_lines.add(line)
    return line, used_lines

# ---------------------------------------------------------
# Utility blocks
# ---------------------------------------------------------

def _block(text, character, block_type):
    return {
        "type": block_type,
        "character": character,
        "voice_id": get_voice(character),
        "text": text,
        "timestamp": time.time()
    }


def _audio_block(text, character, block_type):
    return {
        "character": character,
        "voice_id": get_voice(character),
        "block_type": block_type,
        "text": text,                 # required for TTS
        "content": text,              # compatibility
        "timestamp": time.time()      # required for file naming & ordering
    }


# ---------------------------------------------------------
# MAIN — Build timeline based on PD instructions
# ---------------------------------------------------------

def build_timeline(
        character: str,
        headline: str,
        synthesis: str = "",
        article_context: str = "",
        anchors=None,
        allow_bitsy=False,
        allow_vega=False,
        show_intro=False,
        segment_type="headline"
    ):

    timeline = []
    audio_blocks = []

    # ---------------------------------------------------------
    # TRANSITION SAFETY RULES
    # ---------------------------------------------------------
    transitions_enabled = segment_type not in ("breaking", "show_intro", "closing")


    if anchors is None:
        anchors = ["reef", "lawson", "bond"]
    # ---------------------------------------------------------
    # PD-derived environmental context (MUST be defined early)
    # ---------------------------------------------------------
    time_of_day = "evening"       # placeholder until PD controls it
    season = None                 # q1/q2/q3/q4
    holiday = None                # future holiday awareness
    market_mood = "calm"          # calm/volatility/fear/euphoria

    # Optional GPT refinement (fallback safe)
    def _optional_gpt(prompt):
        try:
            return gpt_analysis("chip", prompt)
        except Exception:
            return None
    # ---------------------------------------------------------
    # SHOW INTRO or CHIP OPENING
    # ---------------------------------------------------------
    if segment_type == "show_intro":
        # Vega intro
        vega_line = vega_intro_block()
        timeline.append(_block(vega_line, "vega", "vega_intro"))
        audio_blocks.append(_audio_block(vega_line, "vega", "vega_intro"))

        # Chip greeting (ChipOpenEngine)
        chip_open = chip_open_line(
            time_of_day=time_of_day,
            holiday=holiday,
            season=season,
            market_mood=market_mood,
            gpt_func=_optional_gpt
        )
        timeline.append(_block(chip_open, "chip", "chip_open"))
        audio_blocks.append(_audio_block(chip_open, "chip", "chip_open"))

    else:
        # Standard non-intro opening
        chip_open = chip_open_line(
            time_of_day=time_of_day,
            holiday=holiday,
            season=season,
            market_mood=market_mood,
            gpt_func=_optional_gpt
        )
        timeline.append(_block(chip_open, "chip", "chip_open"))
        audio_blocks.append(_audio_block(chip_open, "chip", "chip_open"))

    # ---------------------------------------------------------
    # CHIP ANALYSIS
    # ---------------------------------------------------------
    chip_analysis = build_analysis_line("chip", headline, synthesis, article_context)
    timeline.append(_block(chip_analysis, "chip", "chip_analysis"))
    audio_blocks.append(_audio_block(chip_analysis, "chip", "chip_analysis"))

    # ---------------------------------------------------------
    # CHIP STORY TRANSITION (GPT)
    # ---------------------------------------------------------
    if transitions_enabled:
        transition_line = gpt_story_transition(
            headline=headline,
            brain={"summary": synthesis},
            tone="neutral"
        )
        timeline.append(_block(transition_line, "chip", "chip_transition"))
        audio_blocks.append(_audio_block(transition_line, "chip", "chip_transition"))

    # ---------------------------------------------------------
    # ANCHOR CROSSTALK (PD-selected anchors)
    # ---------------------------------------------------------
    _USED_TOSS_LINES = set()

    for anchor in anchors:
        anchor_id = str(anchor).lower()

        # --------------------------------------------
        # HYBRID TOSS ENGINE (domain-aware + identity)
        # --------------------------------------------
        toss, _USED_TOSS_LINES = get_toss_line(
            anchor_id=anchor_id,
            domain="general",      # temp placeholder until PD integration
            used_lines=_USED_TOSS_LINES
        )

        timeline.append(_block(toss, "chip", "chip_toss"))
        audio_blocks.append(_audio_block(toss, "chip", "chip_toss"))

        # --------------------------------------------
        # ANCHOR ANALYSIS BLOCK
        # --------------------------------------------
        a_line = build_analysis_line(anchor_id, headline, synthesis)
        timeline.append(_block(a_line, anchor_id, "anchor_analysis"))
        audio_blocks.append(_audio_block(a_line, anchor_id, "anchor_analysis"))

    # ---------------------------------------------------------
    # VEGA (PD-controlled)
    # ---------------------------------------------------------
    if allow_vega:
        v_line = build_vega_line(headline, synthesis)
        timeline.append(_block(v_line, "vega", "vega_block"))
        audio_blocks.append(_audio_block(v_line, "vega", "vega_block"))

    # ---------------------------------------------------------
    # BITSY (PD-controlled)
    # ---------------------------------------------------------
    if allow_bitsy:
        bits = build_bitsy_interrupt()
        timeline.append(_block(bits, "bitsy", "bitsy_interrupt"))
        audio_blocks.append(_audio_block(bits, "bitsy", "bitsy_interrupt"))

    # ---------------------------------------------------------
    # CHIP STORY TRANSITION OUT OF ANCHOR BLOCK (GPT)
    # ---------------------------------------------------------
    transition_line_out = gpt_story_transition(
        headline=headline,
        brain={"summary": synthesis},
        tone="neutral"
    )
    timeline.append(_block(transition_line_out, "chip", "chip_transition"))
    audio_blocks.append(_audio_block(transition_line_out, "chip", "chip_transition"))


    # ---------------------------------------------------------
    # CHIP RE-ENTRY (always)
    # ---------------------------------------------------------
    chip_re = build_transition_line("chip", "reentry")
    timeline.append(_block(chip_re, "chip", "chip_reentry"))
    audio_blocks.append(_audio_block(chip_re, "chip", "chip_reentry"))

    # ---------------------------------------------------------
    # CLOSING OUTRO (Chip + Vega) — only for final episode cycle
    # ---------------------------------------------------------
    if segment_type == "closing":
        # Chip final outro
        chip_close = "That's the latest — we'll continue tracking developments."
        timeline.append(_block(chip_close, "chip", "chip_outro"))
        audio_blocks.append(_audio_block(chip_close, "chip", "chip_outro"))

        # Vega final outro (rotating personality lines)
        vega_close = vega_outro_block()  # this now returns “Token News”
        timeline.append(_block(vega_close, "vega", "vega_outro"))
        audio_blocks.append(_audio_block(vega_close, "vega", "vega_outro"))

    # ---------------------------------------------------------
    # UNREAL METADATA (Final C-6)
    # ---------------------------------------------------------

    # Ordered characters
    character_list = []
    for b in timeline:
        if b["character"] not in character_list:
            character_list.append(b["character"])

    # Shot plan based on anchor count
    if len(anchors) > 1:
        camera_plan = "two_shot_chip_anchor"
        shot_plan = [
            {"shot": "chip_intro", "camera": "chip_close"},
            {"shot": "primary_analysis", "camera": "chip_mid"},
            {"shot": "anchor_1", "camera": "anchor_close"},
            {"shot": "anchor_2", "camera": "anchor_close"},
            {"shot": "vega", "camera": "chaos_cut"},
            {"shot": "bitsy", "camera": "bitsy_pop"},
            {"shot": "chip_reentry", "camera": "chip_mid"},
            {"shot": "outro", "camera": "chip_close"}
        ]
    else:
        camera_plan = "chip_single"
        shot_plan = [
            {"shot": "chip_intro", "camera": "chip_close"},
            {"shot": "primary_analysis", "camera": "chip_mid"},
            {"shot": "anchor_1", "camera": "anchor_close"},
            {"shot": "vega", "camera": "chaos_cut"},
            {"shot": "bitsy", "camera": "bitsy_pop"},
            {"shot": "chip_reentry", "camera": "chip_mid"},
            {"shot": "outro", "camera": "chip_close"}
        ]

    duration_seconds = max(5, len(timeline) * 3.2)

    audio_tracks = [
        {
            "character": b["character"],
            "voice_id": b["voice_id"],
            "text": b["text"],
            "block_type": b["type"],
            "timestamp": b["timestamp"]
        }
        for b in timeline
    ]

    unreal = {
        "scene_id": f"scene_{int(time.time())}",
        "engine_version": "UE5.3+",
        "camera_plan": camera_plan,
        "characters": character_list,
        "shot_plan": shot_plan,
        "audio_tracks": audio_tracks,
        "duration_seconds": duration_seconds
    }

    # ---------------------------------------------------------
    # FINAL RETURN
    # ---------------------------------------------------------
    return {
        "timeline": timeline,
        "audio_blocks": audio_blocks,
        "unreal": unreal
    }


# ---------------------------------------------------------
# Local test runner
# ---------------------------------------------------------

if __name__ == "__main__":
    sample = build_timeline(
        character="chip",
        headline="Solana ETF surge continues",
        synthesis="capital rotation into solana ecosystem",
        anchors=["reef", "lawson"],
        allow_bitsy=True,
        allow_vega=True,
        show_intro=True,
        segment_type="headline"
    )
    import json
    print(json.dumps(sample, indent=2))
