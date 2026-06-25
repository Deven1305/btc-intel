# services/seeds/ofac_mirror.py
"""
Robust fallback for services/seeds/ofac.py.

OFAC occasionally changes the SDN XML schema, which breaks parsers. The
community-maintained repo github.com/0xB10C/ofac-sanctioned-digital-currency-
addresses publishes a clean, daily-updated sanctioned_addresses_XBT.txt.
If the XML parse fails, fall back to this file — same underlying data,
simpler format, no schema risk.
"""
import requests
from datetime import datetime, timezone

MIRROR = ("https://raw.githubusercontent.com/0xB10C/"
          "ofac-sanctioned-digital-currency-addresses/lists/sanctioned_addresses_XBT.txt")


def fetch_ofac_mirror(timeout: int = 60) -> list[dict]:
    resp = requests.get(MIRROR, timeout=timeout)
    resp.raise_for_status()
    now = datetime.now(timezone.utc).isoformat()
    return [{
        "address": line.strip(), "entity_name": "OFAC_SDN (mirror)",
        "source": "OFAC_SDN", "confidence": 1.0, "category": "BLACKLISTED",
        "fetched_at": now,
    } for line in resp.text.splitlines() if line.strip() and not line.startswith("#")]


if __name__ == "__main__":
    seeds = fetch_ofac_mirror()
    print(f"OFAC mirror: {len(seeds)} Bitcoin addresses")
    for s in seeds[:5]:
        print(" ", s["address"])
