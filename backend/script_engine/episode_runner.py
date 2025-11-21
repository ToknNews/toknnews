#!/usr/bin/env python3
"""
TOKNNews — Episode Runner (Clean Manual Trigger + Audio Stitching)
Builds a full episode:
 - Chip rundown
 - Deep dive
 - Anchor analysis
Then:
 - Generates ALL ElevenLabs audio blocks
 - Stitches them into ONE final .mp3 file
"""

import time
import json
import os
import requests

from script_engine.knowledge.episode_builder import build_episode, save_episode
from script_engine.script_engine_v3 import generate_script
from script_engine.audio.audio_block_renderer import render_audio_blocks

BROADCAST_DIR = "/var/www/toknnews-live/data/broadcast_blocks"


# =====================================================================
# MAIN EPISODE RUNNER
# =====================================================================

def run_episode():

    # 1. Build episode structure
    episode = build_episode(rundown_count=6)

    if "error" in episode:
        print("[EpisodeRunner] No stories available.")
        return None

    # 2. Save episode metadata
    ep_path = save_episode(episode)
    print("[EpisodeRunner] Episode saved:", ep_path)

    os.makedirs(BROADCAST_DIR, exist_ok=True)
    block_files = []

    # =================================================================
    # 3. Generate all segment blocks
    # =================================================================
    for seg in episode["segments"]:
        seg_type = seg["type"]

        # -------------------------------------------------------------
        # CHIP RUNDOWN
        # -------------------------------------------------------------
        if seg_type == "chip_rundown":
            for rd in seg["stories"]:
                primary = "chip"
                pkg = generate_script(
                    headline=rd["headline"],
                    article_context=rd["summary"],
                    cluster_articles=[],
                    character=primary,
                    pd_suggested_anchor=primary,
                    rundown_headlines=[item["headline"] for item in episode["rundown"]],
                    rundown_summaries=[item["summary"] for item in episode["rundown"]],

                )

                # save block
                block_path = save_block(pkg)
                block_files.append(block_path)

                # render audio for this block
                scene_id = pkg.get("scene_id", "manual_scene")
                render_audio_blocks(scene_id, pkg["audio_blocks"])

        # -------------------------------------------------------------
        # DEEP DIVE
        # -------------------------------------------------------------
        elif seg_type == "deep_dive":
            dd = seg["story"]
            anchors = dd.get("anchors", ["chip"])
            primary = anchors[0]

            pkg = generate_script(
                headline=dd["headline"],
                article_context=dd["summary"],
                cluster_articles=[],
                character=primary,
                pd_suggested_anchor=primary,
                rundown_headlines=[item["headline"] for item in episode["rundown"]],
                rundown_summaries=[item["summary"] for item in episode["rundown"]],

            )

            block_path = save_block(pkg)
            block_files.append(block_path)

            scene_id = pkg.get("scene_id", "manual_scene")
            render_audio_blocks(scene_id, pkg["audio_blocks"])

        # -------------------------------------------------------------
        # ANCHOR ANALYSIS
        # -------------------------------------------------------------
        elif seg_type == "anchor_analysis":
            anchors = seg.get("anchors", ["chip"])
            primary = anchors[0]

            pkg = generate_script(
                headline=seg["headline"],
                article_context=seg["summary"],
                cluster_articles=[],
                character=primary,
                pd_suggested_anchor=primary,
                rundown_headlines=[item["headline"] for item in episode["rundown"]],
                rundown_summaries=[item["summary"] for item in episode["rundown"]],

            )

            block_path = save_block(pkg)
            block_files.append(block_path)

            scene_id = pkg.get("scene_id", "manual_scene")
            render_audio_blocks(scene_id, pkg["audio_blocks"])

        time.sleep(1)

    # =================================================================
    # 4. STITCH ALL AUDIO INTO ONE FINAL EPISODE MP3
    # =================================================================
    try:
        final_payload = {
            "scene_id": episode["episode_id"],
            "audio_blocks": []
        }

        # collect EVERY audio block written
        for fp in block_files:
            with open(fp, "r") as f:
                seg = json.load(f)
                final_payload["audio_blocks"].extend(seg["audio_blocks"])

        r = requests.post("http://localhost:8999/render_scene", json=final_payload)
        result = r.json()

        print("[EpisodeRunner] Final episode audio:", result)

    except Exception as e:
        print("[EpisodeRunner] ERROR stitching final audio:", e)

    return block_files



# =====================================================================
# SAVE BLOCK HELPER
# =====================================================================

def save_block(pkg):
    ts = int(time.time())
    fname = f"block_{ts}.json"
    path = os.path.join(BROADCAST_DIR, fname)

    with open(path, "w") as f:
        json.dump(pkg, f, indent=2)

    print(f"[EpisodeRunner] Saved broadcast block: {path}")
    return path



# =====================================================================
# ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    files = run_episode()
    print("[EpisodeRunner] Complete:", files)
