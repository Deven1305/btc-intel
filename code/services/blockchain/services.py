# services/blockchain/services.py
"""
Classify each cluster BEFORE taint propagation. This ordering is the single
most important architectural rule in Phase 3:

  - Exchange       -> BREAKS the taint chain (KYC identifies the criminal
                       without contaminating millions of innocent customers)
  - Mixer/CoinJoin -> amplifies/dilutes taint across all outputs
  - Mining pool    -> origin-clean (mints new coins, no tainted input by
                       definition)

If you propagate taint before classifying services, taint flows THROUGH an
exchange and falsely contaminates every customer. Fixing that afterward
means retroactively un-tainting thousands of downstream addresses.
"""


class ServiceClassifier:
    """taint_modifier controls propagation: 0.0 = exchange/pool (break chain);
    0.5 = CoinJoin coordinator (pass-through, reduced); 1.0 = unknown/criminal
    (full); 2.0 = mixer (amplify all outputs)."""

    def __init__(self, known_exchange_addrs: set[str], known_pool_addrs: set[str]):
        self.exchanges = known_exchange_addrs   # from WalletExplorer service_labels
        self.pools = known_pool_addrs

    def classify(self, cluster_root: str, members: list[str], stats: dict) -> dict:
        if any(a in self.exchanges for a in members):
            return {"service_type": "EXCHANGE", "confidence": 1.0, "taint_modifier": 0.0}
        if any(a in self.pools for a in members):
            return {"service_type": "MINING_POOL", "confidence": 1.0, "taint_modifier": 0.0}

        # feature-based fallback
        if stats.get("coinbase_input_fraction", 0) > 0.9:
            return {"service_type": "MINING_POOL", "confidence": 0.95, "taint_modifier": 0.0}
        if stats.get("distinct_senders_90d", 0) > 10_000 and stats.get("distinct_recipients_90d", 0) > 10_000:
            return {"service_type": "EXCHANGE", "confidence": 0.8, "taint_modifier": 0.0}
        if stats.get("equal_output_fraction", 0) > 0.40 and stats.get("fixed_denomination_fraction", 0) > 0.30:
            return {"service_type": "COINJOIN_COORDINATOR", "confidence": 0.85, "taint_modifier": 0.5}
        return {"service_type": "UNKNOWN", "confidence": 0.5, "taint_modifier": 1.0}
