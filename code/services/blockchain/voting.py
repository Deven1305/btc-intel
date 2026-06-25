# services/blockchain/voting.py
"""
No single clustering heuristic is perfect, so the four heuristics vote with
weights and we merge only when their combined confidence clears a
threshold. 2024 weights lower CIO from 0.50 to 0.40 vs. Delgado 2021's
calibration, redistributing to the others, because CoinJoin adoption
(Wasabi 2.0, Whirlpool) has grown sharply since 2021, raising CIO's
false-positive risk if used at full weight alone.
"""
WEIGHTS = {"CIO": 0.40, "SCRIPT_CHANGE": 0.30, "OPTIMAL_CHANGE": 0.20, "ADDR_REUSE": 0.10}
AUTO_MERGE = 0.65          # >= 0.65 -> confident merge
TENTATIVE  = 0.40          # 0.40-0.65 -> tentative merge (flagged for review)


def vote(fired: dict[str, bool]) -> tuple[str, float]:
    score = sum(WEIGHTS[h] for h, did in fired.items() if did and h in WEIGHTS)
    if score >= AUTO_MERGE:
        return "MERGE", score
    if score >= TENTATIVE:
        return "TENTATIVE_MERGE", score
    return "NO_MERGE", score
