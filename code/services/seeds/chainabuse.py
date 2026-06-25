# services/seeds/chainabuse.py
"""
Chainabuse — community-submitted scam/fraud reports. NOT government-
verified, so confidence = 0.6 (a single community report only nudges the
Bayesian posterior; it never forces BLACKLISTED on its own).

IMPORTANT CORRECTION vs. the original architecture doc: the standard free
API key is rate-limited to 10 calls/month (1 call = up to 50 reports),
not a generous daily quota. That's roughly 500 reports/month total across
every call you make — fine for an occasional seed-refresh before a demo,
but budget calls carefully; don't call this in a loop. Law-enforcement and
partner tiers get higher limits but require a separate vetting/contact
process (see setup/windows/08_dataset_downloads.md).
"""
import requests
from datetime import datetime, timezone

API = "https://api.chainabuse.com/v0/reports"


def fetch_chainabuse(api_key: str | None = None, limit: int = 50) -> list[dict]:
    """limit defaults to 50 (the max reports per call) since the free key
    only allows 10 calls/month total — don't call this repeatedly in a loop."""
    headers = {"X-API-KEY": api_key} if api_key else {}
    now = datetime.now(timezone.utc).isoformat()
    out: list[dict] = []
    try:
        resp = requests.get(API, headers=headers,
                            params={"cryptocurrency": "BTC", "limit": limit},
                            timeout=30)
        resp.raise_for_status()
        for rep in resp.json().get("reports", []):
            addr = rep.get("address")
            if not addr:
                continue
            out.append({
                "address": addr,
                "entity_name": rep.get("scamCategory", "COMMUNITY_REPORT"),
                "source": "CHAINABUSE",
                "confidence": 0.6,          # community report, unverified
                "category": "WATCHLISTED",  # not BLACKLISTED on its own
                "fetched_at": now,
            })
    except Exception as e:           # never let one source break the whole collector
        print(f"  Chainabuse error (non-fatal): {e}")
    return out


if __name__ == "__main__":
    import os
    seeds = fetch_chainabuse(os.getenv("CHAINABUSE_KEY"))
    print(f"Chainabuse: {len(seeds)} reports (remember: 10 calls/month on the free tier)")
