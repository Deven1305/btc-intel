# services/blockchain/taproot.py
"""
Taproot's P2TR outputs all look identical on-chain whether they wrap a
single key, a 100-of-100 multisig, or a complex script. The script-type
change heuristic therefore yields no signal for P2TR. We do not guess —
we flag P2TR transactions as CLUSTERING_UNRESOLVED and apply only CIO to
them (CIO remains valid: co-signing still proves co-ownership even when
script type is hidden).

Honest novelty note: a 2025 paper, "Block Number-Based Address Clustering
for Bitcoin Taproot Upgrade," proposes a confirmation-count heuristic for
P2TR — a novel P2TR clustering heuristic is no longer an open research gap.
The defensible position here is to flag the gap and measure precision
degradation, not to claim a new P2TR heuristic.
"""


def clustering_status(tx_inputs: list[dict], tx_outputs: list[dict]) -> str:
    has_taproot = any(o.get("script_type") == "witness_v1_taproot" for o in tx_outputs)
    return "CLUSTERING_UNRESOLVED" if has_taproot else "RESOLVED"
