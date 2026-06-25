# services/risk/engine.py
"""
Three-layer risk classification engine.

Plain-English summary of the Bayesian fusion: start with a PRIOR belief
that roughly 1 in 1,000 Bitcoin addresses is criminal (prior = 0.001). Each
piece of evidence multiplies that probability up or down by a likelihood
ratio (LR). An OFAC confirmation multiplies it by ~1000x. A dark-web
payment-context appearance multiplies it by ~50x. Evidence that the address
belongs to a verified exchange divides it by ~20 (LR 0.05). The
multiplication happens in log space (adding log-likelihood-ratios to a
log-odds prior) for numerical stability, then converts back to a
probability. This combines weak and strong signals proportionally — a
wallet whose taint was diluted by a mixer to 3% but which also appears in
ten dark-web listings can still cross the threshold, because the signals
stack.
"""
import math
from dataclasses import dataclass, field


@dataclass
class RiskDecision:
    address: str
    category: str                      # BLACKLISTED | WATCHLISTED | PRE_CRIME_WATCHLIST | CLEAN
    final_score: float                 # 0.0 - 1.0 posterior probability
    evidence: list[dict] = field(default_factory=list)
    counterfactual: str = ""
    contradictions: list[str] = field(default_factory=list)
    sources_checked: list[str] = field(default_factory=list)
    brief: str = ""                    # filled by the LLM narration layer, empty until requested


class ThreeLayerRiskEngine:
    PRIOR = 0.001                      # 1 in 1000 addresses criminal
    BLACKLIST_THRESHOLD = 0.85
    WATCHLIST_THRESHOLD = 0.35

    def __init__(self, isolation_forest=None):
        self.iforest = isolation_forest     # pre-trained on WalletExplorer clean addresses

    # ── Layer 1: fast deterministic rules ──────────────────────────────────────
    def fast_path(self, address: str, signals: dict) -> RiskDecision | None:
        if signals.get("ofac_confirmed"):
            return RiskDecision(address, "BLACKLISTED", 1.0,
                [{"source": "OFAC_SDN", "detail": signals.get("ofac_entity", "OFAC SDN match"),
                  "lr": 1000.0, "contribution": "deterministic"}],
                "N/A — OFAC designation is legally deterministic.",
                sources_checked=["OFAC_SDN"])
        if signals.get("un_confirmed"):
            return RiskDecision(address, "BLACKLISTED", 1.0,
                [{"source": "UN_SANCTIONS", "detail": "UN consolidated list match",
                  "lr": 800.0, "contribution": "deterministic"}],
                "N/A — UN sanction is deterministic.", sources_checked=["UN_SANCTIONS"])
        if signals.get("exchange_verified"):
            return RiskDecision(address, "CLEAN", 0.02,
                [{"source": "EXCHANGE_VERIFIED", "detail": "Known exchange address (KYC boundary)",
                  "lr": 0.05, "contribution": "deterministic"}],
                "N/A — verified exchange.", sources_checked=["EXCHANGE_VERIFIED"])
        if signals.get("mining_pool"):
            return RiskDecision(address, "CLEAN", 0.01,
                [{"source": "MINING_POOL", "detail": "Mining pool — mints new BTC, no criminal origin",
                  "lr": 0.01, "contribution": "deterministic"}],
                "N/A — mining pool.", sources_checked=["MINING_POOL"])
        if signals.get("dust_attack"):
            return RiskDecision(address, "CLEAN", 0.0,
                [{"source": "DUST_FILTER", "detail": "Dust received from criminal — not inculpatory",
                  "lr": 0.01, "contribution": "deterministic"}],
                "N/A — dust filter.", sources_checked=["DUST_FILTER"])
        return None

    # ── Layer 2: provenance-aware Bayesian fusion ──────────────────────────────
    LIKELIHOOD_RATIOS = {
        "PGP_CRIMINAL_LINK": 100.0, "DARK_WEB_PAYMENT": 50.0,
        "COMMERCIAL_CONSENSUS": 30.0, "TAINT_HOP_1": 20.0, "BEHAVIORAL_ANOMALY": 8.0,
        "TAINT_HOP_2": 8.0, "COMMUNITY_REPORT": 5.0, "TAINT_HOP_3": 3.0,
        "VICTIM_CONTEXT": 0.2,
    }
    # Each signal's provenance: the source(s) it ultimately derives from.
    PROVENANCE = {
        "COMMERCIAL_CONSENSUS": ["OFAC_SDN"],   # commercial flags re-label OFAC
        "COMMUNITY_REPORT": [],                  # community reports are independent here
    }

    def _signal_to_lr_key(self, signals: dict) -> list[str]:
        keys = []
        if signals.get("pgp_criminal_link"):                          keys.append("PGP_CRIMINAL_LINK")
        if signals.get("dark_web_payment_confidence", 0) >= 0.40:     keys.append("DARK_WEB_PAYMENT")
        if signals.get("commercial_consensus"):                       keys.append("COMMERCIAL_CONSENSUS")
        if signals.get("taint_hop1", 0) >= 0.05:                      keys.append("TAINT_HOP_1")
        if signals.get("taint_hop2", 0) >= 0.05:                      keys.append("TAINT_HOP_2")
        if signals.get("taint_hop3", 0) >= 0.02:                      keys.append("TAINT_HOP_3")
        if signals.get("behavioral_anomaly"):                         keys.append("BEHAVIORAL_ANOMALY")
        if signals.get("community_report"):                           keys.append("COMMUNITY_REPORT")
        if signals.get("victim_context"):                             keys.append("VICTIM_CONTEXT")
        return keys

    def bayesian_fusion(self, signals: dict, already_active: set[str]) -> tuple[float, list[dict]]:
        log_odds = math.log(self.PRIOR / (1 - self.PRIOR))
        active = set(already_active)            # seeded with any Layer-1 deterministic source
        contribs: list[dict] = []

        # apply strongest signals first -> provenance skip is deterministic
        for key in sorted(self._signal_to_lr_key(signals),
                          key=lambda k: self.LIKELIHOOD_RATIOS.get(k, 1.0), reverse=True):
            provenance = self.PROVENANCE.get(key, [])
            if any(p in active for p in provenance):
                contribs.append({"source": key, "skipped": True,
                                 "reason": f"provenance {provenance} already counted"})
                continue
            lr = self.LIKELIHOOD_RATIOS[key]
            c = math.log(lr)
            log_odds += c
            active.add(key)
            contribs.append({"source": key, "lr": lr,
                             "contribution": round(c, 3), "log_odds_after": round(log_odds, 3)})
        posterior = 1 / (1 + math.exp(-log_odds))
        return posterior, contribs

    # ── Layer 3: Isolation Forest anomaly score (supplementary) ────────────────
    def anomaly_score(self, feature_vector) -> float:
        if self.iforest is None or feature_vector is None:
            return 0.0
        raw = self.iforest.decision_function([feature_vector])[0]
        # map decision_function to [0,1] where 1 = most anomalous
        return max(0.0, min(1.0, 1 - (raw - self.iforest.offset_) / (1 - self.iforest.offset_)))

    # ── orchestration ──────────────────────────────────────────────────────────
    def classify(self, address: str, signals: dict) -> RiskDecision:
        fast = self.fast_path(address, signals)
        if fast:
            return fast

        active_seed = {"OFAC_SDN"} if signals.get("ofac_confirmed") else set()
        bayes, contribs = self.bayesian_fusion(signals, active_seed)

        fv = signals.get("feature_vector")
        if fv is not None:
            anomaly = self.anomaly_score(fv)
            score = 0.70 * bayes + 0.30 * anomaly          # anomaly is supplementary
        else:
            score = bayes

        if score >= self.BLACKLIST_THRESHOLD:
            category = "BLACKLISTED"
        elif score >= self.WATCHLIST_THRESHOLD:
            category = "WATCHLISTED"
        elif signals.get("pre_crime_watchlist") and signals.get("dark_web_payment_confidence", 0) >= 0.40:
            category = "PRE_CRIME_WATCHLIST"
        else:
            category = "CLEAN"

        contradictions = []
        if signals.get("victim_context") and score > 0.5:
            contradictions.append(
                "Victim-context classifier flagged this as a potential victim "
                f"(applies LR 0.2 = {abs(math.log(0.2)):.2f} exculpatory log-odds).")

        return RiskDecision(
            address=address, category=category, final_score=round(score, 4),
            evidence=[c for c in contribs if not c.get("skipped")],
            counterfactual=self._counterfactual(score, contribs),
            contradictions=contradictions,
            sources_checked=["OFAC_SDN", "UN_SANCTIONS", "DARK_WEB", "BLOCKCHAIN_GRAPH"],
        )

    def _counterfactual(self, score: float, contribs: list[dict]) -> str:
        """Smallest set of evidence whose removal drops the score below WATCHLISTED."""
        if score <= self.WATCHLIST_THRESHOLD:
            return f"Score {score:.3f} is already below the WATCHLISTED threshold ({self.WATCHLIST_THRESHOLD})."
        applied = [c for c in contribs if not c.get("skipped")]
        # current log-odds:
        log_odds = math.log(score / (1 - score))
        removed = []
        for c in sorted(applied, key=lambda x: abs(x.get("contribution", 0)), reverse=True):
            log_odds -= c.get("contribution", 0)
            removed.append(c["source"])
            if 1 / (1 + math.exp(-log_odds)) <= self.WATCHLIST_THRESHOLD:
                break
        new_p = 1 / (1 + math.exp(-log_odds))
        return (f"Score drops to {new_p:.3f} (below WATCHLISTED) if these evidence "
                f"sources are removed: {', '.join(removed)}.")


if __name__ == "__main__":
    engine = ThreeLayerRiskEngine()
    decision = engine.classify("1ExampleAddress", {
        "dark_web_payment_confidence": 0.75,
        "taint_hop1": 0.30,
        "community_report": True,
    })
    print(decision.category, decision.final_score)
    print(decision.counterfactual)
