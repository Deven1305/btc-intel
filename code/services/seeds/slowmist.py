# services/seeds/slowmist.py
"""SlowMist maintains an open blockchain-blacklist GitHub repo (hacks, exploits,
scams). Free, no key — a plain JSON file fetched over HTTPS."""
import requests
from datetime import datetime, timezone

SLOWMIST = ("https://raw.githubusercontent.com/slowmist/"
            "blockchain-blacklist/main/blacklist.json")


def fetch_slowmist(timeout: int = 60) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    out: list[dict] = []
    try:
        data = requests.get(SLOWMIST, timeout=timeout).json()
        for entry in data if isinstance(data, list) else data.get("blacklist", []):
            addr = entry.get("address", "")
            if addr.startswith(("1", "3", "bc1")):
                out.append({"address": addr, "entity_name": entry.get("type", "slowmist"),
                            "source": "SLOWMIST", "confidence": 0.75,
                            "category": "WATCHLISTED", "fetched_at": now})
    except Exception as e:
        print(f"  SlowMist error (non-fatal): {e}")
    return out


if __name__ == "__main__":
    seeds = fetch_slowmist()
    print(f"SlowMist: {len(seeds)} Bitcoin addresses")
