# services/risk/train_anomaly.py
"""
Layer 3 of the risk engine uses an Isolation Forest trained on KNOWN-CLEAN
addresses (WalletExplorer exchange/service addresses). No labelled
negatives needed — Isolation Forest learns the shape of "normal" and
scores deviations as anomalous.
"""
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest


FEATURE_NAMES = [
    "tx_count", "total_received_btc", "total_sent_btc", "avg_tx_value",
    "in_degree", "out_degree", "peel_chain_len", "fan_out_ratio",
    "consolidation_frac", "active_days", "dormancy_max_gap_days",
]


def train_isolation_forest(clean_feature_matrix: np.ndarray, out_path: str):
    clf = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
    clf.fit(clean_feature_matrix)
    joblib.dump({"model": clf, "features": FEATURE_NAMES}, out_path)
    return clf


if __name__ == "__main__":
    # Smoke test with synthetic data; replace with real WalletExplorer features.
    rng = np.random.default_rng(42)
    fake_clean = rng.normal(size=(500, len(FEATURE_NAMES)))
    train_isolation_forest(fake_clean, "models/iforest.joblib")
    print("Trained and saved models/iforest.joblib")
