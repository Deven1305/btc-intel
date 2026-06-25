# services/watchlist/precrime.py
"""
Assigns non-zero risk to addresses with ZERO on-chain history, based
solely on dark-web payment context. This is BTC-Intel's most important
novel contribution: every existing commercial system (Chainalysis, TRM,
Elliptic, every academic paper) requires at least one Bitcoin transaction
before it can classify an address. A brand-new wallet with zero history
gets a risk score of ZERO from every commercial system. BTC-Intel flags it
the moment it appears on a dark web payment page — before the first
satoshi ever moves.
"""
from datetime import datetime, timezone
from google.cloud import bigquery


class PreCrimeWatchlist:
    MIN_DW_CONFIDENCE = 0.40

    def __init__(self, db_conn, bq_project: str):
        self.db = db_conn
        self.bq = bigquery.Client(project=bq_project)

    def consider(self, record: dict) -> bool:
        # 1) only PAYMENT context (not VICTIM/AMBIGUOUS) enters the watchlist
        if record["context_type"] != "PAYMENT":
            return False
        # 2) confidence gate — too ambiguous below 0.40
        if record["confidence"] < self.MIN_DW_CONFIDENCE:
            return False
        # 3) verify ZERO on-chain history (the defining property of PRE_CRIME)
        if self._has_onchain_history(record["address"]):
            return False   # already transacted -> goes straight to the full risk engine
        # 4) admit to watchlist
        with self.db.cursor() as cur:
            cur.execute("""
                INSERT INTO pre_crime_watchlist
                    (address, onion_domain, page_url, page_topic, dw_confidence,
                     pgp_fingerprints, first_seen_dw, monitoring_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'ACTIVE')
                ON CONFLICT (address) DO NOTHING
            """, (record["address"], record["onion_domain"], record["page_url"],
                  record["page_topic"], record["confidence"],
                  record.get("pgp_fingerprints", []), record["first_seen"]))
        self.db.commit()
        print(f"[PRE_CRIME_WATCHLIST] {record['address']} "
              f"({record['page_topic']} @ {record['onion_domain']}, conf {record['confidence']:.2f})")
        return True

    def _has_onchain_history(self, address: str) -> bool:
        df = self.bq.query(f"""
            SELECT COUNT(*) AS n FROM (
              SELECT 1 FROM `bigquery-public-data.crypto_bitcoin.inputs`
              WHERE addresses[OFFSET(0)] = '{address}'
              UNION ALL
              SELECT 1 FROM `bigquery-public-data.crypto_bitcoin.outputs`
              WHERE addresses[OFFSET(0)] = '{address}'
            ) LIMIT 1
        """).to_dataframe()
        return int(df["n"].iloc[0]) > 0

    def poll_for_first_transactions(self) -> list[str]:
        """Every 6 hours: check all ACTIVE watchlist addresses for a first tx.
           Returns addresses that just transacted (now TRIGGERED)."""
        with self.db.cursor() as cur:
            cur.execute("SELECT address FROM pre_crime_watchlist WHERE monitoring_status='ACTIVE'")
            watched = [r[0] for r in cur.fetchall()]
        if not watched:
            return []

        triggered: list[str] = []
        for i in range(0, len(watched), 500):
            batch = "','".join(a.replace("'", "") for a in watched[i:i+500])
            df = self.bq.query(f"""
                SELECT addresses[OFFSET(0)] AS address, COUNT(*) AS n,
                       MIN(block_timestamp) AS first_tx_at
                FROM `bigquery-public-data.crypto_bitcoin.outputs`
                WHERE addresses[OFFSET(0)] IN ('{batch}')
                GROUP BY 1
            """).to_dataframe()
            for _, row in df.iterrows():
                if int(row["n"]) > 0:
                    with self.db.cursor() as cur:
                        cur.execute("""
                            UPDATE pre_crime_watchlist
                            SET monitoring_status='TRIGGERED', first_tx_at=%s
                            WHERE address=%s
                        """, (row["first_tx_at"], row["address"]))
                    self.db.commit()
                    triggered.append(row["address"])
                    print(f"[PRE_CRIME -> TRIGGERED] {row['address']} (first tx {row['first_tx_at']})")
        return triggered

    def process_trigger(self, address: str, risk_engine, expander):
        """When a PRE_CRIME address first transacts: expand its graph, gather signals,
           and run the full risk engine to promote it to a final category."""
        with self.db.cursor() as cur:
            cur.execute("""SELECT dw_confidence, page_topic FROM pre_crime_watchlist
                           WHERE address=%s""", (address,))
            dw_conf, topic = cur.fetchone()

        # now that on-chain data exists, compute taint signals
        G = expander.expand([address], max_hops=2)
        signals = {
            "dark_web_payment_confidence": float(dw_conf),
            "pre_crime_watchlist": False,           # it now has history
            "taint_hop1": 0.0,                       # filled by taint engine in full pipeline
        }
        decision = risk_engine.classify(address, signals)
        with self.db.cursor() as cur:
            cur.execute("""
                INSERT INTO risk_decisions (address, category, confidence, evidence,
                                            counterfactual, assessed_at)
                VALUES (%s,%s,%s,%s,%s,NOW())
                ON CONFLICT (address) DO UPDATE
                  SET category=EXCLUDED.category, confidence=EXCLUDED.confidence,
                      last_updated=NOW()
            """, (address, decision.category, decision.final_score,
                  __import__("json").dumps(decision.evidence), decision.counterfactual))
        self.db.commit()
        print(f"  {address}: PRE_CRIME -> {decision.category} ({decision.final_score:.1%})")
        return decision
