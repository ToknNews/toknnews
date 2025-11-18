#!/usr/bin/env python3

import json
import sys

# ------------------------------------------------------------
# Dual-Mode Imports (Local vs Package)
# ------------------------------------------------------------
try:
    from script_engine.script_engine_v3 import generate_script
except ImportError:
    from script_engine_v3 import generate_script

filename = sys.argv[1] if len(sys.argv) > 1 else "test_payload.json"

with open(filename, "r") as f:
    enriched = json.load(f)

headline = enriched.get("headline", "")
article_context = enriched.get("article_context", "")
cluster_articles = enriched.get("cluster_articles", [])

script = generate_script(
    headline=headline,
    article_context=article_context,
    cluster_articles=cluster_articles
)

print(json.dumps(script, indent=2))
