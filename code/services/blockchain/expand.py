# services/blockchain/expand.py
"""
Expand the transaction graph N hops out from seed addresses using BigQuery's
free crypto_bitcoin public dataset.

Gap I found vs. the attached file: the original expand.py re-queries
BigQuery every time you run it, even for a hop expansion you've already
paid the (free-tier) cost for once. On a free tier capped at 1 TiB/month
that's a real risk if you re-run the dashboard or re-demo the same seeds
multiple times. Fix: cache every hop-expansion result to PostgreSQL
(graph_cache table) keyed by a hash of (sorted seeds, max_hops), and check
the cache before ever calling BigQuery again for the same expansion.

Cost reality (verified June 2026, see README "BigQuery costs" section):
the on-demand "1 TiB query processing free per month" allowance is a
permanent monthly allowance tied to a Cloud Billing account, separate from
the (also real, but EXPIRING) $300/90-day new-customer credit. The
BigQuery "sandbox" mode can be used with no billing account and no card
for light use, but attaching a billing account is what unlocks the full
1 TiB/month allowance reliably for a project doing repeated multi-hop
expansions like this one — see README for the exact tradeoff.
"""
import hashlib
import json
from datetime import datetime, timezone

from google.cloud import bigquery
import networkx as nx


def _cache_key(seeds: list[str], max_hops: int) -> str:
    blob = json.dumps({"seeds": sorted(seeds), "max_hops": max_hops}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


class GraphExpander:
    def __init__(self, project_id: str, db_conn=None):
        self.bq = bigquery.Client(project=project_id)
        self.G = nx.DiGraph()
        self.db = db_conn   # optional: enables the BigQuery-cost cache

    # ── cache layer ──────────────────────────────────────────────────────────
    def _cache_get(self, key: str) -> dict | None:
        if self.db is None:
            return None
        with self.db.cursor() as cur:
            cur.execute("SELECT graph_json FROM graph_cache WHERE cache_key = %s", (key,))
            row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def _cache_put(self, key: str, seeds: list[str], max_hops: int, graph_json: dict) -> None:
        if self.db is None:
            return
        with self.db.cursor() as cur:
            cur.execute("""
                INSERT INTO graph_cache (cache_key, seeds, max_hops, graph_json, cached_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (cache_key) DO UPDATE
                  SET graph_json = EXCLUDED.graph_json, cached_at = EXCLUDED.cached_at
            """, (key, seeds, max_hops, json.dumps(graph_json), datetime.now(timezone.utc)))
        self.db.commit()

    # ── main expansion ───────────────────────────────────────────────────────
    def expand(self, seeds: list[str], max_hops: int = 3, force_refresh: bool = False) -> nx.DiGraph:
        key = _cache_key(seeds, max_hops)
        if not force_refresh:
            cached = self._cache_get(key)
            if cached is not None:
                print(f"  [cache hit] graph expansion for {len(seeds)} seeds / {max_hops} hops "
                      f"— no BigQuery call made")
                self.G = nx.node_link_graph(cached, directed=True)
                return self.G

        frontier = set(seeds)
        seen = set(seeds)
        for s in seeds:
            self.G.add_node(s, is_seed=True)

        for hop in range(max_hops):
            if not frontier:
                break
            batch = list(frontier)[:200]
            addr_list = "','".join(a.replace("'", "") for a in batch)
            query = f"""
            WITH frontier_txns AS (
              SELECT DISTINCT i.spent_transaction_hash AS txid,
                     i.addresses[OFFSET(0)] AS sender
              FROM `bigquery-public-data.crypto_bitcoin.inputs` i
              WHERE i.addresses[OFFSET(0)] IN ('{addr_list}')
            )
            SELECT f.sender,
                   o.addresses[OFFSET(0)]  AS recipient,
                   o.value                 AS satoshi,
                   t.hash                  AS txid,
                   t.block_timestamp       AS ts,
                   ARRAY_LENGTH(t.inputs)  AS n_inputs,
                   ARRAY_LENGTH(t.outputs) AS n_outputs
            FROM frontier_txns f
            JOIN `bigquery-public-data.crypto_bitcoin.outputs` o ON o.transaction_hash = f.txid
            JOIN `bigquery-public-data.crypto_bitcoin.transactions` t ON t.hash = f.txid
            WHERE o.addresses[OFFSET(0)] IS NOT NULL
              AND o.addresses[OFFSET(0)] != f.sender
            LIMIT 100000
            """
            df = self.bq.query(query).to_dataframe()
            new_frontier = set()
            for _, row in df.iterrows():
                self.G.add_edge(row["sender"], row["recipient"],
                                satoshi=int(row["satoshi"]), txid=row["txid"],
                                timestamp=str(row["ts"]), n_inputs=int(row["n_inputs"]),
                                n_outputs=int(row["n_outputs"]), hop=hop + 1)
                if row["recipient"] not in seen:
                    seen.add(row["recipient"]); new_frontier.add(row["recipient"])
            frontier = new_frontier
            print(f"  hop {hop+1}: +{len(new_frontier)} addresses "
                  f"({self.G.number_of_nodes()} total)")

        self._cache_put(key, seeds, max_hops, nx.node_link_data(self.G))
        return self.G

    def fetch_total_received(self, addresses: list[str]) -> dict[str, int]:
        """Total satoshi each address ever received (denominator for taint fraction)."""
        out: dict[str, int] = {}
        for i in range(0, len(addresses), 200):
            batch = "','".join(a.replace("'", "") for a in addresses[i:i + 200])
            df = self.bq.query(f"""
                SELECT addresses[OFFSET(0)] AS address, SUM(value) AS total_received
                FROM `bigquery-public-data.crypto_bitcoin.outputs`
                WHERE addresses[OFFSET(0)] IN ('{batch}')
                GROUP BY 1
            """).to_dataframe()
            for _, r in df.iterrows():
                out[r["address"]] = int(r["total_received"])
        return out
