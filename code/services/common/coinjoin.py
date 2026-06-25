# services/common/coinjoin.py
"""
CoinJoin is a privacy technique where strangers deliberately combine their
transactions so no observer can tell which input paid which output. If
clustering naively assumed "co-signers = same owner" (the CIO heuristic),
it would wrongly merge those strangers. This detector flags CoinJoin-shaped
transactions so clustering can skip them. Pure math over a list of output
values — no network calls, no blockchain access of its own (the values are
supplied by whatever already fetched the transaction, e.g. expand.py).
"""
from collections import Counter

COINJOIN_EQUAL_FRACTION = 0.40   # >=40% identical output values ...
COINJOIN_MIN_OUTPUTS    = 5      # ... AND >=5 outputs => likely CoinJoin coordination


def is_coinjoin(output_values: list[int]) -> bool:
    """True if a transaction's output-value shape looks like a coordinated
    mix (Wasabi uses fixed 0.1 BTC denominations; JoinMarket uses variable
    amounts; this catches the general coordinated-mix shape, not one mixer)."""
    if len(output_values) < COINJOIN_MIN_OUTPUTS:
        return False
    most_common = Counter(output_values).most_common(1)[0][1]
    return most_common / len(output_values) >= COINJOIN_EQUAL_FRACTION


if __name__ == "__main__":
    # 5 outputs, 4 of them identical (0.1 BTC denomination) -> looks like CoinJoin
    print(is_coinjoin([10_000_000, 10_000_000, 10_000_000, 10_000_000, 3_000_000]))
    # Ordinary payment + change -> not CoinJoin
    print(is_coinjoin([5_000_000, 1_200_000]))
