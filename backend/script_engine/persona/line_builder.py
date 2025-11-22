#!/usr/bin/env python3
"""
line_builder.py – thin compatibility shim
All real logic now lives in hybrid_line_writer.py
"""

# Forward everything to the real implementation
from script_engine.persona.hybrid_line_writer import (
    build_hybrid_line as build_line,
    apply_tone_shift,
    build_anchor_react,
    escalate_confidence,
    apply_style_constraints,
    enforce_phonetics,
    enforce_lexicon
)

# Keep old names alive for timeline_builder
__all__ = [
    "build_line",
    "apply_tone_shift",
    "build_anchor_react",
    "escalate_confidence",
    "apply_style_constraints",
    "enforce_phonetics",
    "enforce_lexicon"
]
