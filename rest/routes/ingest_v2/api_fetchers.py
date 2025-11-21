import time
import requests

# ============================================================
# API FETCHER REGISTRY (CryptoPanic-ready)
# ============================================================

# This dict grows over time. Adding API sources = 1 line.
API_SOURCES = {
    # MarketAux – fast & reliable
    "marketaux": {
        "enabled": True,
        "url": "https://api.marketaux.com/v1/news/all",
        "params": {
            "filter_entities": "true",
            "language": "en",
        },
        "key_env": "MARKETAUX_API_KEY",  # read from env
        "extract": "marketaux"
    },

    # NewsData.io – good backup source
    "newsdata": {
        "enabled": True,
        "url": "https://newsdata.io/api/1/news",
        "params": {
            "category": "top,technology,world",
            "q": "crypto OR blockchain OR bitcoin OR ethereum"
        },
        "key_env": "NEWSDATA_API_KEY",
        "extract": "newsdata"
    },

    # CryptoPanic placeholder (off for now)
    "cryptopanic": {
        "enabled": False,
        "url": "",
        "params": {},
        "key_env": "",
        "extract": "cryptopanic"
    }
}


# ============================================================
# Extractors for each API source
# ============================================================

def extract_marketaux(data):
    items = []
    for a in data.get("data", []):
        headline = a.get("title")
        url = a.get("url")
        ts = a.get("published_at")
        if not headline or not url or not ts:
            continue

        try:
            # Convert timestamp to unix
            published_ts = int(time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")))
        except:
            continue

        items.append({
            "id": headline + url,
            "headline": headline,
            "url": url,
            "source": "marketaux",
            "ts": published_ts
        })
    return items


def extract_newsdata(data):
    items = []
    for a in data.get("results", []):
        headline = a.get("title")
        url = a.get("link")
        ts = a.get("pubDate")

        if not headline or not url or not ts:
            continue

        try:
            published_ts = int(time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S")))
        except:
            continue

        items.append({
            "id": headline + url,
            "headline": headline,
            "url": url,
            "source": "newsdata",
            "ts": published_ts
        })
    return items


# ============================================================
# Main API fetcher
# ============================================================

def fetch_api_from_registry():
    final_items = []

    for name, conf in API_SOURCES.items():
        if not conf.get("enabled"):
            continue

        api_key = None
        if conf["key_env"]:
            import os
            api_key = os.getenv(conf["key_env"])

        params = dict(conf["params"])
        if api_key:
            params["api_token"] = api_key

        try:
            r = requests.get(conf["url"], params=params, timeout=8)
            data = r.json()

            if conf["extract"] == "marketaux":
                final_items.extend(extract_marketaux(data))

            elif conf["extract"] == "newsdata":
                final_items.extend(extract_newsdata(data))

        except Exception as e:
            print(f"[API_FETCH_ERROR] {name}: {e}")

    return final_items
