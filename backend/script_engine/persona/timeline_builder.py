#!/usr/bin/env python3
"""
TOKNNews — Timeline Builder (Final PD-Integrated Build)
Module C-8
"""

import random
import time

# ------------------------------------------------------------
# Dual-Mode Imports (Package vs Local)
# ------------------------------------------------------------
try:
    from script_engine.persona.line_builder import (
        apply_tone_shift,
        build_analysis_line,
        build_transition_line,
        build_vega_line,
        build_bitsy_interrupt,
        build_reaction_line,
        build_anchor_react
    )
    from script_engine.character_brain.persona_loader import get_voice

except ImportError:
    from persona.line_builder import (
        apply_tone_shift,
        build_analysis_line,
        build_transition_line,
        build_vega_line,
        build_bitsy_interrupt,
        build_reaction_line,
        build_anchor_react
    )
    from character_brain.persona_loader import get_voice

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


# ------------------------------------------------------------
# DUO CROSSTALK ENGINE (Step 3-G)
# ------------------------------------------------------------
def _build_duo_crosstalk(primary, duo, headline, synthesis, tone_shift):

    blocks = []

    # 1. Primary reacts
    p_react = build_reaction_line(primary, headline, tone_shift)
    blocks.append({
        "type": "duo_primary_react",
        "speaker": primary,
        "text": p_react,
        "tone_shift": tone_shift
    })

    # 2. Duo counters / reacts
    d_react = build_reaction_line(duo, headline, tone_shift)
    blocks.append({
        "type": "duo_secondary_react",
        "speaker": duo,
        "text": d_react,
        "tone_shift": tone_shift
    })

    # 3. Primary analysis
    p_analysis = build_analysis_line(primary, headline, synthesis, "", tone_shift)
    blocks.append({
        "type": "duo_primary_analysis",
        "speaker": primary,
        "text": p_analysis,
        "tone_shift": tone_shift
    })

    # 4. Duo counter-analysis
    d_analysis = build_analysis_line(duo, headline, synthesis, "", tone_shift)
    blocks.append({
        "type": "duo_secondary_analysis",
        "speaker": duo,
        "text": d_analysis,
        "tone_shift": tone_shift
    })

    # 5. Transition ping-pong
    p_trans = build_transition_line(primary, target_group="analysis", tone_shift=tone_shift)
    d_trans = build_transition_line(duo, target_group="analysis", tone_shift=tone_shift)

    blocks.append({
        "type": "duo_primary_transition",
        "speaker": primary,
        "text": p_trans,
        "tone_shift": tone_shift
    })
    blocks.append({
        "type": "duo_secondary_transition",
        "speaker": duo,
        "text": d_trans,
        "tone_shift": tone_shift
    })

    # 6. Quick react closure
    p_close = build_anchor_react(primary, headline, tone_shift)
    blocks.append({
        "type": "duo_primary_close",
        "speaker": primary,
        "text": p_close,
        "tone_shift": tone_shift
    })

    return blocks

# ------------------------------------------------------------
# MAIN — Build timeline based on PD instructions (Step 3-G)
# ------------------------------------------------------------
def build_timeline(
    headline: str,
    synthesis: str = "",
    article_context: str = "",
    anchors=None,
    allow_bitsy=False,
    allow_vega=False,
    show_intro=False,
    segment_type="headline",
    tone_shift=None
):

    timeline = []
    audio_blocks = []

    # --------------------------------------------------------
    # STEP 3-G: Multi-anchor support (primary + duo)
    # --------------------------------------------------------
    if anchors is None:
        anchors = ["reef"]   # safe fallback

    primary_anchor = anchors[0]
    duo_anchor = anchors[1] if len(anchors) > 1 else None
    speaker = primary_anchor   # used for all lines unless duo logic added later

    # --------------------------------------------------------
    # SHOW INTRO (Vega voiceover)
    # --------------------------------------------------------
    if show_intro:
        intro_line = (
            f"Vega sets the stage for today's update on {headline}."
        )
        timeline.append({
            "type": "intro",
            "speaker": "vega",
            "text": intro_line,
            "tone_shift": None
        })

    # --------------------------------------------------------
    # REACTION LINE (primary anchor)
    # --------------------------------------------------------
    reaction_text = build_reaction_line(
        speaker, headline, tone_shift=tone_shift
    )
    timeline.append({
        "type": "reaction",
        "speaker": speaker,
        "text": reaction_text,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # ANALYSIS LINE (primary anchor)
    # --------------------------------------------------------
    analysis_text = build_analysis_line(
        speaker,
        headline,
        synthesis,
        article_context,
        tone_shift=tone_shift
    )
    timeline.append({
        "type": "analysis",
        "speaker": speaker,
        "text": analysis_text,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # TRANSITION (optional)
    # --------------------------------------------------------
    transition_text = build_transition_line(
        speaker,
        target_group="anchor",
        tone_shift=tone_shift
    )
    timeline.append({
        "type": "transition",
        "speaker": speaker,
        "text": transition_text,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # QUICK REACT (primary anchor)
    # --------------------------------------------------------
    react_text = build_anchor_react(
        speaker, headline, tone_shift=tone_shift
    )
    timeline.append({
        "type": "quick_react",
        "speaker": speaker,
        "text": react_text,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # DUO LOGIC (Step 3-G placeholder)
    # Optional: add duo_anchor cameo without breaking engine
    # --------------------------------------------------------

    if duo_anchor:
        duo_blocks = _build_duo_crosstalk(
            primary_anchor,
            duo_anchor,
            headline,
            synthesis,
            tone_shift
        )
        timeline.extend(duo_blocks)

    # --------------------------------------------------------
    # Return timeline + empty audio blocks (populated later)
    # --------------------------------------------------------

    return {
        "timeline": timeline,
        "audio_blocks": audio_blocks,
        "unreal": {
            "scene_id": f"scene_{int(time.time())}",
            "anchors": anchors,
            "primary_anchor": primary_anchor,
            "duo_anchor": duo_anchor
        },
        "anchors_used": anchors,
        "primary_anchor": primary_anchor,
        "duo_anchor": duo_anchor
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
