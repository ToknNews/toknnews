#!/usr/bin/env python3
"""
TOKNNews — Broadcast Loop (20-minute episode cycle)
 - Builds episode
 - Runs episode (segment → script → audio)
 - Sleeps until next cycle
"""

import time
import sys
import os

ROOT = "/var/www/toknnews-live/backend"
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from script_engine.episode_runner import run_episode

EPISODE_MINUTES = 20

def main_loop():
    while True:
        print("[BroadcastLoop] Starting new ToknNews episode…")

        blocks = run_episode()

        print(f"[BroadcastLoop] Episode complete ({len(blocks)} blocks).")
        print(f"[BroadcastLoop] Sleeping for {EPISODE_MINUTES} minutes…")

        time.sleep(EPISODE_MINUTES * 60)


if __name__ == "__main__":
    main_loop()
