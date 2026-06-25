# services/blockchain/addr_reuse.py
"""
Fourth clustering heuristic: address reuse. High precision, low recall —
when it fires, it is almost always right, but it rarely fires. If an
address that already belongs to cluster C appears again as an output and
is later spent together with other C addresses, that reinforces membership.
"""


def address_reuse_signal(address: str, cluster_root: str, clusterer,
                         spending_history: dict) -> bool:
    """spending_history maps address -> set of txids in which it was an input
    alongside other cluster members."""
    if clusterer.find(address) != cluster_root:
        return False
    co_spends = spending_history.get(address, set())
    # if it was spent in >=2 transactions alongside confirmed cluster members, reuse confirmed
    return len(co_spends) >= 2
