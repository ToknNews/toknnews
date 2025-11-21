#!/usr/bin/env python3
"""
TOKNNews — Multi-Story Ingestion Aggregator
Builds and maintains rolling_stories.json with:
- deduped headlines
- domain classification
- sentiment tag
- importance score
- timestamp
"""

import json
import time
import os
import hashlib

ROLLING_PATH = "/var/www/toknnews-live/data/rolling_stories.json"
# Path for Chip's dynamic top-story rundown feed
TOP_STORIES_PATH = "/var/www/toknnews-live/data/top_stories.json"

# ---------------------------------------------------------
# Save top stories (Chip's rundown input)
# ---------------------------------------------------------
def save_top_stories(stories):
    with open(TOP_STORIES_PATH, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)


# ---------------------------------------------------------
# Build top stories dynamically (3, 5, or 7)
# based on importance, recency, and domain stress.
# ---------------------------------------------------------
def build_top_stories(rolling, max_calm=3, max_medium=5, max_hot=7):
    now = time.time()
    window_sec = 72 * 3600  # 72 hours fast memory

    # Keep only stories in fast memory
    recent = [s for s in rolling if now - s["timestamp"] <= window_sec]

    if not recent:
        save_top_stories([])
        return []

    # Stress score = how "hot" the news environment is
    stress_score = sum(
        1 for s in recent
        if s["importance"] >= 7 or s["domain"] in ("breaking", "markets", "volatility")
    )

    # Determine number of top stories based on stress
    if stress_score <= 2:
        top_n = max_calm
    elif stress_score <= 5:
        top_n = max_medium
    else:
        top_n = max_hot

    # Sort by (importance desc, recency desc)
    ranked = sorted(
        recent,
        key=lambda s: (s["importance"], s["timestamp"]),
        reverse=True
    )

    top = ranked[:top_n]
    save_top_stories(top)
    return top


# ---------------------------------------------------------
# Load existing stories
# ---------------------------------------------------------
def load_rolling():
    if not os.path.exists(ROLLING_PATH):
        return []

    try:
        with open(ROLLING_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# ---------------------------------------------------------
# Save updated stories
# ---------------------------------------------------------
def save_rolling(stories):
    with open(ROLLING_PATH, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)


# ---------------------------------------------------------
# Simple domain classifier (stub — will expand later)
# ---------------------------------------------------------
def classify_domain(text):
    t = text.lower()
    if "defi" in t or "liquidity" in t or "protocol" in t:
        return "defi"
    if "sec" in t or "regulat" in t or "legal" in t:
        return "regulation"
    if "bitcoin" in t or "btc" in t:
        return "bitcoin"
    if "macro" in t or "fed" in t or "interest" in t:
        return "macro"
    if "ai" in t or "gpu" in t or "model" in t:
        return "ai_tech"
    return "general"


# ---------------------------------------------------------
# Headline hashing for deduplication
# ---------------------------------------------------------
def hash_headline(text):
    return hashlib.md5(text.strip().lower().encode()).hexdigest()


# ---------------------------------------------------------
# Add new headlines to rolling memory
# ---------------------------------------------------------
def update_stories(new_headlines):
    """
    new_headlines: list of dicts like:
    {
       "headline": "...",
       "summary": "...",
       "sentiment": ...,
       "importance": ...,
       "timestamp": ...
    }
    """
    rolling = load_rolling()
    existing_hashes = {item["hash"] for item in rolling}

    for story in new_headlines:
        h = hash_headline(story["headline"])
        if h in existing_hashes:
            continue  # skip duplicates

        domain = story.get("domain") or classify_domain(story["headline"])

        rolling.append({
            "headline": story["headline"],
            "summary": story.get("summary", ""),
            "sentiment": story.get("sentiment", "neutral"),
            "importance": story.get("importance", 5),
            "domain": domain,
            "timestamp": story.get("ts", time.time()),
            "timestamp": story.get("timestamp", time.time()),
            "hash": h
        })

        existing_hashes.add(h)

    # keep latest 20 stories
    rolling = sorted(rolling, key=lambda x: x["timestamp"], reverse=True)[:20]

    save_rolling(rolling)

    # ---------------------------------------------------------
    # ALSO BUILD TOP STORIES DYNAMICALLY FOR CHIP / PD
    # ---------------------------------------------------------
    build_top_stories(rolling)

    return rolling
