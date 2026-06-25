# services/blockchain/cluster.py
"""
Common-Input-Ownership (CIO) clustering with Union-Find.

CIO says: if two addresses both appear as inputs to the same transaction,
the same entity controls both — because only someone holding both private
keys could sign both inputs. This is the one heuristic with a cryptographic
basis. Union-Find merges in near-constant amortised time O(alpha(n)).

The CoinJoin pre-filter is non-negotiable: in a CoinJoin, co-signing inputs
belong to different strangers who deliberately mixed together. Merging
them would corrupt the cluster.
"""
from collections import defaultdict
import networkx as nx
from services.common.coinjoin import is_coinjoin


class AddressClusterer:
    def __init__(self):
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}
        self.merge_reason: dict[str, str] = {}

    def find(self, x: str) -> str:
        if x not in self._parent:
            self._parent[x] = x; self._rank[x] = 0
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])   # path compression
        return self._parent[x]

    def union(self, x: str, y: str, reason: str = "CIO") -> None:
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self._rank[px] < self._rank[py]:
            px, py = py, px
        self._parent[py] = px
        if self._rank[px] == self._rank[py]:
            self._rank[px] += 1
        self.merge_reason[y] = reason

    def cluster(self, G: nx.DiGraph) -> dict[str, list[str]]:
        # group inputs by transaction
        tx_inputs: dict[str, list[str]] = defaultdict(list)
        tx_outvals: dict[str, list[int]] = defaultdict(list)
        for src, dst, d in G.edges(data=True):
            tx_inputs[d["txid"]].append(src)
        # output values per tx (for CoinJoin test) — collect from edges sharing a txid
        for src, dst, d in G.edges(data=True):
            tx_outvals[d["txid"]].append(d["satoshi"])

        merged = skipped = 0
        for txid, senders in tx_inputs.items():
            uniq = list(dict.fromkeys(senders))
            if len(uniq) < 2:
                continue                                   # single input: no signal
            if is_coinjoin(tx_outvals.get(txid, [])):
                skipped += 1
                continue                                   # CoinJoin: do NOT merge
            for other in uniq[1:]:
                self.union(uniq[0], other, "CIO")
                merged += 1
        print(f"  CIO merges: {merged}; CoinJoin txns skipped: {skipped}")
        return self.clusters()

    def clusters(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = defaultdict(list)
        for a in self._parent:
            out[self.find(a)].append(a)
        return dict(out)
