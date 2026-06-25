# services/eval/harness.py
"""
Produces the precision/recall/F1/FPR numbers that make the POC defensible.
Test set: OFAC-confirmed addresses as true positives, WalletExplorer
exchange addresses as true negatives.
"""
from dataclasses import dataclass


@dataclass
class EvalResult:
    precision: float; recall: float; f1: float; fpr: float
    tp: int; fp: int; tn: int; fn: int


def evaluate(engine, load_signals, conn, positives: list[str], negatives: list[str]) -> EvalResult:
    tp = fp = tn = fn = 0
    for addr in positives:                      # known criminal -> should be flagged
        d = engine.classify(addr, load_signals(conn, addr))
        if d.category in ("BLACKLISTED", "WATCHLISTED"):
            tp += 1
        else:
            fn += 1
    for addr in negatives:                       # known clean -> should NOT be flagged
        d = engine.classify(addr, load_signals(conn, addr))
        if d.category == "CLEAN":
            tn += 1
        else:
            fp += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return EvalResult(precision, recall, f1, fpr, tp, fp, tn, fn)


def compare_propagation_methods(taint_engine, G, seeds, service_mod, total_recv,
                                labels: dict[str, bool]) -> dict:
    """Three-way comparison (novel contribution): precision/recall per method."""
    methods = {
        "AMOUNT_WEIGHTED": taint_engine.amount_weighted(G, {s: 1.0 for s in seeds}, service_mod, total_recv),
        "LABEL_PROP": taint_engine.label_propagation(G, {s: 1.0 for s in seeds}),
        "PPR": taint_engine.personalised_pagerank(G, seeds),
    }
    out = {}
    for name, scores in methods.items():
        tp = fp = fn = tn = 0
        for addr, is_criminal in labels.items():
            flagged = scores.get(addr, 0.0) >= 0.35
            if is_criminal and flagged: tp += 1
            elif is_criminal and not flagged: fn += 1
            elif not is_criminal and flagged: fp += 1
            else: tn += 1
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        out[name] = {"precision": round(p, 3), "recall": round(r, 3),
                     "f1": round(2*p*r/(p+r), 3) if (p+r) else 0.0}
    return out
