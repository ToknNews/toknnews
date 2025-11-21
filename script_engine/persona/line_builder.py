#!/usr/bin/env python3
"""
TOKNNews — Persona Line Builder (Module C-2)

Deterministic persona line builder:
- persona_loader (phrasing, lexicon, cadence)
- simple theme extraction (fallback)
- persona-accurate reactions/dialogue
"""

import random

from script_engine.character_brain.persona_loader import (
    load_persona,
    get_persona_lines,
    get_analysis_phrasing,
    get_analysis_structure,
    get_transition_phrasing,
    get_risk_phrasing,
    get_lexicon,
    get_cadence,
    get_voice,
    get_rules,
)


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------

def _choose(lst):
    """Safe random choice with fallback."""
    if not lst:
        return ""
    return random.choice(lst)


def _clean(text):
    """Collapse whitespace and strip."""
    return " ".join(text.split()).strip()


# ---------------------------------------------------------
# Persona-driven analysis line
# ---------------------------------------------------------

def build_analysis_line(character: str,
                        headline: str,
                        synthesis: str = "",
                        article_context: str = "") -> str:
    """
    Deterministic persona-driven analysis line.
    Simplified for Script Engine v3.

    Steps:
     1. Load persona DNA
     2. Derive a simple theme from synthesis/headline
     3. Build a structured sentence from persona phrasing
     4. Apply lexicon cleaning + cadence rules
    """

    persona = load_persona(character)

    analysis_phrases = get_analysis_phrasing(character)
    structure_phrases = get_analysis_structure(character)
    risk_phrases = get_risk_phrasing(character)
    lexicon = get_lexicon(character)
    cadence = get_cadence(character)

    # === Step 1: Basic theme extraction (fallback)
    if isinstance(synthesis, str) and synthesis.strip():
        theme = synthesis.strip()
    else:
        # crude fallback: grab 4–7 significant words from headline
        theme = " ".join(headline.split()[:7])

    # === Step 2: Persona structures (very simplified)
    opener = _choose(analysis_phrases)
    struct  = _choose(structure_phrases)
    risk_line = _choose(risk_phrases)

    # Assemble base analysis
    base_line = f"{opener} {theme}. {risk_line}"

    # === Step 3: Lexicon cleaning — remove banned words
    avoid = lexicon.get("avoid", [])
    for term in avoid:
        if term.lower() in base_line.lower():
            base_line = base_line.replace(term, "")

    # === Step 4: Cadence rules (simplified)
    if cadence.get("sentence_style") == "Short → medium, crisp transitions.":
        base_line = _clean(base_line)

    return _clean(base_line)

# ---------------------------------------------------------
# Persona-driven transition line
# ---------------------------------------------------------

def build_transition_line(character: str,
                          target_group: str = "anchor") -> str:
    """
    Returns a transition phrase for Chip or an anchor.
    target_group: 'anchor' | 'vega' | 'reentry'
    """
    phr = get_transition_phrasing(character, target_group)
    return _choose(phr)


# ---------------------------------------------------------
# Vega block builder (persona-driven chaos)
# ---------------------------------------------------------

def build_vega_line(headline: str, synthesis: str = "") -> str:
    """
    Vega's high-energy commentary block.
    Short, sharp, slightly chaotic but useful.
    """
    rules = get_rules("vega")
    max_sec = rules.get("max_duration_seconds", 7)

    # Simple fallback theme: first few words
    raw_text = synthesis if isinstance(synthesis, str) else headline
    theme = " ".join(raw_text.split()[:7])

    line = (
        f"Okay, real talk: {theme}. "
        f"Everyone's pretending this isn't chaotic, but it absolutely is. "
        f"And the psychology is bouncing off the walls right now."
    )

    # Trim for timing
    words = line.split()
    # ~2.5 words/sec → allow max ~2.5 * duration seconds
    limit = int(2.5 * max_sec)
    if len(words) > limit:
        words = words[:limit]

    return _clean(" ".join(words))


# ---------------------------------------------------------
# Bitsy meta-interrupt builder
# ---------------------------------------------------------

def build_bitsy_interrupt() -> str:
    rules = get_rules("bitsy")
    max_words = rules.get("max_words", 16)

    line = (
        "Hi! Sorry! I know the show's serious right now but the soundboard "
        "button is glowing and it’s distracting me."
    )

    words = line.split()
    if len(words) > max_words:
        words = words[:max_words]

    return _clean(" ".join(words))


# ---------------------------------------------------------
# Persona-driven quick reaction line (optional)
# ---------------------------------------------------------

def build_reaction_line(character: str, headline: str) -> str:
    """
    A short, persona-accurate reaction, useful for tosses or intros.
    """
    persona_lines = get_persona_lines(character)
    lexicon = get_lexicon(character)

    opener = _choose(persona_lines[:3]) if persona_lines else ""
    # Simple fallback theme: first few words of headline
    theme = " ".join(headline.split()[:6])

    line = f"{opener} {theme}."

    # Clean lexicon violations
    avoid = lexicon.get("avoid", [])
    for term in avoid:
        if term in line.lower():
            line = line.replace(term, "")

    return _clean(line)
