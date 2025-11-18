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

# ------------- Core Writer Helper ---------------------------
def _gpt(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.8,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        print("[OpenAIWriter] ERROR:", e)
        return None


# ------------------------------------------------------------
# REACTION LINE (GPT)
# ------------------------------------------------------------
def gpt_reaction(character: str, headline: str, domain: str) -> str:
    prompt = f"""
Write a concise newsroom-style reaction from {character} about:
"{headline}"

Character Profile:
- Domain: {domain}
- Tone: direct, adult, newsroom cadence.
- No emojis.

Keep it under 18 words.
"""
    return _gpt(prompt)


# ------------------------------------------------------------
# ANALYSIS LINE (GPT)
# ------------------------------------------------------------
def gpt_analysis(character: str, headline: str, synthesis: str, domain: str) -> str:
    prompt = f"""
Write a brief analysis line for {character} about:
Headline: "{headline}"
Synthesis: "{synthesis}"

Character Profile:
- Domain: {domain}
- Tone: analytical, concise, newsroom energy.
- No emojis.

Keep it under 22 words.
"""
    return _gpt(prompt)


# ------------------------------------------------------------
# TRANSITION LINE (GPT)
# ------------------------------------------------------------
def gpt_transition(character: str, next_anchor: str, domain: str) -> str:
    prompt = f"""
Write a clean newsroom transition from {character} tossing to {next_anchor}.
Domain context: {domain}
No emojis.
Under 18 words.
"""
    return _gpt(prompt)


# ------------------------------------------------------------
# ANCHOR REACT LINE (GPT)
# ------------------------------------------------------------
def gpt_anchor_react(character: str, headline: str, domain: str) -> str:
    prompt = f"""
Write a short reaction line where {character} summarizes the key tension in:
"{headline}"
Domain: {domain}
Keep it tight, adult, newsroom cadence.
No emojis.
"""
    return _gpt(prompt)


# ------------------------------------------------------------
# DUO CROSSTALK LINES (GPT)
# ------------------------------------------------------------
def gpt_duo_line(speaker: str, counter: str, headline: str, domain: str, mode: str) -> str:
    prompt = f"""
Write a duo-crosstalk line.

Speaker: {speaker}
Counterpart: {counter}
Headline: "{headline}"
Domain: {domain}
Mode: {mode} (react, rebuttal, reinforce)

Tone:
- newsroom realism
- adult
- no emojis
- under 22 words
"""
    return _gpt(prompt)
