#!/usr/bin/env python3
"""
ToknNews Script Engine v3
Persona-aware script generator.
Handles:
 - Chip intros (conditional)
 - Primary anchor analysis
 - Secondary anchor color commentary
 - Chip closes (conditional)
"""

import json
from script_engine.character_brain.brain_engine import generate_persona_line
from script_engine.intro_engine.chip_intro_enhancer import enhance_chip_intro
from script_engine.chip_reset.reset_builder import build_reset_transition_line
from datetime import datetime
from zoneinfo import ZoneInfo

def get_broadcast_time_info():
    """
    Returns:
      - greeting (Good morning/evening/etc)
      - is_holiday (bool)
      - holiday_name (str or None)
      - hour (int ET)
    """
    now = datetime.now(ZoneInfo("America/New_York"))
    hour = now.hour

    # Time-based greeting
    if 5 <= hour < 11:
        greeting = "Good morning"
    elif 11 <= hour < 16:
        greeting = "Good afternoon"
    elif 16 <= hour < 22:
        greeting = "Good evening"
    elif 22 <= hour or hour < 2:
        greeting = "Good evening"
    else:
        greeting = "Good early morning"

    # Simple holiday lookup table (expand later)
    date_key = now.strftime("%m-%d")
    holidays = {
        "01-01": "Happy New Year",
        "07-04": "Happy Fourth of July",
        "12-25": "Merry Christmas",
        "12-31": "Happy New Year's Eve",
        "11-28": "Happy Thanksgiving"  # movable but placeholder for now
    }

    holiday_name = holidays.get(date_key)
    is_holiday = holiday_name is not None

    return {
        "greeting": greeting,
        "is_holiday": is_holiday,
        "holiday_name": holiday_name,
        "hour": hour
    }

    # 4. Chip toss to anchor  ← THIS goes here
    toss_line = build_chip_toss(enriched)
    sequence.append({
        "speaker": "Chip Blue",
        "role": "lead_anchor",
        "type": "chip_toss",
        "line": toss_line
    })

def build_chip_greeting(enriched):
    """
    Generates Chip Blue's greeting line using Eastern Time awareness.
    Includes:
      - time-of-day greeting
      - optional holiday greeting
    """
    ti = get_broadcast_time_info()

    greeting = ti["greeting"]  # Good morning/afternoon/etc
    holiday = ti["holiday_name"]

    # Base greeting
    chip_line = f"{greeting}. "

    # Add holiday if today is one
    if holiday:
        chip_line += f"{holiday}. "

    # Clean spacing
    chip_line = " ".join(chip_line.split()).strip()

    # Enhancement layer
    daypart = ti.get("daypart")
    escalation = enriched.get("escalation_level", 0)

    enhanced = enhance_chip_intro(chip_line, enriched, daypart, escalation)
    return enhanced

def build_chip_breaking_news_line(enriched):
    """
    Creates Chip's opening sentence about the top story:
      - breaking news
      - major story
      - normal story
    Based on 'importance' (1–10 scale).
    """
    importance = enriched.get("importance", 5)

    if importance >= 9:
        return "We begin with breaking news."
    elif importance >= 8:
        return "Major developments tonight."
    else:
        return "Here’s what we’re watching."

def build_chip_rundown(stories):
    """
    Takes a list of enriched story objects and returns Chip's show rundown line.
    Uses Option D Hybrid:
      - Direct importance sorting
      - Bands: major (8-10), key (5-7), other (<5)
      - 1-3 stories max
    """

    if not stories:
        return "Here’s what we’re following."

    # Sort by importance descending
    sorted_stories = sorted(stories, key=lambda s: s.get("importance", 5), reverse=True)

    # Extract top 3 titles
    top_stories = sorted_stories[:3]

    titles = [s.get("headline") or s.get("title") or s.get("topic") or "a top story" for s in top_stories]
    importances = [s.get("importance", 5) for s in top_stories]

    # Determine broadcast band
    max_imp = importances[0]

    if max_imp >= 9:
        lead_phrase = "Here are the top developments we're following:"
    elif max_imp >= 8:
        lead_phrase = "Several major stories tonight:"
    elif max_imp >= 5:
        lead_phrase = "Here are the key stories we're watching:"
    else:
        lead_phrase = "One important update tonight:"

    # Build rundown line
    if len(titles) == 1:
        rundown = f"{lead_phrase} {titles[0]}."
    elif len(titles) == 2:
        rundown = f"{lead_phrase} {titles[0]} and {titles[1]}."
    else:
        rundown = f"{lead_phrase} {titles[0]}, {titles[1]}, and {titles[2]}."

    return rundown

def build_chip_anchor_toss(enriched):
    """
    Chip tosses the segment to the appropriate anchor based on primary_character.
    """
    primary = enriched.get("primary_character", "").strip()

    toss_map = {
        "Neura Grey": "Neura, take us in.",
        "Lawson Black": "Lawson, what’s the legal angle?",
        "Cap Silver": "Cap, break this one down from the venture side.",
        "Cash Green": "Cash, give us the market read.",
        "Reef Gold": "Reef, walk us through it.",
        "Rex Vol": "Rex, what’s the move here?",
        "Ledger Stone": "Ledger, break down the on-chain data.",
        "Bond Crimson": "Bond, set the macro context for us.",
        "Bitsy Gold": "Bitsy, what’s the vibe on this one?",
        "Penny Lane": "Penny, talk us through it."
    }

    # If character is recognized
    if primary in toss_map:
        return toss_map[primary]

    # Fallback if not recognized
    return "Let’s get into it."

import random

def build_chip_transition(enriched):
    """
    Builds Chip's transition between stories.
    Dynamic mix of:
      - one-line transitions
      - two-line transitions
      - headline preface
      - domain preface
      - AI-short taglines
    """

    # Extract properties
    headline = enriched.get("headline") or enriched.get("title") or enriched.get("topic") or ""
    domain = enriched.get("domain", "general")
    importance = enriched.get("importance", 5)
    sentiment = enriched.get("sentiment", "neutral")

    # --- Transition phrase sets ---
    short_transitions = [
        "Next up,",
        "Moving on,",
        "Let’s shift gears,",
        "Our next story,",
        "Up ahead,"
    ]

    broadcast_transitions = [
        "In other developments,",
        "Turning now to,",
        "Meanwhile,",
        "Away from that,",
        "We’re also tracking,"
    ]

    # --- Pick transition phrase (hybrid A + B) ---
    transition_phrase = random.choice(short_transitions + broadcast_transitions)

    # --- Preface selection rules (Option D) ---
    if importance >= 8:
        # Major story → use headline
        preface = headline
    elif importance >= 6 and sentiment in ["positive", "negative"]:
        # Mid-tier, strong sentiment → short AI-style tagline
        preface = enriched.get("summary", "").split(".")[0]
    elif importance >= 5:
        # Medium story → domain-based
        preface = f"a key development in {domain}"
    else:
        # Low importance → ultra short cue
        preface = domain

    # --- Build one-line or two-line transition ---
    two_line_probability = 0.5  # 50% (dynamic)
    use_two_line = random.random() < two_line_probability

    if use_two_line:
        # First line = story preface
        line1 = f"{transition_phrase} {preface}."
        # Second line = toss to anchor
        toss = build_chip_anchor_toss(enriched)
        return [
            {
                "speaker": "Chip Blue",
                "role": "lead_anchor",
                "type": "transition_preface",
                "line": line1
            },
            {
                "speaker": "Chip Blue",
                "role": "lead_anchor",
                "type": "transition_toss",
                "line": toss
            }
        ]
    else:
        # One-line transition
        toss = build_chip_anchor_toss(enriched)
        line = f"{transition_phrase} {preface} — {toss}"
        return [
            {
                "speaker": "Chip Blue",
                "role": "lead_anchor",
                "type": "transition_combined",
                "line": line
            }
        ]

def chip_intro(enriched):
    """
    Chip opens the show. Vega may optionally add an energy line if enabled.
    """
    intro = generate_persona_line("Chip Blue", enriched)

    # Decide if Vega adds a vibe line (only if intro is high-energy or sentiment positive)
    sentiment = enriched.get("sentiment", "neutral")
    importance = enriched.get("importance", 5)

    vega_line = None
    if sentiment in ["positive"] or importance >= 8:
        try:
            vega_line = generate_persona_line("Vega Watt", enriched)
        except:
            vega_line = None

    if vega_line:
        return f"{intro} {vega_line}"

    return intro

def chip_outro(enriched):
    """
    Chip closes. Vega may close with a vibe-outro depending on tone.
    """
    outro = generate_persona_line("Chip Blue", enriched)

    sentiment = enriched.get("sentiment", "neutral")
    importance = enriched.get("importance", 5)

    vega_line = None
    if sentiment in ["positive", "neutral"]:
        try:
            vega_line = generate_persona_line("Vega Watt", enriched)
        except:
            vega_line = None

    if vega_line:
        return f"{outro} {vega_line}"

    return outro

def primary_section(enriched):
    """
    Generates the main analysis section for the primary character.
    Placeholder version — will be replaced with persona-aware scripting.
    """
    primary = enriched.get("primary_character")
    if primary == "Vega Watt":
        return None

    summary = enriched.get("summary", "")
    if not primary:
        return None
    return generate_persona_line(primary, enriched)

def secondary_section(enriched):
    """
    Generates color / impact / alternative perspective from the secondary character.
    Placeholder version — will become persona-aware later.
    """
    secondary = enriched.get("secondary_character")
    if secondary == "Vega Watt":
        return None

    summary = enriched.get("summary", "")
    if not secondary:
        return None
    return generate_persona_line(secondary, enriched)

def build_reset_rundown_note():
    """
    Short acknowledgment line Chip delivers after a mid-show reset,
    just before the normal rundown resumes.
    """
    return "Quick reset behind us — here’s what’s next."

def build_script_sequence(enriched_list):
    """
    Main timeline builder for ToknNews.
    Handles:
      - normal multi-story flow
      - chip_reset sequences
      - intro skipping after reset
      - soft re-entry
      - chip toss
      - primary/secondary analysis
      - recap + vega reactions
      - final outro
    """

    from script_engine.toss_engine.toss_line_generator import build_chip_toss
    from script_engine.character_brain.brain_engine import generate_persona_line
    from script_engine.time_logic import get_broadcast_time_info
    from script_engine.timeline_blocks.bitsy_meta_block import build_bitsy_meta_block
    from script_engine.timeline_blocks.vega_pad_block import build_vega_pad_block
    from script_engine.chip_reset.reset_builder import build_chip_reset
    from script_engine.chip_reset.reset_transitions import build_reset_return_line
    from script_engine.montage.montage_block import build_reset_montage
    from script_engine.montage.chip_vega_riff import build_chip_vega_riff

    # ==========================================
    # 0. Sanity Check
    # ==========================================
    if not enriched_list:
        return []

    first = enriched_list[0]
    sequence = []

    # Determine if this story flow begins immediately after a reset
    post_reset = (first.get("type") == "chip_reset")

    # ==========================================
    # 1. EARLY RESET — prepend reset sequence, then continue timeline
    # ==========================================
    if isinstance(first, dict) and first.get("type") == "chip_reset":

        stories = first.get("stories", [])

        # Build reset intro block
        reset_block = build_chip_reset(stories)

        # Vega reset reaction
        ti = get_broadcast_time_info()
        daypart = ti.get("daypart", "default")
        from script_engine.intro_engine.vega_reset_react import vega_reset_reaction
        vega_line = vega_reset_reaction(daypart)

        # Chip return
        chip_return = build_reset_return_line()

        # Prepend reset timeline
        sequence.extend([
            reset_block,
            build_reset_montage(),
            {
                "speaker": "Vega Watt",
                "role": "vibe_booth",
                "type": "reset_vibe",
                "line": vega_line
            },
            *build_chip_vega_riff(),
            {
                "speaker": "Chip Blue",
                "role": "lead_anchor",
                "type": "soft_reentry",
                "line": chip_return
            }
        ])

        # Skip intros for the rest of the segment
        post_reset = True

        # Replace enriched_list with actual stories
        enriched_list = stories

    # ==========================================
    # 2. EARLY EXIT — VEGAPAD (PD hijinx)
    # ==========================================
    if isinstance(first, dict) and first.get("type") == "vega_pad":
        return [build_vega_pad_block(first.get("hijinx_line", "(Vega riff)"))]

    # ==========================================
    # 3. EARLY EXIT — BITSY META BLOCK
    # ==========================================
    if isinstance(first, dict) and first.get("type") == "bitsy_meta":
        return [build_bitsy_meta_block(first.get("line", "Bitsy jumps in..."))]

    # If reset created multiple stories, first entry is now a story dict
    if enriched_list:
        first_story = enriched_list[0]
    else:
        return sequence

    # ==========================================
    # 4. Normal intros (SKIPPED if post_reset = True)
    # ==========================================
    if not post_reset:

        # Vega booth intro
        vega_intro = generate_persona_line("Vega Watt", first_story)
        sequence.append({
            "speaker": "Vega Watt",
            "role": "vibe_booth",
            "type": "intro_booth",
            "line": vega_intro
        })

        # Chip greeting
        chip_greeting = build_chip_greeting(first_story)
        sequence.append({
            "speaker": "Chip Blue",
            "role": "lead_anchor",
            "type": "intro_greeting",
            "line": chip_greeting
        })

        # Holiday line
        ti = get_broadcast_time_info()
        if ti.get("holiday_name"):
            sequence.append({
                "speaker": "Chip Blue",
                "role": "lead_anchor",
                "type": "intro_holiday",
                "line": f"{ti['holiday_name']}."
            })

        # Breaking line
        breaking_line = build_chip_breaking_news_line(first_story)
        sequence.append({
            "speaker": "Chip Blue",
            "role": "lead_anchor",
            "type": "intro_breaking",
            "line": breaking_line
        })

        # Rundown
        rundown = build_chip_rundown(enriched_list)
        sequence.append({
            "speaker": "Chip Blue",
            "role": "lead_anchor",
            "type": "intro_rundown",
            "line": rundown
        })

    # ==========================================
    # 5. Append story content helper
    # ==========================================
    def append_story_content(story):

        # Chip toss
        toss_line = build_chip_toss(story)
        sequence.append({
            "speaker": "Chip Blue",
            "role": "lead_anchor",
            "type": "chip_toss",
            "line": toss_line
        })

        # Primary analysis
        primary = story.get("primary_character")
        if primary:
            sequence.append({
                "speaker": primary,
                "role": "primary_anchor",
                "type": "analysis_primary",
                "line": generate_persona_line(primary, story)
            })

        # Secondary analysis
        secondary = story.get("secondary_character")
        if secondary:
            sequence.append({
                "speaker": secondary,
                "role": "secondary_anchor",
                "type": "analysis_secondary",
                "line": generate_persona_line(secondary, story)
            })

        # Chip recap
        recap_line = generate_persona_line("Chip Blue", story)
        sequence.append({
            "speaker": "Chip Blue",
            "role": "lead_anchor",
            "type": "segment_recap",
            "line": recap_line
        })

        # Optional Vega reaction
        sentiment = story.get("sentiment", "neutral")
        importance = story.get("importance", 5)
        if sentiment in ["positive", "neutral"] or importance >= 8:
            sequence.append({
                "speaker": "Vega Watt",
                "role": "vibe_booth",
                "type": "segment_vega_react",
                "line": generate_persona_line("Vega Watt", story)
            })

    # ==========================================
    # 6. PROCESS STORIES
    # ==========================================
    for idx, story in enumerate(enriched_list):

        if idx == 0:
            append_story_content(story)
        else:
            transitions = build_chip_transition(story)
            sequence.extend(transitions)
            append_story_content(story)

    # ==========================================
    # 7. FINAL OUTRO
    # ==========================================
    final_story = enriched_list[-1]
    final_outro = generate_persona_line("Chip Blue", final_story)
    sequence.append({
        "speaker": "Chip Blue",
        "role": "lead_anchor",
        "type": "final_outro",
        "line": final_outro
    })

    sentiment = final_story.get("sentiment", "neutral")
    importance = final_story.get("importance", 5)
    if sentiment in ["positive", "neutral"] or importance >= 8:
        sequence.append({
            "speaker": "Vega Watt",
            "role": "vibe_booth",
            "type": "final_outro_booth",
            "line": generate_persona_line("Vega Watt", final_story)
        })

    return sequence

def generate_script(enriched):
    """
    Unified timeline script generator.
    Accepts either:
      - a single enriched story dict, or
      - a list of enriched stories.
    Returns a full broadcast script timeline.
    """

    # --- Direct PD-segment override (e.g. vega_pad) ---
    if isinstance(enriched, dict) and enriched.get("type") == "vega_pad":
        from timeline_blocks.vega_pad_block import build_vega_pad_block
        return {
            "script_sequence": [
                build_vega_pad_block(
                    hijinx_line=enriched.get("hijinx_line", "(Vega riff)")
                )
            ]
        }

    # --- Bitsy meta block from PD ---
    if isinstance(enriched, dict) and enriched.get("type") == "bitsy_meta":
        from timeline_blocks.bitsy_meta_block import build_bitsy_meta_block
        return {
            "script_sequence": [
                build_bitsy_meta_block(
                    line=enriched.get("line", "Bitsy has thoughts...")
                )
            ]
        }

    # Normalize: always operate on a list
    if isinstance(enriched, dict):
        enriched_list = [enriched]
    else:
        enriched_list = enriched

    timeline = build_script_sequence(enriched_list)

    # If already formatted (reset, vega_pad, bitsy_meta)
    if isinstance(timeline, dict) and "script_sequence" in timeline:
        return timeline

    # Normal case
    return {
        "script_sequence": timeline
    }
