# services/seeds/cryptoscamdb.py
"""CryptoScamDB publishes an open address blacklist as JSON. Free, no key."""
import requests
from datetime import datetime, timezone

CSDB = "https://api.cryptoscamdb.org/v1/addresses"


def fetch_cryptoscamdb(timeout: int = 60) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    out: list[dict] = []
    try:
        data = requests.get(CSDB, timeout=timeout).json().get("result", {})
        for addr, entries in data.items():
            if addr.startswith(("1", "3", "bc1")):     # Bitcoin only
                cat = entries[0].get("category", "scam") if entries else "scam"
                out.append({"address": addr, "entity_name": cat,
                            "source": "CRYPTOSCAMDB", "confidence": 0.7,
                            "category": "WATCHLISTED", "fetched_at": now})
    except Exception as e:
        print(f"  CryptoScamDB error (non-fatal): {e}")
    return out


if __name__ == "__main__":
    seeds = fetch_cryptoscamdb()
    print(f"CryptoScamDB: {len(seeds)} Bitcoin addresses")
