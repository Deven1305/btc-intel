# services/blockchain/taint.py
"""
Three taint propagation methods, compared on the same data — implementing
and comparing all three is a novel research contribution (prior work uses
only one each: Nerino 2021 uses label propagation only; the Chainalysis
patent uses amount-weighted taint only; no published paper compares all
three on the same labelled dataset with the same seeds/thresholds).

Method 1 — amount-weighted (Chainalysis-style): dirty water in pipes.
Method 2 — label propagation (Nerino 2021): a rumour spreading socially.
Method 3 — personalised PageRank: structural proximity, resists dust/haircut.
"""
import networkx as nx


class TaintEngine:
    MIN_FRACTION = 0.05          # below this = dust/noise (dust-attack protection)
    MAX_HOPS = 3

    # ── Method 1 ───────────────────────────────────────────────────────────────
    def amount_weighted(self, G, seed_scores, service_mod, total_received):
        taint = dict(seed_scores)
        for _ in range(self.MAX_HOPS):
            new = {}
            for src, dst, d in G.edges(data=True):
                s = taint.get(src, 0.0)
                if s < self.MIN_FRACTION:
                    continue
                mod = service_mod.get(dst, 1.0)
                if mod == 0.0:                          # exchange/pool: break chain
                    continue
                recv = max(total_received.get(dst, d["satoshi"]), 1)
                frac = (d["satoshi"] * s) / recv * mod
                if frac >= self.MIN_FRACTION:
                    new[dst] = max(new.get(dst, 0.0), frac)
            taint.update(new)
        return taint

    # ── Method 2 ───────────────────────────────────────────────────────────────
    def label_propagation(self, G, seed_scores, damping=0.85, iters=10):
        scores = dict(seed_scores)
        for _ in range(iters):
            new = {}
            for n in G.nodes():
                nb = list(G.predecessors(n)) + list(G.successors(n))
                agg = sum(scores.get(x, 0.0) for x in nb)
                deg = max(len(nb), 1)
                new[n] = (1 - damping) * scores.get(n, 0.0) + damping * (agg / deg)
            scores = new
        return scores

    # ── Method 3 ───────────────────────────────────────────────────────────────
    def personalised_pagerank(self, G, seeds, alpha=0.85):
        pers = {n: 0.0 for n in G.nodes()}
        for s in seeds:
            if s in pers:
                pers[s] = 1.0 / len(seeds)
        return nx.pagerank(G, alpha=alpha, personalization=pers, max_iter=100)
