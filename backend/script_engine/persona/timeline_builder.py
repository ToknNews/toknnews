#!/usr/bin/env python3
"""
TOKNNews — Timeline Builder (Final PD-Integrated Build)
Module C-8
"""

import random
import time
# Patch 3 imports (Chip follow-up + RKG)
from script_engine.rolling_brain import get_brain_snapshot
from script_engine.openai_writer import gpt_analysis, gpt_reaction, gpt_duo_line

# ------------------------------------------------------------
# Imports (Package Mode; tests run via `python -m script_engine.run_test`)
# ------------------------------------------------------------
from script_engine.persona.line_builder import (
    apply_tone_shift,
    build_analysis_line,
    build_transition_line,
    build_vega_line,
    build_bitsy_interrupt,
    build_reaction_line,
    build_anchor_react
)
from script_engine.character_brain.persona_loader import get_voice, get_domain

# ------------------------------------------------------------
# GLOBAL WRITER TOGGLE IMPORT (Package vs Local)
# ------------------------------------------------------------
try:
    from script_engine.engine_settings import USE_OPENAI_WRITER
except ImportError:
    from engine_settings import USE_OPENAI_WRITER

# ------------------------------------------------------------
# PRIMARY ANCHOR SELECTION (Chip delegates based on domain)
# ------------------------------------------------------------
def select_primary_anchor(headline: str, brain: dict):
    """
    Chooses the best anchor for this headline using:
    - keyword → domain detection
    - Rolling Brain aggregated topic frequencies
    - anchor persona specialties
    """

    from script_engine.character_brain.persona_loader import get_domain

    headline_l = headline.lower()

    # Simple domain detection (expand later)
    if any(x in headline_l for x in ["eth", "ethereum", "rollup", "l2", "altcoin"]):
        domain = "altcoin"

    elif any(x in headline_l for x in ["btc", "bitcoin", "halving", "mining"]):
        domain = "bitcoin"

    elif any(x in headline_l for x in ["defi", "liquidity", "protocol", "amm", "yield"]):
        domain = "defi"

    elif any(x in headline_l for x in ["hacker", "exploit", "bridge", "hack", "drain"]):
        domain = "security"

    else:
        domain = "general"

    # Score anchors by domain match + brain memory weight
    scores = {}
    for anchor, data in brain["anchors"].items():
        specialty = data.get("domain", [])
        score = 0

        # direct specialty alignment
        if domain in specialty:
            score += 10

        # rolling memory weight
        score += data.get("weight", 0)

        scores[anchor] = score

    # pick top scoring anchor
    primary = max(scores, key=scores.get)
    primary_domain = domain

    return primary, primary_domain

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
# Intro Helpers — Vega Ident + Chip Opening
# ---------------------------------------------------------

def _vega_ident_line():
    """
    Vega is zero analysis, all vibe.
    Keep this line as static as possible so we can re-use audio/render.
    """
    return "Good morning, and welcome to TOKN News."


def _chip_opening_line():
    """
    Chip greets the audience with time-aware phrasing.
    Light holiday hooks can be added here later.
    """
    hour = time.localtime().tm_hour

    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Basic, reusable. Holiday-aware logic can be layered later.
    return f"{greeting}, I’m Chip. Let’s get straight into today’s top story."

# ============================================================
# DUO CROSSTALK ENGINE — Persona, Context, Divergence, Interaction
# ============================================================
def _build_duo_crosstalk(
    primary: str,
    duo: str,
    headline: str,
    synthesis: str,
    tone_shift: str,
    last_solo_speaker: str,
    show_mode: str = "news"
):
    """
    Build a natural, contextual, persona-aware back-and-forth
    between two anchors with:
        • contextual recall
        • turn-taking
        • persona divergence
        • noun-diversity enforcement
        • show_mode = "news" | "latenight"
    """

    from ..openai_writer import gpt_duo_line
    from ..character_brain.persona_loader import get_domain

    # Determine persona domains
    primary_domain = get_domain(primary)
    duo_domain     = get_domain(duo)

    # ------------------------------------------------------------
    # PREVENT primary from responding to themselves
    # ------------------------------------------------------------
    if last_solo_speaker == primary:
        primary, duo = duo, primary
        primary_domain, duo_domain = duo_domain, primary_domain

    blocks = []
    used_terms = set()
    last_line = None

    # ------------------------------------------------------------
    # Prevent repeated nouns / jargon loops
    # ------------------------------------------------------------
    def filter_repeated_terms(text):
        nonlocal used_terms
        if not text:
            return None

        terms = [
            "liquidity", "flow", "imbalance", "whale",
            "protocol", "cluster", "yield", "volatility",
            "pressure", "anomaly"
        ]

        # If a term is used already → reject line to avoid loops
        for t in terms:
            if t in used_terms and t in text.lower():
                return None

        # Add new terms seen
        for t in terms:
            if t in text.lower():
                used_terms.add(t)

        return text

    # ============================================================
    # DUO ROUND FLOW (Primary → Duo → Primary → Duo → ...)
    # ============================================================

    # 1. Primary reacts
    p_react = gpt_duo_line(
        speaker=primary,
        counter=duo,
        headline=headline,
        domain=primary_domain,
        duo_mode="react",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    p_react = filter_repeated_terms(p_react)
    if p_react:
        blocks.append({
            "type": "duo_primary_react",
            "speaker": primary,
            "text": p_react,
            "tone_shift": tone_shift
        })
        last_line = p_react

    # 2. Duo counters
    d_react = gpt_duo_line(
        speaker=duo,
        counter=primary,
        headline=headline,
        domain=duo_domain,
        duo_mode="react",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    d_react = filter_repeated_terms(d_react)
    if d_react:
        blocks.append({
            "type": "duo_secondary_react",
            "speaker": duo,
            "text": d_react,
            "tone_shift": tone_shift
        })
        last_line = d_react

    # 3. Primary analysis
    p_analysis = gpt_duo_line(
        speaker=primary,
        counter=duo,
        headline=headline,
        domain=primary_domain,
        duo_mode="analysis",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    p_analysis = filter_repeated_terms(p_analysis)
    if p_analysis:
        blocks.append({
            "type": "duo_primary_analysis",
            "speaker": primary,
            "text": p_analysis,
            "tone_shift": tone_shift
        })
        last_line = p_analysis

    # 4. Duo counter-analysis
    d_analysis = gpt_duo_line(
        speaker=duo,
        counter=primary,
        headline=headline,
        domain=duo_domain,
        duo_mode="analysis",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    d_analysis = filter_repeated_terms(d_analysis)
    if d_analysis:
        blocks.append({
            "type": "duo_secondary_analysis",
            "speaker": duo,
            "text": d_analysis,
            "tone_shift": tone_shift
        })
        last_line = d_analysis

    # 5. Primary transition
    p_trans = gpt_duo_line(
        speaker=primary,
        counter=duo,
        headline=headline,
        domain=primary_domain,
        duo_mode="transition",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    p_trans = filter_repeated_terms(p_trans)
    if p_trans:
        blocks.append({
            "type": "duo_primary_transition",
            "speaker": primary,
            "text": p_trans,
            "tone_shift": tone_shift
        })
        last_line = p_trans

    # 6. Duo transition
    d_trans = gpt_duo_line(
        speaker=duo,
        counter=primary,
        headline=headline,
        domain=duo_domain,
        duo_mode="transition",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    d_trans = filter_repeated_terms(d_trans)
    if d_trans:
        blocks.append({
            "type": "duo_secondary_transition",
            "speaker": duo,
            "text": d_trans,
            "tone_shift": tone_shift
        })
        last_line = d_trans

    # 7. Primary close
    p_close = gpt_duo_line(
        speaker=primary,
        counter=duo,
        headline=headline,
        domain=primary_domain,
        duo_mode="close",
        last_counter_line=last_line,
        show_mode=show_mode
    )
    p_close = filter_repeated_terms(p_close)
    if p_close:
        blocks.append({
            "type": "duo_primary_close",
            "speaker": primary,
            "text": p_close,
            "tone_shift": tone_shift
        })

    return blocks

    # --------------------------------------------------------
    # Fallback: local deterministic crosstalk
    # --------------------------------------------------------
    blocks = []

    from persona.line_builder import (
        build_reaction_line,
        build_analysis_line,
        build_transition_line,
        build_anchor_react
    )

    # Primary
    p_react = build_reaction_line(primary, headline, tone_shift)
    blocks.append({
        "type": "duo_primary_react",
        "speaker": primary,
        "text": p_react,
        "tone_shift": tone_shift
    })

    # Duo
    d_react = build_reaction_line(duo, headline, tone_shift)
    blocks.append({
        "type": "duo_secondary_react",
        "speaker": duo,
        "text": d_react,
        "tone_shift": tone_shift
    })

    # Primary analysis
    p_anal = build_analysis_line(primary, headline, synthesis, "", tone_shift)
    blocks.append({
        "type": "duo_primary_analysis",
        "speaker": primary,
        "text": p_anal,
        "tone_shift": tone_shift
    })

    # Duo counter-analysis
    d_anal = build_analysis_line(duo, headline, synthesis, "", tone_shift)
    blocks.append({
        "type": "duo_secondary_analysis",
        "speaker": duo,
        "text": d_anal,
        "tone_shift": tone_shift
    })

    # Transitions
    p_trans = build_transition_line(primary, target_group=duo, tone_shift=tone_shift)
    blocks.append({
        "type": "duo_primary_transition",
        "speaker": primary,
        "text": p_trans,
        "tone_shift": tone_shift
    })

    d_trans = build_transition_line(duo, target_group=primary, tone_shift=tone_shift)
    blocks.append({
        "type": "duo_secondary_transition",
        "speaker": duo,
        "text": d_trans,
        "tone_shift": tone_shift
    })

    # Primary close
    p_close = build_anchor_react(primary, headline, tone_shift)
    blocks.append({
        "type": "duo_primary_close",
        "speaker": primary,
        "text": p_close,
        "tone_shift": tone_shift
    })

    return blocks


# ============================================================
# CHIP FOLLOW-UP ENGINE (Patch 3 — RKG + Hybrid)
# ============================================================

def chip_followup_question(headline: str, duo_round1: list, brain: dict, mode="news"):
    """
    Chip asks a clarifying, deeper, or redirecting question.
    - 1 sentence in news mode
    - Up to 3 sentences in late-night mode
    """

    tragic_terms = ["death", "tragedy", "killed", "shooting", "terror"]
    tragic = any(t in headline.lower() or t in str(brain).lower() for t in tragic_terms)

    if mode == "latenight" and not tragic:
        style = "Write up to 3 sentences. Clever, insightful, slightly witty."
    else:
        style = "Write ONE professional newsroom sentence."

    last_two = " | ".join([b["text"] for b in duo_round1[-2:]])

    prompt = f"""
You are Chip Blue, lead anchor of TOKNNews.

{style}

Your job:
- Ask a smart, clarifying question.
- Push the discussion deeper.
- Refer subtly to the last two duo lines:
  "{last_two}"
- Avoid humor if tragedy is present.
- Avoid repeating nouns already used.
- Address the domain implicitly (don't say 'domain').

Memory Snapshot (RKG):
{json.dumps(brain, indent=2)}

Write Chip's question ONLY (no name prefix).
"""
    return _gpt(prompt)


def chip_followup_target(chip_question: str):
    """
    Decide which anchor Chip is calling on.
    """
    q = chip_question.lower()

    mapping = {
        "volatility": "rex",
        "vol": "rex",
        "liquidation": "rex",

        "retail": "penny",
        "consumer": "penny",
        "community": "penny",

        "whale": "ledger",
        "flow": "ledger",
        "onchain": "ledger",
        "cluster": "ledger",

        "liquidity": "reef",
        "yield": "reef",
        "defi": "reef",

        "sec": "lawson",
        "legal": "lawson",
        "regulation": "lawson",

        "macro": "bond",
        "rates": "bond",
        "inflation": "bond",

        "ai": "neura",
        "tech": "neura",

        "funding": "cap",
        "vc": "cap",

        "sentiment": "bitsy",
        "culture": "bitsy",
        "reddit": "bitsy",

        "vibe": "vega",
        "pace": "vega",
    }

    for key, val in mapping.items():
        if key in q:
            return val

    # Fallback always Ledger or Reef
    return "ledger"

# ============================================================
# PD SCORING ENGINE — Determines Round 2, Cameos, Mode Switch
# ============================================================

def pd_score_segment(headline: str, brain: dict, duo_round1: list):
    """
    Returns a dictionary of PD signals that inform:
    - whether to escalate (Round 2)
    - whether to bring Bitsy/Vega
    - whether to switch to late-night mode
    """

    text = headline.lower() + " " + str(brain).lower()
    score = {
        "complexity": 0,
        "contradiction": 0,
        "social_heat": 0,
        "volatility_risk": 0,
        "regulatory_risk": 0,
        "tragic": False,
        "latenight_mode": False,
        "bitsy_ok": True,
        "vega_ok": True,
        "round2": False
    }

    # Tragic-day detection (no humor)
    tragic_terms = ["death", "dead", "killed", "shooting", "explosion", "tragedy", "terror"]
    if any(t in text for t in tragic_terms):
        score["tragic"] = True
        score["bitsy_ok"] = False
        score["vega_ok"] = False

    # Complexity detection
    complex_terms = ["liquidity", "regulatory", "on-chain", "cluster", "macro", "rates", "arbitrage"]
    if any(t in text for t in complex_terms):
        score["complexity"] += 1

    # Contradiction detection (between duo lines)
    if len(duo_round1) >= 2:
        l1, l2 = duo_round1[-2]["text"].lower(), duo_round1[-1]["text"].lower()
        contradiction_terms = ["but", "however", "not exactly", "disagree"]
        if any(t in l1 for t in contradiction_terms) or any(t in l2 for t in contradiction_terms):
            score["contradiction"] += 1

    # Social heat detection
    try:
        social = brain["ram"]["social_heat"]
        score["social_heat"] = (
            social.get("fear",0) + social.get("anger",0) + social.get("hype",0)
        )
    except:
        pass

    # Volatility detection
    if "volatility" in text or "liquidation" in text:
        score["volatility_risk"] += 1

    # Regulatory risk
    if "sec" in text or "lawsuit" in text or "cftc" in text:
        score["regulatory_risk"] += 1

    # Latenight mode (RKG-driven)
    if score["tragic"] is False and score["social_heat"] > 0.6:
        score["latenight_mode"] = True

    # Round 2 trigger
    # If there is contradiction OR high complexity OR high heat OR high volatility
    if score["complexity"] > 0 or score["contradiction"] > 0 or score["social_heat"] > 0.4 or score["volatility_risk"] > 0:
        score["round2"] = True

    return score

# ============================================================
# MONTAGE ENGINE (Patch 5 — Foundation Layer)
# ============================================================

def should_trigger_montage(brain: dict, pd_flags: dict, mode="news"):
    """
    Decide if we should insert a montage recap.
    This is light, safe, and tone-aware.
    """
    # Never montage on tragedy
    if pd_flags.get("tragic", False):
        return False

    # Late-night → montage is MORE likely
    if mode == "latenight":
        return True

    # Normal news → montage only if:
    #  - high social heat
    #  - high contradiction
    #  - high volatility
    #  - end of segment
    if pd_flags.get("social_heat", 0) > 0.65:
        return True
    if pd_flags.get("contradiction", 0) > 0:
        return True
    if pd_flags.get("volatility_risk", 0) > 0:
        return True

    return False


def build_montage_sequence(headline: str, brain: dict, tone_shift=None, mode="news"):
    """
    Create a short 1–3 sentence montage-style line.
    Bitsy narrates Late Night montages.
    Chip narrates News montages.
    Vega appears optionally as pacing reset.
    """

    tragic_terms = ["death", "dead", "tragedy", "killed"]
    tragic = any(t in headline.lower() or t in str(brain).lower() for t in tragic_terms)

    if mode == "latenight" and not tragic:
        narrator = "bitsy"
        style = "fun, self-aware, witty — but relevant"
    else:
        narrator = "chip"
        style = "professional, concise, narrative recap"

    # brain context slice
    context_slice = json.dumps(brain["ram"], indent=2)

    prompt = f"""
You are {narrator}.

Write a montage-style recap for TOKNNews.

Mode: {mode}
Style: {style}

Rules:
- 1 to 3 sentences max.
- Capture key themes from the day.
- Avoid repeating nouns already used in the current segment.
- If tragic → NO humor, be empathetic.
- If Vega appears → mention rhythm/pacing lightly.
- Do NOT mention 'montage' or 'segment'.

Context Memory:
{context_slice}

Headline:
"{headline}"

Write only the montage narration.
"""

    return {
        "speaker": narrator,
        "text": _gpt(prompt),
        "type": "montage_recap",
        "tone_shift": tone_shift
    }

# ============================================================
# MODE SELECTION ENGINE (Patch 6 — News vs LateNight Logic)
# ============================================================

def get_show_mode():
    """
    Determines show mode based on:
    - time of day (explicit rule)
    - PD overrides (from Patch 4)
    - tragedy guardrails (no comedy)
    """

    hour = time.localtime().tm_hour

    # Explicit schedule:
    # Morning Show:   06:00–10:00
    # Midday:         11:00–14:00
    # Evening:        16:00–20:00
    # LateNight:      21:00–02:00

    if 6 <= hour <= 10:
        return "morning"
    if 11 <= hour <= 14:
        return "midday"
    if 16 <= hour <= 20:
        return "evening"
    if hour >= 21 or hour <= 2:
        return "latenight"

    # default fallback
    return "morning"


def resolve_mode_with_pd(headline: str, brain: dict, pd_flags: dict):
    """
    Fuse time-of-day default with PD overrides and tone guardrails.
    """

    base_mode = get_show_mode()

    tragic_terms = ["death", "tragedy", "dead", "shooting", "killed", "explosion"]
    is_tragic = any(t in headline.lower() or t in str(brain).lower() for t in tragic_terms)

    # If tragedy → force news mode
    if is_tragic:
        return "news"

    # If PD identifies high social heat and we are in latenight hours → switch to latenight
    if base_mode == "latenight" and pd_flags.get("social_heat", 0) > 0.4:
        return "latenight"

    # Midday or evening can escalate to LateNight if PD dictates
    if pd_flags.get("latenight_mode", False):
        return "latenight"

    # Otherwise map morning/midday/evening → news
    return "news"

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
    # CHIP TOSS (Patch 2 — RKG Hybrid)
    # --------------------------------------------------------
    from script_engine.knowledge.rolling_brain import get_brain_snapshot

    brain = get_brain_snapshot()

    # Chip selects the correct primary anchor based on domain + RKG
    primary_anchor, primary_domain = select_primary_anchor(headline, brain)

    # Determine duo anchor later (PD decides in Patch 3)
    duo_anchor = None
    speaker = primary_anchor

    # Chip tosses the headline to the primary anchor
    chip_line = chip_toss_line(
        headline=headline,
        primary_anchor=primary_anchor,
        brain=brain,
        mode="news"  # PD will switch to 'latenight' when needed
    )

    timeline.append({
        "type": "chip_toss",
        "speaker": "chip",
        "text": chip_line,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # SHOW INTRO — Vega ident + Chip greeting
    # --------------------------------------------------------
    if show_intro:
        # Vega ident — zero analysis, static vibe
        vega_line = _vega_ident_line()
        timeline.append({
            "type": "vega_ident",
            "speaker": "vega",
            "text": vega_line,
            "tone_shift": None
        })

        # Chip opening — time-aware, light context
        chip_line = _chip_opening_line()
        timeline.append({
            "type": "chip_open",
            "speaker": "chip",
            "text": chip_line,
            "tone_shift": tone_shift
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

    # ------------------------------------------------------------
    # DUO LOGIC — Round 1
    # ------------------------------------------------------------
    if duo_anchor:

        # Determine who spoke last (solo anchor)
        last_solo_speaker = timeline[-1]["speaker"] if timeline else None

        # Build Duo Round 1
        duo_blocks = _build_duo_crosstalk(
            primary_anchor,
            duo_anchor,
            headline,
            synthesis,
            tone_shift,
            last_solo_speaker
        )

        timeline.extend(duo_blocks)

    # ============================================================
    # CHIP FOLLOW-UP ENGINE (Patch 7)
    # ============================================================
    # Chip reacts AFTER the duo finishes — this drives narrative depth.
    if primary_anchor != "chip":
        from script_engine.openai_writer import gpt_chip_followup
        from script_engine.character_brain.persona_loader import get_domain

        # Determine Chip's angle based on PD flags, domains, and show mode
        chip_domain = get_domain("chip")

        chip_follow = gpt_chip_followup(
            headline=headline,
            synthesis=synthesis,
            primary=primary_anchor,
            duo=duo_anchor,
            last_line=timeline[-1]["text"],
            pd_flags=pd_flags,
            show_mode=mode,
            brain=brain,
            chip_domain=chip_domain
        )

        # If Chip has something meaningful to add
        if chip_follow:
            timeline.append({
                "type": "chip_followup",
                "speaker": "chip",
                "text": chip_follow,
                "tone_shift": tone_shift
            })

            # ========================================================
            # CHIP SMART TOSS — Who talks next?
            # ========================================================

            # Determine next anchor based on:
            # - PD domain scoring
            # - headline keywords
            # - social_heat
            # - latenight mode (can trigger Bitsy)
            next_anchor = None

            # 1. If tragedy → force stable anchor (reef, lawson, ledger)
            if pd_flags.get("tragedy_block"):
                for stable in ["reef", "lawson", "ledger"]:
                    if stable in anchors:
                        next_anchor = stable
                        break

            # 2. LateNight → prefer Bitsy cameos
            if not next_anchor and mode == "latenight" and allow_bitsy:
                next_anchor = "bitsy"

            # 3. High volatility → prefer Cap, Rex
            if (not next_anchor and
                pd_flags.get("volatility_risk",0) > 0.6):
                for vol in ["cap","rex"]:
                    if vol in anchors:
                        next_anchor = vol
                        break

            # 4. Social sentiment → prefer Ivy, Penny
            if (not next_anchor and 
                pd_flags.get("social_heat",0) > 0.5):
                for soc in ["ivy","penny"]:
                    if soc in anchors:
                        next_anchor = soc
                        break

            # 5. Default → go back to primary anchor
            if not next_anchor:
                next_anchor = primary_anchor

            # ========================================================
            # CHIP TOSS LINE — rhetorical or directive
            # ========================================================
            from script_engine.openai_writer import gpt_chip_toss

            toss_line = gpt_chip_toss(
                next_anchor=next_anchor,
                headline=headline,
                brain=brain,
                show_mode=mode,
                pd_flags=pd_flags
            )

            timeline.append({
                "type": "chip_toss",
                "speaker": "chip",
                "text": toss_line,
                "tone_shift": tone_shift
            })

            # ========================================================
            # RESET SEGMENT STARTER — next speaker takes over
            # ========================================================
            timeline.append({
                "type": "segment_reset",
                "speaker": next_anchor,
                "text": f"{next_anchor} continues the breakdown...",
                "tone_shift": tone_shift
            })

    # --------------------------------------------------------
    # CHIP FOLLOW-UP QUESTION (Patch 3 + PD Integration)
    # --------------------------------------------------------

    brain = get_brain_snapshot()
    duo_round1 = duo_blocks

    # PD score informs follow-up logic
    pd_flags = pd_score_segment(headline, brain, duo_round1)
    mode = resolve_mode_with_pd(headline, brain, pd_flags)

    # Chip asks follow-up
    chip_q = chip_followup_question(headline, duo_round1, brain, mode=mode)

    timeline.append({
        "type": "chip_followup",
        "speaker": "chip",
        "text": chip_q,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # DETERMINE FOLLOW-UP ANCHOR (PD-driven)
    # --------------------------------------------------------
    follow_anchor = chip_followup_target(chip_q)

    # Bitsy cameo guardrail
    if follow_anchor == "bitsy" and pd_flags["bitsy_ok"] is False:
        follow_anchor = "penny"

    # Vega cameo guardrail
    if follow_anchor == "vega" and pd_flags["vega_ok"] is False:
        follow_anchor = primary_anchor

    # Follow-up anchor LINE (Hybrid rules)
    follow_context = brain
    follow_text = gpt_reaction(follow_anchor, headline, follow_context)

    timeline.append({
        "type": "followup_anchor_response",
        "speaker": follow_anchor,
        "text": follow_text,
        "tone_shift": tone_shift
    })

    # --------------------------------------------------------
    # OPTIONAL DUO ROUND 2 — PD decides
    # --------------------------------------------------------
    if pd_flags["round2"]:

        last_solo = timeline[-1]["speaker"]

        # Determine round2 duo partner:
        # If duo exists, use it; otherwise fallback to follow anchor
        round2_duo_target = duo_anchor if duo_anchor else follow_anchor

        duo_round2 = _build_duo_crosstalk(
            primary_anchor,
            round2_duo_target,
            headline,
            synthesis,
            tone_shift,
            last_solo
        )

        # Add to timeline
        timeline.extend(duo_round2)

    # --------------------------------------------------------
    # Bitsy or Vega Cameo (Tone + PD driven)
    # --------------------------------------------------------
    if pd_flags["bitsy_ok"] and allow_bitsy and random.random() < pd_flags["social_heat"]:
        bitsy_line = build_bitsy_interrupt("bitsy", headline, tone_shift)
        timeline.append({
            "type": "bitsy_interrupt",
            "speaker": "bitsy",
            "text": bitsy_line,
            "tone_shift": tone_shift
        })

    if pd_flags["vega_ok"] and allow_vega and pd_flags["volatility_risk"] > 0:
        vega_line = build_vega_line("vega", headline, tone_shift)
        timeline.append({
            "type": "vega_pace_reset",
            "speaker": "vega",
            "text": vega_line,
            "tone_shift": tone_shift
        })

    # --------------------------------------------------------
    # MONTAGE INSERTION (Patch 5 — Tone & PD Driven)
    # --------------------------------------------------------
    try:
        pd_flags  # from Patch 4
        brain = get_brain_snapshot()
    except:
        pd_flags = {}
        brain = {"ram":{}}

    mode = "latenight" if pd_flags.get("latenight_mode") else "news"

    if should_trigger_montage(brain, pd_flags, mode):
        montage_block = build_montage_sequence(headline, brain, tone_shift, mode)
        timeline.append(montage_block)

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
