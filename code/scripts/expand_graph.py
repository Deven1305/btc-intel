# scripts/expand_graph.py
"""
[Anaconda Prompt] python scripts/expand_graph.py --hops 3 --seeds-from-db --limit-seeds 50

See setup/windows/06_resource_budget.md for why you might want
--limit-seeds 20 --hops 2 on the 24 GB laptop instead of the 50/3 example
above (which is fine on the 32 GB desktop).
"""
import argparse
import os
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.blockchain.expand import GraphExpander


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hops", type=int, default=3)
    ap.add_argument("--seeds-from-db", action="store_true",
                    help="Load seeds from seed_addresses instead of --seeds")
    ap.add_argument("--limit-seeds", type=int, default=50,
                    help="Cap the number of seeds used (reduces graph size roughly linearly)")
    ap.add_argument("--seeds", nargs="*", default=None,
                    help="Explicit list of seed addresses, instead of --seeds-from-db")
    ap.add_argument("--force-refresh", action="store_true",
                    help="Ignore the graph_cache and re-query BigQuery even on a cache hit")
    args = ap.parse_args()

    conn = psycopg2.connect(os.environ["POSTGRES_URI"])

    if args.seeds_from_db:
        with conn.cursor() as cur:
            cur.execute("SELECT address FROM seed_addresses ORDER BY confidence DESC LIMIT %s",
                       (args.limit_seeds,))
            seeds = [r[0] for r in cur.fetchall()]
    elif args.seeds:
        seeds = args.seeds[:args.limit_seeds]
    else:
        print("Provide --seeds-from-db or --seeds <addr1> <addr2> ...")
        sys.exit(1)

    if not seeds:
        print("No seeds found — run scripts/collect_seeds.py first.")
        sys.exit(1)

    print(f"Expanding {len(seeds)} seeds, {args.hops} hops...")
    expander = GraphExpander(project_id=os.environ["BIGQUERY_PROJECT_ID"], db_conn=conn)
    G = expander.expand(seeds, max_hops=args.hops, force_refresh=args.force_refresh)
    print(f"[OK] Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


if __name__ == "__main__":
    main()
