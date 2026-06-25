# services/seeds/misttrack.py
"""
MistTrack risk API — IMPORTANT CORRECTION vs. the original architecture
doc: this is no longer a free-signup API as of June 2026. The OpenAPI now
requires an active Standard/Compliance paid plan subscription
(dashboard.misttrack.io), OR per-call payment via the x402 protocol
(EVM/USDC, no subscription needed but each call costs real money). There
is no longer a free tier with a daily quota.

This module is kept as an OPTIONAL enrichment step you can wire in if you
already have or are willing to get a paid MistTrack plan — it's not
required for the pipeline to work, since `collect_seeds.py` doesn't call
it by default. We enrich EXISTING seeds with MistTrack's label/risk score
rather than use it as a primary discovery source.
"""
import requests
from datetime import datetime, timezone


def enrich_with_misttrack(addresses: list[str], api_key: str, max_calls: int = 50) -> list[dict]:
    """Each call costs real quota/money under MistTrack's current pricing
    (paid plan or x402 pay-per-call) — max_calls defaults conservatively low."""
    now = datetime.now(timezone.utc).isoformat()
    out: list[dict] = []
    for addr in addresses[:max_calls]:
        try:
            r = requests.get("https://openapi.misttrack.io/v1/risk_score",
                             params={"coin": "BTC", "address": addr, "api_key": api_key},
                             timeout=30).json()
            if r.get("data", {}).get("score", 0) >= 70:
                out.append({"address": addr, "entity_name": r["data"].get("label", "misttrack"),
                            "source": "MISTTRACK", "confidence": 0.8,
                            "category": "WATCHLISTED", "fetched_at": now})
        except Exception:
            continue
    return out


if __name__ == "__main__":
    import os
    test_addrs = ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"]
    key = os.getenv("MISTTRACK_API_KEY", "")
    if key:
        print(enrich_with_misttrack(test_addrs, key))
    else:
        print("MISTTRACK_API_KEY not set — this is expected if you're not using a paid "
              "MistTrack plan. This module is optional; skip it entirely if you'd rather "
              "not pay for it. See setup/windows/08_dataset_downloads.md.")
