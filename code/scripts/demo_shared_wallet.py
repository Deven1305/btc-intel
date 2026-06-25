# scripts/demo_shared_wallet.py
"""
[Anaconda Prompt] python scripts/demo_shared_wallet.py

Demonstrates the shared-wallet contribution: find onion domains connected
by a SHARES_WALLET edge. That coordination signal is invisible to
hyperlink-only graphs (Biryukov-style).
"""
import os
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.graph.onion_graph import OnionGraphBuilder


def demo():
    db_conn = psycopg2.connect(os.environ["POSTGRES_URI"])
    onion_graph = OnionGraphBuilder(
        os.environ["NEO4J_URI"], os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]
    )
    try:
        n_edges = onion_graph.build_from_records(db_conn)
        print(f"Built {n_edges} SHARES_WALLET edges from dark_web_records.")

        groups = onion_graph.find_infrastructure_groups(min_weight=1)
        print(f"Found {len(groups)} infrastructure groups (operators running >1 site):")
        for g in groups[:10]:
            print(f"  group of {len(g)} domains: {g}")
    finally:
        onion_graph.close()


if __name__ == "__main__":
    demo()
