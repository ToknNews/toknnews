from fastapi import APIRouter
import requests
import time
from .ingestion_aggregator import update_stories

router = APIRouter(prefix="/ingest/v2")

BASE = "http://localhost:8800/ingest/v2"

@router.get("/run_cycle")
def run_cycle():
    items = requests.get(f"{BASE}/fetch_all").json()["items"]

    enriched = []
    for item in items:
        r = requests.post(f"{BASE}/enrich", json=item)
        enriched.append(r.json())

    # DEBUG — always runs
    print("\n[DEBUG] First enriched item:\n", enriched[0], "\n")

    # ---------------------------------------------------------
    # UPDATE MULTI–STORY ROLLING MEMORY
    # ---------------------------------------------------------
    try:
        update_stories(enriched)
    except Exception as exc:
        print("[run_cycle] ERROR updating rolling stories:", exc)

    # ---------------------------------------------------------
    # LEGACY SUBMISSION DISABLED
    # (Episode Builder now handles all script generation)
    # ---------------------------------------------------------
    submitted = []

    return {
        "status": "complete",
        "fetched": len(items),
        "enriched": len(enriched),
        "submitted": len(submitted)
    }
