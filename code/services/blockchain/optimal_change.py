# services/blockchain/optimal_change.py
"""
Optimal-change heuristic: identifies as change the output whose value
equals the exact remainder of (total inputs - payment - fee). Independent
of script type, complements the script-type heuristic.
"""


def optimal_change(tx_inputs: list[dict], tx_outputs: list[dict],
                   fee: int, clusterer) -> str | None:
    if len(tx_outputs) != 2:
        return None
    total_in = sum(i["value"] for i in tx_inputs)
    for i, out in enumerate(tx_outputs):
        other = tx_outputs[1 - i]
        # 'out' is change if it equals total_in - other_output - fee (within dust slack)
        if abs(out["value"] - (total_in - other["value"] - fee)) <= 546:  # dust limit
            if clusterer.find(out["address"]) == out["address"]:          # fresh address
                return out["address"]
    return None
