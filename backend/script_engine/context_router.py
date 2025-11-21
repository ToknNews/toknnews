# Simple context router for anchors based on domains, synthesis, and persona
def get_context_for_anchor(anchor: str):
    """
    Returns a minimal 'context block' for persona_prompt().
    This function is referenced in openai_writer but missing.
    """
    anchor = anchor.lower()

    if anchor in ("reef",):
        return {"domain": "defi", "style": "high_energy"}
    if anchor in ("lawson",):
        return {"domain": "regulatory", "style": "formal"}
    if anchor in ("bond",):
        return {"domain": "macro", "style": "measured"}
    if anchor in ("cash",):
        return {"domain": "retail", "style": "witty"}
    if anchor in ("ivy",):
        return {"domain": "sentiment", "style": "warm"}
    if anchor in ("penny",):
        return {"domain": "retail", "style": "simple"}
    if anchor in ("ledger",):
        return {"domain": "onchain", "style": "dry"}
    if anchor in ("bitsy",):
        return {"domain": "meta", "style": "chaotic"}
    if anchor in ("vega",):
        return {"domain": "voiceover", "style": "smooth"}

    # default to general-news Chip context
    return {"domain": "general", "style": "neutral"}
