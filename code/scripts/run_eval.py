# scripts/run_eval.py
"""
[Anaconda Prompt] python scripts/run_eval.py

Persists precision/recall/F1/FPR results for the dashboard's evaluation panel.
"""
import os
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.eval.harness import evaluate
from services.risk.engine import ThreeLayerRiskEngine
from dashboard.app import load_signals   # reuse the signal loader


def main():
    conn = psycopg2.connect(os.environ["POSTGRES_URI"])
    with conn.cursor() as cur:
        cur.execute("SELECT address FROM seed_addresses WHERE source='OFAC_SDN' LIMIT 50")
        positives = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT address FROM service_labels WHERE label_type='EXCHANGE' LIMIT 100")
        negatives = [r[0] for r in cur.fetchall()]
    res = evaluate(ThreeLayerRiskEngine(), load_signals, conn, positives, negatives)
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO evaluation_results
            (run_id, dataset, precision, recall, f1, fpr, tp_count, fp_count, tn_count, fn_count, notes)
            VALUES ('poc-eval','OFAC+WalletExplorer',%s,%s,%s,%s,%s,%s,%s,%s,'POC evaluation run')""",
            (res.precision, res.recall, res.f1, res.fpr, res.tp, res.fp, res.tn, res.fn))
    conn.commit()
    print(f"precision={res.precision:.3f} recall={res.recall:.3f} f1={res.f1:.3f} fpr={res.fpr:.3f}")


if __name__ == "__main__":
    main()
