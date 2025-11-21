from fastapi import APIRouter
import requests
import feedparser
import json
import time
import hashlib

router = APIRouter(prefix="/ingest/v2")

def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

# ---------------------------------------------------------
# Normalization Helpers (for dedupe)
# ---------------------------------------------------------
from urllib.parse import urlparse, parse_qs, urlunparse

def normalize_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        clean = parsed._replace(query="")  # strip ?utm=...
        return urlunparse(clean).strip().lower()
    except:
        return url.strip().lower()


def normalize_headline(text: str) -> str:
    return text.strip().lower()

# ---------------------------------------------------------
# Dedupe Layer — removes duplicate items across all sources
# ---------------------------------------------------------
def dedupe_items(items):
    seen_ids = set()
    seen_urls = set()
    seen_titles = set()
    final = []

    for item in items:
        url = normalize_url(item.get("url", ""))
        title = normalize_headline(item.get("headline", ""))
        _id = item.get("id", "")

        # Skip if any matcher has been seen
        if _id in seen_ids or url in seen_urls or title in seen_titles:
            continue

        seen_ids.add(_id)
        seen_urls.add(url)
        seen_titles.add(title)
        final.append(item)

    return final

# ---------------------------------------------------------
# LOAD FEED REGISTRY (RSS + API)
# ---------------------------------------------------------
REGISTRY_PATH = "/var/www/toknnews-live/backend/data/feeds/sources.json"

def load_registry():
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("[fetch_all] ERROR loading sources.json:", e)
        return {"rss": [], "api_feeds": {}}


# ---------------------------------------------------------
# FETCH RSS SOURCES (Auto-enabled)
# ---------------------------------------------------------
def fetch_rss_from_registry(rss_list):
    items = []

    for url in rss_list:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                headline = entry.get("title", "").strip()
                link = entry.get("link", "")
                if not headline:
                    continue

                # --------------------------------------------
                # STRICT TIMESTAMP EXTRACTION
                # --------------------------------------------
                published_ts = None

                if "published_parsed" in entry and entry.published_parsed:
                    published_ts = time.mktime(entry.published_parsed)

                elif "updated_parsed" in entry and entry.updated_parsed:
                    published_ts = time.mktime(entry.updated_parsed)

                # STRICT MODE: No timestamp → SKIP
                if not published_ts:
                    continue

                items.append({
                    "id": make_id(headline + link),
                    "headline": headline,
                    "url": link,
                    "source": "rss",
                    "ts": published_ts
                })

        except Exception as e:
            print(f"[fetch_rss] ERROR fetching {url}:", e)

    return items

# ---------------------------------------------------------
# FETCH API FEEDS (Only if enabled)
# ---------------------------------------------------------
def fetch_api_feeds(api_cfg):
    collected = []

    for name, config in api_cfg.items():
        if not config.get("enabled", False):
            continue

        try:
            endpoint = config["endpoint"]

            # Replace variables like {token} or {api_key}
            for key, val in config.items():
                if key in ["enabled"]:
                    continue
                endpoint = endpoint.replace(f"{{{key}}}", val or "")

            r = requests.get(endpoint, timeout=10)
            data = r.json()

            # Normalize different API structures
            if name == "cryptopanic":
                posts = data.get("results", [])
                for p in posts:
                    title = p.get("title", "").strip()
                    url = p.get("url", "")
                    if not title:
                        continue
                    collected.append({
                        "id": make_id(title + url),
                        "headline": title,
                        "url": url,
                        "source": name,
                        "ts": time.time()
                    })

            elif name == "crypto_compare":
                posts = data.get("Data", {}).get("Data", [])
                for p in posts:
                    title = p.get("title", "").strip()
                    url = p.get("url", "")
                    if not title:
                        continue
                    collected.append({
                        "id": make_id(title + url),
                        "headline": title,
                        "url": url,
                        "source": name,
                        "ts": time.time()
                    })

            elif name == "newsapi":
                articles = data.get("articles", [])
                for a in articles:
                    title = a.get("title", "").strip()
                    url = a.get("url", "")
                    if not title:
                        continue
                    collected.append({
                        "id": make_id(title + url),
                        "headline": title,
                        "url": url,
                        "source": name,
                        "ts": time.time()
                    })

            # ---------------------------
            # MarketAux extractor
            # ---------------------------
            elif name == "marketaux":
                posts = data.get("data", [])
                for a in posts:
                    title = a.get("title", "").strip()
                    url = a.get("url", "")
                    ts = a.get("published_at")

                    if not title or not url or not ts:
                        continue

                    # Parse MarketAux timestamp
                    try:
                        # Format: "2025-01-27T14:52:13Z"
                        published_ts = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
                    except:
                        published_ts = time.time()

                    collected.append({
                        "id": make_id(title + url),
                        "headline": title,
                        "url": url,
                        "source": "marketaux",
                        "ts": published_ts
                    })

            # ---------------------------
            # NewsData extractor
            # ---------------------------
            elif name == "newsdata":
                posts = data.get("results", [])
                for a in posts:
                    title = a.get("title", "").strip()
                    url = a.get("link", "")
                    ts = a.get("pubDate")

                    if not title or not url or not ts:
                        continue

                    try:
                        published_ts = time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                    except:
                        published_ts = time.time()

                    collected.append({
                        "id": make_id(title + url),
                        "headline": title,
                        "url": url,
                        "source": "newsdata",
                        "ts": published_ts
                    })


        except Exception as e:
            print(f"[fetch_api_feeds] ERROR in {name}:", e)

    return collected

@router.get("/fetch_all")
def fetch_all():
    registry = load_registry()
    results = []

    # ---------------------------------------------------------
    # Load RSS feeds (auto-enabled)
    # ---------------------------------------------------------
    rss_sources = registry.get("rss", [])
    if rss_sources:
        rss_items = fetch_rss_from_registry(rss_sources)
        results.extend(rss_items)

    # ---------------------------------------------------------
    # Load API feeds (only enabled ones)
    # ---------------------------------------------------------
    api_cfg = registry.get("api_feeds", {})
    if api_cfg:
        api_items = fetch_api_feeds(api_cfg)
        results.extend(api_items)

    # ---------------------------------------------------------
    # FRESHNESS FILTER — 12 hours (choose B)
    # ---------------------------------------------------------
    freshness_window_sec = 12 * 3600
    now = time.time()

    fresh_results = [
        r for r in results
        if (now - r.get("ts", now)) <= freshness_window_sec
    ]

    # Replace results with only fresh items
    results = fresh_results

    # ---------------------------------------------------------
    # DEDUPE — remove duplicates across all sources
    # ---------------------------------------------------------
    results = dedupe_items(results)

    return {
        "count": len(results),
        "items": results
    }
