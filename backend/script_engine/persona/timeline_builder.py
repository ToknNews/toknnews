#!/usr/bin/env python3
"""
TOKNNews — Timeline Builder (Clean GPT-Driven, Rebuild Stack Edition)

Sequence:
  - Vega booth intro
  - Chip greeting (daypart + awareness)
  - Chip rundown (GPT-refined)
  - Anchor reaction → duo exchange → analysis
  - Bitsy / Vega inserts (per PD)
  - Transitions

All lines GPT-authored where applicable.
"""

import time
from script_engine.persona.voice_map import VOICE_MAP
from script_engine.openai_writer import (
    gpt_analysis,
    gpt_transition,
    gpt_duo_line,
    gpt_chip_followup,
    gpt_chip_toss,
    gpt_story_transition,
    gpt_reaction,
)
from script_engine.persona.chip_open_engine import chip_open_line

# === Helpers ===

def _block(text: str, speaker: str, tag: str):
    return {
        "speaker": speaker,
        "text": text,
        "tag": tag,
        "timestamp": time.time(),
    }

def _audio_block(text: str, speaker: str, tag: str):
    return {
        "speaker": speaker,
        "voice_id": VOICE_MAP.get(speaker, "chip"),
        "text": text,
        "block_type": tag,
        "timestamp": time.time(),
        "line": text,
        "tag": tag,
    }

# === Main ===

def build_timeline(character, headline, synthesis, article_context, anchors,
                   allow_bitsy, allow_vega, show_intro, segment_type, pd_config=None):
    
    timeline = []
    audio_blocks = []

    pd_flags = pd_config if pd_config else {}
    show_mode = "LATENIGHT" if pd_flags.get("daypart") == "latenight" else "NEWS"
    brain = {"headline": headline, "synthesis": synthesis}

    primary = anchors[0] if anchors else "chip"
    duo = anchors[1] if len(anchors) > 1 else None

    # === 1. VEGA BOOTH INTRO ===
    vega_line = "You're watching Token News — where clarity meets crypto chaos."
    timeline.append(_block(vega_line, "vega", "vega_intro"))
    audio_blocks.append(_audio_block(vega_line, "vega", "vega_intro"))

    # === 2. CHIP INTRO (time-aware) ===
    if show_intro:
        intro_line = chip_open_line(time_of_day=pd_flags.get("daypart", "evening"))
        chip_greet = gpt_chip_followup(
            headline, synthesis, primary, duo, intro_line,
            pd_flags, show_mode, brain, "general"
        )
        timeline.append(_block(chip_greet, "chip", "chip_intro"))
        audio_blocks.append(_audio_block(chip_greet, "chip", "chip_intro"))

    # === 3. CHIP RUNDOWN REACTION ===
    chip_react = gpt_reaction("chip", headline, brain)
    timeline.append(_block(chip_react, "chip", "chip_rundown"))
    audio_blocks.append(_audio_block(chip_react, "chip", "chip_rundown"))

    # === 4. CHIP → PRIMARY TOSS ===
    chip_toss = gpt_chip_toss(primary, headline, brain, show_mode, pd_flags)
    timeline.append(_block(chip_toss, "chip", "chip_toss"))
    audio_blocks.append(_audio_block(chip_toss, "chip", "chip_toss"))

    # === 5. ANCHOR REACT ===
    anchor_react = gpt_reaction(primary, headline, brain)
    timeline.append(_block(anchor_react, primary, "primary_reaction"))
    audio_blocks.append(_audio_block(anchor_react, primary, "primary_reaction"))

    # === 6. DUO CROSSTALK (Optional) ===
    if duo:
        try:
            l1 = gpt_duo_line(duo, primary, headline, "", show_mode, anchor_react, brain)
            l2 = gpt_duo_line(primary, duo, headline, "", show_mode, l1, brain)
            timeline.append(_block(l1, duo, "duo_crosstalk"))
            timeline.append(_block(l2, primary, "duo_followup"))
            audio_blocks.append(_audio_block(l1, duo, "duo_crosstalk"))
            audio_blocks.append(_audio_block(l2, primary, "duo_followup"))
        except Exception as e:
            print("[TimelineBuilder] Duo crosstalk error:", e)

    # === 7. ANCHOR ANALYSIS ===
    analysis = gpt_analysis(primary, headline, synthesis, brain)
    timeline.append(_block(analysis, primary, "anchor_analysis"))
    audio_blocks.append(_audio_block(analysis, primary, "anchor_analysis"))

    # === 8. OPTIONAL INSERTS ===
    if allow_vega:
        vega_color = "With volatility rising, let’s keep the signal clean."  # or GPT-driven in future
        timeline.append(_block(vega_color, "vega", "vega_block"))
        audio_blocks.append(_audio_block(vega_color, "vega", "vega_block"))

    if allow_bitsy:
        bitsy = "Wait what? I was not ready for that headline."  # Replace with gpt_bitsy_interrupt() if desired
        timeline.append(_block(bitsy, "bitsy", "bitsy_interrupt"))
        audio_blocks.append(_audio_block(bitsy, "bitsy", "bitsy_interrupt"))

    # === 9. CHIP OUTRO TRANSITION ===
    if segment_type != "closing":
        chip_next = gpt_story_transition(headline, brain)
        timeline.append(_block(chip_next, "chip", "chip_transition"))
        audio_blocks.append(_audio_block(chip_next, "chip", "chip_transition"))

    return {
        "timeline": timeline,
        "audio_blocks": audio_blocks
    }
