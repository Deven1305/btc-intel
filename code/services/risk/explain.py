# services/risk/explain.py
"""
SHAP explanation for the Layer-3 Isolation Forest anomaly score. This
explains ONLY the on-chain anomaly model's feature contributions — nothing
about OFAC, dark web evidence, or taint. Those are explained directly by
the evidence list in RiskDecision (services/risk/engine.py); SHAP has no
role there because that scoring is already fully transparent rule-by-rule.
"""
import shap
import numpy as np


def explain_anomaly(bundle, feature_vector: np.ndarray) -> list[dict]:
    """Return per-feature contributions for ONE address's anomaly score."""
    model, names = bundle["model"], bundle["features"]
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(feature_vector.reshape(1, -1))[0]
    ranked = sorted(zip(names, values), key=lambda x: abs(x[1]), reverse=True)
    return [{"feature": n, "contribution": round(float(v), 4),
             "direction": "raises anomaly" if v > 0 else "lowers anomaly"}
            for n, v in ranked]


if __name__ == "__main__":
    import joblib
    bundle = joblib.load("models/iforest.joblib")
    fv = np.zeros(len(bundle["features"]))
    for row in explain_anomaly(bundle, fv)[:5]:
        print(f"{row['feature']}: {row['contribution']} ({row['direction']})")
