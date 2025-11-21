#!/usr/bin/env python3
"""
TOKNNews — Audio Block Renderer (Final)
All audio generation is routed through the tokn-audio service.
"""

import requests
import time

AUDIO_SERVER = "http://localhost:8999/render_scene"

def render_audio_blocks(scene_id, audio_blocks):
    """
    Accepts scene_id and list of audio_blocks (from timeline).
    Calls the tokn-audio service.
    Returns final_audio path or None.
    """

    payload = {
        "scene_id": scene_id,
        "audio_blocks": audio_blocks
    }

    try:
        r = requests.post(AUDIO_SERVER, json=payload)
        data = r.json()

        if data.get("status") == "ok":
            return data.get("final_audio")

        print("[Audio] Error via audio_block_renderer:", data)
        return None

    except Exception as e:
        print("[Audio] Exception:", e)
        return None
