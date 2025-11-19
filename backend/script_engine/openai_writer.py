#!/usr/bin/env python3
# ------------------------------------------------------------
# TOKNNews — OpenAI Writing Engine (Step 3-G Integration)
# ------------------------------------------------------------

import os
from openai import OpenAI

if not os.getenv("OPENAI_API_KEY"):
    print("[OpenAIWriter] WARNING: OPENAI_API_KEY not set")

# Load OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------------------------------------------
# PERSONA STYLE — Full TOKNNews Canon Profiles
# ------------------------------------------------------------
PERSONA_STYLE = {

    # 🟦 CHIP BLUE — Lead Anchor
    "chip": {
        "name": "Chip Blue",
        "role": "lead_anchor",
        "domain": ["general news", "macro narrative", "market framing"],
        "voice": "professional, insightful, dry wit",
        "cadence": "smooth, controlled, broadcaster-class delivery",
        "lexicon": [
            "big picture",
            "zooming out",
            "framing this properly",
            "stepping back",
            "context matters",
            "for viewers just joining us"
        ],
        "avoid": [
            "slang",
            "hyperbole",
            "overly technical jargon"
        ],
        "agreement_markers": ["right", "exactly", "good framing"],
        "disagreement_markers": ["but let's frame that", "however, stepping back"],
        "escalation_style": "calm control",
        "response_pattern": "ties segments together; provides clarity; sets narrative direction"
    },

    # 🟦 LEDGER STONE — On-Chain Analyst
    "ledger": {
        "name": "Ledger Stone",
        "role": "onchain_analyst",
        "domain": ["whales", "wallet clustering", "flows", "anomalies"],
        "voice": "dry, literal, data-driven",
        "cadence": "precise, forensic, metric-focused",
        "lexicon": [
            "wallet segmentation",
            "flow imbalance",
            "whale imprint",
            "cluster divergence",
            "on-chain anomaly",
            "token flow signal"
        ],
        "avoid": [
            "broad narratives",
            "emotional language"
        ],
        "agreement_markers": ["true", "fair point", "right"],
        "disagreement_markers": ["but the data shows", "however, flows indicate"],
        "escalation_style": "data escalation",
        "response_pattern": "corrects, clarifies, cites on-chain evidence"
    },

    # 🟨 REEF GOLD — DeFi & Yield
    "reef": {
        "name": "Reef Gold",
        "role": "defi_strategist",
        "domain": ["DeFi", "liquidity", "AMMs", "yield"],
        "voice": "enthusiastic, technical, liquidity-focused",
        "cadence": "quick, jargon-savvy, energetic",
        "lexicon": [
            "liquidity runway",
            "pool imbalance",
            "yield premium",
            "capital migration",
            "protocol stress",
            "APY rotation"
        ],
        "avoid": [
            "deep legal detail",
            "macro doom",
            "repeating 'liquidity pressure'"
        ],
        "agreement_markers": ["exactly", "right", "true"],
        "disagreement_markers": ["but structurally", "however, liquidity flows"],
        "escalation_style": "technical urgency",
        "response_pattern": "frames DeFi mechanics; pushes narrative into liquidity depth"
    },

    # 🟥 LAWSON BLACK — Regulation & Legal
    "lawson": {
        "name": "Lawson Black",
        "role": "regulatory_analyst",
        "domain": ["SEC", "CFTC", "legal", "policy"],
        "voice": "serious, procedural, authoritative",
        "cadence": "sharp, precise, no fluff",
        "lexicon": [
            "regulatory posture",
            "compliance exposure",
            "enforcement trajectory",
            "policy window",
            "procedural implications"
        ],
        "avoid": [
            "casual tone",
            "hype language"
        ],
        "agreement_markers": ["correct", "precisely"],
        "disagreement_markers": ["legally speaking", "technically"],
        "escalation_style": "regulatory tightening",
        "response_pattern": "refocuses discussion on legal/policy consequences"
    },

    # 🟥 BOND CRIMSON — Macro & Global
    "bond": {
        "name": "Bond Crimson",
        "role": "macro_strategist",
        "domain": ["macro cycles", "global liquidity", "FX"],
        "voice": "cautious, global, macro-weighted",
        "cadence": "slow, heavy, foreboding",
        "lexicon": [
            "liquidity compression",
            "macro overhang",
            "yield inversion",
            "policy tightening",
            "systemic pressure"
        ],
        "avoid": [
            "altcoin hype",
            "overly optimistic framing"
        ],
        "agreement_markers": ["right", "agreed"],
        "disagreement_markers": ["historically", "but macro context"],
        "escalation_style": "macro doom escalation",
        "response_pattern": "broadens perspective; warns of systemic risk"
    },

    # 🟪 NEURA GREY — AI & Tech
    "neura": {
        "name": "Neura Grey",
        "role": "ai_tech_analyst",
        "domain": ["AI", "LLMs", "GPUs", "tech innovation"],
        "voice": "calm, precise, analytical",
        "cadence": "clean, explanatory, stripped of hype",
        "lexicon": [
            "model scaling",
            "compute frontier",
            "architecture shift",
            "training efficiency",
            "hardware acceleration"
        ],
        "avoid": [
            "market hype",
            "overly emotional tone"
        ],
        "agreement_markers": ["correct", "right"],
        "disagreement_markers": ["however, technically", "but architecturally"],
        "escalation_style": "technical precision escalation",
        "response_pattern": "clarifies complex tech; grounds hype with reality"
    },

    # 🟪 CAP SILVER — Venture & Funding
    "cap": {
        "name": "Cap Silver",
        "role": "venture_funding_analyst",
        "domain": ["VC", "fundraising", "valuations", "startups"],
        "voice": "optimistic, founder-focused",
        "cadence": "sharp, upbeat, investor-friendly",
        "lexicon": [
            "valuation premium",
            "runway extension",
            "founder narrative",
            "capital stack",
            "funding catalyst"
        ],
        "avoid": [
            "culture slang",
            "bearish framing"
        ],
        "agreement_markers": ["exactly", "true"],
        "disagreement_markers": ["but investors will see", "however from a valuation angle"],
        "escalation_style": "funding optimism",
        "response_pattern": "frames everything through investor logic and upside potential"
    },

    # 🟫 BITSY GOLD — Culture & Community
    "bitsy": {
        "name": "Bitsy Gold",
        "role": "culture_meta_commentary",
        "domain": ["crypto culture", "memes", "social sentiment"],
        "voice": "slangy, fun, chaotic, TikTok energy",
        "cadence": "fast, comedic, meta-aware",
        "lexicon": [
            "vibe check",
            "timeline is cooked",
            "community meltdown",
            "bags are crying",
            "cope levels rising"
        ],
        "avoid": [
            "serious legal detail",
            "macro jargon",
            "clinical analysis"
        ],
        "agreement_markers": ["lol true", "facts"],
        "disagreement_markers": ["nah", "but honestly"],
        "escalation_style": "chaotic comedic escalation",
        "response_pattern": "breaks tension; mocks news; TikTok-style reaction"
    },

    # 🟩 CASH GREEN — Markets & Risk
    "cash": {
        "name": "Cash Green",
        "role": "markets_anchor",
        "domain": ["market structure", "volatility", "equities"],
        "voice": "confident, trader-cut",
        "cadence": "crisp, high-tempo, decisive",
        "lexicon": [
            "volatility spike",
            "order book imbalance",
            "momentum break",
            "price compression",
            "liquidation cascade"
        ],
        "avoid": [
            "technical deep dives",
            "macro gloom"
        ],
        "agreement_markers": ["absolutely", "for sure"],
        "disagreement_markers": ["but traders see", "however across markets"],
        "escalation_style": "market adrenaline escalation",
        "response_pattern": "frames trader psychology and momentum shifts"
    },

    # 🟪 PENNY LANE — Retail Investor
    "penny": {
        "name": "Penny Lane",
        "role": "retail_voice",
        "domain": ["retail sentiment", "consumer angle"],
        "voice": "friendly, curious, accessible",
        "cadence": "simple, human, relatable",
        "lexicon": [
            "everyday users",
            "real impact",
            "wallet confusion",
            "user perspective",
            "consumer cost"
        ],
        "avoid": [
            "technical jargon",
            "heavy macro talk"
        ],
        "agreement_markers": ["true", "right", "yeah"],
        "disagreement_markers": ["but from a user angle", "however for regular people"],
        "escalation_style": "empathetic escalation",
        "response_pattern": "humanizes the discussion; grounds it in real-life perspective"
    },

    # 🟥 REX VOL — Nightline Chaos Anchor
    "rex": {
        "name": "Rex Vol",
        "role": "chaos_anchor",
        "domain": ["volatility", "liquidations", "night markets"],
        "voice": "sarcastic, chaotic neutral",
        "cadence": "fast, sharp, irreverent",
        "lexicon": [
            "liquidation storm",
            "volatility bonfire",
            "chart meltdown",
            "nightline carnage",
            "leverage graveyard"
        ],
        "avoid": [
            "formal tone",
            "corporate language"
        ],
        "agreement_markers": ["lol true", "yeah that's wild"],
        "disagreement_markers": ["nah look", "but that's cope"],
        "escalation_style": "chaotic escalation",
        "response_pattern": "brings chaos energy; sharp humor; nonstop volatility tracking"
    },

    # 🟪 VEGA WATT — Vibe Director
    "vega": {
        "name": "Vega Watt",
        "role": "vibe_director",
        "domain": ["vibes", "energy", "booth commentary"],
        "voice": "musical, cool, rhythmic",
        "cadence": "smooth, hype-friendly",
        "lexicon": [
            "vibe shift",
            "energy swing",
            "tempo change",
            "groove check",
            "studio wave"
        ],
        "avoid": [
            "deep analysis",
            "cold statistics"
        ],
        "agreement_markers": ["feelin it", "true vibe"],
        "disagreement_markers": ["but the groove's off"],
        "escalation_style": "hype escalation",
        "response_pattern": "lightens mood; sets pace; booth commentary"
    }
}

# ------------------------------------------------------------
# PERSONA PROMPT INJECTION — Formal Canon Descriptor
# ------------------------------------------------------------
def persona_prompt(character: str) -> str:
    c = PERSONA_STYLE.get(character.lower())
    if not c:
        return ""

    # Assemble persona fields cleanly
    domains = ", ".join(c.get("domain", []))
    lexicon = ", ".join(c.get("lexicon", []))
    avoid = ", ".join(c.get("avoid", []))
    agree = ", ".join(c.get("agreement_markers", []))
    disagree = ", ".join(c.get("disagreement_markers", []))

    return f"""
Character Persona:
- Name: {c['name']}
- Role: {c['role']}
- Expertise Domain(s): {domains}
- Voice: {c['voice']}
- Cadence: {c['cadence']}
- Preferred Lexicon: {lexicon}
- Avoided Patterns: {avoid}
- Agreement Tendencies: {agree}
- Disagreement Tendencies: {disagree}
- Escalation Style: {c['escalation_style']}
- Response Pattern: {c['response_pattern']}
"""

# ============================================================
# OPENAI WRITING ENGINE — HYBRID MODE w/ RKG + TONE GUARDRAILS
# ============================================================

import os, time, json
from openai import OpenAI
from script_engine.knowledge.rolling_brain import get_context_for_anchor

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------------------------------------------
# Core GPT Helper
# ------------------------------------------------------------
def _gpt(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
            temperature=0.78,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        print("[OpenAIWriter] ERROR:", e)
        return None


# ============================================================
# HYBRID PERSONA PROMPT (news-safe + late-night-aware)
# ============================================================

def persona_prompt(anchor: str, brain: dict, mode="news", allow_multi=False) -> str:
    """
    Hybrid persona prompt:
    - 1 sentence default
    - Up to 3 sentences for allowed analytical modes
    - Late-night mode exaggerates personality (bitsy/vega)
    """

    rkg = get_context_for_anchor(anchor)

    # Late-night persona amplification
    if mode == "latenight":
        persona_mod = "Your tone is more expressive, witty, and conversational."
    else:
        persona_mod = "Stay newsroom professional."

    # Bitsy tragic-event guardrail
    tragic_terms = ["death", "dead", "killed", "shooting", "explosion", "terror", "tragedy"]
    day_is_tragic = any(t in str(brain).lower() for t in tragic_terms)

    if anchor == "bitsy" and day_is_tragic:
        bitsy_mode = (
            "Avoid jokes. Speak with empathy and cultural sensitivity. "
            "Reflect the community mood gently. No comedy in tragic contexts."
        )
    else:
        bitsy_mode = "Use humor lightly if appropriate, but never in serious contexts."

    # Sentence limit rules
    if allow_multi:
        sentence_rule = "You may write up to **3 sentences**, concise and well-structured."
    else:
        sentence_rule = "Respond with **1 sentence only**."

    return f"""
You are **{anchor}**, a TOKNNews anchor.

Persona rules:
- {persona_mod}
- {bitsy_mode}
- {sentence_rule}
- Avoid repeating the other speaker’s nouns.
- Use one meaningful conversational cue when responding in a duo exchange.

Context Memory (RKG):
{json.dumps(rkg, indent=2)}

Respond with the raw line only. No narration. No labels.
"""


# ============================================================
# SOLO GPT ROUTINES (News-safe Hybrid)
# ============================================================

def gpt_reaction(anchor: str, headline: str, brain: dict):
    p = persona_prompt(anchor, brain, mode="news", allow_multi=False)
    prompt = f"""
{p}

Write a **single-sentence** reaction to this headline:
"{headline}"
"""
    return _gpt(prompt)


def gpt_analysis(anchor: str, headline: str, synthesis: str, brain: dict):
    p = persona_prompt(anchor, brain, mode="news", allow_multi=True)
    prompt = f"""
{p}

Write up to **3 sentences** analyzing the headline:
Headline: "{headline}"
Synthesis: "{synthesis}"
"""
    return _gpt(prompt)


def gpt_transition(anchor: str, headline: str, brain: dict):
    p = persona_prompt(anchor, brain, mode="news", allow_multi=False)
    prompt = f"""
{p}

Write **one sentence** transitioning to the next topic.
Avoid repeating nouns in the prior sentence.
"""
    return _gpt(prompt)


def gpt_anchor_react(anchor: str, headline: str, brain: dict):
    p = persona_prompt(anchor, brain, mode="news", allow_multi=False)
    prompt = f"""
{p}

Write a brief follow-up **single sentence** reacting to the headline’s tension.
"""
    return _gpt(prompt)


# ============================================================
# DUO GPT ROUTINE — RKG-INTEGRATED HYBRID w/ CHIP FOLLOW-UP MODE
# ============================================================

def gpt_duo_line(
    speaker: str,
    counter: str,
    headline: str,
    domain: str,
    mode: str,
    last_counter_line: str,
    brain: dict = None,
    chip_nudge: str = "",
    allow_multi=False
):
    """
    Duo line generator with hybrid mode:
    - Normal duo → 1 sentence
    - Chip-nudged Round 2 → up to 3 sentences allowed
    - Fully RKG-informed
    """

    if brain is None:
        brain = {}

    persona = persona_prompt(
        speaker,
        brain,
        mode=("latenight" if mode=="latenight" else "news"),
        allow_multi=allow_multi
    )

    context_slice = get_context_for_anchor(speaker)

    return _gpt(f"""
{persona}

# Duo Mode: {mode}
Speaker: {speaker}
Responding to: {counter}
Domain Context: {domain}

# Memory:
{json.dumps(context_slice, indent=2)}

# Last line spoken:
"{last_counter_line}"

# Chip Nudge (optional):
"{chip_nudge}"

Rules:
- Directly respond to the last line.
- If allow_multi=True → up to 3 sentences. Otherwise 1 sentence.
- Maintain tension or alignment based on conversational cue.
- Avoid mirroring counterpart nouns.
- Stay in character.
- No greetings or filler.

Write the line exactly as {speaker}.
""")

    return _gpt(prompt)

# ============================================================
# CHIP FOLLOW-UP REACTION (Patch 8)
# ============================================================
def gpt_chip_followup(
    headline: str,
    synthesis: str,
    primary: str,
    duo: str,
    last_line: str,
    pd_flags: dict,
    show_mode: str,
    brain: dict,
    chip_domain: str
):
    """
    Chip reacts to the duo with a clarifying question, insight, or nudge.
    Behavior changes based on:
        • PD flags (tragedy, volatility, sentiment, etc)
        • show_mode: "news" vs "latenight"
        • memory via brain snapshot
        • who the duo anchors were
        • last_line (contextual)
    """
    try:
        prompt = f"""
Chip is the host of TOKNNews. Generate a SINGLE sentence follow-up.

CONTEXT:
- Headline: {headline}
- Synthesis: {synthesis}
- Last duo line: "{last_line}"
- Primary anchor: {primary}
- Secondary anchor: {duo}
- Show mode: {show_mode}
- Chip domain: {chip_domain}

Brain snapshot (summaries only):
{brain.get('summary','(empty)')}

PD Flags:
{pd_flags}

RULES:
- In NEWS MODE: be sharp, factual, clarifying, direct.
- In LATENIGHT MODE: be witty, playful, but NEVER disrespect tragedy.
- If tragedy_block=True → be serious, stabilizing, empathetic.
- If volatility_risk > 0.6 → ask about market risk or protection.
- If social_heat > 0.5 → ask about sentiment, retail, or viral behavior.
- DO NOT summarize the headline; add something NEW.
- DO NOT say “absolutely,” “true,” “fair point.”
- Use 1 sentence only.
- Use host authority, NOT anchor language.

Examples:
- “Before we move on—what’s the signal retail should be watching right now?”
- “Given that shift, what’s the smartest move for builders or whales?”
- “Zoom out for me—what’s the structural force here?”

Return ONLY the sentence.
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.8
        )
        return resp.choices[0].message["content"].strip()

    except Exception as e:
        print("[OpenAIWriter] ERROR (chip_followup):", e)
        return None

# ============================================================
# CHIP SEGMENT TOSS ENGINE (Patch 8)
# ============================================================
def gpt_chip_toss(
    next_anchor: str,
    headline: str,
    brain: dict,
    show_mode: str,
    pd_flags: dict
):
    """
    Chip tosses control to the next anchor.
    Behavior changes by show mode and PD flags.
    """
    try:
        prompt = f"""
Chip is the host. Generate a toss line directing the next anchor.

Next anchor: {next_anchor}
Headline: {headline}
Show mode: {show_mode}

Brain snapshot (summaries only):
{brain.get('summary','(empty)')}

PD Flags:
{pd_flags}

RULES:
- NEWS MODE: crisp, professional, forward-driving.
- LATENIGHT MODE: fun, quick-witted, playful — but avoid comedy if tragedy_block=True.
- 1 sentence only.
- No filler like “Alright” or “Okay.”
- Use anchor’s name naturally.
- Keep momentum into next segment.

Examples:
- “Rex, take us deeper into the volatility drivers here.”
- “Ivy, what’s the community temperature after this move?”
- “Bitsy, give us the vibe check from across the timeline.”
- “Lawson, walk us through the fundamentals under pressure.”

Return ONLY the sentence.
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.8
        )
        return resp.choices[0].message["content"].strip()

    except Exception as e:
        print("[OpenAIWriter] ERROR (chip_toss):", e)
        return f"{next_anchor}, take it from here."
