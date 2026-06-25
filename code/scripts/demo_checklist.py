# scripts/demo_checklist.py
"""
[Anaconda Prompt] python scripts/demo_checklist.py

Run this before you leave for a demo. Checks that every table the
dashboard reads from has a non-trivial row count, so you don't discover
an empty table live in front of someone.
"""
import os
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CHECKS = [
    ("seed_addresses", "SELECT COUNT(*) FROM seed_addresses", 50),
    ("service_labels", "SELECT COUNT(*) FROM service_labels", 10),
    ("dark_web_records", "SELECT COUNT(*) FROM dark_web_records", 10),
    ("pre_crime_watchlist", "SELECT COUNT(*) FROM pre_crime_watchlist", 1),
    ("graph_cache (>= 1 cached expansion)", "SELECT COUNT(*) FROM graph_cache", 1),
    ("risk_decisions", "SELECT COUNT(*) FROM risk_decisions", 1),
    ("evaluation_results", "SELECT COUNT(*) FROM evaluation_results", 1),
]


def main():
    conn = psycopg2.connect(os.environ["POSTGRES_URI"])
    all_ok = True
    print("=== BTC-Intel Pre-Demo Data Checklist ===\n")
    for label, query, min_expected in CHECKS:
        with conn.cursor() as cur:
            cur.execute(query)
            count = cur.fetchone()[0]
        ok = count >= min_expected
        all_ok &= ok
        status = "OK" if ok else "EMPTY/LOW"
        print(f"[{status:9}] {label}: {count} rows (expected >= {min_expected})")

    print()
    if all_ok:
        print("All checks passed. Safe to demo.")
    else:
        print("SOME CHECKS FAILED. Run the relevant script before you leave:")
        print("  scripts/collect_seeds.py        -> seed_addresses, service_labels")
        print("  scripts/ingest_archive.py       -> dark_web_records, pre_crime_watchlist")
        print("  scripts/expand_graph.py         -> graph_cache")
        print("  dashboard 'Assess Risk' button  -> risk_decisions")
        print("  scripts/run_eval.py             -> evaluation_results")
        sys.exit(1)


if __name__ == "__main__":
    main()
