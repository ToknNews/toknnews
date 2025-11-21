#!/usr/bin/env python3
"""
TOKNNews — Episode Runner
Executes a full 20-minute episode using:
 - Episode Builder
 - Script Engine V3
 - PD Hand-off for segment types
"""

import time
import json
import os

from script_engine.knowledge.episode_builder import build_episode, save_episode
from script_engine.script_engine_v3 import generate_script

BROADCAST_DIR = "/var/www/toknnews-live/data/broadcast_blocks"


def run_episode():
    # 1. Build episode structure
    episode = build_episode(rundown_count=6)

    if "error" in episode:
        print("[EpisodeRunner] No stories available.")
        return None

    # 2. Save the episode metadata file
    ep_path = save_episode(episode)
    print("[EpisodeRunner] Episode saved:", ep_path)

    # 3. Execute segment by segment
    os.makedirs(BROADCAST_DIR, exist_ok=True)
    block_files = []

    for idx, seg in enumerate(episode["segments"]):
        seg_type = seg["type"]

        # Determine segment headline + summary + anchors
        if seg_type == "chip_rundown":
            # Chip reads multiple short headlines
            for rd in seg["stories"]:
                pkg = generate_script(
                    headline=rd["headline"],
                    article_context=rd["summary"],
                    cluster_articles=[],
                    character="chip"
                )

                block_path = save_block(pkg)
                block_files.append(block_path)

        elif seg_type == "deep_dive":
            dd = seg["story"]
            pkg = generate_script(
                headline=dd["headline"],
                article_context=dd["summary"],
                cluster_articles=[],
                character="chip"
            )
            block_path = save_block(pkg)
            block_files.append(block_path)

        elif seg_type == "anchor_analysis":
            pkg = generate_script(
                headline=seg["headline"],
                article_context=seg["summary"],
                cluster_articles=[],
                character="chip"
            )
            block_path = save_block(pkg)
            block_files.append(block_path)

        time.sleep(1)

    return block_files


def save_block(pkg):
    """Save a script_engine_v3 output block."""
    ts = int(time.time())
    fname = f"block_{ts}.json"
    path = os.path.join(BROADCAST_DIR, fname)

    with open(path, "w") as f:
        json.dump(pkg, f, indent=2)

    print(f"[EpisodeRunner] Saved broadcast block: {path}")
    return path


if __name__ == "__main__":
    files = run_episode()
    print("[EpisodeRunner] Complete:", files)
