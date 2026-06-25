# services/blockchain/run_voting.py
"""Plug all four clustering heuristics (CIO, script-type change, optimal
change, address reuse) into the weighted voter from voting.py."""
from services.blockchain.voting import vote
from services.blockchain.change_heuristic import script_type_change
from services.blockchain.optimal_change import optimal_change
from services.blockchain.addr_reuse import address_reuse_signal


def decide_merge(addr_a, addr_b, tx, clusterer, fee, spending_history) -> tuple[str, float]:
    fired = {
        "CIO": addr_a in [i["address"] for i in tx["inputs"]] and
               addr_b in [i["address"] for i in tx["inputs"]],
        "SCRIPT_CHANGE": script_type_change(tx["inputs"], tx["outputs"], clusterer) == addr_b,
        "OPTIMAL_CHANGE": optimal_change(tx["inputs"], tx["outputs"], fee, clusterer) == addr_b,
        "ADDR_REUSE": address_reuse_signal(addr_b, clusterer.find(addr_a), clusterer, spending_history),
    }
    return vote(fired)   # -> ("MERGE"|"TENTATIVE_MERGE"|"NO_MERGE", confidence)
