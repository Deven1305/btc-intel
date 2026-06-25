# services/blockchain/change_heuristic.py
"""
Script-type change-address heuristic (~5% FPR vs ~23% FPR for the naive
"fresh address = change" heuristic, per Delgado-Segura 2021). Asks: which
output has the same script type as the inputs? Invariant to amount, more
precise than the naive version, and we deliberately skip Taproot (P2TR)
because all P2TR outputs look identical (see taproot.py).
"""
from collections import Counter


def script_type_change(tx_inputs: list[dict], tx_outputs: list[dict],
                       clusterer) -> str | None:
    """
    Return the change-address candidate (same script type as inputs, fresh address),
    or None if ambiguous. tx_* items are {'address','script_type'}.
    """
    if len(tx_outputs) != 2:
        return None                                   # apply only to 2-output txns
    in_types = [i["script_type"] for i in tx_inputs if i.get("script_type")]
    if not in_types:
        return None
    dominant = Counter(in_types).most_common(1)[0][0]
    if dominant == "witness_v1_taproot":
        return None                                   # Taproot: unreliable, skip
    candidates = [o["address"] for o in tx_outputs
                  if o.get("script_type") == dominant
                  and clusterer.find(o["address"]) == o["address"]]  # fresh = own root
    return candidates[0] if len(candidates) == 1 else None
